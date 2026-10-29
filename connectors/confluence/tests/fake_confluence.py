"""An in-test Confluence Data Center REST API over HTTP: the few endpoints the connector uses, with paging and CQL."""

import json
import re
import threading
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


@dataclass
class Page:
    id: str
    space: str
    title: str
    body: str
    version: int = 1
    when: str = "2026-10-20T10:00:00.000Z"
    labels: list[str] = field(default_factory=list)
    ancestors: list[str] = field(default_factory=list)  # ids, root first
    status: str = "current"


class FakeConfluence:
    def __init__(self):
        self.pages: dict[str, Page] = {}
        self.requests: list[tuple[str, str, dict]] = []
        self.token = "fixture-pat"
        self.page_size = 100
        self.status_errors: list[int] = []
        self.retry_after = "0"
        self.loop = False  # ignore `start`, like a cursor-paged server
        self.redirect = False

    def add(self, id, space, title, body, **kw) -> str:
        self.pages[id] = Page(id, space, title, body, **kw)
        return id

    def edit(self, id, body=None, title=None, labels=None):
        p = self.pages[id]
        p.version += 1
        p.when = f"2026-10-28T12:{p.version:02d}:00.000Z"
        if body is not None:
            p.body = body
        if title is not None:
            p.title = title
        if labels is not None:
            p.labels = labels

    def _summary(self, p: Page, expand: str) -> dict:
        out = {"id": p.id, "type": "page", "status": p.status, "title": p.title,
               "_links": {"webui": f"/pages/viewpage.action?pageId={p.id}", "self": f"/rest/api/content/{p.id}"}}
        if "version" in expand:
            out["version"] = {"number": p.version, "when": p.when}
        if "space" in expand:
            out["space"] = {"key": p.space, "name": f"Space {p.space}"}
        if "body.storage" in expand:
            out["body"] = {"storage": {"value": p.body, "representation": "storage"}}
        if "ancestors" in expand:
            out["ancestors"] = [{"id": a, "title": self.pages[a].title} for a in p.ancestors if a in self.pages]
        if "metadata.labels" in expand:
            out["metadata"] = {"labels": {"results": [{"name": lb} for lb in p.labels]}}
        return out

    def _paged(self, items: list[dict], start: int, limit: int, path: str, q: dict) -> dict:
        chunk = items[start:start + limit]
        out = {"results": chunk, "start": start, "limit": limit, "size": len(chunk), "_links": {}}
        if start + limit < len(items):
            rest = "&".join(f"{k}={v}" for k, v in q.items() if k != "start")
            out["_links"]["next"] = f"{path}?{rest}&start={start + limit}"
        return out

    def respond(self, method: str, path: str, q: dict, auth: str) -> tuple[int, dict | str]:
        self.requests.append((method, path, q))
        if self.status_errors:
            return self.status_errors.pop(0), "later"
        if self.redirect:
            return 302, {"message": "login"}
        if auth != f"Bearer {self.token}":
            return 401, {"message": "unauthorized"}
        if method != "GET":
            return 405, {"message": "read-only fake"}
        limit = min(int(q.get("limit", "25")), self.page_size)
        start = 0 if self.loop else int(q.get("start", "0"))
        expand = q.get("expand", "")
        if path == "/rest/api/content":
            pages = [p for p in self.pages.values() if p.space == q.get("spaceKey") and p.status == "current"]
            return 200, self._paged([self._summary(p, expand) for p in pages], start, limit, path, q)
        if path == "/rest/api/content/search":
            cql = q.get("cql", "")
            m = re.search(r'space in \(([^)]*)\)', cql)
            spaces = [s.strip().strip('"') for s in m.group(1).split(",")] if m else []
            since = re.search(r'lastModified >= "([^"]+)"', cql)
            pages = [p for p in self.pages.values() if p.space in spaces and p.status == "current" and "type = page" in cql
                     and (not since or p.when.replace("T", " ")[:16] >= since.group(1)[:16])]
            return 200, self._paged([self._summary(p, expand) for p in pages], start, limit, path, q)
        if m := re.fullmatch(r"/rest/api/content/(\d+)", path):
            p = self.pages.get(m.group(1))
            if not p or p.status != "current":
                return 404, {"message": "no content"}
            return 200, self._summary(p, expand)
        return 404, {"message": "unknown"}


def serve(api: FakeConfluence):
    class Handler(BaseHTTPRequestHandler):
        def _handle(self):
            url = urlparse(self.path)
            q = {k: v[0] for k, v in parse_qs(url.query).items()}
            status, body = api.respond(self.command, url.path, q, self.headers.get("Authorization", ""))
            payload = (json.dumps(body) if isinstance(body, dict) else body).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json" if isinstance(body, dict) else "text/plain")
            self.send_header("Retry-After", api.retry_after)
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        do_GET = do_POST = do_PUT = do_DELETE = _handle

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True).start()
    return server


def seed(api: FakeConfluence) -> None:
    api.add("100", "OPS", "Operations", "<p>The operations space.</p>")
    api.add("101", "OPS", "Rotating certificates",
            '<p>Rotate the signing certificate every year.</p><h2>Steps</h2><ol><li>Create the new certificate.</li>'
            '<li>Deploy it, see <ac:link><ri:page ri:content-title="Deploying" /><ac:plain-text-link-body><![CDATA[the deploy page]]></ac:plain-text-link-body></ac:link>.</li></ol>'
            '<h3>Checks</h3><ac:structured-macro ac:name="code"><ac:parameter ac:name="language">bash</ac:parameter>'
            '<ac:plain-text-body><![CDATA[openssl x509 -noout -dates]]></ac:plain-text-body></ac:structured-macro>'
            '<ac:structured-macro ac:name="toc"/><ac:structured-macro ac:name="info"><ac:rich-text-body><p>Takes an hour.</p></ac:rich-text-body></ac:structured-macro>',
            labels=["security", "howto"], ancestors=["100"])
    api.add("102", "OPS", "Deploying", "<p>How to deploy.</p><table><tbody><tr><th>Step</th><th>Who</th></tr><tr><td>Build</td><td>CI</td></tr></tbody></table>",
            labels=["howto"], ancestors=["100", "101"])
    api.add("200", "HR", "Cafeteria menu", "<p>Monday: soup.</p>")
    api.add("300", "SECRET", "Payroll", "<p>Nothing to see.</p>")
    api.add("103", "OPS", "Draft page", "<p>Not published.</p>", status="draft")
