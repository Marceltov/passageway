"""passageway eval cases.toml: build the configured sources into a fresh index, ask the questions, report."""

import argparse
import json
import logging
import os
import sys
import time
from collections.abc import Mapping
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path

from passageway.config import ConfigError, load_config
from passageway.embed import EmbedderError
from passageway.eval.cases import CasesError, load_cases
from passageway.eval.report import ReportError, build_report, check_page, machine_line, render_markdown, write_block
from passageway.eval.measure import SyncFailed, UsageError, measure, sweep_values, threshold_value


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="passageway eval", formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Measure retrieval quality: build the sources of passageway.toml into a fresh index, ask the "
                    "questions of a cases file and report hit@1, hit@3, MRR, silence on unanswerable questions and "
                    "latency. The reports hold no question, title or URL unless --include-cases is given.",
        epilog="Exit codes: 0 done, 1 below the [targets] with --enforce, a source that failed to sync or an embedder that "
               "failed, 2 bad input. `passageway eval compare cases.toml` runs the questions with several embedders.")
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


def _run(args, env: Mapping[str, str], embedder, targets, cases) -> tuple[dict, list]:
    config = load_config(env, require_password=False)
    started = time.perf_counter()
    if embedder is None:
        from passageway.embed import build_embedder

        embedder = build_embedder(config.embedder, config)
    load_seconds = round(time.perf_counter() - started, 1)
    try:
        done = measure(config, embedder, cases, data_dir=args.data_dir, threshold=args.threshold, sweep=sweep_values(args.sweep))
    finally:
        if hasattr(embedder, "close"):
            embedder.close()  # a command embedder is a process of its own
    run = {"date": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"), "passageway": version("passageway"),
           "embedder": done.embedder, "dim": done.dim, "threshold": done.threshold, "machine": machine_line(),
           "load_seconds": load_seconds, "index_seconds": done.index_seconds, "sources": done.sources}
    return build_report(run=run, results=done.results, targets=targets, sweep=done.sweep or None,
                        include_cases=args.include_cases), done.results


def _folder(path: Path | None, option: str) -> None:
    if path is not None and path.exists() and not path.is_dir():
        raise UsageError(f"{option}: {path} exists and is not a folder")


def main(argv: list[str] | None = None, *, env: Mapping[str, str] | None = None, embedder=None,
         stdout=None, stderr=None) -> int:
    stdout, stderr = stdout or sys.stdout, stderr or sys.stderr
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["compare"]:  # `passageway eval compare cases.toml`; a cases file of that name is ./compare
        from passageway.eval.compare import compare_main

        return compare_main(argv[1:], env=dict(os.environ if env is None else env), stdout=stdout, stderr=stderr)
    args = _parser().parse_args(argv)
    env = dict(os.environ if env is None else env)
    if args.config:
        env["PASSAGEWAY_CONFIG"] = str(args.config)
    if args.model_dir:
        env["PASSAGEWAY_MODEL_DIR"] = str(args.model_dir)
    sync_log = logging.getLogger("passageway.sync")
    level = sync_log.level
    sync_log.setLevel(logging.CRITICAL)  # a failing source is reported once, below, not with the server's traceback
    try:
        try:
            if args.threshold is not None:
                args.threshold = threshold_value(str(args.threshold), "--threshold")
            sweep_values(args.sweep)
            _folder(args.data_dir, "--data-dir")
            _folder(args.out, "--out")
            cases, targets = load_cases(args.cases)
            if args.write:
                try:
                    check_page(args.write)
                except ReportError as e:
                    raise UsageError(f"--write: {e}") from None
            report, _ = _run(args, env, embedder, targets, cases)
        except (UsageError, CasesError, ConfigError, ReportError) as e:
            print(f"eval: {e}", file=stderr)
            return 2
        except SyncFailed as e:
            print(f"eval: a source failed to sync, so the index would be incomplete: {e}", file=stderr)
            return 1
        except EmbedderError as e:
            print(f"eval: the embedder failed, so the numbers would be meaningless: {e}", file=stderr)
            return 1
        print(render_markdown(report), end="", file=stdout)  # first: whatever happens to the files, the run is not lost
        try:
            if args.out:
                args.out.mkdir(parents=True, exist_ok=True)
                (args.out / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                                                      encoding="utf-8")
                (args.out / "report.md").write_text(render_markdown(report), encoding="utf-8")
            if args.write:
                write_block(args.write, report)
        except (OSError, ReportError) as e:
            print(f"eval: the report could not be saved: {e}", file=stderr)
            return 2
        if args.enforce and not report["targets"]:
            print("eval: --enforce has nothing to check: the cases file has no [targets]", file=stderr)
        return 1 if args.enforce and not all(t["passed"] for t in report["targets"]) else 0
    finally:
        sync_log.setLevel(level)
