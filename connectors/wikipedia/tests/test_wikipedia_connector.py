import io
import json

import pytest

from passageway.protocol import parse_item
from passageway_connector_wikipedia.connector import ScopeError, parse_scope, run

TEXT = "Heligoland is an island.\n\n== History ==\nSettled early.\n\n== References ==\nA citation."


def call(env, mode, stdin=""):
    out, err = io.StringIO(), io.StringIO()
    code = run(["connector", mode], env, io.StringIO(stdin), out, err, sleep=lambda s: None)
    return code, [json.loads(line) for line in out.getvalue().splitlines()], err.getvalue()


@pytest.fixture
def env(wiki_server):
    url, wiki = wiki_server
    wiki.add(1, "Heligoland", TEXT, revid=11, ts="2026-10-05T00:00:00Z")
    wiki.add(2, "Cape Arkona", "Cape text.", revid=22)
    wiki.categories["Category:Lighthouses"] = {"pages": [1, 2], "subcats": []}
    return {"API_URL": url, "PAGE_URL": "https://wiki.example/wiki/", "CATEGORIES": "Lighthouses",
            "PAUSE_SECONDS": "0"}


def test_list_prints_page_ids_with_revision_ids(env):
    code, records, _ = call(env, "list")
    assert code == 0 and sorted(records, key=lambda r: r["id"]) == [
        {"id": "1", "version": "11"}, {"id": "2", "version": "22"}]


def test_check_counts_the_scope(env):
    assert call(env, "check")[1] == [{"ok": True, "count": 2}]


def test_fetch_returns_valid_items_with_sections_and_urls(env):
    code, records, _ = call(env, "fetch", '{"id": "1"}\n')
    assert code == 0 and len(records) == 1
    item = parse_item(records[0])  # the core's own parser accepts it
    assert (item.id, item.title, item.version, item.updated) == ("1", "Heligoland", "11", "2026-10-05T00:00:00Z")
    assert item.url == "https://wiki.example/wiki/Heligoland"
    assert [(s.heading, s.text) for s in item.sections] == [(None, "Heligoland is an island."), ("History", "Settled early.")]


def test_urls_encode_spaces_and_special_characters(env, wiki_server):
    _, wiki = wiki_server
    wiki.add(3, "Roter Sand (Leuchtturm)", "Text.")
    _, records, _ = call(env, "fetch", '{"id": "3"}\n')
    assert records[0]["url"] == "https://wiki.example/wiki/Roter_Sand_(Leuchtturm)"


def test_a_page_deleted_after_list_or_an_unknown_id_is_skipped_not_an_error(env):
    code, records, _ = call(env, "fetch", '{"id": "1"}\n{"id": "999"}\n{"id": "not-a-page-id"}\n')
    assert code == 0 and [r["id"] for r in records] == ["1"]


def test_a_page_without_text_is_an_item_with_no_sections(env, wiki_server):
    _, wiki = wiki_server
    wiki.add(4, "Empty page", "")
    _, records, _ = call(env, "fetch", '{"id": "4"}\n')
    assert records[0]["sections"] == []


def test_changed_prints_nothing(env):
    assert call(env, "changed")[:2] == (0, [])


def test_titles_and_geo_scopes(env, wiki_server):
    _, wiki = wiki_server
    wiki.geo = [2]
    base = {k: v for k, v in env.items() if k != "CATEGORIES"}
    assert [r["id"] for r in call({**base, "TITLES": "Heligoland"}, "list")[1]] == ["1"]
    assert [r["id"] for r in call({**base, "GEO": "54.18,7.88,5000"}, "list")[1]] == ["2"]


def test_a_scope_over_max_pages_fails_loudly_with_empty_stdout(env):
    code, records, err = call({**env, "MAX_PAGES": "1"}, "list")
    assert code == 1 and records == [] and "MAX_PAGES" in err


@pytest.mark.parametrize("bad", [
    {"CATEGORIES": ""}, {"CATEGORY_DEPTH": "-1"}, {"CATEGORY_DEPTH": "x"}, {"MAX_PAGES": "0"},
    {"GEO": "54.18,7.88"}, {"GEO": "54.18,7.88,20000"}, {"GEO": "a,b,c"}, {"LANGUAGE": "../x"},
    {"PAUSE_SECONDS": "-1"}, {"PAUSE_SECONDS": "soon"}])
def test_bad_settings_exit_2_with_a_message_and_empty_stdout(env, bad):
    base = {k: v for k, v in env.items() if k != "CATEGORIES"}
    code, records, err = call({**base, **({"CATEGORIES": "Lighthouses"} if "CATEGORIES" not in bad else {}), **bad}, "list")
    assert code == 2 and records == [] and err.strip() and "Traceback" not in err


def test_unknown_mode_exits_2(env):
    assert call(env, "frobnicate")[0] == 2


def test_parse_scope_defaults():
    scope = parse_scope({"CATEGORIES": "A|B", "CONTACT": "me@example.org"})
    assert scope.api_url == "https://en.wikipedia.org/w/api.php" and scope.categories == ("A", "B")
    assert (scope.depth, scope.max_pages) == (1, 500) and "references" in scope.skip
    with pytest.raises(ScopeError, match="CATEGORIES"):
        parse_scope({})


def test_german_settings():
    scope = parse_scope({"LANGUAGE": "de", "CATEGORIES": "Kategorie:Leuchtturm in Deutschland"})
    assert scope.api_url == "https://de.wikipedia.org/w/api.php" and scope.page_url == "https://de.wikipedia.org/wiki/"
    assert scope.categories == ("Kategorie:Leuchtturm in Deutschland",) and "einzelnachweise" in scope.skip


def test_german_page_sections_urls_and_umlauts(env, wiki_server):
    _, wiki = wiki_server
    wiki.add(5, "Köln Süd", "Einleitung.\n\n== Geschichte ==\nAlt.\n\n== Einzelnachweise ==\nBeleg.")
    _, records, _ = call(env, "fetch", '{"id": "5"}\n')
    assert [s["heading"] for s in records[0]["sections"]] == [None, "Geschichte"]
    assert records[0]["title"] == "Köln Süd" and records[0]["url"] == "https://wiki.example/wiki/K%C3%B6ln_S%C3%BCd"


def test_redirect_pages_in_a_category_are_not_listed_counted_or_fetched(env, wiki_server):
    _, wiki = wiki_server
    wiki.add(20, "Helgoland", "#REDIRECT Heligoland", revid=5)
    wiki.redirect_pages.add(20)
    wiki.categories["Category:Lighthouses"]["pages"].append(20)
    assert sorted(r["id"] for r in call(env, "list")[1]) == ["1", "2"]
    assert call(env, "check")[1] == [{"ok": True, "count": 2}]  # check and list must agree
    assert call(env, "fetch", '{"id": "20"}\n')[1] == []
