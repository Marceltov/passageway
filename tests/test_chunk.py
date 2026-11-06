from passageway.chunk import MAX_CHARS, chunks, passage_text, split_text
from passageway.protocol import Item, Section


def item(*sections, path=()):
    return Item("a", "Title", "u", "1", tuple(sections), path=path)


def test_short_text_is_one_piece():
    assert split_text("hello") == ["hello"] and split_text("  \n ") == []


def test_long_text_splits_at_paragraphs_within_the_cap():
    paras = ["word " * 150 for _ in range(4)]  # 750 chars each
    pieces = split_text("\n\n".join(p.strip() for p in paras))
    assert len(pieces) == 2 and all(len(p) <= MAX_CHARS for p in pieces)


def test_one_huge_paragraph_and_one_huge_word_are_cut():
    pieces = split_text("w" * (MAX_CHARS * 2 + 10))
    assert all(len(p) <= MAX_CHARS for p in pieces) and "".join(pieces) == "w" * (MAX_CHARS * 2 + 10)
    assert all(len(p) <= MAX_CHARS for p in split_text("lorem ipsum " * 400))


def test_chunks_numbers_pieces_and_skips_empty_sections():
    out = chunks(item(Section("A", "x"), Section(None, "  "), Section("B", "y")))
    assert [(c.heading, c.text, c.ordinal) for c in out] == [("A", "x", 0), ("B", "y", 1)]


def test_item_without_sections_has_no_chunks():
    assert chunks(item()) == []


def test_passage_text_joins_title_path_heading():
    it = item(Section("Steps", "do it"), path=("Ops", "Sec"))
    assert passage_text(it, chunks(it)[0]) == "Title › Ops › Sec › Steps: do it"
    plain = item(Section(None, "do it"))
    assert passage_text(plain, chunks(plain)[0]) == "Title: do it"


# ---- chunking by tokens -------------------------------------------------------------------

import math

import pytest

from passageway.chunk import ChunkError


class Words:
    """Counts like a model: one token per word, plus `overhead` for the passage prefix and special tokens."""

    def __init__(self, max_tokens: int, overhead: int = 3):
        self.max_tokens, self.overhead = max_tokens, overhead

    def count_passages(self, texts):
        return [len(t.split()) + self.overhead for t in texts]


class Chars:
    """One token per four characters: a long word costs more than one token."""

    def __init__(self, max_tokens: int):
        self.max_tokens = max_tokens

    def count_passages(self, texts):
        return [math.ceil(len(t) / 4) + 2 for t in texts]


def words(n, stem="w"):
    return " ".join(f"{stem}{i}" for i in range(n))


def fits(it, counter):
    out = chunks(it, counter)
    return out, [counter.count_passages([passage_text(it, c)])[0] for c in out]


def test_a_short_section_stays_one_piece():
    it = item(Section("Steps", "do it now"))
    out, _ = fits(it, Words(50))
    assert [c.text for c in out] == ["do it now"] and passage_text(it, out[0]) == "Title › Steps: do it now"


def test_every_passage_fits_and_no_word_is_lost():
    text = "\n\n".join(words(30, f"p{p}w") for p in range(5))
    it = item(Section("H", text), path=("Ops",))
    out, counts = fits(it, Words(40))
    assert len(out) > 1 and max(counts) <= 40
    assert " ".join(c.text for c in out).split() == text.split()


def test_paragraphs_are_kept_whole_when_they_fit():
    a, b = words(20, "a"), words(20, "b")
    it = item(Section(None, f"{a}\n\n{b}"))
    out, _ = fits(it, Words(30))
    assert [c.text for c in out] == [a, b]


def test_a_long_paragraph_is_cut_at_lines_then_sentences_before_words():
    lines = f"{words(15, 'x')}\n{words(15, 'y')}"
    out, _ = fits(item(Section(None, lines)), Words(25))
    assert [c.text for c in out] == [words(15, "x"), words(15, "y")]
    sentences = f"{words(15, 'x')}. {words(15, 'y')}."
    out, _ = fits(item(Section(None, sentences)), Words(25))
    assert [c.text for c in out] == [words(15, "x") + ".", words(15, "y") + "."]


def test_a_word_longer_than_the_budget_is_cut_by_tokens():
    word = "z" * 3000
    it = item(Section(None, word))
    out, counts = fits(it, Chars(200))
    assert len(out) > 1 and max(counts) <= 200 and "".join(c.text for c in out) == word


def test_a_long_trail_is_shortened_to_half_the_budget_keeping_its_ends():
    path = ("Act", *[f"Part {i} " + words(10, f"p{i}") for i in range(6)])
    it = Item("a", "Title " + words(5, "t"), "u", "1", (Section("§ 1 Heading", words(200)),), path=path)
    counter = Words(100)
    out, counts = fits(it, counter)
    label = out[0].label
    assert counter.count_passages([label + ": "])[0] <= 50 and max(counts) <= 100
    assert label.startswith("Title t0") and label.endswith("§ 1 Heading") and "› … ›" in label and "Act" in label
    assert " ".join(c.text for c in out).split() == words(200).split()


def test_a_title_too_long_on_its_own_loses_its_end():
    it = Item("a", "Title " + words(120, "t"), "u", "1", (Section("Head", words(10)),))
    counter = Words(100)
    out, counts = fits(it, counter)
    assert counter.count_passages([out[0].label + ": "])[0] <= 50 and max(counts) <= 100
    assert out[0].label.startswith("Title t0") and "…" in out[0].label


def test_without_a_token_count_the_character_cap_applies():
    class NoCount:
        max_tokens = None

    it = item(Section(None, "lorem ipsum " * 400))
    assert [c.text for c in chunks(it, NoCount())] == [c.text for c in chunks(it)]
    assert all(len(c.text) <= MAX_CHARS for c in chunks(it))


def test_a_budget_too_small_for_any_text_is_an_error():
    with pytest.raises(ChunkError, match="budget"):
        chunks(item(Section(None, "some text")), Words(3, overhead=3))
