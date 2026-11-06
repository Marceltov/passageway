"""Turns an item into the pieces that are embedded and returned as passages."""

import re
from dataclasses import dataclass
from typing import Protocol

from passageway.protocol import Item

# Without a token count from the embedder (a command embedder that does not answer `count`), sections are cut here.
MAX_CHARS = 1500
ELLIPSIS = "…"


class ChunkError(Exception):
    """The model's token budget leaves no room for text: a configuration that cannot work, never a silent cut."""


class TokenCounter(Protocol):
    """What the chunker needs from an embedder: its limit, and how many tokens it would see for each passage text
    (its own passage prefix and special tokens included, before any cut). max_tokens None: it does not count."""

    max_tokens: int | None

    def count_passages(self, texts: list[str]) -> list[int]: ...


@dataclass(frozen=True)
class Chunk:
    heading: str
    text: str
    ordinal: int
    label: str = ""  # what goes in front of the text when it is embedded; empty: the item's full trail


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


def full_label(item: Item, heading: str | None) -> str:
    return " › ".join([item.title, *item.path, *([heading] if heading else [])])


def chunks(item: Item, counter: TokenCounter | None = None) -> list[Chunk]:
    """The pieces of an item. With a counter, every embedded text (label and piece) fits its max_tokens: pieces are cut
    at blank lines, then lines, then sentences, then words, and a word longer than the budget by tokens. Without one,
    sections are cut at MAX_CHARS characters."""
    budget = getattr(counter, "max_tokens", None) if counter is not None else None
    out: list[Chunk] = []
    for section in item.sections:
        heading = section.heading or ""
        if budget is None:
            for piece in split_text(section.text):
                out.append(Chunk(heading, piece, len(out)))
            continue
        label = _fit_label(item, section.heading, counter, budget // 2)

        def fits(piece: str, label=label) -> bool:
            return counter.count_passages([f"{label}: {piece}"])[0] <= budget

        for piece in _split(section.text, fits, 0):
            out.append(Chunk(heading, piece, len(out), label))
    if budget is not None and out:
        counts = counter.count_passages([passage_text(item, c) for c in out])
        over = [(c, n) for c, n in zip(out, counts) if n > budget]
        if over:  # the tokenizer counted a whole differently from its parts: a bug to see, not a cut to hide
            _, n = over[0]
            raise ChunkError(f"{item.id!r}: a piece of {n} tokens is over the model's limit of {budget}")
    return out


def passage_text(item: Item, chunk: Chunk) -> str:
    return f"{chunk.label or full_label(item, chunk.heading)}: {chunk.text}"


# ---- by tokens ----------------------------------------------------------------------------------

_LEVELS = (
    (re.compile(r"\n\s*\n"), "\n\n"),  # paragraphs
    (re.compile(r"\n"), "\n"),  # lines (list items)
    (re.compile(r"(?<=[.!?;:])\s+"), " "),  # sentences
    (re.compile(r"\s+"), " "),  # words
)


def _split(text: str, fits, level: int) -> list[str]:
    text = text.strip()
    if not text:
        return []
    if level == 0 and fits(text):
        return [text]
    if level == len(_LEVELS):
        return _cut_by_tokens(text, fits)
    pattern, joiner = _LEVELS[level]
    units = [u.strip() for u in pattern.split(text) if u.strip()]
    out, i = [], 0
    while i < len(units):
        if not fits(units[i]):
            out += _split(units[i], fits, level + 1)
            i += 1
            continue
        lo, hi = i + 1, len(units)  # the most units from i on that fit together: lo fits, hi is the upper bound
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if fits(joiner.join(units[i:mid])):
                lo = mid
            else:
                hi = mid - 1
        out.append(joiner.join(units[i:lo]))
        i = lo
    return out


def _cut_by_tokens(word: str, fits) -> list[str]:
    out = []
    while word:
        lo, hi = 0, len(word)  # the longest prefix that fits
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if fits(word[:mid]):
                lo = mid
            else:
                hi = mid - 1
        if lo == 0:
            raise ChunkError("the model's token budget leaves no room for text after the title and trail")
        out.append(word[:lo])
        word = word[lo:]
    return out


def _fit_label(item: Item, heading: str | None, counter: TokenCounter, half: int) -> str:
    """The item's trail, shortened until it takes at most half the budget: the middle of the path first (the first
    part and the part nearest the heading stay longest), then the end of the title, then the end of the heading."""
    title, path, head = item.title, list(item.path), heading or ""

    def label(t: str, p: list[str], h: str) -> str:
        return " › ".join([t, *p, *([h] if h else [])])

    def ok(text: str) -> bool:
        return counter.count_passages([f"{text}: "])[0] <= half

    current = label(title, path, head)
    if ok(current):
        return current
    tail = path[1:]
    while tail:
        tail.pop(0)
        path = [item.path[0], ELLIPSIS, *tail]
        current = label(title, path, head)
        if ok(current):
            return current
    for cut in (0, 2):  # the title, then the heading
        words = (title if cut == 0 else head).split()
        while len(words) > 1:
            words.pop()
            short = " ".join(words) + " " + ELLIPSIS
            title, head = (short, head) if cut == 0 else (title, short)
            current = label(title, path, head)
            if ok(current):
                return current
    return current
