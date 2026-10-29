"""Reports: a JSON document for machines, markdown for people, and a block that keeps a page of yours up to date."""

import json
import platform
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


# -- markdown ------------------------------------------------------------------------------------

def _pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value * 100:.1f}%"


def _num(value: float | None, digits: int = 3) -> str:
    return "n/a" if value is None else f"{value:.{digits}f}"


def _cell(text: object) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def _table(header: list[str], rows: list[list[object]]) -> list[str]:
    lines = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    return lines + ["| " + " | ".join(_cell(c) for c in row) + " |" for row in rows] + [""]


def render_markdown(report: dict, *, heading: bool = True, history: list[dict] | None = None) -> str:
    run, m = report["run"], report["metrics"]
    sub = "##" if heading else "###"
    sources = ", ".join(f"{name}: {s['items']} items, {s['sections']} sections" for name, s in run["sources"].items())
    out = ["# Retrieval evaluation", ""] if heading else []
    out += [f"{run['date'][:10]} · passageway {run['passageway']} · {run['embedder']} ({run['dim']} dimensions) · "
            f"relevance threshold {run['threshold']}", "",
            f"{run['machine']} · index built in {run['index_seconds']} s ({sources})", ""]
    out += _table(["Metric", "Value"], [
        ["Questions", f"{m['cases']} ({m['answerable']} answerable, {m['unanswerable']} unanswerable)"],
        ["Hit@1", _pct(m["hit_at_1"])], ["Hit@3", _pct(m["hit_at_3"])], ["MRR", _num(m["mrr"])],
        ["Silence on unanswerable questions", _pct(m["silence"])],
        ["False silence on answerable questions", _pct(m["false_silence"])],
        ["Latency p50 / p95", f"{m['p50_ms']} ms / {m['p95_ms']} ms"],
        ["Embedding the question", f"{m['embed_ms']} ms ({_pct(m['embed_share'])} of the latency)"]])
    if report["targets"]:
        out += [f"{sub} Targets", ""]
        out += _table(["Target", "Limit", "Required", "Measured", "Result"], [
            [t["name"], t["limit"], t["target"], "n/a" if t["value"] is None else t["value"],
             "pass" if t["passed"] else "fail"] for t in report["targets"]])
    if report.get("sweep"):
        out += [f"{sub} Relevance threshold", ""]
        out += _table(["Threshold", "Hit@1", "Hit@3", "MRR", "Silence", "False silence", "p95"], [
            [row["threshold"], _pct(row["metrics"]["hit_at_1"]), _pct(row["metrics"]["hit_at_3"]),
             _num(row["metrics"]["mrr"]), _pct(row["metrics"]["silence"]), _pct(row["metrics"]["false_silence"]),
             f"{row['metrics']['p95_ms']} ms"] for row in report["sweep"]])
    if report["groups"]:
        out += [f"{sub} Groups", ""]
        out += _table(["Group", "Questions", "Hit@3", "Silence"], [
            [name, g["cases"], _pct(g["hit_at_3"]), _pct(g["silence"])] for name, g in report["groups"].items()])
    if report.get("cases"):
        out += [f"{sub} Questions", ""]
        out += _table(["Question", "Accepted", "Rank", "Found", "ms"], [
            [c["query"], ", ".join(c["expect"] + c["expect_id"]) or "(silence)", c["rank"] or "–",
             "; ".join(f"{h['title']} › {h['heading']}" if h["heading"] else h["title"] for h in c["hits"]) or "–",
             c["ms"]] for c in report["cases"]])
    if history:
        out += [f"{sub} History", ""]
        out += _table(["Date", "Embedder", "Threshold", "Questions", "Hit@3", "Silence", "p95"], [
            [e["date"], e["embedder"], e["threshold"], e["cases"], _pct(e["hit_at_3"]), _pct(e["silence"]),
             f"{e['p95_ms']} ms"] for e in history])
    return "\n".join(out).rstrip() + "\n"


# -- the page you keep up to date ------------------------------------------------------------------

def _history_file(page: Path) -> Path:
    return page.with_name(page.stem + ".history.json")


def _entry(report: dict) -> dict:
    run, m = report["run"], report["metrics"]
    return {"date": run["date"][:10], "embedder": run["embedder"], "threshold": run["threshold"],
            "passageway": run["passageway"], "cases": m["cases"], "hit_at_3": m["hit_at_3"], "silence": m["silence"],
            "p95_ms": m["p95_ms"]}


def _key(entry: dict) -> tuple:
    return entry["date"], entry["embedder"], entry["threshold"], entry["passageway"]


def check_page(page: Path) -> tuple[str, int, int]:
    """The page's text and where its markers are; raises ReportError if it cannot take the results (checked before
    a long measurement, so that a typo in the page does not cost a run)."""
    try:
        text = page.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise ReportError(f"{page} not found: create the page with the markers {START} and {END} in it") from None
    start, end = text.find(START), text.find(END)
    if start < 0 or end < start:
        raise ReportError(f"{page} needs the markers {START} and {END}, in this order, around where the results go")
    return text, start, end


def write_block(page: Path, report: dict) -> None:
    """Replaces what is between the markers in `page` with this run and the last ten, and records the run in
    <page>.history.json (one entry per date, embedder, threshold and version: a repeated run replaces it)."""
    text, start, end = check_page(page)
    history_file = _history_file(page)
    try:
        history = json.loads(history_file.read_text(encoding="utf-8")) if history_file.exists() else []
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise ReportError(f"{history_file}: {e}") from None
    entry = _entry(report)
    history = sorted([e for e in history if _key(e) != _key(entry)] + [entry], key=_key)
    body = render_markdown(report, heading=False, history=list(reversed(history))[:HISTORY_ROWS]).rstrip("\n")
    history_file.write_text(json.dumps(history, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    page.write_text(text[:start + len(START)] + "\n" + body + "\n" + text[end:], encoding="utf-8")
