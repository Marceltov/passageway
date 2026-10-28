"""passageway connector for Wikipedia (and any MediaWiki site): a topic, some titles or a place."""

import re
import time
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from typing import TextIO
from urllib.parse import quote

import httpx
from passageway_sdk import Connector, SettingsError

from passageway_connector_wikipedia.mediawiki import Wiki, WikiError
from passageway_connector_wikipedia.sections import DEFAULT_SKIP, split_sections

VERSION = "0.1.0"


class ScopeError(SettingsError):
    pass


@dataclass(frozen=True)
class Scope:
    api_url: str
    page_url: str
    categories: tuple[str, ...]
    depth: int
    titles: tuple[str, ...]
    geo: tuple[float, float, int] | None
    max_pages: int
    skip: frozenset[str]
    contact: str
    pause: float


def _list(env: Mapping[str, str], key: str) -> tuple[str, ...]:
    return tuple(p.strip() for p in env.get(key, "").split("|") if p.strip())


def _int(env: Mapping[str, str], key: str, default: int, low: int) -> int:
    raw = env.get(key, "").strip()
    try:
        value = int(raw) if raw else default
    except ValueError:
        raise ScopeError(f"{key} must be a whole number, got {raw!r}") from None
    if value < low:
        raise ScopeError(f"{key} must be at least {low}, got {value}")
    return value


def parse_scope(env: Mapping[str, str]) -> Scope:
    language = env.get("LANGUAGE", "").strip() or "en"
    if not re.fullmatch(r"[a-z][a-z-]*", language):
        raise ScopeError(f"LANGUAGE must be a wiki language code such as en or de, got {language!r}")
    categories, titles = _list(env, "CATEGORIES"), _list(env, "TITLES")
    geo = None
    if env.get("GEO", "").strip():
        try:
            lat, lon, radius = (x.strip() for x in env["GEO"].split(","))
            geo = (float(lat), float(lon), int(radius))
        except ValueError:
            raise ScopeError("GEO must look like 'lat,lon,radius_in_meters', e.g. 48.1372,11.5756,5000") from None
        if not 10 <= geo[2] <= 10000:
            raise ScopeError("GEO radius must be between 10 and 10000 meters (a MediaWiki limit); "
                             "use CATEGORIES for a larger region")
    if not (categories or titles or geo):
        raise ScopeError("set at least one of CATEGORIES, TITLES or GEO")
    skip_raw = env.get("SKIP_SECTIONS", "").strip()
    skip = DEFAULT_SKIP if not skip_raw else frozenset() if skip_raw == "none" else \
        frozenset(s.casefold() for s in _list(env, "SKIP_SECTIONS"))
    try:
        pause = float(env.get("PAUSE_SECONDS", "0.1"))
    except ValueError:
        raise ScopeError("PAUSE_SECONDS must be a number") from None
    if pause < 0:
        raise ScopeError("PAUSE_SECONDS must not be negative")
    return Scope(
        api_url=env.get("API_URL", "").strip() or f"https://{language}.wikipedia.org/w/api.php",
        page_url=env.get("PAGE_URL", "").strip() or f"https://{language}.wikipedia.org/wiki/",
        categories=categories, depth=_int(env, "CATEGORY_DEPTH", 1, 0), titles=titles, geo=geo,
        max_pages=_int(env, "MAX_PAGES", 500, 1), skip=skip, contact=env.get("CONTACT", "").strip(), pause=pause)


def _user_agent(scope: Scope) -> str:
    contact = f"; {scope.contact}" if scope.contact else ""
    return f"passageway-connector-wikipedia/{VERSION} (+https://github.com/Marceltov/passageway{contact})"


def _pages(wiki: Wiki, scope: Scope) -> dict[int, str]:
    found: dict[int, str] = {}
    if scope.categories:
        found.update(wiki.pages_in_categories(scope.categories, scope.depth, scope.max_pages))
    if scope.titles:
        found.update(wiki.resolve_titles(scope.titles))
    if scope.geo:
        found.update(wiki.geo_pages(*scope.geo))
    if len(found) > scope.max_pages:
        raise WikiError(f"the scope has more than {scope.max_pages} pages: narrow it or raise MAX_PAGES")
    return found


def article_url(scope: Scope, title: str) -> str:
    return scope.page_url + quote(title.replace(" ", "_"), safe="()_,:;@$&+=!*'~-./")


class Wikipedia(Connector):
    name = "wikipedia connector"
    expected_errors = (WikiError, httpx.HTTPError, ValueError, KeyError)

    def __init__(self, env: Mapping[str, str], *, sleep=time.sleep):
        self.scope = parse_scope(env)
        self.wiki = Wiki(self.scope.api_url, _user_agent(self.scope), pause=self.scope.pause, sleep=sleep)

    def versions(self) -> dict[str, str]:
        pages = _pages(self.wiki, self.scope)
        revisions = self.wiki.revisions(list(pages))
        return {str(page_id): revisions[page_id][0] for page_id in pages if page_id in revisions}

    def fetch(self, ids: list[str]) -> Iterator[dict]:
        for page_id in ids:
            article = self.wiki.article(int(page_id)) if page_id.isdigit() else None
            if article is None:  # deleted since list, or not one of our ids: skip; the next reconcile settles it
                continue
            title, extract, revid, timestamp = article
            yield {
                "id": page_id, "title": title, "version": revid, "updated": timestamp,
                "url": article_url(self.scope, title),
                "sections": split_sections(extract, self.scope.skip)}
    # changed: not implemented; edits appear at the next reconcile


def run(argv: list[str], env: Mapping[str, str], stdin: TextIO, stdout: TextIO, stderr: TextIO,
        *, sleep=time.sleep) -> int:
    return Wikipedia.run(argv, env, stdin, stdout, stderr, sleep=sleep)


def main() -> None:
    Wikipedia.main()
