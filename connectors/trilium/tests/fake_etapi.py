"""An in-test Trilium ETAPI served over HTTP: the search grammar the connector sends, note JSON as Trilium 0.106 returns it.
Ported from trilium-recall's in-process fake; the fixture world is trilium-recall's public, synthetic seed (fixed fx… ids)."""

import itertools
import json
import re
import threading
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

SCOPE = "note.type = text or note.type = code"
SINCE = re.compile(r"^note\.utcDateModified >= '([^']+)' and \(" + re.escape(SCOPE) + r"\)$")
_ids = itertools.count(1)


@dataclass
class FakeNote:
    note_id: str
    title: str
    type: str
    parents: list[str]
    content: str = ""
    attrs: list[tuple[str, str, str, bool]] = field(default_factory=list)  # (type, name, value, owned)
    archived: bool = False
    modified: str = "2026-10-24 10:00:00.000Z"
    blob: int = 0


class FakeEtapi:
    def __init__(self):
        self.notes: dict[str, FakeNote] = {}
        self.requests: list[tuple[str, str, dict]] = []
        self.fail = False
        self.token = "fixture-token"
        self.clock = 0

    def tick(self) -> str:
        self.clock += 1
        stamp = datetime.now(UTC) + timedelta(milliseconds=self.clock)
        return stamp.strftime("%Y-%m-%d %H:%M:%S.") + f"{stamp.microsecond // 1000:03d}Z"

    def add(self, title, parent="root", type="text", content="", labels=(), relations=(), note_id=None, inherited=()):
        nid = note_id or f"n{next(_ids)}"
        attrs = [("label", n, v, True) for n, v in labels] + [("relation", n, v, True) for n, v in relations]
        attrs += [("label", n, v, False) for n, v in inherited]
        self.notes[nid] = FakeNote(nid, title, type, [parent], content, attrs, blob=next(_ids))
        return nid

    def set_content(self, nid, content):
        n = self.notes[nid]
        n.content, n.blob, n.modified = content, next(_ids), self.tick()

    def add_label(self, nid, name, value):
        n = self.notes[nid]
        n.attrs = [a for a in n.attrs if a[1] != name] + [("label", name, value, True)]
        n.modified = self.tick()

    def move(self, nid, under):
        self.notes[nid].parents = [under]
        self.notes[nid].modified = self.tick()

    def delete(self, nid):
        del self.notes[nid]

    # -- ETAPI ----------------------------------------------------------------------------------------

    def _ancestors(self, nid):
        seen, stack = set(), [nid]
        while stack:
            cur = stack.pop()
            if cur in seen or cur not in self.notes:
                continue
            seen.add(cur)
            stack.extend(self.notes[cur].parents)
        return seen

    def _json(self, n: FakeNote):
        return {"noteId": n.note_id, "title": n.title, "type": n.type, "blobId": f"b{n.blob}", "parentNoteIds": n.parents,
                "utcDateModified": n.modified, "dateModified": n.modified,
                "attributes": [{"type": t, "name": name, "value": v, "noteId": n.note_id if owned else "TEMPLATE"}
                               for t, name, v, owned in n.attrs]}

    def _search(self, query, ancestor):
        notes = [n for n in self.notes.values() if not n.archived and not n.note_id.startswith("_")]
        if ancestor:
            notes = [n for n in notes if ancestor in self._ancestors(n.note_id)]
        if query.startswith("#") and "=" not in query:
            name = query[1:]
            return [n for n in notes if any(a[1] == name for a in n.attrs)]
        in_scope = [n for n in notes if n.type in ("text", "code")]
        if query == SCOPE:
            return in_scope
        if m := SINCE.match(query):
            return [n for n in in_scope if n.modified >= m.group(1)]
        raise AssertionError(f"the fake ETAPI does not understand the query {query!r}")

    def respond(self, method: str, path: str, query: dict, auth: str) -> tuple[int, bytes, str]:
        self.requests.append((method, path, query))
        if self.fail:
            return 503, b"down", "text/plain"
        if auth != self.token:
            return 401, b'{"message": "bad token"}', "application/json"
        path = path.removeprefix("/etapi")
        if method != "GET":
            return 405, b"", "text/plain"
        if path == "/notes":
            try:
                hits = self._search(query["search"], query.get("ancestorNoteId"))
            except AssertionError as e:
                return 400, json.dumps({"message": str(e)}).encode(), "application/json"
            return 200, json.dumps({"results": [self._json(n) for n in hits]}).encode(), "application/json"
        if m := re.fullmatch(r"/notes/([^/]+)/content", path):
            n = self.notes.get(m.group(1))
            return (200, n.content.encode(), "text/html") if n else (404, b"", "text/plain")
        if path == "/app-info":
            return 200, b'{"appVersion": "0.106.0-fake"}', "application/json"
        return 404, b"", "text/plain"


def serve(etapi: FakeEtapi):
    class Handler(BaseHTTPRequestHandler):
        def _handle(self):
            url = urlparse(self.path)
            query = {k: v[0] for k, v in parse_qs(url.query).items()}
            status, body, ctype = etapi.respond(self.command, url.path, query, self.headers.get("Authorization", ""))
            self.send_response(status)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        do_GET = do_POST = do_PUT = do_DELETE = _handle

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True).start()
    return server


def link(note_id: str, title: str) -> str:
    return f'<a class="reference-link" href="#root/{note_id}">{title}</a>'


def seed_fixture(api: FakeEtapi) -> dict[str, str]:
    """The synthetic LLM wiki of trilium-recall's fixture (same ids, same text), for the parity cases."""
    wiki = api.add("Wiki", note_id="fxWiki", labels=[("llmWikiPart", "wiki")])
    sources = api.add("Sources", note_id="fxSources", labels=[("llmWikiPart", "sources")])
    year = api.add("2026", parent=sources, note_id="fxYear", labels=[("wikiSourceGroup", "2026")])
    locks = api.add("Locks", note_id="fxLocks", labels=[("llmWikiPart", "locks")])
    templates = api.add("Templates", note_id="fxTemplates", labels=[("llmWikiPart", "templates")])
    journal = api.add("Journal", note_id="fxJournal", labels=[("calendarRoot", "")])
    tpl = {t: api.add(t.title(), parent=templates, note_id=f"fxTpl{t.title()}", labels=[("llmWikiTemplate", t), ("wikiType", t)])
           for t in ("hub", "concept", "entity", "summary")}

    def page(nid, parent, kind, title, html, topic, status="draft", relations=()):
        return api.add(title, parent=parent, content=html, note_id=nid,
                       labels=[("wikiTopic", topic), ("wikiStatus", status), ("aiAssisted", "")],
                       relations=[("template", tpl[kind]), *relations], inherited=[("wikiType", kind)])

    page("fxHubHomelab", wiki, "hub", "Homelab", "<p>The home servers.</p>", "homelab")
    page("fxHubTrilium", wiki, "hub", "Trilium", "<p>The notes app and its tooling.</p>", "trilium")
    page("fxHubReisen", wiki, "hub", "Reisen", "<p>Reisen und Planung.</p>", "reisen")
    page("fxLxcMemory", "fxHubHomelab", "concept", "LXC memory limits",
         "<p>CT 101 (the database container) has 4 GB RAM and 2 GB swap. The OOM killer fires when the guest exceeds "
         f"its memory limit; raise it in the Proxmox resources tab. See {link('fxBackups', 'Nightly backups')} before resizing.</p>",
         "homelab")
    page("fxBridges", "fxHubHomelab", "concept", "Network bridges",
         "<p>vmbr0 carries the LAN and vmbr1 carries the IoT VLAN (tag 30). vmbr1 has an MTU of 1500 and no IP of its own.</p>",
         "homelab")
    page("fxBackups", "fxHubHomelab", "concept", "Nightly backups",
         "<p>vzdump runs every night at 02:00 for every guest and keeps 7 daily and 4 weekly snapshots.</p>"
         f"<h2>Offsite</h2><p>{link('fxRestic', 'restic')} copies the datastore to an S3 bucket every Sunday.</p>",
         "homelab", relations=[("relatesTo", "fxLxcMemory")])
    page("fxRestic", "fxHubHomelab", "entity", "restic",
         "<p>restic 0.16 with the S3 backend; the repository password is in the vault. Prune runs monthly.</p>", "homelab")
    page("fxTailscale", "fxHubHomelab", "entity", "Tailscale", "<p>Mesh VPN; page still to be written.</p>", "homelab", status="stub")
    page("fxTrBackup", "fxHubTrilium", "concept", "Trilium backups",
         "<p>Trilium writes its own backup database daily into the data folder. To restore, stop the container, copy the "
         "backup over document.db and start it again.</p>", "trilium")
    page("fxEtapi", "fxHubTrilium", "entity", "ETAPI",
         "<p>Trilium's REST API. Tokens are created in Options › ETAPI; each token is shown once. The engine only sends GET "
         "requests.</p>", "trilium")
    page("fxJrPass", "fxHubReisen", "concept", "Zugpass für Japan",
         "<p>Der Japan Rail Pass lohnt sich ab etwa zwei langen Shinkansen-Fahrten in 7 Tagen; seit 2023 ist er deutlich "
         "teurer. Für eine Reise nur in Kansai reicht ein regionaler Pass.</p>", "reisen")
    page("fxPackliste", "fxHubReisen", "concept", "Packliste",
         "<p>Für Japan: Reisepass, IC-Karte (Suica), Steckdosenadapter Typ A, leichte Schuhe zum An- und Ausziehen, "
         "Bargeld für kleine Läden, ein Handtuch für Onsen.</p>", "reisen")
    for hub, pages in {"fxHubHomelab": ["fxLxcMemory", "fxBridges", "fxBackups", "fxRestic", "fxTailscale"],
                       "fxHubTrilium": ["fxTrBackup", "fxEtapi"], "fxHubReisen": ["fxJrPass", "fxPackliste"]}.items():
        n = api.notes[hub]
        n.content += "<ul>" + "".join(f"<li>{link(p, api.notes[p].title)}</li>" for p in pages) + "</ul>"
        n.attrs += [("relation", "internalLink", p, True) for p in pages]
    api.add("Article: Sizing LXC containers", parent=year, note_id="fxSrcArticle",
            content="<p>A long article about memory for database containers: a database wants RAM for its cache and dislikes "
                    "swap; give the container what the working set needs and set swap low. Benchmarks follow.</p>")
    page("fxSumArticle", "fxHubHomelab", "summary", "Summary: Sizing LXC containers",
         "<p>A database container needs RAM for its cache; size it for the working set and keep swap low. The article "
         "argues against swap.</p>", "homelab", relations=[("wikiSource", "fxSrcArticle")])
    api.add("Clip: Kubernetes ingress annotations", parent=year, note_id="fxSrcClip",
            content="<p>nginx.ingress.kubernetes.io/proxy-body-size: 50m raises the upload limit of an ingress.</p>")
    api.add("2026-10-24", parent=journal, note_id="fxDay",
            content=f"<h2>Wiki</h2><ul><li><strong>ingest</strong>: {link('fxSumArticle', 'Sizing LXC containers')}</li></ul>")
    api.add("fixture-session: seeding", parent=locks, note_id="fxLockClaim", content="<p>zebra lock claim</p>")
    old = api.add("Old firewall rules", note_id="fxArchived", content="<p>zebra iptables legacy rules</p>")
    api.notes[old].archived = True
    api.add("Scratch", note_id="fxOther", content="<p>A note outside every area.</p>")
    api.add("deploy.sh", note_id="fxCode", type="code", content="#!/bin/sh\nrestic backup /data\n\necho done")
    return {"wiki": wiki, "sources": sources, "locks": locks, "journal": journal, "templates": templates}
