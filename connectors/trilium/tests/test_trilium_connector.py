import json
from pathlib import Path

import pytest

from passageway.protocol import parse_item

README = Path(__file__).resolve().parents[1] / "README.md"


# ---- what exists ----------------------------------------------------------------------------------------

def test_list_holds_every_text_and_code_note_in_scope_and_nothing_excluded(world):
    ids = world.ids()
    assert {"fxLxcMemory", "fxSrcArticle", "fxDay", "fxOther", "fxCode", "fxHubHomelab", "fxSumArticle"} <= set(ids)
    assert "fxLockClaim" not in ids and "fxTplHub" not in ids  # locks and templates are plumbing
    assert "fxArchived" not in ids  # archived notes are not returned by ETAPI search
    assert "fxWiki" in ids and "fxSources" in ids  # the area roots themselves are notes too


def test_check_counts_what_list_lists(world):
    assert world.call("check")[1][0]["count"] == len(world.ids())


def test_the_version_changes_with_content_title_attributes_and_place(world):
    before = world.ids()["fxBridges"]
    world.etapi.set_content("fxBridges", "<p>new</p>")
    after_content = world.ids()["fxBridges"]
    world.etapi.add_label("fxBridges", "wikiStatus", "reviewed")
    after_label = world.ids()["fxBridges"]
    world.etapi.move("fxBridges", "fxHubTrilium")
    after_move = world.ids()["fxBridges"]
    assert len({before, after_content, after_label, after_move}) == 4


# ---- the item ---------------------------------------------------------------------------------------------

def test_a_wiki_page_becomes_an_item_with_area_weight_labels_path_and_link(world):
    item = world.fetch("fxBackups")["fxBackups"]
    parsed = parse_item(item)
    assert parsed.title == "Nightly backups" and parsed.url == f"{world.url}/#root/fxBackups"
    assert parsed.weight == 1.0 and parsed.path == ("Homelab",)
    assert set(parsed.labels) == {"area:wiki", "type:concept", "topic:homelab", "status:draft"}
    assert [(s.heading, s.text[:30]) for s in parsed.sections] == [(None, "vzdump runs every night at 02:"),
                                                                    ("Offsite", "restic copies the datastore to")]
    assert set(parsed.links) == {"fxRestic", "fxLxcMemory"}  # the link in the text and the relatesTo relation
    assert parsed.updated.endswith("Z") and "T" in parsed.updated


def test_areas_give_weights_and_the_journal_and_the_rest_are_recognised(world):
    got = world.fetch("fxSrcArticle", "fxDay", "fxOther", "fxHubHomelab")
    assert got["fxSrcArticle"]["weight"] == 0.8 and "area:source" in got["fxSrcArticle"]["labels"]
    assert got["fxDay"]["weight"] == 0.6 and "area:journal" in got["fxDay"]["labels"]
    assert got["fxOther"]["weight"] == 0.6 and "area:other" in got["fxOther"]["labels"] and "path" not in got["fxOther"]
    assert got["fxHubHomelab"]["weight"] == 1.0 and "type:hub" in got["fxHubHomelab"]["labels"]


def test_the_path_is_the_ancestor_titles_below_the_area_root(world):
    assert world.fetch("fxSrcArticle")["fxSrcArticle"]["path"] == ["2026"]
    deep = world.etapi.add("Deep", parent="fxLxcMemory", content="<p>deep</p>")
    assert world.fetch(deep)[deep]["path"] == ["Homelab", "LXC memory limits"]


def test_a_summary_links_its_source_and_the_source_links_back(world):
    got = world.fetch("fxSumArticle", "fxSrcArticle")
    assert "fxSrcArticle" in got["fxSumArticle"]["links"] and "type:summary" in got["fxSumArticle"]["labels"]
    assert got["fxSrcArticle"]["links"] == ["fxSumArticle"]  # the source has no relation of its own: the reverse is added


def test_links_point_only_at_notes_in_scope(world):
    world.etapi.notes["fxBackups"].attrs.append(("relation", "relatesTo", "fxLockClaim", True))
    world.etapi.notes["fxBackups"].attrs.append(("relation", "relatesTo", "nope", True))
    assert set(world.fetch("fxBackups")["fxBackups"]["links"]) == {"fxRestic", "fxLxcMemory"}


def test_a_code_note_is_split_at_blank_lines_not_parsed_as_html(world):
    sections = world.fetch("fxCode")["fxCode"]["sections"]
    assert [s["text"] for s in sections] == ["#!/bin/sh\nrestic backup /data\necho done"]  # small paragraphs share a passage
    assert "<" not in sections[0]["text"]


def test_html_becomes_readable_text_lists_tables_and_headings(world):
    nid = world.etapi.add("Rich", parent="fxHubHomelab", content=(
        "<p>Intro with <strong>bold</strong> and a <a href='#root/fxRestic'>link</a>.</p><h2>Steps</h2><ul><li>one</li>"
        "<li>two<ul><li>nested</li></ul></li></ul><h3>Table</h3><table><tr><th>a</th><th>b</th></tr><tr><td>1</td><td>2</td></tr></table>"
        "<pre><code>raw  code</code></pre><script>evil()</script>"))
    sections = world.fetch(nid)[nid]["sections"]
    assert [(s["heading"], s["text"]) for s in sections] == [
        (None, "Intro with bold and a link."), ("Steps", "- one\n- two\n  - nested"), ("Steps › Table", "a | b\n1 | 2\nraw  code")]


def test_an_empty_note_is_an_item_without_sections(world):
    nid = world.etapi.add("Empty", parent="fxHubHomelab", content="")
    assert world.fetch(nid)[nid]["sections"] == []


def test_fetch_skips_ids_that_are_gone_or_out_of_scope(world):
    assert set(world.fetch("fxBackups", "fxLockClaim", "nope")) == {"fxBackups"}


# ---- changed ----------------------------------------------------------------------------------------------

def test_changed_returns_what_was_modified_since_in_trilium_time(world):
    world.etapi.set_content("fxBridges", "<p>changed</p>")
    code, records, err = world.call("changed", extra=["--since", "2026-10-25T00:00:00Z"])
    assert code == 0, err
    assert [r["id"] for r in records] == ["fxBridges"]
    query = next(q for m, p, q in world.etapi.requests if p.endswith("/notes") and "utcDateModified" in q.get("search", ""))
    assert "2026-10-25 00:00:00" in query["search"]  # Trilium's own time format


def test_a_note_moved_into_an_excluded_area_is_not_in_changed_and_drops_at_list(world):
    world.etapi.move("fxBridges", "fxLocks")
    _, records, _ = world.call("changed", extra=["--since", "2026-10-25T00:00:00Z"])
    assert all(r["id"] != "fxBridges" for r in records) and "fxBridges" not in world.ids()


# ---- settings and failure ----------------------------------------------------------------------------------

@pytest.mark.parametrize("settings,message", [
    ({"URL": ""}, "URL"), ({"URL": "ftp://x"}, "URL"), ({"TOKEN": ""}, "TOKEN"), ({"TIMEOUT": "soon"}, "TIMEOUT"),
    ({"WEB_URL": "not a url"}, "WEB_URL"),
])
def test_bad_settings_exit_2_with_a_message_and_no_output(world, settings, message):
    code, records, err = world.call("list", **settings)
    assert code == 2 and records == [] and message in err


def test_a_wrong_token_is_a_runtime_error_that_does_not_show_the_token(world):
    code, records, err = world.call("list", TOKEN="wrong-token-value")
    assert code == 1 and records == [] and "401" in err and "wrong-token-value" not in err


def test_a_trilium_that_is_down_is_exit_1_with_nothing_printed(world):
    world.etapi.fail = True
    code, records, err = world.call("list")
    assert code == 1 and records == [] and "503" in err


def test_only_get_requests_are_ever_sent(world):
    world.ids(); world.fetch("fxBackups"); world.call("changed", extra=["--since", "2026-10-25T00:00:00Z"])
    assert {m for m, _, _ in world.etapi.requests} == {"GET"}


def test_the_web_url_for_links_can_differ_from_the_api_url(world):
    item = world.fetch("fxBackups", WEB_URL="https://notes.example.org/")["fxBackups"]
    assert item["url"] == "https://notes.example.org/#root/fxBackups"


def test_every_setting_is_in_the_readme():
    import re
    code = (Path(__file__).resolve().parents[1] / "passageway_connector_trilium" / "connector.py").read_text()
    names = sorted(set(re.findall(r'env\.get\(\s*"([A-Z_]+)"', code)))
    assert len(names) >= 4, names
    readme = README.read_text()
    for name in names:
        assert f"`{name}`" in readme, f"{name} is read by the Trilium connector but missing from its README"
