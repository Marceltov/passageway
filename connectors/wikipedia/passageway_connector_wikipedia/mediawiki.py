"""A minimal, polite, read-only client for the MediaWiki Action API: only what the connector needs."""

import json
import sys
import time
from collections.abc import Iterator

from passageway_sdk import SourceError
from passageway_sdk.web import Reply, Retry, Web

BATCH = 50  # page ids per request (the API limit for anonymous clients)
RETRY_BUDGET = 900  # seconds of waiting per request before giving up: a rate limit can last minutes
MAX_BACKOFF = 60  # the longest wait the client picks itself
MAX_RETRY_AFTER = 300  # the longest wait a Retry-After may ask for
SAY_WAITS_FROM = 10  # seconds: a wait this long is said in the log, shorter ones stay quiet
RETRY_STATUS = (429, 502, 503, 504)  # the wiki or its edge asking us to come back later


class WikiError(Exception):
    pass


def _batches(items: list, size: int) -> Iterator[list]:
    for i in range(0, len(items), size):
        yield items[i:i + size]


def _category_title(name: str) -> str:
    return name if ":" in name else f"Category:{name}"


def _lagging(reply: Reply) -> str | None:
    """The API answers 200 with `maxlag` when the wiki's replicas are behind: that is a request to come back later."""
    try:
        error = json.loads(reply.text).get("error")
    except (ValueError, AttributeError):
        return None
    return "maxlag" if isinstance(error, dict) and error.get("code") == "maxlag" else None


class Wiki:
    def __init__(self, api_url: str, user_agent: str, *, pause: float = 0.1, sleep=time.sleep, timeout: float = 30.0):
        retry = Retry(statuses=RETRY_STATUS, network=True, budget=RETRY_BUDGET, max_backoff=MAX_BACKOFF, max_after=MAX_RETRY_AFTER,
                      say_from=SAY_WAITS_FROM)
        # on stderr, which the core logs as it comes: a waiting sync does not look hung
        say = lambda message: print(f"wikipedia connector: {message}", file=sys.stderr, flush=True)  # noqa: E731
        self._web = Web(user_agent, pause=pause, timeout=timeout, max_bytes=256_000_000, retry=retry, log=say, sleep=sleep)
        self._url = api_url

    # -- requests ----------------------------------------------------------------------------

    def _get(self, **params) -> dict:
        params = {"format": "json", "formatversion": "2", "maxlag": "5", **params}
        try:
            reply = self._web.get(self._url, params=params, retry_if=_lagging)
        except SourceError as e:  # the wiki kept asking to try again later, or could not be reached
            raise WikiError(f"the wiki kept asking to try again later or could not be reached; {e}") from e
        if reply.status >= 400:
            raise WikiError(f"{self._url}: HTTP {reply.status}")
        data = reply.json()
        if (error := data.get("error")) is not None:
            raise WikiError(f"{error.get('code')}: {error.get('info')}")
        return data

    def _query(self, **params) -> Iterator[dict]:
        """Every page of an action=query result, following the API's continuation."""
        extra: dict = {}
        while True:
            data = self._get(**{"action": "query", **params, **extra})
            yield data.get("query", {})
            if "continue" not in data:
                return
            extra = data["continue"]

    # -- scopes ------------------------------------------------------------------------------

    def _members(self, category: str, found: dict[int, str], max_pages: int) -> list[str]:
        """Adds the category's pages to `found` and returns its subcategories; refuses as soon as the scope is too big."""
        subcats: list[str] = []
        for q in self._query(list="categorymembers", cmtitle=category, cmlimit="500",
                             cmprop="ids|title|type", cmtype="page|subcat", cmnamespace="0|14"):
            for member in q.get("categorymembers", []):
                if member["type"] == "subcat":
                    subcats.append(member["title"])
                else:
                    found[member["pageid"]] = member["title"]
            if len(found) > max_pages:  # checked per response: a million-page category must not be listed to the end
                raise WikiError(f"the scope has more than {max_pages} pages: narrow it "
                                f"(fewer categories, a lower CATEGORY_DEPTH) or raise MAX_PAGES")
        return subcats

    def pages_in_categories(self, categories: tuple[str, ...], depth: int, max_pages: int) -> dict[int, str]:
        found: dict[int, str] = {}
        seen: set[str] = set()
        frontier = [(_category_title(c), 0) for c in categories]
        while frontier:
            title, level = frontier.pop(0)
            if title in seen:
                continue
            seen.add(title)
            subcats = self._members(title, found, max_pages)
            if level < depth:
                frontier += [(s, level + 1) for s in subcats]
        return found

    def resolve_titles(self, titles: tuple[str, ...]) -> dict[int, str]:
        found: dict[int, str] = {}
        for chunk in _batches(list(titles), BATCH):
            for q in self._query(titles="|".join(chunk), redirects="1"):
                for page in q.get("pages", []):
                    if not (page.get("missing") or page.get("invalid")):
                        found[page["pageid"]] = page["title"]
        return found

    def geo_pages(self, lat: float, lon: float, radius: int) -> dict[int, str]:
        found: dict[int, str] = {}
        for q in self._query(list="geosearch", gscoord=f"{lat}|{lon}", gsradius=str(radius),
                             gslimit="500", gsnamespace="0"):
            for page in q.get("geosearch", []):
                found[page["pageid"]] = page["title"]
        return found

    # -- content -----------------------------------------------------------------------------

    def revisions(self, page_ids: list[int]) -> dict[int, tuple[str, str]]:
        found: dict[int, tuple[str, str]] = {}
        for chunk in _batches(list(page_ids), BATCH):
            for q in self._query(prop="revisions|info", rvprop="ids|timestamp", pageids="|".join(map(str, chunk))):
                for page in q.get("pages", []):
                    if page.get("revisions") and not page.get("redirect"):  # a redirect stub has no text of its own
                        rev = page["revisions"][0]
                        found[page["pageid"]] = (str(rev["revid"]), rev["timestamp"])
        return found

    def article(self, page_id: int) -> tuple[str, str, str, str] | None:
        """(title, plain-text extract with == headings ==, revision id, timestamp); None if the page is gone."""
        for q in self._query(prop="extracts|revisions|info", explaintext="1", exsectionformat="wiki",
                             rvprop="ids|timestamp", pageids=str(page_id)):
            for page in q.get("pages", []):
                if page.get("missing") or page.get("redirect") or not page.get("revisions"):
                    return None
                rev = page["revisions"][0]
                return page["title"], page.get("extract", ""), str(rev["revid"]), rev["timestamp"]
        return None
