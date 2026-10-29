"""passageway eval compare cases.toml: the same questions with several embedders, side by side."""

import argparse
import json
import logging
import os
import sys
import time
from collections.abc import Mapping
from dataclasses import replace
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path

from passageway.config import Config, ConfigError, load_config
from passageway.embed import EmbedderError, build_embedder
from passageway.eval.cases import CasesError, load_cases
from passageway.eval.measure import SyncFailed, UsageError, measure, sweep_values, threshold_value
from passageway.eval.report import (ReportError, build_comparison, check_page, machine_line, render_markdown,
                                    write_block)
from passageway.eval.run import score

DEFAULT = "default"


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="passageway eval compare", formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Ask the questions of a cases file with several embedders and report them side by side: each runs "
                    "with its own fresh index and its own relevance threshold. The candidates are the [embedders.NAME] "
                    "tables of passageway.toml, and 'default' is the [embedder] the server uses.",
        epilog="Exit codes: 0 done, 1 a source failed to sync, 2 bad input or an embedder that cannot start.")
    p.add_argument("cases", type=Path, help="the cases file (TOML: [[case]])")
    p.add_argument("--embedder", action="append", default=[], metavar="NAME",
                   help="a candidate to compare; repeat it (default: 'default' and every [embedders.NAME])")
    p.add_argument("--config", type=Path, help="passageway.toml (default: PASSAGEWAY_CONFIG)")
    p.add_argument("--model-dir", type=Path, help="the built-in model (default: PASSAGEWAY_MODEL_DIR)")
    p.add_argument("--threshold", type=float, help="one relevance threshold for every candidate")
    p.add_argument("--sweep", help="also run each candidate at these thresholds, e.g. 0.80,0.84,0.88")
    p.add_argument("--out", type=Path, help="write report.json and report.md into this folder")
    p.add_argument("--write", type=Path, help="update the block between the passageway:results markers of this page")
    return p


def _choose(names: list[str], config: Config) -> list[str]:
    known = [DEFAULT, *sorted(config.embedders)]
    chosen = names or known
    for name in chosen:
        if name not in known:
            raise UsageError(f"--embedder: unknown embedder {name!r} (known: {', '.join(known)})")
    if len(set(chosen)) != len(chosen):
        raise UsageError("--embedder: an embedder is named twice")
    if len(chosen) < 2:
        raise UsageError("a comparison needs at least two embedders: configure [embedders.NAME] tables in passageway.toml "
                         "or name two with --embedder")
    return chosen


def compare_main(argv: list[str], *, env: Mapping[str, str], stdout, stderr) -> int:
    args = _parser().parse_args(argv)
    env = dict(env)
    if args.config:
        env["PASSAGEWAY_CONFIG"] = str(args.config)
    if args.model_dir:
        env["PASSAGEWAY_MODEL_DIR"] = str(args.model_dir)
    sync_log = logging.getLogger("passageway.sync")
    level = sync_log.level
    sync_log.setLevel(logging.CRITICAL)
    try:
        try:
            if args.threshold is not None:
                args.threshold = threshold_value(str(args.threshold), "--threshold")
            sweep = sweep_values(args.sweep)
            if args.out is not None and args.out.exists() and not args.out.is_dir():
                raise UsageError(f"--out: {args.out} exists and is not a folder")
            cases, _ = load_cases(args.cases)
            if args.write:
                try:
                    check_page(args.write)
                except ReportError as e:
                    raise UsageError(f"--write: {e}") from None
            config = load_config(env, require_password=False)
            names = _choose(args.embedder, config)
            embedders: dict[str, tuple[object, float]] = {}
            try:
                for name in names:  # every embedder first: one that cannot start must not waste the others' indexing
                    cfg = config.embedder if name == DEFAULT else config.embedders[name]
                    started = time.perf_counter()
                    embedders[name] = (build_embedder(cfg, config, label=name),
                                       round(time.perf_counter() - started, 1))
                results = []
                for name in names:
                    cfg = config.embedder if name == DEFAULT else config.embedders[name]
                    embedder, load_seconds = embedders.pop(name)
                    try:
                        done = measure(replace(config, embedder=cfg, min_similarity=cfg.min_similarity), embedder, cases,
                                       threshold=args.threshold, sweep=sweep)
                    except EmbedderError as e:
                        raise EmbedderError(f"{name}: {e}") from None
                    finally:
                        if hasattr(embedder, "close"):
                            embedder.close()
                    results.append({"label": name, "embedder": done.embedder, "dim": done.dim, "threshold": done.threshold,
                                    "load_seconds": load_seconds, "index_seconds": done.index_seconds,
                                    "sources": done.sources, "results": done.results, "sweep": done.sweep})
            finally:
                for embedder, _ in embedders.values():
                    if hasattr(embedder, "close"):
                        embedder.close()
        except (UsageError, CasesError, ConfigError, ReportError) as e:
            print(f"eval: {e}", file=stderr)
            return 2
        except SyncFailed as e:
            print(f"eval: a source failed to sync, so the index would be incomplete: {e}", file=stderr)
            return 1
        except EmbedderError as e:
            print(f"eval: an embedder failed, so the numbers would be meaningless: {e}", file=stderr)
            return 1
        run = {"date": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"), "passageway": version("passageway"),
               "machine": machine_line()}
        questions = score(results[0]["results"])
        report = build_comparison(
            run=run, candidates=results,
            questions={k: questions[k] for k in ("cases", "answerable", "unanswerable")})
        print(render_markdown(report), end="", file=stdout)
        try:
            if args.out:
                args.out.mkdir(parents=True, exist_ok=True)
                (args.out / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                (args.out / "report.md").write_text(render_markdown(report), encoding="utf-8")
            if args.write:
                write_block(args.write, report)
        except (OSError, ReportError) as e:
            print(f"eval: the report could not be saved: {e}", file=stderr)
            return 2
        return 0
    finally:
        sync_log.setLevel(level)
