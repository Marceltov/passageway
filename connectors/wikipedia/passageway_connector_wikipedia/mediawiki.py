"""A minimal, polite, read-only client for the MediaWiki Action API: only what the connector needs."""

import time
from collections.abc import Iterator

import httpx

BATCH = 50  # page ids per request (the API limit for anonymous clients)
MAX_ATTEMPTS = 5
RETRY_STATUS = (429, 502, 503, 504)  # the wiki or its edge asking us to come back later


class WikiError(Exception):
    pass


def _batches(items: list, size: int) -> Iterator[list]:
    for i in range(0, len(items), size):
        yield items[i:i + size]


def _retry_after(response: httpx.Response, default: float) -> float:
    try:
        return min(float(response.headers["Retry-After"]), 30.0)
    except (KeyError, ValueError):
        return default


def _category_title(name: str) -> str:
    return name if ":" in name else f"Category:{name}"


class Wiki:
    def __init__(self, api_url: str, user_agent: str, *, pause: float = 0.1, sleep=time.sleep, timeout: float = 30.0):
        self._http = httpx.Client(headers={"User-Agent": user_agent}, timeout=timeout)
        self._url, self._pause, self._sleep = api_url, pause, sleep

    # -- requests ----------------------------------------------------------------------------

    def _get(self, **params) -> dict:
        params = {"format": "json", "formatversion": "2", "maxlag": "5", **params}
        for attempt in range(MAX_ATTEMPTS):
            wait = min(2 ** attempt, 30)
            try:
                response = self._http.get(self._url, params=params)
            except httpx.TransportError:  # timeout, refused or dropped connection: worth another try
                response = None
            if response is not None:
                if response.status_code in RETRY_STATUS:
                    wait = _retry_after(response, wait)
                else:
                    response.raise_for_status()
                    data = response.json()
                    error = data.get("error")
                    if error is None:
                        if self._pause:
                            self._sleep(self._pause)
                        return data
                    if error.get("code") != "maxlag":
                        raise WikiError(f"{error.get('code')}: {error.get('info')}")
            if attempt < MAX_ATTEMPTS - 1:
                self._sleep(wait)
        raise WikiError("the wiki kept asking to try again later or could not be reached "
                        "(maxlag, 429, 502-504, timeouts); giving up")

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
