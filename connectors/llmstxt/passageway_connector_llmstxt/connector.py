"""passageway connector for the llms-full.txt (and llms.txt) of a list of websites."""

import hashlib
import re
import time
from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass
from urllib.parse import urldefrag, urljoin, urlparse

import httpx
from passageway_sdk import Connector, SettingsError, SourceError, split_markdown
from passageway_sdk.settings import weight_of, weights, whole
from passageway_sdk.web import TooLarge, Web

FRONT_MATTER = re.compile(r"\A---[ \t]*\r?\n.*?\r?\n(?:---|\.\.\.)[ \t]*(?:\r?\n|\Z)", re.S)
LINK = re.compile(r"\]\(\s*<?([^)\s>]+)")
FENCE = re.compile(r"^\s*(```|~~~)")
PAGE_URL = re.compile(r"url:[ \t]*(\S+)[ \t]*$")
BLOCK_LINES = 20  # a front matter block longer than this is not one


def _slug(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.casefold()).strip("-") or "page"


@dataclass(frozen=True)
class Page:
    id: str
    title: str
    file: str
    text: str
    url: str = ""  # the address a hit opens; the file's own when the page has none of its own
    path: tuple[str, ...] = ()


def split_pages(file: str, text: str) -> list[Page]:
    """Pages of a file: at every front matter block with a `url:` key (the layout of the VitePress llms plugin), else at every
    top-level heading. A block or a `#` inside a code fence does not count; text before the first block is split by heading."""
    lines = text.splitlines()
    starts = _page_blocks(lines)
    if not starts:
        return _by_headings(file, FRONT_MATTER.sub("", text, count=1))
    pages = _by_headings(file, "\n".join(lines[:starts[0][0]]))
    used = {p.id for p in pages}
    for n, (start, end, url) in enumerate(starts):
        stop = starts[n + 1][0] if n + 1 < len(starts) else len(lines)
        body = "\n".join(lines[end:stop]).strip()
        if body:
            pages.append(_page_of_url(file, url, body, used))
    return pages


def _page_blocks(lines: list[str]) -> list[tuple[int, int, str]]:
    """(first line, line after the last, url) of every front matter block with a `url:` key, outside code fences."""
    blocks, fenced, i = [], False, 0
    while i < len(lines):
        if FENCE.match(lines[i]):
            fenced = not fenced
        elif not fenced and lines[i].strip() == "---":
            close = next((j for j in range(i + 1, min(i + BLOCK_LINES, len(lines))) if lines[j].strip() == "---"), None)
            found = close and next((m.group(1) for m in map(PAGE_URL.match, (l.strip() for l in lines[i + 1:close])) if m), None)
            if found:
                blocks.append((i, close + 1, found))
                i = close
        i += 1
    return blocks


def _page_of_url(file: str, url: str, body: str, used: set[str]) -> Page:
    path = urlparse(urljoin(file, url)).path
    target = urljoin(file, url[:-3] if url.endswith(".md") else url)  # the HTML page, not the raw markdown
    heading = next((l[2:].strip() for l in body.splitlines() if l.startswith("# ") and l[2:].strip()), "")
    title = heading or (path.rstrip("/").rsplit("/", 1)[-1].removesuffix(".md") or urlparse(file).netloc)
    page_id, n = f"{file}#{url}", 1
    while page_id in used:
        n += 1
        page_id = f"{file}#{url}-{n}"
    used.add(page_id)
    folders = tuple(p for p in path.split("/")[1:-1] if p)
    return Page(page_id, title, file, body, target, (urlparse(file).netloc, *folders))


def _by_headings(file: str, text: str) -> list[Page]:
    """One page per top-level heading; text before the first goes to a page of its own."""
    host = urlparse(file).netloc
    chunks: list[tuple[str, list[str]]] = [(host, [])]
    fenced = False
    for line in text.splitlines():
        if FENCE.match(line):
            fenced = not fenced
        if not fenced and line.startswith("# "):
            chunks.append((line[2:].strip() or host, [line]))
        else:
            chunks[-1][1].append(line)
    pages, used = [], set()
    for title, lines in chunks:
        body = "\n".join(lines).strip()
        if not body:
            continue
        slug, n = _slug(title), 1
        while slug in used:
            n += 1
            slug = f"{_slug(title)}-{n}"
        used.add(slug)
        pages.append(Page(f"{file}#{slug}", title, file, body, file, (host,)))
    return pages


class LlmsTxt(Connector):
    name = "llmstxt connector"

    def __init__(self, env: Mapping[str, str], *, transport: httpx.BaseTransport | None = None,
                 sleep: Callable[[float], None] = time.sleep):
        self.urls = [u.strip() for u in env.get("URLS", "").split("|") if u.strip()]
        if not self.urls:
            raise SettingsError("URLS must name at least one site or file")
        for url in self.urls:
            if urlparse(url).scheme not in ("http", "https") or not urlparse(url).netloc:
                raise SettingsError(f"URLS must be http(s) addresses, got {url!r}")
        self.max_bytes = whole(env, "MAX_BYTES", 20_000_000)
        self.max_pages = whole(env, "MAX_PAGES", 500)
        self.weights = weights(env, "WEIGHTS")
        self._web = Web("passageway-connector-llmstxt", max_bytes=self.max_bytes, transport=transport, sleep=sleep)

    # -- the protocol ------------------------------------------------------------------------

    def versions(self) -> dict[str, str]:
        return {p.id: self._version(p) for p in self._pages()}

    def fetch(self, ids: list[str]) -> Iterator[dict]:
        wanted = set(ids)
        for file in dict.fromkeys(i.split("#")[0] for i in ids if urlparse(i).scheme in ("http", "https")):  # an id that is no address names nothing
            for page in split_pages(file, self._get(file)):
                if page.id in wanted:
                    yield self._item(page)

    # -- the sites ---------------------------------------------------------------------------

    def _files(self) -> list[str]:
        files: list[str] = []
        for url in self.urls:
            parsed = urlparse(url)
            if parsed.path in ("", "/"):
                files.append(f"{parsed.scheme}://{parsed.netloc}/llms-full.txt")
            elif parsed.path.rsplit("/", 1)[-1] == "llms.txt":
                files.extend(self._linked(url))
            else:
                files.append(urldefrag(url)[0])
        return list(dict.fromkeys(files))

    def _linked(self, index: str) -> list[str]:
        host, links = urlparse(index).netloc, []
        for target in LINK.findall(self._get(index)):
            link = urldefrag(urljoin(index, target))[0]
            if urlparse(link).scheme in ("http", "https") and urlparse(link).netloc == host and link != index:
                links.append(link)
        links = list(dict.fromkeys(links))
        if len(links) > self.max_pages:
            self.warn(f"{index} links to {len(links)} pages; only the first {self.max_pages} are indexed (MAX_PAGES)")
        return links[:self.max_pages]

    def _pages(self) -> list[Page]:
        return [page for file in self._files() for page in split_pages(file, self._get(file))]

    def _get(self, url: str) -> str:
        try:
            return self._web.get(url, required=True).text
        except TooLarge:
            raise SourceError(f"{url}: larger than MAX_BYTES ({self.max_bytes})") from None

    def _weight(self, page: Page) -> float:
        return weight_of(self.weights, urlparse(page.url).path)

    def _version(self, page: Page) -> str:
        weight = self._weight(page)  # a changed weight is a changed item, so the index follows it
        return hashlib.sha256((page.text if weight == 1.0 else f"{page.text}\0{weight}").encode()).hexdigest()[:16]

    def _item(self, page: Page) -> dict:
        item = {
            "id": page.id,
            "title": page.title,
            "url": page.url,
            "version": self._version(page),
            "sections": split_markdown(page.text, skip_first_h1=True),
            "path": list(page.path),
        }
        if self._weight(page) != 1.0:
            item["weight"] = self._weight(page)
        return item


def main() -> None:
    LlmsTxt.main()
