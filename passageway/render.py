"""The compact text Claude gets, for the hook and the MCP tool alike."""

import math

from passageway.rank import Hit

HEADER = "Recall results{source} — open a link for the full document:"
SHORT_PASSAGE = 120


def approx_tokens(s: str) -> int:
    return math.ceil(len(s.split()) * 1.3)


def _hit_lines(n: int, hit: Hit, several: bool, with_links: bool, passage: str) -> list[str]:
    tags = f" [{' · '.join(hit.labels)}]" if hit.labels else ""
    line = f"{n}. {hit.title}{tags} {hit.url}"
    if several:
        line += f" @{hit.source}"
    lines = [line]
    passage = " ".join(passage.split())  # one line: list breaks and blank lines cost tokens
    where = " › ".join([*hit.path, *([hit.heading] if hit.heading else [])])
    lines.append(f'   § {where}: "{passage}"' if where else f'   "{passage}"')
    if with_links and hit.links:
        lines.append("   related: " + ", ".join(f"{title} {url}" for title, url in hit.links))
    return lines


def _shorten(passage: str) -> str:
    if len(passage) <= SHORT_PASSAGE:
        return passage
    return passage[:SHORT_PASSAGE].rsplit(" ", 1)[0].rstrip("…") + "…"


def render(hits: list[Hit], max_tokens: int = 400) -> str:
    return fit(hits, max_tokens)[0]


def fit(hits: list[Hit], max_tokens: int = 400) -> tuple[str, list[Hit]]:
    """The text and the hits it actually contains (the budget may drop hits from the end)."""
    if not hits:
        return "", []
    several = len({h.source for h in hits}) > 1
    header = HEADER.format(source="" if several else f" ({hits[0].source})")
    # Degrade until it fits: drop links, then shorten passages, then drop hits from the end.
    for count in range(len(hits), 0, -1):
        for with_links, short in ((True, False), (False, False), (False, True)):
            lines = [header]
            for n, hit in enumerate(hits[:count], 1):
                lines += _hit_lines(n, hit, several, with_links, _shorten(hit.passage) if short else hit.passage)
            text = "\n".join(lines)
            if approx_tokens(text) <= max_tokens:
                return text, hits[:count]
    return text, hits[:1]
