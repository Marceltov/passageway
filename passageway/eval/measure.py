"""One measurement: build the sources into a fresh index with an embedder, ask the questions, optionally at more thresholds."""

import logging
import shutil
import tempfile
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, replace
from pathlib import Path

from passageway.config import Config
from passageway.eval.cases import Case
from passageway.eval.run import CaseResult, TimedEmbedder, run_cases
from passageway.server import Engine

PROGRESS_EVERY = 30.0  # seconds between two progress lines of one source; the last batch is always shown


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


def _duration(seconds: float) -> str:
    minutes = round(seconds / 60)
    if minutes < 1:
        return "under a minute"
    if minutes < 60:
        return f"{minutes} min"
    return f"{minutes // 60} h {minutes % 60} min" if minutes % 60 else f"{minutes // 60} h"


class _Progress(logging.Handler):
    """Turns the sync's `fetched N of M` records into a line per source at most every PROGRESS_EVERY seconds."""

    def __init__(self, say: Callable[[str], None]):
        super().__init__(logging.INFO)
        self.say = say
        self.seen: dict[str, tuple[float, int, float]] = {}  # source: (first seen, fetched then, last shown)

    def emit(self, record: logging.LogRecord) -> None:
        if record.levelno != logging.INFO or record.msg != "sync %s: fetched %d of %d":
            return  # the failure warning is reported once by eval itself, without the traceback
        name, fetched, total = record.args
        now = time.monotonic()
        first, at_first, shown = self.seen.get(name, (now, fetched, None))
        if shown is not None and fetched < total and now - shown < PROGRESS_EVERY:
            return
        self.seen[name] = (first, at_first, now)
        line = f"{name}: {fetched:,} of {total:,} items ({fetched * 100 // total} %)"
        if fetched < total and fetched > at_first:
            line += f", about {_duration((total - fetched) * (now - first) / (fetched - at_first))} left"
        self.say(line)


@contextmanager
def sync_progress(say: Callable[[str], None]) -> Iterator[None]:
    """While it runs, the sync's progress goes to `say` and nothing else of its logging goes anywhere."""
    log = logging.getLogger("passageway.sync")
    handler = _Progress(say)
    level, propagate = log.level, log.propagate
    log.setLevel(logging.INFO)
    log.propagate = False
    log.addHandler(handler)
    try:
        yield
    finally:
        log.removeHandler(handler)
        log.setLevel(level)
        log.propagate = propagate


def measure(config: Config, embedder, cases: list[Case], *, data_dir: Path | None = None, threshold: float | None = None,
            sweep: list[float] = (), say: Callable[[str], None] = lambda line: None) -> Measurement:
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
        with sync_progress(say):
            engine.sync_all_once()
        index_seconds = round(time.perf_counter() - started, 1)
        failed = {n: s.status.last_error for n, s in engine.syncers.items() if s.status.last_error}
        if failed:
            raise SyncFailed("; ".join(f"{n}: {e}" for n, e in failed.items()))
        if threshold is not None:
            engine.params = replace(engine.params, min_cos=threshold)
        used = engine.params.min_cos
        rounds = f" at {len(sweep) + 1} thresholds" if sweep else ""
        say(f"built in {_duration(index_seconds)}, asking {len(cases)} questions{rounds}")
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
