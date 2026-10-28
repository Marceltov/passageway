"""Runs connectors: executables that print JSON Lines on stdout (docs/reference/connector-protocol.md)."""

import json
import logging
import os
import signal
import subprocess
import threading
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable

PROTOCOL_VERSION = "1"
MAX_LINE_BYTES = 4 * 1024 * 1024
MAX_OUTPUT_BYTES = 64 * 1024 * 1024
_STDERR_LINES = 5  # shown in the error; /health hides it unless the caller is authenticated


class ConnectorError(Exception):
    pass


def _kill(proc: subprocess.Popen) -> None:
    """Kill the connector and everything it started: a wrapper that forks would otherwise keep the pipe open."""
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        proc.kill()


@dataclass(frozen=True)
class Section:
    heading: str | None
    text: str


@dataclass(frozen=True)
class Item:
    id: str
    title: str
    url: str
    version: str
    sections: tuple[Section, ...] = ()
    weight: float = 1.0
    path: tuple[str, ...] = ()
    links: tuple[str, ...] = ()  # ids of related items
    labels: tuple[str, ...] = ()
    updated: str | None = None


def _str(record: dict, key: str, *, non_empty: bool = False) -> str:
    value = record.get(key)
    if not isinstance(value, str):
        raise ValueError(f"'{key}' must be a string")
    if non_empty and not value:
        raise ValueError(f"'{key}' must not be empty")
    return value


def _strings(record: dict, key: str) -> tuple[str, ...]:
    values = record.get(key, [])
    if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
        raise ValueError(f"'{key}' must be a list of strings")
    return tuple(values)


def parse_item(record: dict) -> Item:
    if not isinstance(record, dict):
        raise ValueError("a record must be a JSON object")
    raw_sections = record.get("sections")
    if not isinstance(raw_sections, list):
        raise ValueError("'sections' must be a list")
    sections = []
    for s in raw_sections:
        if not isinstance(s, dict):
            raise ValueError("a section must be an object")
        heading = s.get("heading")
        if heading is not None and not isinstance(heading, str):
            raise ValueError("'heading' must be a string")
        sections.append(Section(heading, _str(s, "text")))
    weight = record.get("weight", 1.0)
    if isinstance(weight, bool) or not isinstance(weight, (int, float)) or not 0 <= weight <= 2:
        raise ValueError("'weight' must be a number from 0 to 2")
    links = _strings(record, "links")
    if not all(links):
        raise ValueError("'links' must not contain empty ids")
    updated = record.get("updated")
    if updated is not None and not isinstance(updated, str):
        raise ValueError("'updated' must be a string")
    return Item(_str(record, "id", non_empty=True), _str(record, "title"), _str(record, "url"),
                _str(record, "version"), tuple(sections), float(weight), _strings(record, "path"),
                links, _strings(record, "labels"), updated)


class Connector:
    """One configured connector. Every call is a fresh process; it succeeds completely or returns nothing."""

    def __init__(self, name: str, command: list[str], *, env: dict[str, str] | None = None,
                 secrets: dict[str, str] | None = None, timeout: float = 300.0,
                 max_line_bytes: int = MAX_LINE_BYTES, max_output_bytes: int = MAX_OUTPUT_BYTES):
        self.name = name
        self._command, self._env, self._secrets = list(command), dict(env or {}), dict(secrets or {})
        self._timeout, self._max_line, self._max_output = timeout, max_line_bytes, max_output_bytes
        self._log = logging.getLogger(f"connector.{name}")

    # -- public calls ------------------------------------------------------------------------

    def check(self) -> int:
        counts: list[int] = []

        def parse(record: dict) -> None:
            if "protocol" in record:  # first: a newer protocol may change the rest
                if not isinstance(record["protocol"], str):
                    raise ValueError(f"'protocol' must be the string {PROTOCOL_VERSION!r}")
                if record["protocol"] != PROTOCOL_VERSION:
                    raise ValueError(f"speaks protocol {record['protocol']!r}, this core speaks {PROTOCOL_VERSION!r}")
            count = record.get("count")
            if isinstance(count, float) and count.is_integer():  # 3.0 is the whole number 3 in JSON
                count = int(count)
            if record.get("ok") is not True or isinstance(count, bool) or not isinstance(count, int) or count < 0:
                raise ValueError("expected {\"ok\": true, \"count\": n} with n a whole number from 0")
            counts.append(count)

        self._run(["check"], parse)
        if not counts:
            raise self._fail("check printed nothing")
        return counts[0]

    def list_versions(self) -> dict[str, str]:
        versions: dict[str, str] = {}

        def parse(record: dict) -> None:
            item_id = _str(record, "id", non_empty=True)
            if item_id in versions:
                raise ValueError(f"duplicate id '{item_id}'")
            versions[item_id] = _str(record, "version")

        self._run(["list"], parse)
        return versions

    def fetch(self, ids: list[str]) -> list[Item]:
        wanted, items = set(ids), []

        def parse(record: dict) -> None:
            item = parse_item(record)
            if item.id not in wanted:
                raise ValueError(f"returned '{item.id}', which was not requested")
            items.append(item)

        self._run(["fetch"], parse, stdin="".join(json.dumps({"id": i}) + "\n" for i in ids))
        return items

    def changed(self, since: datetime) -> list[Item]:
        stamp = since.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        items: list[Item] = []
        self._run(["changed", "--since", stamp], lambda record: items.append(parse_item(record)))
        return items

    # -- process handling --------------------------------------------------------------------

    def _fail(self, message: str) -> ConnectorError:
        return ConnectorError(f"connector '{self.name}': {message}")

    def _mask(self, text: str) -> str:
        for value in self._secrets.values():
            if value:
                text = text.replace(value, "***")
        return text

    def _run(self, args: list[str], parse: Callable[[dict], None], stdin: str = "") -> None:
        env = {k: os.environ[k] for k in ("PATH", "HOME") if k in os.environ}
        env.update(self._env)
        env.update(self._secrets)
        env["PASSAGEWAY_PROTOCOL"] = PROTOCOL_VERSION
        proc = subprocess.Popen([*self._command, *args], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, env=env, start_new_session=True)
        timed_out = threading.Event()
        timer = threading.Timer(self._timeout, lambda: None if proc.poll() is not None else (timed_out.set(), _kill(proc)))
        tail: deque[str] = deque(maxlen=_STDERR_LINES)

        def drain_stderr() -> None:
            for raw in proc.stderr:
                line = self._mask(raw.decode(errors="replace").rstrip())
                tail.append(line)
                self._log.info("%s", line)

        def feed_stdin() -> None:
            try:
                proc.stdin.write(stdin.encode())
                proc.stdin.close()
            except (BrokenPipeError, OSError):
                pass

        threads = [threading.Thread(target=drain_stderr, daemon=True),
                   threading.Thread(target=feed_stdin, daemon=True)]
        timer.start()
        for t in threads:
            t.start()
        try:
            total = number = 0
            for raw in iter(lambda: proc.stdout.readline(self._max_line + 2), b""):
                number += 1
                total += len(raw)
                if len(raw.rstrip(b"\r\n")) > self._max_line:  # the limit is on content, not the newline
                    raise self._fail(f"line {number} is longer than {self._max_line} bytes")
                if total > self._max_output:
                    raise self._fail(f"more than {self._max_output} bytes of output")
                if not raw.strip():
                    continue
                try:
                    record = json.loads(raw)
                    if not isinstance(record, dict):
                        raise ValueError("expected a JSON object")
                    parse(record)
                except (ValueError, TypeError) as e:  # includes JSONDecodeError
                    raise self._fail(f"line {number}: {e}") from None
            proc.wait()
        finally:
            timer.cancel()
            if proc.poll() is None:
                _kill(proc)
                proc.wait()
            for t in threads:
                t.join(timeout=5)
        if timed_out.is_set() and proc.returncode != 0:  # a call that finished first is not a timeout
            raise self._fail(f"{args[0]} timed out after {self._timeout:g} s")
        if proc.returncode != 0:
            raise self._fail(f"{args[0]} exited with status {proc.returncode}: {' | '.join(tail)}")
