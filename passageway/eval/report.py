"""Reports: a JSON document for machines, markdown for people, and a block that keeps a page of yours up to date."""

import json
import os
import platform
import re
from pathlib import Path

from passageway.eval.run import CaseResult, check_targets, group_scores, score

SCHEMA = 1
START = "<!-- passageway:results:start -->"
END = "<!-- passageway:results:end -->"
HISTORY_ROWS = 10


class ReportError(Exception):
    pass


def machine_line() -> str:
    """Enough to explain a latency, nothing that identifies a person or a host."""
    return f"{platform.system()} {platform.machine()}, Python {platform.python_version()}"


def build_report(*, run: dict, results: list[CaseResult], targets: dict[str, float],
                 sweep: list[tuple[float, list[CaseResult]]] | None, include_cases: bool) -> dict:
    """Aggregate-only unless include_cases: the questions and what was found are quotes from the user's sources."""
    metrics = score(results)
    report = {"schema": SCHEMA, "run": run, "metrics": metrics, "groups": group_scores(results),
              "targets": check_targets(metrics, targets)}
    if sweep:
        report["sweep"] = [{"threshold": threshold, "metrics": score(rs)} for threshold, rs in sweep]
    if include_cases:
        report["cases"] = [{
            "query": r.case.query, "group": r.case.group, "expect": list(r.case.expect), "expect_id": list(r.case.expect_id),
            "rank": r.rank, "ms": round(r.ms, 1),
            "hits": [{"title": h.title, "heading": h.heading} for h in r.hits]} for r in results]
    return report


def build_comparison(*, run: dict, questions: dict, candidates: list[dict]) -> dict:
    """One entry per embedder: who it is, what loading and indexing took, and the same metrics as a single run.
    Each candidate dict: label, embedder, dim, threshold, load_seconds, index_seconds, sources, results, sweep."""
    entries = []
    for c in candidates:
        entry = {k: c[k] for k in ("label", "embedder", "dim", "threshold", "load_seconds", "index_seconds", "sources")}
        entry["metrics"] = score(c["results"])
        entry["groups"] = group_scores(c["results"])
        if c["sweep"]:
            entry["sweep"] = [{"threshold": t, "metrics": score(rs)} for t, rs in c["sweep"]]
        entries.append(entry)
    return {"schema": SCHEMA, "kind": "compare", "run": run, "questions": questions, "candidates": entries}


# -- markdown ------------------------------------------------------------------------------------

def _pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value * 100:.1f}%"


def _num(value: float | None, digits: int = 3) -> str:
    return "n/a" if value is None else f"{value:.{digits}f}"


def _rate(metrics: dict, name: str) -> str:
    """A rate with the 95% interval in brackets: 85.0% (77–91%)."""
    interval = metrics.get("intervals", {}).get(name)
    if metrics[name] is None or not interval:
        return _pct(metrics[name])
    return f"{_pct(metrics[name])} ({interval[0] * 100:.0f}–{interval[1] * 100:.0f}%)"


def _fmt(name: str, value: float | None) -> str:
    if value is None:
        return "n/a"
    if name.endswith("_ms"):
        return f"{value} ms"
    return _num(value) if name == "mrr" else _pct(value)


def _cell(text: object) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def _table(header: list[str], rows: list[list[object]]) -> list[str]:
    lines = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    return lines + ["| " + " | ".join(_cell(c) for c in row) + " |" for row in rows] + [""]


_INTERVAL_NOTE = ("In brackets: the 95% interval of a rate, the range that holds the true rate in 95 of 100 repetitions with "
                  "other questions of the same kind. Overlapping intervals are a warning against over-reading a difference, "
                  "not a test of it. The tables below show point values only.")


def _sweep_table(sweep: list[dict]) -> list[str]:
    return _table(["Threshold", "Hit@1", "Hit@3", "MRR", "Silence", "False silence", "p95"], [
        [row["threshold"], _pct(row["metrics"]["hit_at_1"]), _pct(row["metrics"]["hit_at_3"]), _num(row["metrics"]["mrr"]),
         _pct(row["metrics"]["silence"]), _pct(row["metrics"]["false_silence"]), f"{row['metrics']['p95_ms']} ms"]
        for row in sweep])


def _history_table(history: list[dict], sub: str) -> list[str]:
    return [f"{sub} History", ""] + _table(["Date", "Embedder", "Threshold", "Questions", "Hit@3", "Silence", "p95"], [
        [e["date"], f"{e['label']}: {e['embedder']}" if e.get("label") else e["embedder"], e["threshold"], e["cases"],
         _pct(e["hit_at_3"]), _pct(e["silence"]), f"{e['p95_ms']} ms"] for e in history])


def render_comparison(report: dict, *, heading: bool = True, history: list[dict] | None = None) -> str:
    run, q = report["run"], report["questions"]
    sub = "##" if heading else "###"
    out = ["# Embedder comparison", ""] if heading else []
    out += [f"{run['date'][:10]} · passageway {run['passageway']} · {q['cases']} questions "
            f"({q['answerable']} answerable, {q['unanswerable']} unanswerable) · {run['machine']}", "",
            "Each embedder ran with its own fresh index and its own relevance threshold, because similarity scales differ "
            "between models. Load is the time to start the model, Index the time to embed all sources.", ""]
    out += _table(["Embedder", "Dimensions", "Threshold", "Load", "Index", "Hit@1", "Hit@3", "MRR", "Silence", "False silence",
                   "p50 / p95"], [
        [f"{c['label']}: {c['embedder']}", c["dim"], c["threshold"], f"{c['load_seconds']} s", f"{c['index_seconds']} s",
         _rate(c["metrics"], "hit_at_1"), _rate(c["metrics"], "hit_at_3"), _num(c["metrics"]["mrr"]),
         _rate(c["metrics"], "silence"), _rate(c["metrics"], "false_silence"),
         f"{c['metrics']['p50_ms']} / {c['metrics']['p95_ms']} ms"] for c in report["candidates"]])
    out += [_INTERVAL_NOTE, ""]
    for c in report["candidates"]:
        if c.get("sweep"):
            out += [f"{sub} Relevance threshold: {c['label']}", ""] + _sweep_table(c["sweep"])
    if history:
        out += _history_table(history, sub)
    return "\n".join(out).rstrip() + "\n"


def render_markdown(report: dict, *, heading: bool = True, history: list[dict] | None = None) -> str:
    if report.get("kind") == "compare":
        return render_comparison(report, heading=heading, history=history)
    run, m = report["run"], report["metrics"]
    sub = "##" if heading else "###"
    sources = ", ".join(f"{name}: {s['items']} items, {s['sections']} sections" for name, s in run["sources"].items())
    out = ["# Retrieval evaluation", ""] if heading else []
    out += [f"{run['date'][:10]} · passageway {run['passageway']} · {run['embedder']} ({run['dim']} dimensions) · "
            f"relevance threshold {run['threshold']}", "",
            f"{run['machine']} · index built in {run['index_seconds']} s ({sources})", ""]
    out += _table(["Metric", "Value"], [
        ["Questions", f"{m['cases']} ({m['answerable']} answerable, {m['unanswerable']} unanswerable)"],
        ["Hit@1", _rate(m, "hit_at_1")], ["Hit@3", _rate(m, "hit_at_3")], ["MRR", _num(m["mrr"])],
        ["Silence on unanswerable questions", _rate(m, "silence")],
        ["False silence on answerable questions", _rate(m, "false_silence")],
        ["Latency p50 / p95", f"{m['p50_ms']} ms / {m['p95_ms']} ms"],
        ["Embedding the question", f"{m['embed_ms']} ms ({_pct(m['embed_share'])} of the latency)"]])
    out += [_INTERVAL_NOTE, ""]
    if report["targets"]:
        out += [f"{sub} Targets", ""]
        out += _table(["Target", "Limit", "Required", "Measured", "Result"], [
            [t["name"], t["limit"], _fmt(t["name"], t["target"]), _fmt(t["name"], t["value"]),
             "pass" if t["passed"] else "fail"] for t in report["targets"]])
    if report.get("sweep"):
        out += [f"{sub} Relevance threshold", ""]
        out += _sweep_table(report["sweep"])
        out += ["A passage that shares three or more words with the question is returned whatever the threshold "
                "(see How it works), so a high threshold only silences short or loosely worded questions.", ""]
    if report["groups"]:
        out += [f"{sub} Groups", ""]
        out += _table(["Group", "Questions", "Hit@3", "Silence"], [
            [name, g["cases"], _rate(g, "hit_at_3"), _rate(g, "silence")] for name, g in report["groups"].items()])
    if report.get("cases"):
        out += [f"{sub} Questions", ""]
        out += _table(["Question", "Accepted", "Rank", "Found", "ms"], [
            [c["query"], ", ".join(c["expect"] + c["expect_id"]) or "(silence)", c["rank"] or "–",
             "; ".join(f"{h['title']} › {h['heading']}" if h["heading"] else h["title"] for h in c["hits"]) or "–",
             c["ms"]] for c in report["cases"]])
    if history:
        out += _history_table(history, sub)
    return "\n".join(out).rstrip() + "\n"


# -- the page you keep up to date ------------------------------------------------------------------

HISTORY_KEYS = ("date", "embedder", "threshold", "passageway", "cases", "hit_at_3", "silence", "p95_ms")
_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")


def _history_file(page: Path) -> Path:
    return page.with_name(page.stem + ".history.json")


def _entries(report: dict) -> list[dict]:
    """The history lines of a run: one, or one per embedder of a comparison."""
    run = report["run"]
    if report.get("kind") == "compare":
        parts = [(c["label"], c["embedder"], c["dim"], c["threshold"], c["metrics"]) for c in report["candidates"]]
    else:
        parts = [(None, run["embedder"], run["dim"], run["threshold"], report["metrics"])]
    return [{"date": run["date"][:10], "embedder": name, "threshold": threshold, "passageway": run["passageway"],
             "cases": m["cases"], "hit_at_3": m["hit_at_3"], "silence": m["silence"], "p95_ms": m["p95_ms"], "dim": dim,
             **({"label": label} if label else {})}
            for label, name, dim, threshold, m in parts]


def _key(entry: dict) -> tuple:
    return entry["date"], entry["embedder"], entry["threshold"], entry["passageway"], entry.get("label")


def _markers(text: str) -> tuple[int, int] | None:
    """Where the results go: the end of the start marker's line and the start of the end marker, for markers that sit on
    lines of their own outside code blocks (a page that explains the markers in a code block has them there too)."""
    starts: list[int] = []
    ends: list[int] = []
    fence, offset = "", 0
    for line in text.splitlines(keepends=True):
        match = _FENCE.match(line)
        if fence:
            if match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence):
                fence = ""
        elif match:
            fence = match.group(1)
        elif line.strip() == START:
            starts.append(offset + line.index(START) + len(START))
        elif line.strip() == END and starts:
            ends.append(offset + line.index(END))
        offset += len(line)
    if len(starts) > 1 or len(ends) > 1:
        raise ReportError("the markers appear more than once outside code blocks: use exactly one pair")
    return (starts[0], ends[0]) if starts and ends else None


def check_page(page: Path) -> tuple[str, int, int]:
    """The page's text and where its markers are; raises ReportError if it cannot take the results (checked before
    a long measurement, so that a typo in the page does not cost a run)."""
    try:
        with open(page, encoding="utf-8", newline="") as f:  # newline="": keep the page's own line endings
            text = f.read()
    except FileNotFoundError:
        raise ReportError(f"{page} not found: create the page with the markers {START} and {END} in it") from None
    except (OSError, UnicodeDecodeError) as e:
        raise ReportError(f"cannot read {page}: {getattr(e, 'strerror', None) or e}") from None
    try:
        found = _markers(text)
    except ReportError as e:
        raise ReportError(f"{page}: {e}") from None
    if found is None:
        raise ReportError(f"{page} needs the markers {START} and {END}, on lines of their own and in this order, "
                          "around where the results go")
    if not os.access(page, os.W_OK):
        raise ReportError(f"cannot write {page}: it is read-only")
    return text, *found


def _read_history(history_file: Path) -> list[dict]:
    if not history_file.exists():
        return []
    try:
        history = json.loads(history_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as e:
        raise ReportError(f"{history_file}: {e}") from None
    if not isinstance(history, list) or not all(isinstance(e, dict) and all(k in e for k in HISTORY_KEYS) for e in history):
        raise ReportError(f"{history_file} is not a history written by passageway eval: move it away or fix it")
    return history


def _write(path: Path, text: str) -> None:
    """Whole or not at all: a half-written page or history would be worse than the old one."""
    tmp = path.with_name(path.name + ".tmp")
    try:
        with open(tmp, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        os.replace(tmp, path)
    except OSError as e:
        tmp.unlink(missing_ok=True)
        raise ReportError(f"cannot write {path}: {e.strerror}") from None


def write_block(page: Path, report: dict) -> None:
    """Replaces what is between the markers in `page` with this run and the last ten, and records the run in
    <page>.history.json (one entry per date, embedder, threshold and version: a repeated run replaces it)."""
    text, start, end = check_page(page)
    history_file = _history_file(page)
    entries = _entries(report)
    replaced = {_key(e) for e in entries}
    history = sorted([e for e in _read_history(history_file) if _key(e) not in replaced] + entries, key=_key)
    newline = "\r\n" if "\r\n" in text else "\n"
    body = render_markdown(report, heading=False, history=list(reversed(history))[:HISTORY_ROWS]).rstrip("\n")
    _write(page, text[:start] + newline + body.replace("\n", newline) + newline + text[end:])
    _write(history_file, json.dumps(history, indent=2, ensure_ascii=False) + "\n")
