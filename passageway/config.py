"""Configuration: environment variables for the core, one TOML file for connectors (docs/install.md)."""

import re
import sys
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from mcp.server.auth.routes import validate_issuer_url
from pydantic import AnyHttpUrl

from passageway.protocol import MAX_LINE_BYTES, MAX_OUTPUT_BYTES


class ConfigError(Exception):
    pass


DEFAULT_TOOL_DESCRIPTION = (
    "Search the user's indexed sources (documents, notes, decisions, how their systems and tools actually "
    "behave) and get up to 3 short passages with links. Call it on your own before a task the sources may "
    "cover, when you hit an unfamiliar error, host or service, and before making a decision they may already "
    "have made. Returns nothing-relevant when there is no match. Open the link for the full document.")

DEFAULT_INSTRUCTIONS = (
    "This server searches the user's indexed sources: their documents, notes, decisions and how their systems "
    "and tools actually behave. Call `recall` before starting a task the sources may cover, when you hit an "
    "unfamiliar error, host or service, and before making a decision they may already have made, even when you "
    "think you know the answer: the sources hold what is true for this user. A hit is a pointer: open its link "
    "for the full document before relying on it. If the context already holds passages headed \"Recall results\", "
    "those came from this server; don't search for the same thing again.")

_NAME = re.compile(r"[a-z0-9][a-z0-9_-]*")


@dataclass(frozen=True)
class ConnectorConfig:
    name: str
    command: tuple[str, ...]
    env: dict[str, str]
    secrets: dict[str, str]  # already resolved from env:NAME references
    timeout: float = 300.0
    max_line_bytes: int = MAX_LINE_BYTES
    max_output_bytes: int = MAX_OUTPUT_BYTES
    max_delete_fraction: float = 0.3  # a reconcile that would delete more than this share of a source is refused


EMBEDDER_KINDS = ("onnx", "command")
_ONNX_KEYS = {"kind", "min_similarity", "model_dir"}
_COMMAND_KEYS = {"kind", "command", "env", "secrets", "min_similarity", "batch_size", "timeout"}


@dataclass(frozen=True)
class EmbedderConfig:
    """How texts become vectors: the built-in ONNX model, or any program speaking the embedder protocol."""
    kind: str = "onnx"
    command: tuple[str, ...] = ()
    env: dict[str, str] = field(default_factory=dict)
    secrets: dict[str, str] = field(default_factory=dict)  # already resolved from env:NAME references
    min_similarity: float | None = None  # the relevance gate of this model; None keeps the built-in default
    batch_size: int = 32  # texts per request
    timeout: float = 60.0  # seconds per request
    model_dir: Path | None = None  # onnx only; None: PASSAGEWAY_MODEL_DIR


@dataclass
class Config:
    password: str  # PASSAGEWAY_LOGIN_PASSWORD: static Bearer token and the OAuth login page's password
    connectors: list[ConnectorConfig]
    data_dir: Path
    model_dir: Path
    base_url: str | None = None  # public URL; set, it turns on OAuth for /mcp
    host: str = "127.0.0.1"
    port: int = 8082
    poll_seconds: int = 60
    reconcile_seconds: int = 1800
    log_level: str = "INFO"
    tool_description: str = DEFAULT_TOOL_DESCRIPTION
    instructions: str = DEFAULT_INSTRUCTIONS
    min_similarity: float | None = None  # the relevance gate; None keeps the embedder preset's value
    embedder: EmbedderConfig = field(default_factory=EmbedderConfig)  # the one the server uses
    embedders: dict[str, EmbedderConfig] = field(default_factory=dict)  # candidates for `passageway eval compare`


def default_config_path() -> Path:
    return Path.home() / ".config" / "passageway" / "passageway.toml"


def default_data_dir() -> Path:
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "passageway"
    return Path.home() / ".local" / "share" / "passageway"


def _int(env: Mapping[str, str], key: str, default: int) -> int:
    raw = env.get(key)
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        raise ConfigError(f"{key} must be an integer, got {raw!r}") from None


def _resolve(connector: str, ref: object, env: Mapping[str, str], what: str = "connector") -> str:
    if not isinstance(ref, str) or not ref.startswith("env:") or len(ref) == 4:
        raise ConfigError(f"{what} {connector!r}: a secret must be a reference like \"env:NAME\" (in 'secrets')")
    var = ref[4:]
    if not env.get(var):
        raise ConfigError(f"{what} {connector!r}: the environment variable {var} is not set")
    return env[var]


def _table(connector: str, raw: dict, key: str, what: str = "connector") -> dict[str, str]:
    table = raw.get(key, {})
    if not isinstance(table, dict) or not all(isinstance(v, str) for v in table.values()):
        raise ConfigError(f"{what} {connector!r}: '{key}' must be a table of strings")
    return table


def _embedder(name: str, raw: object, env: Mapping[str, str]) -> EmbedderConfig:
    where = f"embedder {name!r}"
    if not isinstance(raw, dict):
        raise ConfigError(f"{where}: must be a table")
    kind = raw.get("kind", "onnx")
    if kind not in EMBEDDER_KINDS:
        raise ConfigError(f"{where}: 'kind' must be one of {', '.join(EMBEDDER_KINDS)}, got {kind!r}")
    allowed = _ONNX_KEYS if kind == "onnx" else _COMMAND_KEYS
    for key in raw:
        if key not in allowed:
            raise ConfigError(f"{where}: unknown key {key!r} for kind {kind!r} (known: {', '.join(sorted(allowed))})")
    gate = raw.get("min_similarity")
    if gate is not None:
        if isinstance(gate, bool) or not isinstance(gate, (int, float)) or not 0 <= gate <= 1:
            raise ConfigError(f"{where}: 'min_similarity' must be a number from 0 to 1")
        gate = float(gate)
    if kind == "onnx":
        model_dir = raw.get("model_dir")
        if model_dir is not None and not isinstance(model_dir, str):
            raise ConfigError(f"{where}: 'model_dir' must be a path")
        return EmbedderConfig("onnx", min_similarity=gate, model_dir=Path(model_dir) if model_dir else None)
    command = raw.get("command")
    if not isinstance(command, list) or not command or not all(isinstance(c, str) for c in command):
        raise ConfigError(f"{where}: 'command' must be a non-empty list of strings")
    secrets = {k: _resolve(name, v, env, "embedder") for k, v in _table(name, raw, "secrets", "embedder").items()}
    batch = raw.get("batch_size", 32)
    if isinstance(batch, bool) or not isinstance(batch, int) or not 1 <= batch <= 1024:
        raise ConfigError(f"{where}: 'batch_size' must be a whole number from 1 to 1024")
    timeout = raw.get("timeout", 60.0)
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or timeout <= 0:
        raise ConfigError(f"{where}: 'timeout' must be a number of seconds greater than 0")
    return EmbedderConfig("command", tuple(command), _table(name, raw, "env", "embedder"), secrets, gate, batch, float(timeout))


def _number(connector: str, raw: dict, key: str, default, *, kind=float, low=None, high=None):
    value = raw.get(key, default)
    ok = isinstance(value, (int, float)) and not isinstance(value, bool) and (kind is float or isinstance(value, int))
    if not ok or (low is not None and value <= low) or (high is not None and value > high):
        bound = f" (greater than {low}{'' if high is None else f' and at most {high}'})" if low is not None else ""
        raise ConfigError(f"connector {connector!r}: '{key}' must be a number{bound}")
    return kind(value)


def _load_toml(path: Path, env: Mapping[str, str]) -> tuple[list[ConnectorConfig], EmbedderConfig, dict[str, EmbedderConfig]]:
    try:
        data = tomllib.loads(path.read_text())
    except FileNotFoundError:
        raise ConfigError(f"{path} not found: list your connectors in a passageway.toml (see docs/install.md)") from None
    except tomllib.TOMLDecodeError as e:
        raise ConfigError(f"{path}: {e}") from None
    connectors: list[ConnectorConfig] = []
    entries = data.get("connector", [])
    if not isinstance(entries, list) or not all(isinstance(e, dict) for e in entries):
        raise ConfigError(f"{path}: connectors are written as [[connector]] tables, one per source")
    for raw in entries:
        name = raw.get("name", "")
        if not isinstance(name, str) or not _NAME.fullmatch(name):
            raise ConfigError(f"connector name {name!r} must match [a-z0-9][a-z0-9_-]* (it names the index file)")
        if any(c.name == name for c in connectors):
            raise ConfigError(f"duplicate connector name {name!r}")
        command = raw.get("command")
        if not isinstance(command, list) or not command or not all(isinstance(c, str) for c in command):
            raise ConfigError(f"connector {name!r}: 'command' must be a non-empty list of strings")
        secrets = {k: _resolve(name, v, env) for k, v in _table(name, raw, "secrets").items()}
        connectors.append(ConnectorConfig(
            name, tuple(command), _table(name, raw, "env"), secrets,
            _number(name, raw, "timeout", 300.0, low=0),
            _number(name, raw, "max_line_bytes", MAX_LINE_BYTES, kind=int, low=0),
            _number(name, raw, "max_output_bytes", MAX_OUTPUT_BYTES, kind=int, low=0),
            _number(name, raw, "max_delete_fraction", 0.3, low=0, high=1)))
    if not connectors:
        raise ConfigError(f"no connectors in {path}: add at least one [[connector]]")
    embedder = _embedder("default", data.get("embedder", {}), env)
    candidates = data.get("embedders", {})
    if not isinstance(candidates, dict):
        raise ConfigError(f"{path}: 'embedders' holds the candidates for `passageway eval compare`, one [embedders.NAME] table each")
    embedders: dict[str, EmbedderConfig] = {}
    for name, raw in candidates.items():
        if not _NAME.fullmatch(name):
            raise ConfigError(f"embedder name {name!r} must match [a-z0-9][a-z0-9_-]*")
        if name == "default":
            raise ConfigError("the embedder name 'default' is taken: it stands for the [embedder] the server uses")
        embedders[name] = _embedder(name, raw, env)
    return connectors, embedder, embedders


def load_config(env: Mapping[str, str], *, require_password: bool = True) -> Config:
    """require_password=False is for commands that do not serve (the evaluation): nobody logs in to them."""
    password = env.get("PASSAGEWAY_LOGIN_PASSWORD", "").strip()
    if require_password and not password:
        raise ConfigError("PASSAGEWAY_LOGIN_PASSWORD is not set: clients authenticate with it, "
                          "so the engine refuses to start without it")
    base_url = env.get("PASSAGEWAY_BASE_URL", "").strip().rstrip("/") or None
    if base_url:
        try:
            validate_issuer_url(AnyHttpUrl(base_url))
        except ValueError as e:
            raise ConfigError(f"PASSAGEWAY_BASE_URL={base_url!r} is not a valid OAuth issuer "
                              f"(https, no query or fragment; plain http only for localhost): {e}") from None
    config_path = Path(env.get("PASSAGEWAY_CONFIG") or default_config_path())
    connectors, embedder, embedders = _load_toml(config_path, env)
    data_dir = Path(env.get("PASSAGEWAY_DATA_DIR") or default_data_dir())
    return Config(
        password=password, connectors=connectors, data_dir=data_dir,
        model_dir=Path(env.get("PASSAGEWAY_MODEL_DIR") or data_dir / "models" / "e5-small"),
        base_url=base_url, host=env.get("PASSAGEWAY_HOST", "127.0.0.1"),
        port=_int(env, "PASSAGEWAY_PORT", 8082), poll_seconds=_int(env, "PASSAGEWAY_POLL_SECONDS", 60),
        reconcile_seconds=_int(env, "PASSAGEWAY_RECONCILE_SECONDS", 1800),
        log_level=env.get("PASSAGEWAY_LOG_LEVEL", "INFO"),
        tool_description=env.get("PASSAGEWAY_TOOL_DESCRIPTION", "").strip() or DEFAULT_TOOL_DESCRIPTION,
        instructions=env.get("PASSAGEWAY_INSTRUCTIONS", "").strip() or DEFAULT_INSTRUCTIONS,
        min_similarity=embedder.min_similarity, embedder=embedder, embedders=embedders)
