"""passageway connector for Wikipedia (and any MediaWiki site): a topic, some titles or a place."""

import json
import os
import re
import sys
import time
from collections.abc import Mapping
from dataclasses import dataclass
from typing import TextIO
from urllib.parse import quote

import httpx

from passageway_connector_wikipedia.mediawiki import Wiki, WikiError
from passageway_connector_wikipedia.sections import DEFAULT_SKIP, split_sections

VERSION = "0.1.0"


class ScopeError(Exception):
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


class _Buffer:
    def __init__(self):
        self._parts: list[str] = []

    def emit(self, record: dict) -> None:
        self._parts.append(json.dumps(record) + "\n")

    def getvalue(self) -> str:
        return "".join(self._parts)


def run(argv: list[str], env: Mapping[str, str], stdin: TextIO, stdout: TextIO, stderr: TextIO,
        *, sleep=time.sleep) -> int:
    mode = argv[1] if len(argv) > 1 else ""
    if mode not in ("check", "list", "fetch", "changed"):
        print("usage: python -m passageway_connector_wikipedia check|list|fetch|changed", file=stderr)
        return 2
    try:
        scope = parse_scope(env)
    except ScopeError as e:
        print(f"wikipedia connector: {e}", file=stderr)
        return 2
    wiki = Wiki(scope.api_url, _user_agent(scope), pause=scope.pause, sleep=sleep)
    out = _Buffer()
    try:
        if mode == "check":
            # the same set `list` prints (redirect stubs are not items), so check and list always agree
            out.emit({"ok": True, "count": len(wiki.revisions(list(_pages(wiki, scope))))})
        elif mode == "list":
            pages = _pages(wiki, scope)
            revisions = wiki.revisions(list(pages))
            for page_id in pages:
                if page_id in revisions:
                    out.emit({"id": str(page_id), "version": revisions[page_id][0]})
        elif mode == "fetch":
            for line in stdin:
                if not line.strip():
                    continue
                page_id = str(json.loads(line)["id"])
                article = wiki.article(int(page_id)) if page_id.isdigit() else None
                if article is None:  # deleted since list, or not one of our ids: skip; the next reconcile settles it
                    continue
                title, extract, revid, timestamp = article
                out.emit({
                    "id": page_id, "title": title, "version": revid, "updated": timestamp,
                    "url": scope.page_url + quote(title.replace(" ", "_"), safe="()_,:;@$&+=!*'~-./"),
                    "sections": split_sections(extract, scope.skip)})
        # changed: nothing to print; edits appear at the next reconcile
    except (WikiError, httpx.HTTPError, ValueError, KeyError) as e:
        print(f"wikipedia connector: {e}", file=stderr)
        return 1
    stdout.write(out.getvalue())  # all or nothing: a failure above leaves stdout empty
    return 0


def main() -> None:
    sys.exit(run(sys.argv, os.environ, sys.stdin, sys.stdout, sys.stderr))
