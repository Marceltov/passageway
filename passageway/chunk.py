"""Turns an item into the pieces that are embedded and returned as passages."""

import re
from dataclasses import dataclass

from passageway.protocol import Item

MAX_CHARS = 1500  # a section over this is split; the embedding model cuts at a few hundred tokens anyway


@dataclass(frozen=True)
class Chunk:
    heading: str
    text: str
    ordinal: int


def _cut_words(paragraph: str, cap: int) -> list[str]:
    out, line = [], ""
    for word in paragraph.split():
        while len(word) > cap:
            if line:
                out.append(line)
                line = ""
            out.append(word[:cap])
            word = word[cap:]
        if line and len(line) + 1 + len(word) > cap:
            out.append(line)
            line = word
        else:
            line = f"{line} {word}" if line else word
    if line:
        out.append(line)
    return out


def split_text(text: str, cap: int = MAX_CHARS) -> list[str]:
    """Pieces of at most `cap` characters, cut at blank lines first, then between words."""
    text = text.strip()
    if len(text) <= cap:
        return [text] if text else []
    pieces, current = [], ""
    for paragraph in re.split(r"\n\s*\n", text):
        paragraph = paragraph.strip()
        for part in [paragraph] if len(paragraph) <= cap else _cut_words(paragraph, cap):
            if not part:
                continue
            if current and len(current) + 2 + len(part) > cap:
                pieces.append(current)
                current = part
            else:
                current = f"{current}\n\n{part}" if current else part
    if current:
        pieces.append(current)
    return pieces


def chunks(item: Item) -> list[Chunk]:
    out: list[Chunk] = []
    for section in item.sections:
        for piece in split_text(section.text):
            out.append(Chunk(section.heading or "", piece, len(out)))
    return out


def passage_text(item: Item, chunk: Chunk) -> str:
    trail = " › ".join([*item.path, *([chunk.heading] if chunk.heading else [])])
    return f"{item.title} › {trail}: {chunk.text}" if trail else f"{item.title}: {chunk.text}"
