"""The roadmap is data (docs/roadmap.yml) rendered as a timeline by a MkDocs hook (docs_hooks/roadmap.py)."""

import importlib.util
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
STATUSES = {"next", "later", "decide", "done"}
# The plan must not be lost: every step and every open decision of the roadmap has an entry.
REQUIRED = {"markdown-connector", "frozen-corpus", "eval-harness", "embedders", "trilium-connector", "confluence-connector",
            "hook-plugin-image", "trilium-recall-adopts", "decide-transport", "decide-sdk"}


def hook():
    spec = importlib.util.spec_from_file_location("roadmap_hook", ROOT / "docs_hooks" / "roadmap.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def data() -> dict:
    return yaml.safe_load((ROOT / "docs" / "roadmap.yml").read_text())


def item(**kw):
    return {"id": "x", "status": "next", "when": "Next", "icon": "check-circle", "title": "T", "summary": "S", **kw}


def test_every_entry_is_complete_and_the_plan_is_all_there():
    items = data()["items"]
    ids = [i["id"] for i in items]
    assert len(ids) == len(set(ids)), "ids must be unique"
    assert REQUIRED <= set(ids), f"roadmap steps missing from roadmap.yml: {sorted(REQUIRED - set(ids))}"
    for i in items:
        assert i["status"] in STATUSES, i["id"]
        assert re.fullmatch(r"[a-z0-9-]+", i["icon"]), i["id"]
        assert i["title"] and i["summary"], i["id"]
        for link in i.get("links", []):
            assert link["label"] and link["url"].startswith("https://"), i["id"]
        if i["status"] == "done":
            assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(i["date"])), f"{i['id']}: a done entry needs its date"
            assert i.get("links"), f"{i['id']}: a done entry links its pull request or release"
        else:
            assert i["when"] and i.get("details"), f"{i['id']}: an open entry says when and carries the details"
    assert "done" in {i["status"] for i in items}  # every step may be done; what is parked is on the page itself


def test_open_entries_come_first_in_file_order_and_done_ones_follow_newest_first():
    html = hook().render({"items": [
        item(id="a", title="First open"), item(id="b", status="later", when="Later", title="Second open"),
        item(id="c", status="done", date="2026-10-01", links=[{"label": "PR 1", "url": "https://e.org/1"}], title="Old done"),
        item(id="d", status="done", date="2026-10-20", links=[{"label": "PR 2", "url": "https://e.org/2"}], title="New done")]},
        icon=lambda name: "<svg/>")
    order = [html.index(t) for t in ("First open", "Second open", "New done", "Old done")]
    assert order == sorted(order)
    assert "20 Oct 2026" in html and "1 Oct 2026" in html


def test_the_markup_is_escaped_and_survives_markdowns_raw_html_rules():
    html = hook().render({"items": [item(title="<script>alert(1)</script> & co", details="**bold** and a [link](https://e.org)")]},
                         icon=lambda name: "<svg/>")
    assert "<script>" not in html and "&lt;script&gt;" in html
    assert "<strong>bold</strong>" in html and 'href="https://e.org"' in html
    assert "\n\n" not in html, "a blank line would end the raw HTML block in Python-Markdown"
    assert 'class="pw-timeline"' in html and 'aria-hidden="true"' in html


def test_the_page_shell_the_hook_and_the_pointers_are_wired():
    assert "<!-- roadmap -->" in (ROOT / "docs" / "roadmap.md").read_text()
    config = (ROOT / "mkdocs.yml").read_text()
    assert "docs_hooks/roadmap.py" in config and "roadmap.md" in config
    assert "docs/roadmap.yml" in (ROOT / "CLAUDE.md").read_text()
    assert "(roadmap.md)" in (ROOT / "docs" / "index.md").read_text()


def test_the_stylesheet_has_the_timeline_and_a_layout_for_narrow_screens():
    css = (ROOT / "docs" / "stylesheets" / "extra.css").read_text()
    for selector in (".pw-timeline", ".pw-tl-row", ".pw-tl-dot", ".pw-tl-card"):
        assert selector in css, selector
    assert "max-width" in css.split(".pw-timeline", 1)[1]
