"""passageway connector for the llms-full.txt (and llms.txt) of a list of websites."""

import hashlib
import re
import time
from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass
from urllib.parse import urldefrag, urljoin, urlparse

import httpx
from passageway_sdk import Connector, SettingsError, SourceError, split_markdown
from passageway_sdk.settings import whole
from passageway_sdk.web import TooLarge, Web

FRONT_MATTER = re.compile(r"\A---[ \t]*\r?\n.*?\r?\n(?:---|\.\.\.)[ \t]*(?:\r?\n|\Z)", re.S)
LINK = re.compile(r"\]\(\s*<?([^)\s>]+)")
FENCE = re.compile(r"^\s*(```|~~~)")


def _slug(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.casefold()).strip("-") or "page"


@dataclass(frozen=True)
class Page:
    id: str
    title: str
    file: str
    text: str


def split_pages(file: str, text: str) -> list[Page]:
    """One page per top-level heading (a `#` inside a code fence is not one); text before the first goes to a page of its own."""
    text = FRONT_MATTER.sub("", text, count=1)
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
        pages.append(Page(f"{file}#{slug}", title, file, body))
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
        self._web = Web("passageway-connector-llmstxt", max_bytes=self.max_bytes, transport=transport, sleep=sleep)

    # -- the protocol ------------------------------------------------------------------------

    def versions(self) -> dict[str, str]:
        return {p.id: hashlib.sha256(p.text.encode()).hexdigest()[:16] for p in self._pages()}

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

    def _item(self, page: Page) -> dict:
        return {
            "id": page.id,
            "title": page.title,
            "url": page.file,
            "version": hashlib.sha256(page.text.encode()).hexdigest()[:16],
            "sections": split_markdown(page.text, skip_first_h1=True),
            "path": [urlparse(page.file).netloc],
        }


def main() -> None:
    LlmsTxt.main()
