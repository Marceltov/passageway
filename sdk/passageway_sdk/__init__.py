"""Write a passageway connector as three small functions; the protocol plumbing is done here.

Subclass Connector, implement versions() and fetch() (and changed() if the source can answer it cheaply), and call
YourConnector.main(). The reference is https://passageway.marceltov.de/reference/connector-protocol/.
"""

import json
import os
import sys
from collections.abc import Iterable, Mapping
from datetime import datetime
from typing import NoReturn, TextIO

__all__ = ["Connector", "SettingsError", "SourceError", "validate_item"]

PROTOCOL = "1"
MODES = "check|list|fetch|changed"


class SettingsError(Exception):
    """The settings are wrong. The connector exits 2 with the message on stderr and prints nothing."""


class SourceError(Exception):
    """The source failed (down, refused, unreadable). The connector exits 1 with the message and prints nothing."""


def _check(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def _strings(record: dict, key: str, *, non_empty: bool = False) -> None:
    values = record.get(key, [])
    _check(isinstance(values, list) and all(isinstance(v, str) and (v or not non_empty) for v in values),
           f"'{key}' must be a list of {'non-empty ' if non_empty else ''}strings")


def validate_item(record: object) -> None:
    """Raises ValueError if the record is not a valid item (the same rules the core applies)."""
    _check(isinstance(record, dict), "a record must be a JSON object")
    for key in ("title", "url", "version"):
        _check(isinstance(record.get(key), str), f"'{key}' must be a string")
    _check(isinstance(record.get("id"), str) and record["id"], "'id' must be a non-empty string")
    sections = record.get("sections")
    _check(isinstance(sections, list), "'sections' must be a list")
    for s in sections:
        _check(isinstance(s, dict) and isinstance(s.get("text"), str), "a section needs a string 'text'")
        _check(s.get("heading") is None or isinstance(s["heading"], str), "'heading' must be a string")
    weight = record.get("weight", 1.0)
    _check(isinstance(weight, (int, float)) and not isinstance(weight, bool) and 0 <= weight <= 2,
           "'weight' must be a number from 0 to 2")
    _strings(record, "path")
    _strings(record, "labels")
    _strings(record, "links", non_empty=True)
    _check(record.get("updated") is None or isinstance(record["updated"], str), "'updated' must be a string")


class Connector:
    """One source. Subclass it; settings arrive in __init__ as the environment."""

    name = "connector"  # prefixes the messages on stderr
    expected_errors: tuple[type[Exception], ...] = ()  # extra exceptions that mean "the source failed" (exit 1)

    def __init__(self, env: Mapping[str, str]):
        """Read and validate the settings; raise SettingsError if they are wrong."""

    def versions(self) -> dict[str, str]:
        """Every item that exists, as id -> version. The version changes when the content changes."""
        raise NotImplementedError

    def fetch(self, ids: list[str]) -> Iterable[dict]:
        """The item record for each requested id that still exists."""
        raise NotImplementedError

    def changed(self, since: datetime) -> Iterable[dict]:
        """Optional: items changed since `since` (timezone-aware). Print nothing if that is not cheap."""
        return ()

    def count(self) -> int:
        return len(self.versions())

    # -- the plumbing ------------------------------------------------------------------------

    @classmethod
    def run(cls, argv: list[str], env: Mapping[str, str], stdin: TextIO, stdout: TextIO, stderr: TextIO,
            **options) -> int:
        """Run one mode and return the exit code. Output is written only if everything succeeded."""
        mode = argv[1] if len(argv) > 1 else ""
        if mode not in MODES.split("|"):
            print(f"usage: {MODES} (changed takes --since <UTC time>)", file=stderr)
            return 2
        since = None
        if mode == "changed" and cls.changed is not Connector.changed:  # a connector without `changed` has no use for the time
            try:
                since = _since(argv)
            except ValueError as e:
                print(f"{cls.name}: {e}", file=stderr)
                return 2
        try:
            lines = cls(env, **options)._lines(mode, stdin, since)
        except SettingsError as e:
            print(f"{cls.name}: {e}", file=stderr)
            return 2
        except (SourceError, *cls.expected_errors) as e:
            print(f"{cls.name}: {e}", file=stderr)
            return 1
        stdout.write("".join(lines))
        return 0

    @classmethod
    def main(cls) -> NoReturn:
        sys.exit(cls.run(sys.argv, os.environ, sys.stdin, sys.stdout, sys.stderr))

    def _lines(self, mode: str, stdin: TextIO, since: datetime | None) -> list[str]:
        if mode == "check":
            return [_line({"ok": True, "count": self.count(), "protocol": PROTOCOL})]
        if mode == "list":
            return [_line({"id": i, "version": v}) for i, v in self.versions().items()]
        items = self.fetch(_ids(stdin)) if mode == "fetch" else self.changed(since)
        return [_line(_valid(item)) for item in items]


def _line(record: dict) -> str:
    return json.dumps(record) + "\n"  # ASCII-safe on purpose: a locale without UTF-8 must not crash the output


def _valid(item: object) -> dict:
    try:
        validate_item(item)
    except ValueError as e:
        label = item.get("id") if isinstance(item, dict) else None
        raise SourceError(f"invalid item{f' {label!r}' if label else ''}: {e}") from None
    return item


def _ids(stdin: TextIO) -> list[str]:
    try:
        return [json.loads(line)["id"] for line in stdin if line.strip()]
    except (ValueError, KeyError, TypeError):
        raise SourceError("fetch expects one JSON object with an 'id' per line on stdin") from None


def _since(argv: list[str]) -> datetime:
    try:
        value = datetime.fromisoformat(argv[argv.index("--since") + 1].replace("Z", "+00:00"))
    except (ValueError, IndexError):
        raise ValueError("changed needs --since <UTC time>, e.g. 2026-01-01T00:00:00Z") from None
    if value.tzinfo is None:
        raise ValueError("--since must carry a timezone, e.g. 2026-01-01T00:00:00Z")
    return value
