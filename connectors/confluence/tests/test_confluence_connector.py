import re
from pathlib import Path

import pytest

from passageway.protocol import parse_item

README = Path(__file__).resolve().parents[1] / "README.md"


def test_list_holds_the_current_pages_of_the_chosen_spaces_only(world):
    ids = world.ids()
    assert set(ids) == {"100", "101", "102", "200"}  # not SECRET, not the draft


def test_the_version_changes_with_content_title_and_labels(world):
    before = world.ids()["101"]
    world.api.edit("101", body="<p>new</p>")
    after_body = world.ids()["101"]
    world.api.edit("101", labels=["security"])
    after_labels = world.ids()["101"]
    assert len({before, after_body, after_labels}) == 3


def test_a_page_becomes_an_item_with_sections_path_labels_and_url(world):
    item = world.fetch("101")["101"]
    parsed = parse_item(item)
    assert parsed.title == "Rotating certificates" and parsed.url == f"{world.url}/pages/viewpage.action?pageId=101"
    assert parsed.path == ("Operations",) and set(parsed.labels) == {"space:OPS", "security", "howto"}
    assert parsed.updated == "2026-10-20T10:00:00Z" and parsed.weight == 1.0
    assert [(s.heading, s.text) for s in parsed.sections] == [
        (None, "Rotate the signing certificate every year."),
        ("Steps", "- Create the new certificate.\n- Deploy it, see the deploy page."),
        ("Steps › Checks", "openssl x509 -noout -dates\nTakes an hour."),
    ]


def test_tables_become_rows_and_ancestors_the_path(world):
    item = world.fetch("102")["102"]
    assert item["path"] == ["Operations", "Rotating certificates"]
    assert item["sections"][0]["text"] == "How to deploy.\nStep | Who\nBuild | CI"


def test_label_filters(world):
    assert set(world.ids(INCLUDE_LABELS="howto")) == {"101", "102"}
    assert set(world.ids(EXCLUDE_LABELS="security")) == {"100", "102", "200"}


def test_fetch_skips_ids_that_are_gone_or_out_of_scope(world):
    assert set(world.fetch("101", "300", "999", "103")) == {"101"}


def test_paging_walks_every_page(world):
    world.api.page_size = 2
    assert set(world.ids()) == {"100", "101", "102", "200"}
    listing = [q for m, p, q in world.api.requests if p == "/rest/api/content"]
    assert any(q.get("start") == "2" for q in listing)


def test_changed_asks_cql_in_confluence_time_and_returns_the_modified_pages(world):
    world.api.edit("200", body="<p>Tuesday: stew.</p>")
    code, records, err = world.call("changed", extra=["--since", "2026-10-25T00:00:00Z"])
    assert code == 0, err
    assert [r["id"] for r in records] == ["200"]
    cql = next(q["cql"] for m, p, q in world.api.requests if p.endswith("/search"))
    assert 'space in ("OPS","HR")' in cql and "type = page" in cql and 'lastModified >= "2026-10-2' in cql


def test_more_pages_than_max_pages_is_an_error_not_a_silent_subset(world):
    code, records, err = world.call("list", MAX_PAGES="2")
    assert code == 1 and records == [] and "MAX_PAGES" in err


@pytest.mark.parametrize("settings,message", [
    ({"URL": ""}, "URL"), ({"URL": "ftp://x"}, "URL"), ({"SPACES": ""}, "SPACES"), ({"TOKEN": ""}, "TOKEN"),
    ({"MAX_PAGES": "lots"}, "MAX_PAGES"), ({"TIMEOUT": "0"}, "TIMEOUT"), ({"VERIFY_TLS": "maybe"}, "VERIFY_TLS"),
])
def test_bad_settings_exit_2_with_a_message_and_no_output(world, settings, message):
    code, records, err = world.call("list", **settings)
    assert code == 2 and records == [] and message in err


def test_a_wrong_token_is_exit_1_without_the_token_in_the_message(world):
    code, records, err = world.call("list", TOKEN="wrong-pat-value")
    assert code == 1 and records == [] and "401" in err and "wrong-pat-value" not in err


def test_429_and_5xx_are_retried_then_given_up(world):
    world.api.status_errors = [429, 503]
    assert set(world.ids()) == {"100", "101", "102", "200"}
    world.api.status_errors = [503] * 100
    code, records, err = world.call("list")
    assert code == 1 and records == [] and "503" in err


def test_a_429_longer_than_a_minute_is_waited_out(world):
    world.api.status_errors = [429] * 8  # 1+2+4+…: over two minutes of waiting
    assert world.fetch("101").keys() == {"101"}
    assert sum(world.slept) > 120


def test_retry_after_is_honoured_beyond_30_seconds(world):
    world.api.status_errors, world.api.retry_after = [429], "200"
    assert world.fetch("101").keys() == {"101"}
    assert world.slept == [200]


def test_a_429_that_never_ends_fails_and_says_how_long_it_waited(world):
    world.api.status_errors = [429] * 1000
    code, records, err = world.call("fetch", '{"id": "101"}\n')
    assert code == 1 and records == [] and "HTTP 429" in err
    waited = sum(world.slept)
    assert 600 <= waited <= 1200 and f"{waited:.0f} s" in err


def test_only_get_requests_are_ever_sent(world):
    world.ids(); world.fetch("101"); world.call("changed", extra=["--since", "2026-10-25T00:00:00Z"])
    assert {m for m, _, _ in world.api.requests} == {"GET"}


def test_every_setting_is_in_the_readme():
    code = (Path(__file__).resolve().parents[1] / "passageway_connector_confluence" / "connector.py").read_text()
    names = sorted(set(re.findall(r'env\.get\(\s*"([A-Z_]+)"', code)) | set(re.findall(r'_list\(\s*env,\s*"([A-Z_]+)"', code)))
    assert len(names) >= 6, names
    readme = README.read_text()
    for name in names:
        assert f"`{name}`" in readme, f"{name} is read by the Confluence connector but missing from its README"


# ---- review findings ------------------------------------------------------------------------------

def test_a_page_id_containing_404_is_not_skipped_on_a_real_failure(world):
    world.api.add("14045", "OPS", "Unlucky", "<p>x</p>")
    world.api.status_errors = [503] * 100
    code, records, err = world.call("fetch", '{"id": "14045"}\n')
    assert code == 1 and records == [] and "503" in err


def test_a_page_that_is_really_gone_is_skipped(world):
    assert world.fetch("999") == {}


def test_changed_asks_with_a_margin_for_confluences_timezone(world):
    world.call("changed", extra=["--since", "2026-10-25T12:00:00Z"])
    cql = next(q["cql"] for m, p, q in world.api.requests if p.endswith("/search"))
    assert 'lastModified >= "2026-10-24 22:00"' in cql  # 14 hours earlier: CQL reads the time in the server's zone


def test_paging_stops_when_a_page_brings_nothing_new(world):
    world.api.page_size = 2
    world.api.loop = True  # a server that ignores `start`, as cursor-paged ones do
    assert set(world.ids()) == {"100", "101"} or len(world.ids()) >= 2  # ends, instead of looping forever


def test_a_space_that_lists_nothing_is_a_warning(world):
    code, records, err = world.call("list", SPACES="OPS|EMPTY")
    assert code == 0 and "EMPTY" in err and "no pages" in err


def test_a_redirect_is_a_clear_error(world):
    world.api.redirect = True
    code, _, err = world.call("list")
    assert code == 1 and "redirect" in err.lower()


def test_verify_tls_false_warns(world):
    code, _, err = world.call("check", VERIFY_TLS="false")
    assert code == 0 and "VERIFY_TLS" in err
