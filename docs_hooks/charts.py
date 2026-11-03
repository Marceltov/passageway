"""MkDocs hook: draws the charts of the measurement pages as inline SVG, from the numbers the pages already hold.

`<!-- chart:outcomes -->`, `<!-- chart:sweep -->` and `<!-- chart:groups -->` in docs/measurements.md are read from the
results block `corpus/measure.sh` writes (its tables), and `<!-- chart:models -->` in docs/models.md from
docs/models.history.json, so a chart is never typed by hand and moves with the next measurement (V3). The tables stay
on the page as the table view; every mark carries its value as a tooltip. Colours are CSS variables (extra.css).
"""

import html
import json
import re
from pathlib import Path

DOCS = Path(__file__).resolve().parents[1] / "docs"
W = 640
FONT = 'font-family="inherit"'


def _pct(text: str) -> float:
    return float(text.split("%")[0]) / 100


def _table(block: str, heading: str) -> list[list[str]]:
    """The rows (header and rule dropped) of the first table at or after `heading`."""
    rows, started = [], False
    for line in block.split(heading, 1)[1].splitlines():
        if line.startswith("|"):
            started = True
            rows.append([c.strip() for c in line.strip("|").split("|")])
        elif started:
            break
    return rows[2:]


def _svg(height: int, body: str, label: str) -> str:
    # one line: a blank line would end the raw HTML block in Python-Markdown
    return f'<figure class="pw-chart"><svg viewBox="0 0 {W} {height}" role="img" aria-label="{html.escape(label)}">{body}</svg></figure>'


def _text(x: float, y: float, s: str, anchor: str = "start", cls: str = "") -> str:
    return f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" class="{cls}" {FONT}>{html.escape(s)}</text>'


def _segmented(rows: list[tuple[str, list[tuple[str, int, int]]]]) -> str:
    """Stacked share bars: a row is (label, [(segment label, count, colour slot)])."""
    body, y = "", 18
    for label, segments in rows:
        total = sum(c for _, c, _ in segments)
        body += _text(0, y, f"{label}", cls="pw-chart-label")
        x, width = 0.0, W
        for name, count, slot in segments:
            w = width * count / total
            if w > 0:
                body += (f'<rect x="{x + 1:.1f}" y="{y + 8}" width="{max(w - 2, 0):.1f}" height="26" rx="3" class="pw-s{slot}">'
                         f"<title>{html.escape(name)}: {count} of {total}</title></rect>")
                if w > 54:
                    body += _text(x + w / 2, y + 26, str(count), "middle", "pw-chart-ontext")
            x += w
        body += f'<g transform="translate(0,{y + 52})">'
        lx = 0.0
        for name, count, slot in segments:
            body += f'<rect x="{lx:.1f}" y="-9" width="10" height="10" rx="2" class="pw-s{slot}"/>' + _text(lx + 16, 0, f"{name} ({count})", cls="pw-chart-small")
            lx += 16 + 7 * len(f"{name} ({count})") * 0.9 + 18
        body += "</g>"
        y += 92
    return _svg(y - 14, body, "Where the questions land")


def outcomes(block: str) -> str:
    head = {r[0]: r[1] for r in _table(block, block.strip().splitlines()[0])}
    answerable, unanswerable = map(int, re.search(r"\((\d+) answerable, (\d+) unanswerable\)", head["Questions"]).groups())
    hit1 = round(_pct(head["Hit@1"]) * answerable)
    hit3 = round(_pct(head["Hit@3"]) * answerable)
    silent = round(_pct(head["Silence on unanswerable questions"]) * unanswerable)
    return _segmented([
        (f"{answerable} questions with an answer in the corpus", [("right article first", hit1, 1), ("second or third", hit3 - hit1, 3), ("not in the top three", answerable - hit3, 2)]),
        (f"{unanswerable} questions the corpus cannot answer", [("silent", silent, 1), ("returned a passage", unanswerable - silent, 2)]),
    ])


def sweep(block: str) -> str:
    rows = _table(block, "### Relevance threshold")
    default = float(re.search(r"relevance threshold ([\d.]+)", block).group(1))
    xs = [float(r[0]) for r in rows]
    series = [("Hit@3", 2, 1), ("Silence", 4, 3), ("False silence", 5, 2)]
    left, right, top, bottom = 40, 96, 12, 36
    h = 280
    px = lambda v: left + (v - xs[0]) / (xs[-1] - xs[0]) * (W - left - right)
    py = lambda v: top + (1 - v) * (h - top - bottom)
    body = ""
    for g in (0, .25, .5, .75, 1):
        body += f'<line x1="{left}" x2="{W - right}" y1="{py(g):.1f}" y2="{py(g):.1f}" class="pw-grid"/>' + _text(left - 8, py(g) + 4, f"{g:.0%}", "end", "pw-chart-small")
    ticks = [round(xs[0] + i * 0.02, 2) for i in range(int((xs[-1] - xs[0]) / 0.02 + 1e-9) + 1)]
    for v in ticks:
        body += _text(px(v), h - 14, f"{v:g}", "middle", "pw-chart-small")
    body += f'<line x1="{px(default):.1f}" x2="{px(default):.1f}" y1="{top}" y2="{h - bottom}" class="pw-default"/>' + _text(px(default) + 6, top + 10, f"default {default:g}", cls="pw-chart-small")
    for name, col, slot in series:
        vals = [_pct(r[col]) for r in rows]
        pts = " ".join(f"{px(x):.1f},{py(v):.1f}" for x, v in zip(xs, vals))
        body += f'<polyline points="{pts}" class="pw-line pw-l{slot}"/>'
        for x, v in zip(xs, vals):
            body += f'<circle cx="{px(x):.1f}" cy="{py(v):.1f}" r="4" class="pw-s{slot} pw-ring"><title>{name} at {x:g}: {v:.1%}</title></circle>'
        body += _text(W - right + 10, py(vals[-1]) + 4, name, cls="pw-chart-label")
    return _svg(h, body, "Hit@3, silence and false silence at each relevance threshold")


def groups(block: str) -> str:
    rows = _table(block, "### Groups")
    parsed = []
    for name, n, hit, sil in rows:
        cell, slot, metric = (hit, 1, "Hit@3") if hit != "n/a" else (sil, 3, "Silence")
        value = _pct(cell)
        lo, hi = (int(v) / 100 for v in re.search(r"\((\d+)–(\d+)%\)", cell).groups())
        parsed.append((f"{name} ({n})", metric, value, lo, hi, slot))
    left, right, top = 150, 120, 8
    row_h = 38
    h = top + row_h * len(parsed) + 30
    px = lambda v: left + v * (W - left - right)
    body = ""
    for g in (0, .25, .5, .75, 1):
        body += f'<line x1="{px(g):.1f}" x2="{px(g):.1f}" y1="{top}" y2="{h - 26}" class="pw-grid"/>' + _text(px(g), h - 8, f"{g:.0%}", "middle", "pw-chart-small")
    for i, (label, metric, v, lo, hi, slot) in enumerate(parsed):
        y = top + row_h * i + row_h / 2
        tip = f"{label}, {metric}: {v:.1%} (95% interval {lo:.0%}–{hi:.0%})"
        body += _text(left - 12, y + 4, label, "end", "pw-chart-label")
        body += f'<line x1="{px(lo):.1f}" x2="{px(hi):.1f}" y1="{y:.1f}" y2="{y:.1f}" class="pw-whisker pw-l{slot}"/>'
        body += f'<circle cx="{px(v):.1f}" cy="{y:.1f}" r="6" class="pw-s{slot} pw-ring"><title>{html.escape(tip)}</title></circle>'
        body += _text(W - right + 12, y + 4, f"{metric} {v:.0%}", cls="pw-chart-small")
    return _svg(h, body, "Hit@3 and silence per question group, with 95% intervals")


def models(_: str) -> str:
    data = json.loads((DOCS / "models.history.json").read_text())
    latest = {}
    for d in data:
        latest[d["embedder"]] = d  # the file is in date order
    entries = sorted(latest.values(), key=lambda d: -d["hit_at_3"])
    left, right, top, row_h = 130, 16, 8, 62
    h = top + row_h * len(entries) + 54
    px = lambda v: left + v * (W - left - right)
    body = ""
    for g in (0, .25, .5, .75, 1):
        body += f'<line x1="{px(g):.1f}" x2="{px(g):.1f}" y1="{top}" y2="{h - 46}" class="pw-grid"/>' + _text(px(g), h - 30, f"{g:.0%}", "middle", "pw-chart-small")
    for i, d in enumerate(entries):
        y = top + row_h * i
        body += _text(left - 12, y + 30, d.get("label", d["embedder"]), "end", "pw-chart-label")
        for j, (name, key, slot) in enumerate((("Hit@3", "hit_at_3", 1), ("Silence", "silence", 3))):
            v = d[key]
            by = y + 8 + j * 22
            body += (f'<path d="M{left},{by} H{px(v) - 4:.1f} a4,4 0 0 1 4,4 v10 a4,4 0 0 1 -4,4 H{left} Z" class="pw-s{slot}">'
                     f'<title>{d.get("label", d["embedder"])}, {name}: {v:.1%}</title></path>')
            body += _text(px(v) + 6, by + 14, f"{v:.1%}", cls="pw-chart-small")
    ly = h - 8
    body += f'<rect x="{left}" y="{ly - 9}" width="10" height="10" rx="2" class="pw-s1"/>' + _text(left + 16, ly, "Hit@3", cls="pw-chart-small")
    body += f'<rect x="{left + 80}" y="{ly - 9}" width="10" height="10" rx="2" class="pw-s3"/>' + _text(left + 96, ly, "Silence", cls="pw-chart-small")
    return _svg(h, body, "Hit@3 and silence of each built-in model")


CHARTS = {"outcomes": outcomes, "sweep": sweep, "groups": groups, "models": models}


def on_page_markdown(markdown: str, page, config, files) -> str:
    if "<!-- chart:" not in markdown:
        return markdown
    block = markdown.split("<!-- passageway:results:start -->", 1)[-1].split("<!-- passageway:results:end -->", 1)[0]
    return re.sub(r"<!-- chart:(\w+) -->", lambda m: CHARTS[m.group(1)](block), markdown)
