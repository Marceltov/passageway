"""Read connector settings from the environment: every value is a string, and a wrong one is a SettingsError."""

import re
from collections.abc import Callable, Mapping

from passageway_sdk import SettingsError


def names(env: Mapping[str, str], key: str) -> tuple[str, ...]:
    """A list setting: values separated by `|`, blanks dropped; empty if the setting is missing."""
    return tuple(p.strip() for p in env.get(key, "").split("|") if p.strip())


def whole(env: Mapping[str, str], key: str, default: int, low: int = 1) -> int:
    """A whole number of at least `low`."""
    raw = env.get(key, "").strip()
    try:
        value = int(raw) if raw else default
    except ValueError:
        raise SettingsError(f"{key} must be a whole number, got {raw!r}") from None
    if value < low:
        raise SettingsError(f"{key} must be at least {low}, got {value}")
    return value


def flag(env: Mapping[str, str], key: str, default: bool) -> bool:
    """`true` or `false`, in any case."""
    raw = env.get(key, "").strip().lower()
    if not raw:
        return default
    if raw not in ("true", "false"):
        raise SettingsError(f"{key} must be true or false, got {raw!r}")
    return raw == "true"


def seconds(env: Mapping[str, str], key: str, default: float) -> float:
    """A number of seconds that is not negative."""
    raw = env.get(key, "").strip()
    try:
        value = float(raw) if raw else default
    except ValueError:
        raise SettingsError(f"{key} must be a number of seconds, got {raw!r}") from None
    if value < 0:
        raise SettingsError(f"{key} must not be negative, got {value}")
    return value


def weights(env: Mapping[str, str], key: str) -> list[tuple[str, float]]:
    """`changelog=0.5,archive/=0.3`: a weight for every item whose path starts with a prefix, in order (see `weight_of`)."""
    out = []
    for part in (p.strip() for p in env.get(key, "").split(",") if p.strip()):
        prefix, _, value = part.partition("=")
        try:
            weight = float(value)
        except ValueError:
            weight = 0.0
        if not prefix.strip() or weight <= 0:
            raise SettingsError(f"{key} must be prefix=weight pairs with a weight above 0, got {part!r}")
        out.append((prefix.strip().lstrip("/"), weight))
    return out


def weight_of(table: list[tuple[str, float]], path: str) -> float:
    """The weight of the first prefix of `table` that `path` starts with (a leading `/` ignored), else 1.0."""
    where = path.lstrip("/")
    return next((w for prefix, w in table if where.startswith(prefix)), 1.0)


def _glob(pattern: str) -> re.Pattern:
    out, i = "", 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out, i = out + "(?:.*/)?", i + 3
        elif pattern.startswith("**", i):
            out, i = out + ".*", i + 2
        elif pattern[i] == "*":
            out, i = out + "[^/]*", i + 1
        elif pattern[i] == "?":
            out, i = out + "[^/]", i + 1
        else:
            out, i = out + re.escape(pattern[i]), i + 1
    return re.compile(("" if "/" in pattern else "(?:.*/)?") + out + r"\Z")


def globs(env: Mapping[str, str], key: str, default: tuple[str, ...]) -> Callable[[str], bool]:
    """Glob patterns separated by `|` (`default` when the setting is missing), as a test of a relative path with `/`: true
    when any pattern matches. `**` crosses folders, `*` and `?` stay inside one; a pattern without `/` matches the file
    name at any depth."""
    patterns = [_glob(p) for p in names(env, key) or default]
    return lambda path: any(p.match(path) for p in patterns)
