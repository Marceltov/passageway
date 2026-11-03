"""Read connector settings from the environment: every value is a string, and a wrong one is a SettingsError."""

from collections.abc import Mapping

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
