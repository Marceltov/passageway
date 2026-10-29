"""Configuration: environment variables for the core, one TOML file for connectors (docs/install.md)."""

import re
import sys
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
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


def _resolve(connector: str, ref: object, env: Mapping[str, str]) -> str:
    if not isinstance(ref, str) or not ref.startswith("env:") or len(ref) == 4:
        raise ConfigError(f"connector {connector!r}: a secret must be a reference like \"env:NAME\"")
    var = ref[4:]
    if not env.get(var):
        raise ConfigError(f"connector {connector!r}: the environment variable {var} is not set")
    return env[var]


def _table(connector: str, raw: dict, key: str) -> dict[str, str]:
    table = raw.get(key, {})
    if not isinstance(table, dict) or not all(isinstance(v, str) for v in table.values()):
        raise ConfigError(f"connector {connector!r}: '{key}' must be a table of strings")
    return table


def _number(connector: str, raw: dict, key: str, default, *, kind=float, low=None, high=None):
    value = raw.get(key, default)
    ok = isinstance(value, (int, float)) and not isinstance(value, bool) and (kind is float or isinstance(value, int))
    if not ok or (low is not None and value <= low) or (high is not None and value > high):
        bound = f" (greater than {low}{'' if high is None else f' and at most {high}'})" if low is not None else ""
        raise ConfigError(f"connector {connector!r}: '{key}' must be a number{bound}")
    return kind(value)


def _load_toml(path: Path, env: Mapping[str, str]) -> tuple[list[ConnectorConfig], float | None]:
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
    threshold = data.get("embedder", {}).get("min_similarity")
    return connectors, float(threshold) if threshold is not None else None


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
    connectors, min_similarity = _load_toml(config_path, env)
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
        min_similarity=min_similarity)
