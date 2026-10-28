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
