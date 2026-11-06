"""passageway connector for websites built with MkDocs: one item per section of the site's search index."""

import hashlib
import json
import time
from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass
from urllib.parse import urldefrag, urlparse

import httpx
from passageway_sdk import Connector, SettingsError, SourceError
from passageway_sdk.html import clean, to_markdown
from passageway_sdk.settings import names, weight_of, weights, whole
from passageway_sdk.web import TooLarge, Web

INDEX = "search/search_index.json"


@dataclass(frozen=True)
class Section:
    id: str  # the address: the site, the page, and the heading's anchor if it has one
    page_title: str
    heading: str | None  # None for the text before the page's first heading
    text: str
    where: str  # the page's location below the site, for WEIGHTS and the breadcrumb


def _base(url: str) -> str:
    """The site an address names: the folder of a search index, else the address itself, ending in `/`."""
    url = urldefrag(url)[0]
    if url.endswith(INDEX):
        return url.removesuffix(INDEX)
    return url if url.endswith("/") else url + "/"


def _intro(page_text: str, first: str | None) -> str:
    """The page entry of MkDocs' own search plugin holds the whole page; keep what comes before its first section."""
    if first:
        at = page_text.find(first)
        if at > 0:
            return page_text[:at]
    return page_text


def sections(base: str, docs: list[dict]) -> list[Section]:
    """The sections of a search index, in its order; entries without text are left out, a repeated address counts once."""
    pages: dict[str, str] = {}  # page location -> page title
    firsts: dict[str, tuple[str, str]] = {}  # page location -> (title, text) of its first section with text
    texts = {d["location"]: to_markdown(d["text"]) for d in docs}
    for d in docs:
        page, _, anchor = d["location"].partition("#")
        if not anchor:
            pages.setdefault(page, clean(d["title"]))
        elif texts[d["location"]]:
            firsts.setdefault(page, (clean(d["title"]), texts[d["location"]]))
    out, seen = [], set()
    for d in docs:
        location = d["location"]
        if location in seen:
            continue
        seen.add(location)
        page, _, anchor = location.partition("#")
        text = texts[location]
        if not anchor:
            # the first section of this page, with its heading, starts where the intro ends
            first_title, first = firsts.get(page, (None, None))
            text = _intro(text, first)
            if first_title and text.rstrip().endswith(first_title):
                text = text.rstrip()[: -len(first_title)]
            text = text.strip()
        if text:
            title = pages.get(page) or clean(d["title"]) or urlparse(base).netloc
            out.append(Section(base + location, title, clean(d["title"]) if anchor else None, text, page))
    return out


class MkDocs(Connector):
    name = "mkdocs connector"

    def __init__(self, env: Mapping[str, str], *, transport: httpx.BaseTransport | None = None,
                 sleep: Callable[[float], None] = time.sleep):
        urls = names(env, "URLS")
        if not urls:
            raise SettingsError("URLS must name at least one site")
        for url in urls:
            if urlparse(url).scheme not in ("http", "https") or not urlparse(url).netloc:
                raise SettingsError(f"URLS must be http(s) addresses, got {url!r}")
        self.sites = list(dict.fromkeys(_base(u) for u in urls))
        self.max_bytes = whole(env, "MAX_BYTES", 50_000_000)
        self.weights = weights(env, "WEIGHTS")
        self._web = Web("passageway-connector-mkdocs", max_bytes=self.max_bytes, transport=transport, sleep=sleep)

    # -- the protocol ------------------------------------------------------------------------

    def versions(self) -> dict[str, str]:
        return {s.id: self._version(s) for site in self.sites for s in self._sections(site)}

    def fetch(self, ids: list[str]) -> Iterator[dict]:
        wanted = set(ids)
        for site in self.sites:
            if any(i.startswith(site) for i in wanted):
                for section in self._sections(site):
                    if section.id in wanted:
                        yield self._item(section)

    # -- the sites ---------------------------------------------------------------------------

    def _sections(self, site: str) -> list[Section]:
        url = site + INDEX
        try:
            text = self._web.get(url, required=True).text
        except TooLarge:
            raise SourceError(f"{url}: larger than MAX_BYTES ({self.max_bytes})") from None
        try:
            docs = json.loads(text)["docs"]
            docs = [{"location": str(d["location"]), "title": str(d.get("title") or ""), "text": str(d.get("text") or "")}
                    for d in docs]
        except (ValueError, KeyError, TypeError):
            raise SourceError(f"{url}: not an MkDocs search index") from None
        return sections(site, docs)

    def _weight(self, section: Section) -> float:
        return weight_of(self.weights, section.where)

    def _version(self, section: Section) -> str:
        weight = self._weight(section)  # a changed weight is a changed item, so the index follows it
        body = f"{section.page_title}\0{section.heading}\0{section.text}" + (f"\0{weight}" if weight != 1.0 else "")
        return hashlib.sha256(body.encode()).hexdigest()[:16]

    def _item(self, section: Section) -> dict:
        item = {
            "id": section.id,
            "title": section.page_title,
            "url": section.id,
            "version": self._version(section),
            "sections": [{"heading": section.heading, "text": section.text}],
        }
        if folders := [p for p in section.where.split("/") if p]:
            item["path"] = folders
        if (weight := self._weight(section)) != 1.0:
            item["weight"] = weight
        return item


def main() -> None:
    MkDocs.main()
