"""One measurement: build the sources into a fresh index with an embedder, ask the questions, optionally at more thresholds."""

import shutil
import tempfile
import time
from dataclasses import dataclass, replace
from pathlib import Path

from passageway.config import Config
from passageway.eval.cases import Case
from passageway.eval.run import CaseResult, TimedEmbedder, run_cases
from passageway.server import Engine


class UsageError(Exception):
    pass


class SyncFailed(Exception):
    pass


@dataclass
class Measurement:
    embedder: str
    dim: int
    threshold: float
    index_seconds: float
    sources: dict[str, dict[str, int]]
    results: list[CaseResult]
    sweep: list[tuple[float, list[CaseResult]]]


def threshold_value(text: str, option: str) -> float:
    try:
        value = float(text)
    except ValueError:
        raise UsageError(f"{option}: {text!r} is not a number") from None
    if not 0 <= value <= 1:
        raise UsageError(f"{option}: {value} must be between 0 and 1")
    return value


def sweep_values(text: str | None) -> list[float]:
    return sorted({threshold_value(t, "--sweep") for t in text.split(",")}) if text is not None else []


def measure(config: Config, embedder, cases: list[Case], *, data_dir: Path | None = None, threshold: float | None = None,
            sweep: list[float] = ()) -> Measurement:
    """Builds into `data_dir` (kept, and refused if it holds an index of another embedder) or into a throwaway folder."""
    embedder = TimedEmbedder(embedder)
    scratch = None if data_dir else Path(tempfile.mkdtemp(prefix="passageway-eval-"))
    folder = data_dir or scratch
    try:
        folder.mkdir(parents=True, exist_ok=True)
        engine = Engine(replace(config, data_dir=folder), embedder)
        for name, syncer in engine.syncers.items():  # a kept index of another model cannot be compared with this one
            stored = syncer.index.stored_embedder()
            if syncer.index.counts()[0] > 0 and stored not in (None, embedder.name):
                raise UsageError(f"the index of {name!r} in {folder} was built with {stored!r}, not {embedder.name!r}: "
                                 "use a fresh --data-dir")
        started = time.perf_counter()
        engine.sync_all_once()
        index_seconds = round(time.perf_counter() - started, 1)
        failed = {n: s.status.last_error for n, s in engine.syncers.items() if s.status.last_error}
        if failed:
            raise SyncFailed("; ".join(f"{n}: {e}" for n, e in failed.items()))
        if threshold is not None:
            engine.params = replace(engine.params, min_cos=threshold)
        used = engine.params.min_cos
        results = run_cases(engine, cases)
        swept = []
        for value in sweep:
            engine.params = replace(engine.params, min_cos=value)
            swept.append((value, run_cases(engine, cases)))
        return Measurement(embedder.name, embedder.dim, used, index_seconds,
                           {n: dict(zip(("items", "sections"), s.index.counts())) for n, s in engine.syncers.items()},
                           results, swept)
    finally:
        if scratch:
            shutil.rmtree(scratch, ignore_errors=True)
