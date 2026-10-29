"""The cases file: questions with the answers that count as right, and optional targets for --enforce."""

import math
import tomllib
from dataclasses import dataclass
from pathlib import Path

from passageway.rank import Hit

RATIO_TARGETS = ("hit_at_1", "hit_at_3", "mrr", "silence", "false_silence")  # fractions from 0 to 1
MS_TARGETS = ("p50_ms", "p95_ms")
AT_MOST = ("false_silence", "p50_ms", "p95_ms")  # every other target is a minimum
CASE_KEYS = {"query", "expect", "expect_id", "group"}


class CasesError(Exception):
    pass


@dataclass(frozen=True)
class Case:
    query: str
    expect: tuple[str, ...] = ()  # substrings of a hit's title, heading or URL
    expect_id: tuple[str, ...] = ()  # exact item ids
    group: str | None = None

    @property
    def answerable(self) -> bool:
        return bool(self.expect or self.expect_id)  # no accepted answer: the index must stay silent


def _strings(raw: dict, key: str, where: str) -> tuple[str, ...]:
    value = raw.get(key, [])
    if not isinstance(value, list) or not all(isinstance(v, str) and v.strip() for v in value):
        raise CasesError(f"{where}: '{key}' must be a list of non-empty strings")
    return tuple(value)


def _case(raw: object, number: int) -> Case:
    where = f"case {number}"
    if not isinstance(raw, dict):
        raise CasesError(f"{where}: a case is a [[case]] table")
    unknown = set(raw) - CASE_KEYS
    if unknown:
        raise CasesError(f"{where}: unknown key {sorted(unknown)[0]!r} (known: {', '.join(sorted(CASE_KEYS))})")
    query = raw.get("query")
    if not isinstance(query, str) or not query.strip():
        raise CasesError(f"{where}: 'query' must be a non-empty string")
    group = raw.get("group")
    if group is not None and not isinstance(group, str):
        raise CasesError(f"{where}: 'group' must be a string")
    return Case(query, _strings(raw, "expect", where), _strings(raw, "expect_id", where), group)


def _targets(raw: object) -> dict[str, float]:
    if not isinstance(raw, dict):
        raise CasesError("[targets] must be a table")
    targets: dict[str, float] = {}
    for key, value in raw.items():
        if key not in RATIO_TARGETS + MS_TARGETS:
            raise CasesError(f"[targets]: unknown target {key!r} (known: {', '.join(RATIO_TARGETS + MS_TARGETS)})")
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise CasesError(f"[targets]: {key} must be a finite number")
        if value < 0 or (key in RATIO_TARGETS and value > 1):
            raise CasesError(f"[targets]: {key} must be {'between 0 and 1' if key in RATIO_TARGETS else 'at least 0'}")
        targets[key] = float(value)
    return targets


def load_cases(path: Path) -> tuple[list[Case], dict[str, float]]:
    try:
        data = tomllib.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise CasesError(f"{path} not found") from None
    except OSError as e:  # a folder, no permission
        raise CasesError(f"cannot read {path}: {e.strerror}") from None
    except (tomllib.TOMLDecodeError, UnicodeDecodeError) as e:
        raise CasesError(f"{path}: {e}") from None
    unknown = set(data) - {"case", "targets"}
    if unknown:
        raise CasesError(f"{path}: unknown section {sorted(unknown)[0]!r}: a cases file has [targets] and [[case]]")
    raw_cases = data.get("case", [])
    if not isinstance(raw_cases, list) or not raw_cases:
        raise CasesError(f"{path} has no [[case]]: add at least one question")
    return [_case(raw, n) for n, raw in enumerate(raw_cases, 1)], _targets(data.get("targets", {}))


def matches(hit: Hit, case: Case) -> bool:
    """A hit is right when it carries an accepted id, or when an accepted text is part of its title, heading or URL."""
    if hit.item_id in case.expect_id:
        return True
    haystacks = [text.casefold() for text in (hit.title, hit.heading, hit.url)]
    return any(entry.casefold() in text for entry in case.expect for text in haystacks)
