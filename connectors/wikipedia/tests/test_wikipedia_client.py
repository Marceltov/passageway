import pytest

from passageway_connector_wikipedia import mediawiki
from passageway_connector_wikipedia.mediawiki import Wiki, WikiError


def client(url, sleeps=None):
    return Wiki(url, "test-agent/1.0", pause=0, sleep=(sleeps.append if sleeps is not None else lambda s: None))


def lighthouse_wiki(wiki):
    for i, t in [(1, "Heligoland"), (2, "Cape Arkona"), (3, "Roter Sand"), (4, "Lindau"), (5, "Neuwerk")]:
        wiki.add(i, t)
    wiki.categories["Category:Lighthouses"] = {"pages": [1, 2], "subcats": ["Category:Sea lighthouses"]}
    wiki.categories["Category:Sea lighthouses"] = {"pages": [3], "subcats": ["Category:Lighthouses"]}  # a cycle


def test_category_members_follow_continuation(wiki_server):
    url, wiki = wiki_server
    lighthouse_wiki(wiki)
    wiki.page_size = 1
    assert client(url).pages_in_categories(("Category:Lighthouses",), 0, 100) == {1: "Heligoland", 2: "Cape Arkona"}


def test_depth_follows_subcategories_and_survives_cycles(wiki_server):
    url, wiki = wiki_server
    lighthouse_wiki(wiki)
    found = client(url).pages_in_categories(("Category:Lighthouses",), 5, 100)  # the cycle must not loop
    assert found == {1: "Heligoland", 2: "Cape Arkona", 3: "Roter Sand"}


def test_a_bare_category_name_gets_the_category_prefix(wiki_server):
    url, wiki = wiki_server
    lighthouse_wiki(wiki)
    assert set(client(url).pages_in_categories(("Lighthouses",), 0, 100)) == {1, 2}


def test_a_prefixed_category_name_is_used_as_given(wiki_server):  # de: "Kategorie:..." must not become "Category:Kategorie:..."
    url, wiki = wiki_server
    wiki.add(11, "Roter Sand")
    wiki.categories["Kategorie:Leuchtturm in Deutschland"] = {"pages": [11], "subcats": []}
    assert client(url).pages_in_categories(("Kategorie:Leuchtturm in Deutschland",), 0, 10) == {11: "Roter Sand"}


def test_too_many_pages_refuses_instead_of_truncating(wiki_server):
    url, wiki = wiki_server
    lighthouse_wiki(wiki)
    with pytest.raises(WikiError, match="MAX_PAGES"):
        client(url).pages_in_categories(("Category:Lighthouses",), 5, 2)


def test_resolve_titles_follows_redirects_and_drops_missing(wiki_server):
    url, wiki = wiki_server
    lighthouse_wiki(wiki)
    wiki.redirects["Helgoland"] = "Heligoland"
    assert client(url).resolve_titles(("Helgoland", "Cape Arkona", "No such page")) == {1: "Heligoland", 2: "Cape Arkona"}


def test_geo_pages(wiki_server):
    url, wiki = wiki_server
    lighthouse_wiki(wiki)
    wiki.geo = [4, 5]
    assert client(url).geo_pages(53.55, 9.99, 5000) == {4: "Lindau", 5: "Neuwerk"}
    assert wiki.requests[-1]["query"]["gscoord"] == "53.55|9.99"


def test_revisions_are_requested_in_batches(wiki_server, monkeypatch):
    url, wiki = wiki_server
    lighthouse_wiki(wiki)
    monkeypatch.setattr(mediawiki, "BATCH", 2)
    revs = client(url).revisions([1, 2, 3, 4, 5])
    assert revs[3] == ("100", "2026-10-01T00:00:00Z") and len(revs) == 5
    assert sum("rvprop" in r["query"] for r in wiki.requests) == 3


def test_article_returns_text_and_revision_or_none_when_gone(wiki_server):
    url, wiki = wiki_server
    wiki.add(7, "Seven", "Lead text.\n\n== History ==\nOld.", revid=555, ts="2026-10-02T00:00:00Z")
    assert client(url).article(7) == ("Seven", "Lead text.\n\n== History ==\nOld.", "555", "2026-10-02T00:00:00Z")
    assert client(url).article(8) is None


def test_every_request_identifies_itself_and_sets_maxlag(wiki_server):
    url, wiki = wiki_server
    lighthouse_wiki(wiki)
    client(url).resolve_titles(("Cape Arkona",))
    assert wiki.requests[0]["ua"] == "test-agent/1.0" and wiki.requests[0]["query"]["maxlag"] == "5"


def test_maxlag_is_retried_with_backoff(wiki_server):
    url, wiki = wiki_server
    lighthouse_wiki(wiki)
    wiki.lag_errors = 2
    sleeps = []
    assert client(url, sleeps).resolve_titles(("Cape Arkona",)) == {2: "Cape Arkona"}
    assert sleeps == [1, 2]


def test_429_and_503_are_retried_and_persistent_trouble_finally_fails(wiki_server):
    url, wiki = wiki_server
    lighthouse_wiki(wiki)
    wiki.status_errors = [429, 503]
    assert client(url).resolve_titles(("Cape Arkona",)) == {2: "Cape Arkona"}
    wiki.lag_errors = 99
    sleeps = []
    with pytest.raises(WikiError, match="900 s"):
        client(url, sleeps).resolve_titles(("Cape Arkona",))
    assert sum(sleeps) == 900 and len(wiki.requests) < 30  # it gave up after its budget; it did not hammer


def test_a_429_longer_than_a_minute_is_waited_out(wiki_server):
    url, wiki = wiki_server
    lighthouse_wiki(wiki)
    wiki.status_errors = [429] * 8
    sleeps = []
    assert client(url, sleeps).resolve_titles(("Cape Arkona",)) == {2: "Cape Arkona"}
    assert sum(sleeps) > 120


def test_a_retry_after_beyond_30_seconds_is_honored(wiki_server):
    url, wiki = wiki_server
    lighthouse_wiki(wiki)
    wiki.status_errors, wiki.retry_after = [429], "200"
    sleeps = []
    assert client(url, sleeps).resolve_titles(("Cape Arkona",)) == {2: "Cape Arkona"}
    assert sleeps == [200]


def test_a_long_wait_is_said_in_the_log_as_it_starts(wiki_server, capsys):
    url, wiki = wiki_server
    lighthouse_wiki(wiki)
    wiki.status_errors = [429] * 5  # waits 1, 2, 4, 8, then 16
    assert client(url, []).resolve_titles(("Cape Arkona",)) == {2: "Cape Arkona"}
    assert capsys.readouterr().err.splitlines() == [
        "wikipedia connector: HTTP 429 from the wiki: waiting 16 s (15 s of 900 s waited)"]


def test_a_429_that_never_ends_fails_and_says_how_long_it_waited(wiki_server):
    url, wiki = wiki_server
    lighthouse_wiki(wiki)
    wiki.status_errors = [429] * 1000
    sleeps = []
    with pytest.raises(WikiError, match="HTTP 429") as e:
        client(url, sleeps).resolve_titles(("Cape Arkona",))
    assert sum(sleeps) == 900 and "900 s" in str(e.value)


def test_api_errors_become_wiki_errors(wiki_server):
    url, _ = wiki_server
    with pytest.raises(WikiError, match="badrequest"):
        client(url)._get(action="query", bogus="1")


def test_max_pages_is_enforced_while_listing_not_after_the_whole_category(wiki_server):
    url, wiki = wiki_server
    for i in range(1, 2001):
        wiki.add(i, f"Page {i}")
    wiki.categories["Category:Huge"] = {"pages": list(range(1, 2001)), "subcats": []}
    wiki.page_size = 50
    with pytest.raises(WikiError, match="MAX_PAGES"):
        client(url).pages_in_categories(("Category:Huge",), 0, 100)
    assert len(wiki.requests) <= 3  # it refused after the batch that crossed the limit, not after 40 batches


def test_502_and_504_are_retried_and_retry_after_is_honored(wiki_server):
    url, wiki = wiki_server
    lighthouse_wiki(wiki)
    wiki.status_errors = [502, 504]
    wiki.retry_after = "7"
    sleeps = []
    assert client(url, sleeps).resolve_titles(("Cape Arkona",)) == {2: "Cape Arkona"}
    assert sleeps == [7.0, 7.0]


def test_an_unreachable_wiki_is_retried_then_reported_without_a_pointless_last_sleep():
    sleeps = []
    with pytest.raises(WikiError, match="could not be reached|try again later"):
        client("http://127.0.0.1:9/w/api.php", sleeps).resolve_titles(("Cape Arkona",))
    assert sum(sleeps) == 900  # it waits out its budget, then gives up without a pointless last sleep


def test_a_continuation_that_repeats_a_request_key_does_not_crash(wiki_server):
    url, _ = wiki_server
    calls = []

    def fake_get(**params):
        calls.append(params)
        return {"query": {}, **({"continue": {"list": "categorymembers"}} if len(calls) == 1 else {})}

    wiki = client(url)
    wiki._get = fake_get
    assert list(wiki._query(list="categorymembers")) == [{}, {}]
