"""An in-test MediaWiki Action API: the JSON shapes (formatversion=2) the live API returned, served over HTTP."""

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qsl, urlparse


class FakeWiki:
    def __init__(self):
        self.pages = {}       # page id -> {"title", "text", "revid", "ts"}
        self.categories = {}  # "Category:X" -> {"pages": [ids], "subcats": ["Category:Y"]}
        self.geo = []         # page ids returned by geosearch
        self.redirects = {}   # title -> title
        self.page_size = 500  # category members per response; small values exercise continuation
        self.lag_errors = 0   # answer this many requests with a maxlag error
        self.status_errors = []  # answer the next requests with these HTTP statuses
        self.requests = []    # {"query": {...}, "ua": "..."} for every request

    def add(self, page_id, title, text="", revid=100, ts="2026-10-01T00:00:00Z"):
        self.pages[page_id] = {"title": title, "text": text, "revid": revid, "ts": ts}

    def respond(self, q):
        if self.lag_errors > 0:
            self.lag_errors -= 1
            return {"error": {"code": "maxlag", "info": "Waiting for a database server: 5 seconds lagged."}}
        if q.get("list") == "categorymembers":
            cat = self.categories.get(q["cmtitle"], {"pages": [], "subcats": []})
            members = [{"pageid": i, "ns": 0, "title": self.pages[i]["title"], "type": "page"} for i in cat["pages"]]
            members += [{"pageid": 9000 + n, "ns": 14, "title": t, "type": "subcat"} for n, t in enumerate(cat["subcats"])]
            start = int(q.get("cmcontinue", "0"))
            out = {"batchcomplete": True, "query": {"categorymembers": members[start:start + self.page_size]}}
            if start + self.page_size < len(members):
                out["continue"] = {"cmcontinue": str(start + self.page_size), "continue": "-||"}
            return out
        if q.get("list") == "geosearch":
            return {"batchcomplete": True, "query": {"geosearch": [
                {"pageid": i, "ns": 0, "title": self.pages[i]["title"], "lat": 0.0, "lon": 0.0, "dist": 1.0}
                for i in self.geo]}}
        if "titles" in q:
            by_title = {p["title"]: i for i, p in self.pages.items()}
            pages = []
            for title in q["titles"].split("|"):
                title = self.redirects.get(title, title)
                if title in by_title:
                    pages.append({"pageid": by_title[title], "ns": 0, "title": title})
                else:
                    pages.append({"title": title, "missing": True})
            return {"batchcomplete": True, "query": {"pages": pages}}
        if "pageids" in q:
            pages = []
            for i in (int(x) for x in q["pageids"].split("|")):
                p = self.pages.get(i)
                if p is None:
                    pages.append({"pageid": i, "missing": True})
                    continue
                page = {"pageid": i, "ns": 0, "title": p["title"],
                        "revisions": [{"revid": p["revid"], "timestamp": p["ts"]}]}
                if "extracts" in q.get("prop", ""):
                    page["extract"] = p["text"]
                pages.append(page)
            return {"batchcomplete": True, "query": {"pages": pages}}
        return {"error": {"code": "badrequest", "info": f"unsupported request {q}"}}


def serve(wiki: FakeWiki):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            q = dict(parse_qsl(urlparse(self.path).query))
            wiki.requests.append({"query": q, "ua": self.headers.get("User-Agent", "")})
            if wiki.status_errors:
                self.send_response(wiki.status_errors.pop(0))
                self.send_header("Retry-After", "0")
                self.end_headers()
                return
            body = json.dumps(wiki.respond(q)).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True).start()
    return server
