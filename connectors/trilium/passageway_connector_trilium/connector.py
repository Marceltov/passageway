"""passageway connector for Trilium Notes: every text and code note of a Trilium server, read through ETAPI with GET only.

The LLM-wiki structure of trilium-recall is kept: areas from the owned #llmWikiPart roots (wiki, sources, locks, templates,
views, schema) and the journal from #calendarRoot give each note a weight; its wiki labels become labels; relations and
links in the text become links. Nothing source-specific reaches the core.
"""

import hashlib
import json
import re
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urlparse

import httpx
from passageway_sdk import Connector, SettingsError, SourceError

from passageway_connector_trilium.html import html_to_sections

SCOPE = "note.type = text or note.type = code"
# Trilium 0.106 returns nothing for a query that starts with "(", so the date clause goes first.
SCOPE_SINCE = "note.utcDateModified >= '{since}' and (" + SCOPE + ")"
# #llmWikiPart value -> area of everything below it; None = excluded (plumbing, not knowledge).
CLASSIFY = {"wiki": "wiki", "sources": "source", "locks": None, "templates": None, "views": None, "schema": "wiki"}
WEIGHTS = {"wiki": 1.0, "source": 0.8, "journal": 0.6, "other": 0.6}
LINK_RELATIONS = ("internalLink", "relatesTo", "wikiSource")
TEXT_LINK = re.compile(r'href="#root/([A-Za-z0-9_]+)"')  # a link in the note's text (Trilium derives internalLink from it on save)
MAX_PATH = 4


@dataclass(frozen=True)
class Settings:
    url: str
    web_url: str
    token: str
    timeout: float


def parse_settings(env: Mapping[str, str]) -> Settings:
    url = env.get("URL", "").strip().rstrip("/")
    if not url or urlparse(url).scheme not in ("http", "https") or not urlparse(url).hostname:
        raise SettingsError(f"URL must be the Trilium server's http(s) address, got {url!r}")
    token = env.get("TOKEN", "").strip()
    if not token:
        raise SettingsError("TOKEN is required: an ETAPI token (Options › ETAPI), as a secret reference")
    web_url = env.get("WEB_URL", "").strip().rstrip("/") or url
    if urlparse(web_url).scheme not in ("http", "https") or not urlparse(web_url).hostname:
        raise SettingsError(f"WEB_URL must be an http(s) address, got {web_url!r}")
    try:
        timeout = float(env.get("TIMEOUT", "").strip() or 30)
    except ValueError:
        raise SettingsError(f"TIMEOUT must be a number of seconds, got {env.get('TIMEOUT')!r}") from None
    if timeout <= 0:
        raise SettingsError("TIMEOUT must be greater than 0")
    return Settings(url, web_url, token, timeout)


class Etapi:
    """Read-only: only GET requests, by construction."""

    def __init__(self, settings: Settings):
        self._http = httpx.Client(base_url=settings.url + "/etapi", headers={"Authorization": settings.token},
                                  timeout=settings.timeout)

    def _get(self, path: str, **params) -> httpx.Response:
        response = self._http.get(path, params=params)
        if response.status_code >= 400:
            raise SourceError(f"Trilium answered HTTP {response.status_code} to GET {path}")
        return response

    def search(self, query: str, ancestor: str | None = None) -> list[dict]:
        params = {"search": query, "fastSearch": "true"}
        if ancestor:
            params["ancestorNoteId"] = ancestor
        return self._get("/notes", **params).json()["results"]

    def content(self, note_id: str) -> str | None:
        response = self._http.get(f"/notes/{note_id}/content")
        if response.status_code == 404:
            return None
        if response.status_code >= 400:
            raise SourceError(f"Trilium answered HTTP {response.status_code} to GET /notes/{note_id}/content")
        return response.text


def _owned(note: dict, name: str) -> list[dict]:
    return [a for a in note["attributes"] if a["name"] == name and a["noteId"] == note["noteId"]]


def _labels(note: dict, name: str) -> list[str]:
    """Values of a label, owned or inherited from a template, empty values dropped, order kept."""
    values = [a["value"] for a in note["attributes"] if a["type"] == "label" and a["name"] == name and a["value"]]
    return list(dict.fromkeys(values))


def _iso(trilium_time: str) -> str:
    """Trilium's 'YYYY-MM-DD HH:MM:SS.mmmZ' as ISO 8601."""
    try:
        return datetime.strptime(trilium_time[:19], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return trilium_time


@dataclass
class Scan:
    notes: dict[str, dict]  # in scope: noteId -> note
    area: dict[str, str]
    roots: set[str]
    reverse: dict[str, list[str]]  # noteId -> ids of the summaries whose wikiSource it is


class Trilium(Connector):
    name = "trilium connector"
    expected_errors = (httpx.HTTPError, ValueError, KeyError)

    def __init__(self, env: Mapping[str, str]):
        self.settings = parse_settings(env)
        self.client = Etapi(self.settings)

    # -- the scan ------------------------------------------------------------------------------------

    def _roots(self) -> tuple[dict[str, str | None], str | None]:
        roots: dict[str, str | None] = {}
        for note in self.client.search("#llmWikiPart"):
            for attr in _owned(note, "llmWikiPart"):
                if attr["value"] in CLASSIFY:
                    roots[note["noteId"]] = CLASSIFY[attr["value"]]
        calendars = [n for n in self.client.search("#calendarRoot") if _owned(n, "calendarRoot")]
        return roots, calendars[0]["noteId"] if calendars else None

    def _scan(self, query: str = SCOPE) -> Scan:
        roots, journal = self._roots()
        notes = {n["noteId"]: n for n in self.client.search(query)}
        area: dict[str, str | None] = {}
        # Excluded wins over everything, then wiki > source > journal; the rest is "other".
        ordered = [r for r, a in roots.items() if a is None] + [r for r, a in roots.items() if a == "wiki"] + \
                  [r for r, a in roots.items() if a == "source"] + ([journal] if journal else [])
        for root in ordered:
            label = roots.get(root, "journal")
            for note in self.client.search(query, ancestor=root):
                if note["noteId"] in notes:
                    area.setdefault(note["noteId"], label)
        in_scope = {nid: n for nid, n in notes.items() if area.get(nid, "other") is not None}
        reverse: dict[str, list[str]] = {}
        for nid, note in in_scope.items():
            for a in note["attributes"]:
                if a["type"] == "relation" and a["name"] == "wikiSource" and a["noteId"] == nid:
                    reverse.setdefault(a["value"], []).append(nid)
        return Scan(in_scope, {nid: area.get(nid, "other") for nid in in_scope}, set(roots) | ({journal} if journal else set()),
                    reverse)

    @staticmethod
    def _version(note: dict, area: str) -> str:
        attrs = sorted((a["type"], a["name"], a["value"]) for a in note["attributes"])
        payload = json.dumps([attrs, note["title"], sorted(note["parentNoteIds"]), area])
        return f"{note['blobId']}:{hashlib.sha256(payload.encode()).hexdigest()[:12]}"

    def _path(self, note: dict, scan: Scan) -> list[str]:
        path, parents, seen = [], note["parentNoteIds"], set()
        while (parents and parents[0] in scan.notes and parents[0] not in seen and parents[0] not in scan.roots
               and len(path) < MAX_PATH):
            seen.add(parents[0])
            path.insert(0, scan.notes[parents[0]]["title"])
            parents = scan.notes[parents[0]]["parentNoteIds"]
        return path

    def _item(self, note: dict, scan: Scan) -> dict | None:
        nid, area = note["noteId"], scan.area[note["noteId"]]
        content = self.client.content(nid)
        if content is None:  # gone since the listing: the next reconcile settles it
            return None
        sections = [{"heading": " › ".join(s.heading_path) or None, "text": s.text}
                    for s in html_to_sections(content, plain=note["type"] == "code")]
        labels = [f"area:{area}"] + [f"type:{t}" for t in _labels(note, "wikiType")[:1]] + \
                 [f"topic:{t}" for t in _labels(note, "wikiTopic")] + [f"status:{s}" for s in _labels(note, "wikiStatus")[:1]]
        links = [a["value"] for a in note["attributes"] if a["type"] == "relation" and a["name"] in LINK_RELATIONS
                 and a["noteId"] == nid] + (TEXT_LINK.findall(content) if note["type"] != "code" else []) + scan.reverse.get(nid, [])
        links = [i for i in dict.fromkeys(links) if i in scan.notes and i != nid]
        item = {"id": nid, "title": note["title"], "url": f"{self.settings.web_url}/#root/{nid}",
                "version": self._version(note, area), "sections": sections, "weight": WEIGHTS[area],
                "labels": labels, "updated": _iso(note["utcDateModified"])}
        if path := self._path(note, scan):
            item["path"] = path
        if links:
            item["links"] = links
        return item

    # -- the protocol --------------------------------------------------------------------------------

    def versions(self) -> dict[str, str]:
        scan = self._scan()
        return {nid: self._version(note, scan.area[nid]) for nid, note in scan.notes.items()}

    def fetch(self, ids: list[str]) -> Iterator[dict]:
        scan = self._scan()
        for nid in ids:
            if nid in scan.notes and (item := self._item(scan.notes[nid], scan)):
                yield item

    def changed(self, since: datetime) -> Iterator[dict]:
        stamp = since.strftime("%Y-%m-%d %H:%M:%S")
        full = self._scan()  # paths and links need every note
        changed = self._scan(SCOPE_SINCE.format(since=stamp))
        for nid in changed.notes:
            if nid in full.notes and (item := self._item(full.notes[nid], full)):
                yield item


def main() -> None:
    Trilium.main()
