"""Splits a MediaWiki plain-text extract (exsectionformat=wiki) into sections at its == headings ==."""

import re

HEADING = re.compile(r"^(={2,6})[ \t]*(.+?)[ \t]*\1[ \t]*$", re.M)
DISPLAY = re.compile(r"^\s+\{\\displaystyle (.*)\}\s*$")  # the TeX line that closes each formula in the plain-text extract
INVISIBLE = dict.fromkeys(range(0x2061, 0x2065))  # invisible function application, times, separator, plus

DEFAULT_SKIP = frozenset({
    "see also", "references", "external links", "further reading", "notes", "footnotes", "bibliography", "sources",
    "siehe auch", "einzelnachweise", "weblinks", "literatur", "anmerkungen", "fußnoten", "quellen",
})


def clean_math(text: str) -> str:
    """Formulas in the plain-text extract are a MathML block, one token per indented line, then a {\\displaystyle TeX} line.
    Replace each block with its TeX between $ signs; other indented text is kept."""
    out: list[str] = []
    pending: list[str] = []  # blank or indented lines that may be the start of a formula block

    def flush() -> None:
        out.extend(line if line.strip() else "" for line in pending)
        pending.clear()

    for line in text.translate(INVISIBLE).split("\n"):
        match = DISPLAY.match(line)
        if match:
            if not all(len(p.strip()) <= 60 for p in pending):  # real text in front of it: keep that
                flush()
            pending.clear()
            out.append(f"${match.group(1)}$")
        elif line.startswith("  ") or (pending and not line.strip()):  # MathML is indented by two or more; a blank line inside stays
            pending.append(line)
        else:
            flush()
            out.append(line)
    flush()
    return "\n".join(out)


def split_sections(extract: str, skip: frozenset[str]) -> list[dict]:
    parts = HEADING.split(clean_math(extract))  # lead, then (marks, title, body) triples
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
