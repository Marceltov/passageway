"""passageway eval cases.toml: build the configured sources into a fresh index, ask the questions, report."""

import argparse
import json
import os
import shutil
import sys
import tempfile
import time
from collections.abc import Mapping
from dataclasses import replace
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path

from passageway.config import ConfigError, load_config
from passageway.eval.cases import CasesError, load_cases
from passageway.eval.report import ReportError, build_report, check_page, machine_line, render_markdown, write_block
from passageway.eval.run import TimedEmbedder, run_cases
from passageway.server import Engine


class UsageError(Exception):
    pass


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="passageway eval", formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Measure retrieval quality: build the sources of passageway.toml into a fresh index, ask the "
                    "questions of a cases file and report hit@1, hit@3, MRR, silence on unanswerable questions and "
                    "latency. The reports hold no question, title or URL unless --include-cases is given.",
        epilog="Exit codes: 0 done, 1 below the [targets] with --enforce or a source failed to sync, 2 bad input.")
    p.add_argument("cases", type=Path, help="the cases file (TOML: [targets] and [[case]])")
    p.add_argument("--config", type=Path, help="passageway.toml (default: PASSAGEWAY_CONFIG)")
    p.add_argument("--model-dir", type=Path, help="the embedding model (default: PASSAGEWAY_MODEL_DIR)")
    p.add_argument("--data-dir", type=Path, help="keep the index here and reuse it (default: a throwaway folder)")
    p.add_argument("--threshold", type=float, help="relevance threshold (min_similarity) for this run")
    p.add_argument("--sweep", help="also run at these thresholds, e.g. 0.80,0.84,0.88")
    p.add_argument("--enforce", action="store_true", help="exit 1 if a [targets] value is not met")
    p.add_argument("--out", type=Path, help="write report.json and report.md into this folder")
    p.add_argument("--write", type=Path, help="update the block between the passageway:results markers of this page")
    p.add_argument("--include-cases", action="store_true", help="also report every question (quotes your sources)")
    return p


def _threshold(text: str, option: str) -> float:
    try:
        value = float(text)
    except ValueError:
        raise UsageError(f"{option}: {text!r} is not a number") from None
    if not 0 <= value <= 1:
        raise UsageError(f"{option}: {value} must be between 0 and 1")
    return value


def _run(args, env: Mapping[str, str], embedder, targets, cases) -> tuple[dict, list]:
    config = load_config(env, require_password=False)
    if embedder is None:
        from passageway.embed import OnnxEmbedder

        if not (config.model_dir / "model.onnx").exists():
            raise ConfigError(f"embedding model not found in {config.model_dir} (see docs/install.md)")
        embedder = OnnxEmbedder(config.model_dir)
    embedder = TimedEmbedder(embedder)
    scratch = None if args.data_dir else Path(tempfile.mkdtemp(prefix="passageway-eval-"))
    data_dir = args.data_dir or scratch
    try:
        data_dir.mkdir(parents=True, exist_ok=True)
        engine = Engine(replace(config, data_dir=data_dir), embedder)
        for name, syncer in engine.syncers.items():  # a kept index of another model cannot be compared with this one
            if syncer.index.counts()[0] > 0 and syncer.index.needs_rebuild():
                raise UsageError(f"the index of {name!r} in {data_dir} was built with {syncer.index.stored_embedder()!r}, "
                                 f"not {embedder.name!r}: use a fresh --data-dir")
        started = time.perf_counter()
        engine.sync_all_once()
        index_seconds = round(time.perf_counter() - started, 1)
        failed = {n: s.status.last_error for n, s in engine.syncers.items() if s.status.last_error}
        if failed:
            raise SyncFailed("; ".join(f"{n}: {e}" for n, e in failed.items()))
        if args.threshold is not None:
            engine.params = replace(engine.params, min_cos=args.threshold)
        threshold = engine.params.min_cos
        results = run_cases(engine, cases)
        sweep = []
        for value in sorted({_threshold(t, "--sweep") for t in args.sweep.split(",")}) if args.sweep else []:
            engine.params = replace(engine.params, min_cos=value)
            sweep.append((value, run_cases(engine, cases)))
        run = {"date": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"), "passageway": version("passageway"),
               "embedder": embedder.name, "dim": embedder.dim, "threshold": threshold, "machine": machine_line(),
               "index_seconds": index_seconds,
               "sources": {n: dict(zip(("items", "sections"), s.index.counts())) for n, s in engine.syncers.items()}}
        return build_report(run=run, results=results, targets=targets, sweep=sweep or None,
                            include_cases=args.include_cases), results
    finally:
        if scratch:
            shutil.rmtree(scratch, ignore_errors=True)


class SyncFailed(Exception):
    pass


def main(argv: list[str] | None = None, *, env: Mapping[str, str] | None = None, embedder=None,
         stdout=None, stderr=None) -> int:
    stdout, stderr = stdout or sys.stdout, stderr or sys.stderr
    args = _parser().parse_args(argv)
    env = dict(os.environ if env is None else env)
    if args.config:
        env["PASSAGEWAY_CONFIG"] = str(args.config)
    if args.model_dir:
        env["PASSAGEWAY_MODEL_DIR"] = str(args.model_dir)
    try:
        if args.threshold is not None:
            args.threshold = _threshold(str(args.threshold), "--threshold")
        for t in args.sweep.split(",") if args.sweep else []:
            _threshold(t, "--sweep")
        cases, targets = load_cases(args.cases)
        if args.write:
            check_page(args.write)
        report, _ = _run(args, env, embedder, targets, cases)
    except (UsageError, CasesError, ConfigError, ReportError) as e:
        print(f"eval: {e}", file=stderr)
        return 2
    except SyncFailed as e:
        print(f"eval: a source failed to sync, so the index would be incomplete: {e}", file=stderr)
        return 1
    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
        (args.out / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (args.out / "report.md").write_text(render_markdown(report), encoding="utf-8")
    if args.write:
        try:
            write_block(args.write, report)
        except ReportError as e:
            print(f"eval: {e}", file=stderr)
            return 2
    print(render_markdown(report), end="", file=stdout)
    if args.enforce and not report["targets"]:
        print("eval: --enforce has nothing to check: the cases file has no [targets]", file=stderr)
    return 1 if args.enforce and not all(t["passed"] for t in report["targets"]) else 0
