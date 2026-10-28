from passageway_sdk import split_markdown, strip_code


def sections(text, **kw):
    return [(s["heading"], s["text"]) for s in split_markdown(text, **kw)]


def test_text_before_the_first_heading_is_a_section_without_heading():
    assert sections("Intro text.\n\n## Setup\nInstall it.") == [(None, "Intro text."), ("Setup", "Install it.")]


def test_the_heading_is_the_trail_of_its_parents():
    text = "# Guide\n\n## Setup\nA\n\n### Linux\nB\n\n### Mac\nC\n\n## Usage\nD"
    assert sections(text) == [("Guide › Setup", "A"), ("Guide › Setup › Linux", "B"),
                              ("Guide › Setup › Mac", "C"), ("Guide › Usage", "D")]


def test_the_first_h1_can_be_left_out_because_it_is_the_title():
    text = "# Guide\nIntro.\n\n## Setup\nA\n\n# Second\nB"
    assert sections(text, skip_first_h1=True) == [(None, "Intro."), ("Setup", "A"), ("Second", "B")]


def test_a_level_can_be_skipped_and_a_shallower_heading_resets_the_trail():
    assert sections("## A\nx\n\n##### Deep\ny\n\n## B\nz") == [("A", "x"), ("A › Deep", "y"), ("B", "z")]


def test_headings_without_text_are_dropped_but_stay_in_the_trail():
    assert sections("## A\n### B\ntext") == [("A › B", "text")]


def test_a_hash_inside_a_fenced_code_block_is_not_a_heading():
    text = "## Setup\n```bash\n# install\nmake\n```\nAfter.\n\n~~~\n## also not\n~~~\n"
    assert sections(text) == [("Setup", "```bash\n# install\nmake\n```\nAfter.\n\n~~~\n## also not\n~~~")]


def test_a_longer_fence_is_not_closed_by_a_shorter_one():
    text = "## A\n````\n```\n## inside\n```\n````\nend"
    assert sections(text) == [("A", "````\n```\n## inside\n```\n````\nend")]


def test_heading_syntax_rules():
    assert sections("#NoSpace\ntext") == [(None, "#NoSpace\ntext")]  # needs a space
    assert sections("####### seven\ntext") == [(None, "####### seven\ntext")]
    assert sections("## Closed ##\ntext") == [("Closed", "text")]
    assert sections("   ## Indented up to three\ntext") == [("Indented up to three", "text")]
    assert sections("    ## four spaces is code\ntext") == [(None, "## four spaces is code\ntext")]  # not a heading


def test_empty_input_has_no_sections():
    assert split_markdown("") == [] and split_markdown("\n\n  \n") == []


def test_strip_code_removes_fenced_blocks_and_inline_code():
    text = "See [a](a.md).\n```\n[b](b.md)\n```\nand `[c](c.md)` but [d](d.md)."
    out = strip_code(text)
    assert "a.md" in out and "d.md" in out and "b.md" not in out and "c.md" not in out


def test_first_h1_is_the_first_level_one_heading_outside_code():
    from passageway_sdk import first_h1
    assert first_h1("intro\n\n# Real title\n\n# Second") == "Real title"
    assert first_h1("```\n# not a title\n```\n## Sub\n# Title `with code` ##") == "Title `with code`"
    assert first_h1("## Only a sub heading") is None and first_h1("") is None


def test_a_first_h1_that_comes_after_other_headings_resets_the_trail_when_skipped():
    assert sections("## Setup\nx\n# Appendix\ny\n## A\nz", skip_first_h1=True) == [("Setup", "x"), (None, "y"), ("A", "z")]


def test_strip_code_handles_spans_that_contain_a_backtick():
    assert "e.md" in strip_code("x ``a`b`` [`f()`](e.md)")
    out = strip_code("a ``x ` [c](d.md)`` b")
    assert "d.md" not in out and out.startswith("a") and out.endswith("b")


def test_a_backtick_fence_whose_info_string_has_a_backtick_is_not_a_fence():
    assert sections("```foo`bar\n## B\ntext") == [(None, "```foo`bar"), ("B", "text")]
