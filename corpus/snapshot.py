"""Writes Wikipedia articles as markdown files with front matter, for the frozen corpus (corpus/README.md).

Not part of the Wikipedia connector: a maintenance script that uses the connector as a library. Settings are the
connector's (LANGUAGE, CATEGORIES, CATEGORY_DEPTH, TITLES, SKIP_SECTIONS, MAX_PAGES, CONTACT, PAUSE_SECONDS, API_URL,
PAGE_URL) plus OUT (the folder to write), LIMIT (keep the N longest articles) and FORCE=1 (overwrite files).

    OUT=corpus/en LANGUAGE=en CATEGORIES="Deep learning" CATEGORY_DEPTH=0 LIMIT=30 uv run python corpus/snapshot.py
"""

import os
import re
import sys
import time
import unicodedata
from collections.abc import Mapping
from pathlib import Path
from urllib.parse import quote

import httpx
import yaml
from passageway_connector_wikipedia.connector import Scope, ScopeError, _int, _pages, _user_agent, article_url, parse_scope
from passageway_connector_wikipedia.mediawiki import Wiki, WikiError
from passageway_connector_wikipedia.sections import HEADING

LICENSE = "CC BY-SA 4.0"
LICENSE_URL = "https://creativecommons.org/licenses/by-sa/4.0/"


def to_markdown(extract: str, skip: frozenset[str]) -> str:
    """The article body with `==` headings as `##` headings, without skipped sections (and their subsections)."""
    parts = HEADING.split(extract)  # the lead, then (marks, title, body) triples
    out = [parts[0].strip()] if parts[0].strip() else []
    trail: list[tuple[int, str]] = []
    for i in range(1, len(parts), 3):
        level, title, body = len(parts[i]), parts[i + 1].strip(), parts[i + 2].strip()
        trail = [t for t in trail if t[0] < level] + [(level, title)]
        if any(t[1].casefold() in skip for t in trail):
            continue
        out.append(f"{'#' * level} {title}" + (f"\n\n{body}" if body else ""))
    return "\n\n".join(out)


def file_name(title: str, taken: set[str], page_id: int) -> str:
    slug = re.sub(r"[\W_]+", "-", unicodedata.normalize("NFC", title).casefold()).strip("-") or str(page_id)
    if slug in taken:
        slug = f"{slug}-{page_id}"
    taken.add(slug)
    return f"{slug}.md"


def history_url(scope: Scope, title: str) -> str:
    return f"{scope.api_url.rsplit('/', 1)[0]}/index.php?title={quote(title.replace(' ', '_'))}&action=history"


def snapshot(env: Mapping[str, str], stdout, stderr, *, sleep=time.sleep) -> int:
    try:
        out = Path(env.get("OUT", "").strip() or "")
        if not env.get("OUT", "").strip():
            raise ScopeError("OUT must name the folder to write")
        limit = _int(env, "LIMIT", 0, 0)
        if env.get("LIMIT", "").strip() and limit < 1:
            raise ScopeError("LIMIT must be at least 1")
        scope = parse_scope(env)
        wiki = Wiki(scope.api_url, _user_agent(scope), pause=scope.pause, sleep=sleep)
        revisions = wiki.revisions(list(_pages(wiki, scope)))  # redirects have no revision: they drop out here
        articles = []
        for page_id in revisions:
            article = wiki.article(page_id)
            if article is not None:
                title, extract, revid, timestamp = article
                articles.append((page_id, title, to_markdown(extract, scope.skip), revid, timestamp))
    except ScopeError as e:
        print(f"snapshot: {e}", file=stderr)
        return 2
    except (WikiError, httpx.HTTPError) as e:
        print(f"snapshot: {e}", file=stderr)
        return 1
    articles.sort(key=lambda a: (-len(a[2]), a[1]))  # the longest first, ties by title
    if limit:
        articles = articles[:limit]

    taken: set[str] = set()
    # names are given in page-id order: ids never change, so a clash resolves the same way every time
    files = sorted(((file_name(a[1], taken, a[0]), a) for a in sorted(articles)), key=lambda f: f[1][1])
    existing = [name for name, _ in files if (out / name).exists()]
    if existing and env.get("FORCE") != "1":
        print(f"snapshot: {len(existing)} files exist in {out}, e.g. {existing[0]}; set FORCE=1 to overwrite them", file=stderr)
        return 2

    out.mkdir(parents=True, exist_ok=True)
    notes = [f"Articles from {scope.page_url.split('/wiki/')[0]}, licensed {LICENSE} ({LICENSE_URL}).",
             "Changes: converted to markdown; boilerplate sections (references, external links) removed.",
             "The authors of each article are listed in its history page.", ""]
    for name, (page_id, title, body, revid, timestamp) in files:
        meta = {"title": title, "url": article_url(scope, title), "updated": timestamp,
                "language": env.get("LANGUAGE", "").strip() or "en", "revision": revid, "license": LICENSE,
                "source": "Wikipedia"}
        head = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True, width=1000)
        (out / name).write_text(f"---\n{head}---\n\n{body}\n", encoding="utf-8")
        notes.append(f"- {title}: {meta['url']} (revision {revid}, {timestamp}); authors: {history_url(scope, title)}")
        print(title, file=stdout)
    (out / "ATTRIBUTION.txt").write_text("\n".join(notes) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(snapshot(os.environ, sys.stdout, sys.stderr))
