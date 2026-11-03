"""passageway connector for a website: the pages of its sitemap and, optionally, the pages they link to."""

import hashlib
import re
import ssl
import time
from collections import deque
from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass
from html import unescape
from urllib.parse import urldefrag, urljoin, urlparse
from urllib.robotparser import RobotFileParser

import httpx
import truststore
from passageway_sdk import Connector, SettingsError, SourceError, split_markdown
from selectolax.lexbor import LexborHTMLParser as HTMLParser, LexborNode as Node

LOC = re.compile(r"<loc>\s*(.*?)\s*</loc>", re.S)
MAX_PAGE_BYTES = 2_000_000
MAX_SITEMAP_FILES = 50  # a sitemap index nests at most this many files
MAX_LINKS = 30  # related items per page
SKIP_TAGS = {"script", "style", "nav", "header", "footer", "aside", "form", "noscript", "svg", "iframe", "template", "head", "button"}
LEAF_TAGS = {"p", "td", "th", "dt", "dd", "figcaption", "summary", "caption"}


def _list(env: Mapping[str, str], key: str) -> tuple[str, ...]:
    return tuple(p.strip() for p in env.get(key, "").split("|") if p.strip())


def _int(env: Mapping[str, str], key: str, default: int) -> int:
    raw = env.get(key, "").strip()
    try:
        value = int(raw) if raw else default
    except ValueError:
        raise SettingsError(f"{key} must be a whole number, got {raw!r}") from None
    if value < 1:
        raise SettingsError(f"{key} must be at least 1, got {value}")
    return value


def _bool(env: Mapping[str, str], key: str, default: bool) -> bool:
    raw = env.get(key, "").strip().lower()
    if not raw:
        return default
    if raw not in ("true", "false"):
        raise SettingsError(f"{key} must be true or false, got {raw!r}")
    return raw == "true"


def _seconds(env: Mapping[str, str], key: str, default: float) -> float:
    raw = env.get(key, "").strip()
    try:
        value = float(raw) if raw else default
    except ValueError:
        raise SettingsError(f"{key} must be a number of seconds, got {raw!r}") from None
    if value < 0:
        raise SettingsError(f"{key} must not be negative, got {value}")
    return value


def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def _blocks(node: Node, out: list[str]) -> None:
    for child in node.iter(include_text=True):
        tag = child.tag
        if tag == "-text":
            if text := _clean(child.text_content or ""):
                out.append(text)
        elif tag in SKIP_TAGS:
            continue
        elif len(tag) == 2 and tag[0] == "h" and tag[1] in "123456":
            if text := _clean(child.text(deep=True, separator=" ")):
                out.append(f"{'#' * int(tag[1])} {text}")
        elif tag == "pre":
            out.append("```\n" + (child.text(deep=True, strip=False) or "").strip("\n") + "\n```")
        elif tag == "li" and not child.css_first("ul, ol"):
            if text := _clean(child.text(deep=True, separator=" ")):
                out.append(f"- {text}")
        elif tag in LEAF_TAGS:
            if text := _clean(child.text(deep=True, separator=" ")):
                out.append(text)
        else:
            _blocks(child, out)


@dataclass(frozen=True)
class Page:
    url: str
    title: str
    markdown: str
    links: tuple[str, ...]
    has_h1: bool


class Sitemap(Connector):
    name = "sitemap connector"

    def __init__(self, env: Mapping[str, str], *, transport: httpx.BaseTransport | None = None,
                 sleep: Callable[[float], None] = time.sleep):
        self.seeds = _list(env, "SITEMAP")
        if not self.seeds:
            raise SettingsError("SITEMAP must name at least one site or sitemap address")
        for url in self.seeds:
            if urlparse(url).scheme not in ("http", "https") or not urlparse(url).netloc:
                raise SettingsError(f"SITEMAP must hold http(s) addresses, got {url!r}")
        self.hosts = {urlparse(u).netloc for u in self.seeds}
        self.include = _list(env, "INCLUDE")
        self.exclude = _list(env, "EXCLUDE")
        self.follow = _bool(env, "FOLLOW_LINKS", True)
        self.respect_robots = _bool(env, "RESPECT_ROBOTS", True)
        self.max_pages = _int(env, "MAX_PAGES", 500)
        self.pause = _seconds(env, "PAUSE", 0.2)
        contact = env.get("CONTACT", "").strip()
        agent = "passageway-connector-sitemap" + (f" ({contact})" if contact else "")
        self._http = httpx.Client(headers={"User-Agent": agent}, timeout=30.0, follow_redirects=True, transport=transport,
                                  verify=truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT))
        self._sleep, self._robots, self._last = sleep, {}, 0.0

    # -- the protocol ------------------------------------------------------------------------

    def versions(self) -> dict[str, str]:
        return {p.url: hashlib.sha256(p.markdown.encode()).hexdigest()[:16] for p in self._crawl()}

    def fetch(self, ids: list[str]) -> Iterator[dict]:
        for url in dict.fromkeys(i for i in ids if urlparse(i).scheme in ("http", "https")):
            if (page := self._page(url)) is not None:
                yield self._item(page)

    # -- the site ----------------------------------------------------------------------------

    def _wanted(self, url: str) -> bool:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or parsed.netloc not in self.hosts:
            return False
        if self.include and not any(url.startswith(p) for p in self.include):
            return False
        return not any(url.startswith(p) for p in self.exclude)

    def _crawl(self) -> list[Page]:
        queue, seen, pages, skipped = deque(self._sitemap_urls()), set(), [], 0
        seen.update(queue)
        while queue:
            url = queue.popleft()
            if len(pages) >= self.max_pages:
                self.warn(f"stopped at {self.max_pages} pages (MAX_PAGES); the rest of the site is not indexed")
                break
            page = self._page(url)
            if page is None:
                skipped += 1
                continue
            pages.append(page)
            if self.follow:
                for link in page.links:
                    if link not in seen:
                        seen.add(link)
                        queue.append(link)
        return pages

    def _sitemap_urls(self) -> list[str]:
        urls, files, todo = [], 0, deque(f"{s.rstrip('/')}/sitemap.xml" if urlparse(s).path in ("", "/") else s for s in self.seeds)
        done = set(todo)
        while todo:
            files += 1
            if files > MAX_SITEMAP_FILES:
                self.warn(f"more than {MAX_SITEMAP_FILES} sitemap files; the rest are skipped")
                break
            xml = self._get(todo.popleft(), required=True)[1]
            locs = [unescape(loc) for loc in LOC.findall(xml)]
            if "<sitemapindex" in xml:
                for loc in locs:
                    if loc not in done:
                        done.add(loc)
                        todo.append(loc)
            else:
                urls.extend(urldefrag(loc)[0] for loc in locs)
        return [u for u in dict.fromkeys(urls) if self._wanted(u)]

    def _allowed(self, url: str) -> bool:
        if not self.respect_robots:
            return True
        parsed = urlparse(url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        if origin not in self._robots:
            robots = RobotFileParser()
            got = self._get(f"{origin}/robots.txt", required=False)
            robots.parse(got[1].splitlines() if got and got[0] == 200 else [])
            self._robots[origin] = robots
        return self._robots[origin].can_fetch("passageway-connector-sitemap", url)

    def _get(self, url: str, *, required: bool) -> tuple[int, str, str] | None:
        """(status, body, content type); a failure to reach the site, or a 5xx or 429, fails the whole call."""
        wait = self.pause - (time.monotonic() - self._last)
        if wait > 0:
            self._sleep(wait)
        try:
            with self._http.stream("GET", url) as response:
                body = bytearray()
                for chunk in response.iter_bytes():
                    body += chunk
                    if len(body) > MAX_PAGE_BYTES:
                        self.warn(f"skipped {url}: larger than {MAX_PAGE_BYTES} bytes")
                        return None
                status, kind = response.status_code, response.headers.get("content-type", "")
        except httpx.HTTPError as e:
            raise SourceError(f"{url}: {e}") from e
        finally:
            self._last = time.monotonic()
        if status >= 500 or status == 429:
            raise SourceError(f"{url}: HTTP {status}")
        if required and status != 200:
            raise SourceError(f"{url}: HTTP {status}")
        return status, body.decode("utf-8", errors="replace"), kind

    def _page(self, url: str) -> Page | None:
        if not self._allowed(url):
            return None
        got = self._get(url, required=False)
        if got is None:
            return None
        status, body, kind = got
        if status != 200:
            self.warn(f"skipped {url}: HTTP {status}")
            return None
        if "html" not in kind.lower():
            return None
        tree = HTMLParser(body)
        root = tree.css_first("main") or tree.css_first("article") or tree.css_first("[role=main]") or tree.body
        out: list[str] = []
        if root is not None:
            _blocks(root, out)
        title_node = tree.css_first("title")
        title = _clean(title_node.text()) if title_node else ""
        markdown = "\n\n".join(out).strip()
        h1 = re.match(r"# (.+)", markdown)
        links = []
        for a in tree.css("a[href]"):
            link = urldefrag(urljoin(url, a.attributes.get("href") or ""))[0]
            if link != url and link not in links and self._wanted(link):
                links.append(link)
        return Page(url, (h1.group(1).strip() if h1 else title) or url, markdown, tuple(links), bool(h1))

    def _item(self, page: Page) -> dict:
        folders = [p for p in urlparse(page.url).path.split("/")[1:-1] if p]
        item = {
            "id": page.url,
            "title": page.title,
            "url": page.url,
            "version": hashlib.sha256(page.markdown.encode()).hexdigest()[:16],
            "sections": split_markdown(page.markdown, skip_first_h1=page.has_h1),
        }
        if folders:
            item["path"] = folders
        if page.links:
            item["links"] = list(page.links[:MAX_LINKS])
        return item


def main() -> None:
    Sitemap.main()
