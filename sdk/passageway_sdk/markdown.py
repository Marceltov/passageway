"""Markdown helpers for connectors: cut a document into sections at its headings, and see it without code."""

import re
from collections.abc import Iterator

_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
_HEADING = re.compile(r"^ {0,3}(#{1,6})[ \t]+(.*?)(?:[ \t]+#+)?[ \t]*$")
_INLINE_CODE = re.compile(r"(?<!`)(`+)(?!`)[^\n]+?(?<!`)\1(?!`)")  # a span closes with a run of exactly the same length
SEPARATOR = " › "


def _lines(text: str) -> Iterator[tuple[str, bool]]:
    """Each line with whether it is inside a fenced code block (the fence lines themselves count as inside)."""
    fence = ""  # the opening fence while inside a block
    for line in text.splitlines():
        match = _FENCE.match(line)
        if not fence:
            # the info string of a backtick fence cannot contain a backtick: "```a`b" is not a fence
            opens = bool(match) and not (match.group(1)[0] == "`" and "`" in match.group(2))
            if opens:
                fence = match.group(1)
            yield line, opens
        else:
            # a closing fence: the same character, at least as long, and nothing after it
            if match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence) and not match.group(2).strip():
                fence = ""
            yield line, True


def split_markdown(text: str, *, skip_first_h1: bool = False) -> list[dict]:
    """Sections for an item: {"heading": "Setup › Linux", "text": "…"}, one per heading level (# to ######).

    The heading is the trail of the parent headings. Text before the first heading has heading None. A `#` inside a fenced
    code block is not a heading. Sections without text are dropped (their heading stays in the trail of their children).
    With skip_first_h1 the first level-1 heading is left out of the trail, because it is the title of the item.
    """
    sections: list[dict] = []
    trail: list[tuple[int, str]] = []
    lines: list[str] = []
    heading: str | None = None
    seen_h1 = False

    def flush() -> None:
        body = "\n".join(lines).strip()
        if body:
            sections.append({"heading": heading, "text": body})
        lines.clear()

    for line, in_code in _lines(text):
        match = None if in_code else _HEADING.match(line)
        if not match or not match.group(2).strip():
            lines.append(line)
            continue
        flush()
        level, title = len(match.group(1)), match.group(2).strip()
        if skip_first_h1 and level == 1 and not seen_h1:
            seen_h1 = True
            trail = []  # the title is above everything: what follows starts again from the top
        else:
            trail = [t for t in trail if t[0] < level] + [(level, title)]
        heading = SEPARATOR.join(t[1] for t in trail) or None
    flush()
    return sections


def strip_code(text: str) -> str:
    """The text without fenced code blocks and inline code, e.g. to find the links a document really contains."""
    outside = "\n".join(line for line, in_code in _lines(text) if not in_code)
    return _INLINE_CODE.sub("", outside)


def first_h1(text: str) -> str | None:
    """The text of the first level-1 heading outside code, or None: the title of a document that has no other."""
    for line, in_code in _lines(text):
        match = None if in_code else _HEADING.match(line)
        if match and len(match.group(1)) == 1 and match.group(2).strip():
            return match.group(2).strip()
    return None
