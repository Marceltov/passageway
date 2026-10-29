"""passageway connector for Confluence Data Center: the current pages of chosen spaces, read through the REST API with GET only.

Written from the public REST documentation. Settings come from the environment and are documented in README.md.
"""

import hashlib
import re
import time
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from urllib.parse import urlparse

import httpx
from passageway_sdk import Connector, SettingsError, SourceError

from passageway_connector_confluence.html import html_to_sections

PAGE = 100  # results per request (the API's usual maximum)
MAX_ATTEMPTS = 5
RETRY_STATUS = (429, 500, 502, 503, 504)
FETCH_EXPAND = "body.storage,version,space,ancestors,metadata.labels"
def _list(env: Mapping[str, str], key: str) -> tuple[str, ...]:
    return tuple(p.strip() for p in env.get(key, "").split("|") if p.strip())


@dataclass(frozen=True)
class Settings:
    url: str
    spaces: tuple[str, ...]
    token: str
    include: frozenset[str]
    exclude: frozenset[str]
    max_pages: int
    timeout: float
    pause: float
    verify: bool


def parse_settings(env: Mapping[str, str]) -> Settings:
    url = env.get("URL", "").strip().rstrip("/")
    parsed = urlparse(url)
    if not url or parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise SettingsError(f"URL must be the Confluence site's http(s) address, got {url!r}")
    spaces = _list(env, "SPACES")
    if not spaces or not all(re.fullmatch(r"[A-Za-z0-9_~.-]+", s) for s in spaces):
        raise SettingsError("SPACES must list the space keys to index, separated by |, e.g. OPS|HR")
    token = env.get("TOKEN", "").strip()
    if not token:
        raise SettingsError("TOKEN is required: a personal access token from your Confluence profile, as a secret reference")
    raw = env.get("MAX_PAGES", "").strip()
    if raw and (not raw.isdecimal() or int(raw) < 1):
        raise SettingsError(f"MAX_PAGES must be a whole number from 1, got {raw!r}")
    try:
        timeout = float(env.get("TIMEOUT", "").strip() or 30)
        pause = float(env.get("PAUSE_SECONDS", "").strip() or 0)
    except ValueError:
        raise SettingsError("TIMEOUT and PAUSE_SECONDS must be numbers of seconds") from None
    if timeout <= 0 or pause < 0:
        raise SettingsError("TIMEOUT must be greater than 0 and PAUSE_SECONDS not negative")
    verify = env.get("VERIFY_TLS", "").strip().lower() or "true"
    if verify not in ("true", "false"):
        raise SettingsError("VERIFY_TLS must be true or false")
    return Settings(url, spaces, token, frozenset(_list(env, "INCLUDE_LABELS")), frozenset(_list(env, "EXCLUDE_LABELS")),
                    int(raw) if raw else 5000, timeout, pause, verify == "true")


class ApiError(SourceError):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status


class Api:
    """Read-only: only GET requests, by construction."""

    def __init__(self, s: Settings, sleep=time.sleep):
        self.s, self._sleep = s, sleep
        self._http = httpx.Client(base_url=s.url, headers={"Authorization": f"Bearer {s.token}"}, timeout=s.timeout,
                                  verify=s.verify)

    def get(self, path: str, **params) -> dict:
        for attempt in range(MAX_ATTEMPTS):
            wait = min(2 ** attempt, 30)
            try:
                response = self._http.get(path, params=params)
            except httpx.TransportError as e:
                response, reason = None, f"{type(e).__name__}: {e}"
            if response is not None:
                if response.status_code in RETRY_STATUS:
                    reason = f"HTTP {response.status_code}"
                    try:
                        wait = min(max(float(response.headers.get("Retry-After", wait)), 0), 30)
                    except ValueError:
                        pass
                elif response.status_code == 401:
                    raise ApiError(401, "Confluence answered HTTP 401: check TOKEN (a personal access token) and its permissions")
                elif 300 <= response.status_code < 400:
                    raise ApiError(response.status_code, f"Confluence answered GET {path} with a redirect to "
                                   f"{response.headers.get('Location', '?')}: check URL (and whether a login page is in the way)")
                elif response.status_code >= 400:
                    raise ApiError(response.status_code, f"Confluence answered HTTP {response.status_code} to GET {path}")
                else:
                    if self.s.pause:
                        self._sleep(self.s.pause)
                    data = response.json()
                    if not isinstance(data, dict):
                        raise SourceError(f"Confluence did not answer GET {path} with a JSON object")
                    return data
            if attempt < MAX_ATTEMPTS - 1:
                self._sleep(wait)
        raise SourceError(f"giving up on GET {path} after {MAX_ATTEMPTS} attempts: {reason}")

    def paged(self, path: str, **params) -> Iterator[dict]:
        start, seen = 0, set()
        while True:
            data = self.get(path, limit=str(PAGE), start=str(start), **params)
            results = data.get("results")
            if not isinstance(results, list):
                raise SourceError(f"Confluence answered GET {path} without a results list")
            fresh = [r for r in results if str(r.get("id")) not in seen]
            seen.update(str(r.get("id")) for r in results)
            yield from fresh
            # the server caps `limit` as it likes: follow `next`; a server that ignores `start` repeats itself: stop then
            if not fresh or not data.get("_links", {}).get("next"):
                return
            start += len(results)


def _iso(when: str) -> str:
    try:
        return datetime.fromisoformat(when.replace("Z", "+00:00")).astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return when


_ENTITIES = re.compile(r"&([A-Za-z][A-Za-z0-9]*);")
_KEEP_ENTITIES = {"amp", "lt", "gt", "quot", "apos"}


def _entities(storage: str) -> str:
    """Named HTML entities as characters, so that the XML parser accepts them; the five XML ones stay."""
    from html.entities import html5

    def one(m):
        name = m.group(1)
        return m.group(0) if name in _KEEP_ENTITIES else html5.get(name + ";", m.group(0))
    return _ENTITIES.sub(one, storage)


def _macro_param(node, name: str) -> str:
    for child in node:
        if child.tag == "{ac}parameter" and child.get("{ac}name") == name:
            return "".join(child.itertext()).strip()
    return ""


def _walk(node, out: list[str]) -> None:
    """Serialise a storage-format element as plain HTML: ac:/ri: elements become their readable part."""
    from xml.sax.saxutils import escape, quoteattr

    tag = node.tag
    if tag == "{ac}structured-macro":
        name = node.get("{ac}name", "")
        if name in ("code", "noformat"):
            body = next((c for c in node if c.tag == "{ac}plain-text-body"), None)
            out.append("<pre>" + escape("".join(body.itertext()) if body is not None else "") + "</pre>")
        elif name == "status":
            out.append(escape(_macro_param(node, "title")))
        else:  # a box, an expand, a section, a column, an excerpt: what it holds; a toc, a jira macro: nothing
            for child in node:
                if child.tag == "{ac}rich-text-body":
                    for grandchild in child:
                        _walk(grandchild, out)
                    out.append(escape(child.tail or ""))
        out.append(escape(node.tail or ""))
        return
    if tag == "{ac}link":
        body = next((c for c in node if c.tag in ("{ac}link-body", "{ac}plain-text-link-body")), None)
        if body is not None:
            out.append(escape("".join(body.itertext())))
        else:
            page = next((c for c in node if c.tag == "{ri}page"), None)
            out.append(escape(page.get("{ri}content-title", "")) if page is not None else "")
        out.append(escape(node.tail or ""))
        return
    if tag == "{ac}task-list":
        items = ["".join(b.itertext()) for task in node if task.tag == "{ac}task"
                 for b in task if b.tag == "{ac}task-body"]
        out.append("<ul>" + "".join(f"<li>{escape(i)}</li>" for i in items) + "</ul>" + escape(node.tail or ""))
        return
    if tag in ("{ac}placeholder", "{ac}image", "{ac}emoticon", "{ac}parameter", "{ac}task-id", "{ac}task-status") \
            or (isinstance(tag, str) and tag.startswith("{ri}")):
        out.append(escape(node.tail or ""))
        return
    if isinstance(tag, str) and tag.startswith("{ac}"):  # layouts, inline-comment markers, rich-text bodies: transparent
        out.append(escape(node.text or ""))
        for child in node:
            _walk(child, out)
        out.append(escape(node.tail or ""))
        return
    if not isinstance(tag, str):  # a comment
        out.append(escape(node.tail or ""))
        return
    attrs = "".join(f" {k}={quoteattr(v)}" for k, v in node.attrib.items() if not k.startswith("{"))
    out.append(f"<{tag}{attrs}>{escape(node.text or '')}")
    for child in node:
        _walk(child, out)
    out.append(f"</{tag}>{escape(node.tail or '')}")


def storage_to_html(storage: str) -> str:
    """Confluence's storage format as plain HTML: code macros become <pre>, boxes and expands keep what they hold, task
    lists become lists, links keep their text or the linked page's title; images, emoticons, placeholders, a table of
    contents, Jira and other macros without a body disappear. Storage that is not well-formed XML is read as HTML with
    the ac:/ri: markup stripped."""
    import xml.etree.ElementTree as ET

    wrapped = f'<root xmlns:ac="ac" xmlns:ri="ri">{_entities(storage)}</root>'
    try:
        root = ET.fromstring(wrapped)
    except ET.ParseError:
        return re.sub(r"</?(?:ac|ri):[^>]*>", "", storage)
    out: list[str] = [root.text or ""]
    for child in root:
        _walk(child, out)
    return "".join(out)


class Confluence(Connector):
    name = "confluence connector"
    expected_errors = (httpx.HTTPError, ValueError, KeyError, TypeError)

    def __init__(self, env: Mapping[str, str], *, sleep=time.sleep):
        self.s = parse_settings(env)
        self.api = Api(self.s, sleep)
        if not self.s.verify:
            self.warn("VERIFY_TLS is false: the server's certificate is not checked")

    def _wanted(self, labels: set[str]) -> bool:
        if self.s.include and not labels & self.s.include:
            return False
        return not (labels & self.s.exclude)

    @staticmethod
    def _labels(page: dict) -> set[str]:
        return {lb.get("name", "") for lb in page.get("metadata", {}).get("labels", {}).get("results", []) if lb.get("name")}

    def _version(self, page: dict) -> str:
        labels = hashlib.sha256(",".join(sorted(self._labels(page))).encode()).hexdigest()[:8]
        return f"{page['version']['number']}:{labels}"

    def _listing(self, pages: Iterator[dict]) -> dict[str, dict]:
        found: dict[str, dict] = {}
        for page in pages:
            if page.get("status", "current") != "current" or not self._wanted(self._labels(page)):
                continue
            found[str(page["id"])] = page
            if len(found) > self.s.max_pages:
                raise SourceError(f"the spaces hold more than {self.s.max_pages} pages: narrow them or raise MAX_PAGES")
        return found

    def _item(self, page: dict) -> dict | None:
        if page.get("status", "current") != "current" or not self._wanted(self._labels(page)):
            return None
        html = storage_to_html(page.get("body", {}).get("storage", {}).get("value", ""))
        sections = [{"heading": " › ".join(s.heading_path) or None, "text": s.text} for s in html_to_sections(html)]
        item = {"id": str(page["id"]), "title": page["title"], "url": self.s.url + page["_links"]["webui"],
                "version": self._version(page), "sections": sections, "weight": 1.0,
                "labels": [f"space:{page['space']['key']}", *sorted(self._labels(page))],
                "updated": _iso(page["version"]["when"])}
        if ancestors := [a["title"] for a in page.get("ancestors", [])][-4:]:
            item["path"] = ancestors
        return item

    # -- the protocol --------------------------------------------------------------------------------

    def versions(self) -> dict[str, str]:
        found: dict[str, dict] = {}
        for space in self.s.spaces:
            pages = self._listing(self.api.paged("/rest/api/content", spaceKey=space, type="page", status="current",
                                                 expand="version,metadata.labels"))
            if not pages:
                self.warn(f"the space {space!r} lists no pages: check the key and the token's permissions")
            found.update(pages)
            if len(found) > self.s.max_pages:
                raise SourceError(f"the spaces hold more than {self.s.max_pages} pages: narrow them or raise MAX_PAGES")
        return {pid: self._version(p) for pid, p in found.items()}

    def fetch(self, ids: list[str]) -> Iterator[dict]:
        for pid in ids:
            if not pid.isdecimal():
                continue
            try:
                page = self.api.get(f"/rest/api/content/{pid}", expand=FETCH_EXPAND)
            except ApiError as e:
                if e.status == 404:  # gone since the listing: the next reconcile settles it
                    continue
                raise
            if page.get("space", {}).get("key") in self.s.spaces and (item := self._item(page)):
                yield item

    def changed(self, since: datetime) -> Iterator[dict]:
        # CQL reads the time in the server's (or the user's) zone, not UTC: ask 14 hours early, which covers every
        # zone; pages whose version is unchanged are dropped by the core anyway
        stamp = (since.astimezone(UTC) - timedelta(hours=14)).strftime("%Y-%m-%d %H:%M")
        keys = ",".join(f'"{s}"' for s in self.s.spaces)
        cql = f'space in ({keys}) and type = page and lastModified >= "{stamp}"'
        for page in self.api.paged("/rest/api/content/search", cql=cql, expand=FETCH_EXPAND):
            if item := self._item(page):
                yield item


def main() -> None:
    Confluence.main()
