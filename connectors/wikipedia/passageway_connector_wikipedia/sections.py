"""Splits a MediaWiki plain-text extract (exsectionformat=wiki) into sections at its == headings ==."""

import re

HEADING = re.compile(r"^(={2,6})[ \t]*(.+?)[ \t]*\1[ \t]*$", re.M)

DEFAULT_SKIP = frozenset({
    "see also", "references", "external links", "further reading", "notes", "footnotes", "bibliography", "sources",
    "siehe auch", "einzelnachweise", "weblinks", "literatur", "anmerkungen", "fußnoten", "quellen",
})


def split_sections(extract: str, skip: frozenset[str]) -> list[dict]:
    parts = HEADING.split(extract)  # lead, then (marks, title, body) triples
    out: list[dict] = []
    if parts[0].strip():
        out.append({"heading": None, "text": parts[0].strip()})
    trail: list[tuple[int, str]] = []
    for i in range(1, len(parts), 3):
        level, title, body = len(parts[i]), parts[i + 1].strip(), parts[i + 2].strip()
        trail = [t for t in trail if t[0] < level] + [(level, title)]
        if any(t[1].casefold() in skip for t in trail):  # a skipped heading skips its subsections too
            continue
        if body:
            out.append({"heading": " › ".join(t[1] for t in trail), "text": body})
    return out
