"""Asking the engine the questions, and scoring the answers."""

import math
import time
from dataclasses import dataclass

from passageway.eval.cases import AT_MOST, Case, matches
from passageway.rank import Hit

LIMIT = 3  # the answer the hook and the tool give: up to three passages


class TimedEmbedder:
    """Wraps an embedder and adds up the time it spends embedding questions, to report that share of the latency."""

    def __init__(self, inner):
        self._inner = inner
        self.name, self.dim = inner.name, inner.dim
        self.query_seconds = 0.0

    def embed_queries(self, texts):
        started = time.perf_counter()
        try:
            return self._inner.embed_queries(texts)
        finally:
            self.query_seconds += time.perf_counter() - started

    def embed_passages(self, texts):
        return self._inner.embed_passages(texts)


@dataclass
class CaseResult:
    case: Case
    hits: list[Hit]
    rank: int | None  # position of the first accepted hit, None if there is none (or nothing is expected)
    ms: float
    embed_ms: float


def run_cases(engine, cases: list[Case]) -> list[CaseResult]:
    timer = engine.embedder if hasattr(engine.embedder, "query_seconds") else None
    engine.recall(cases[0].query, limit=LIMIT)  # a warm-up: loading and first allocations must not count as latency
    results = []
    for case in cases:
        before = timer.query_seconds if timer else 0.0
        started = time.perf_counter()
        hits = engine.recall(case.query, limit=LIMIT)
        ms = (time.perf_counter() - started) * 1000
        embed_ms = ((timer.query_seconds - before) * 1000) if timer else 0.0
        rank = next((i for i, h in enumerate(hits, 1) if matches(h, case)), None) if case.answerable else None
        results.append(CaseResult(case, hits, rank, ms, embed_ms))
    return results


def _percentile(values: list[float], p: float) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, max(0, math.ceil(p * len(ordered)) - 1))] if ordered else 0.0


def _share(count: int, total: int) -> float | None:
    return count / total if total else None  # nothing behind it: not a perfect score


def score(results: list[CaseResult]) -> dict:
    answerable = [r for r in results if r.case.answerable]
    unanswerable = [r for r in results if not r.case.answerable]
    ms = [r.ms for r in results]
    mean_ms = sum(ms) / len(ms) if ms else 0.0
    mean_embed = sum(r.embed_ms for r in results) / len(results) if results else 0.0
    return {
        "cases": len(results), "answerable": len(answerable), "unanswerable": len(unanswerable),
        "hit_at_1": _share(sum(r.rank == 1 for r in answerable), len(answerable)),
        "hit_at_3": _share(sum(r.rank is not None and r.rank <= 3 for r in answerable), len(answerable)),
        "mrr": sum(1 / r.rank for r in answerable if r.rank) / len(answerable) if answerable else None,
        "silence": _share(sum(not r.hits for r in unanswerable), len(unanswerable)),
        "false_silence": _share(sum(not r.hits for r in answerable), len(answerable)),
        "p50_ms": round(_percentile(ms, 0.5), 1), "p95_ms": round(_percentile(ms, 0.95), 1),
        "embed_ms": round(mean_embed, 1), "embed_share": round(mean_embed / mean_ms, 3) if mean_ms else None,
    }


def group_scores(results: list[CaseResult]) -> dict[str, dict]:
    groups: dict[str, list[CaseResult]] = {}
    for r in results:
        if r.case.group is not None:
            groups.setdefault(r.case.group, []).append(r)
    return {name: score(rs) for name, rs in groups.items()}


def check_targets(metrics: dict, targets: dict[str, float]) -> list[dict]:
    checks = []
    for name, target in targets.items():
        value = metrics.get(name)
        at_most = name in AT_MOST
        passed = value is not None and (value <= target if at_most else value >= target)
        checks.append({"name": name, "target": target, "limit": "at most" if at_most else "at least",
                       "value": value, "passed": passed})
    return checks
