"""passageway connector for a website: the pages of its sitemap and, optionally, the pages they link to."""

import hashlib
import re
import time
from collections import deque
from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass
from html import unescape
from urllib.parse import urldefrag, urljoin, urlparse
from urllib.robotparser import RobotFileParser

import httpx
from passageway_sdk import Connector, SettingsError, split_markdown
from passageway_sdk.settings import flag, names, seconds, whole
from passageway_sdk.web import TooLarge, Web
from selectolax.lexbor import LexborHTMLParser as HTMLParser, LexborNode as Node

LOC = re.compile(r"<loc>\s*(.*?)\s*</loc>", re.S)
MAX_PAGE_BYTES = 2_000_000
MAX_SITEMAP_FILES = 50  # a sitemap index nests at most this many files
MAX_LINKS = 30  # related items per page
SKIP_TAGS = {"script", "style", "nav", "header", "footer", "aside", "form", "noscript", "svg", "iframe", "template", "head", "button"}
LEAF_TAGS = {"p", "td", "th", "dt", "dd", "figcaption", "summary", "caption"}


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
        self.seeds = names(env, "SITEMAP")
        if not self.seeds:
            raise SettingsError("SITEMAP must name at least one site or sitemap address")
        for url in self.seeds:
            if urlparse(url).scheme not in ("http", "https") or not urlparse(url).netloc:
                raise SettingsError(f"SITEMAP must hold http(s) addresses, got {url!r}")
        self.hosts = {urlparse(u).netloc for u in self.seeds}
        self.include = names(env, "INCLUDE")
        self.exclude = names(env, "EXCLUDE")
        self.follow = flag(env, "FOLLOW_LINKS", True)
        self.respect_robots = flag(env, "RESPECT_ROBOTS", True)
        self.max_pages = whole(env, "MAX_PAGES", 500)
        self.pause = seconds(env, "PAUSE", 0.2)
        contact = env.get("CONTACT", "").strip()
        agent = "passageway-connector-sitemap" + (f" ({contact})" if contact else "")
        self._web = Web(agent, pause=self.pause, max_bytes=MAX_PAGE_BYTES, transport=transport, sleep=sleep)
        self._robots = {}

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
            xml = self._web.get(todo.popleft(), required=True).text
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
            got = self._web.get(f"{origin}/robots.txt")
            robots.parse(got.text.splitlines() if got.status == 200 else [])
            self._robots[origin] = robots
        return self._robots[origin].can_fetch("passageway-connector-sitemap", url)

    def _page(self, url: str) -> Page | None:
        if not self._allowed(url):
            return None
        try:
            reply = self._web.get(url)
        except TooLarge:
            self.warn(f"skipped {url}: larger than {MAX_PAGE_BYTES} bytes")
            return None
        if reply.status != 200:
            self.warn(f"skipped {url}: HTTP {reply.status}")
            return None
        if "html" not in reply.content_type.lower():
            return None
        tree = HTMLParser(reply.text)
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
