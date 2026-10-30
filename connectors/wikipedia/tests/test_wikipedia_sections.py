from passageway_connector_wikipedia.sections import DEFAULT_SKIP, split_sections

TEXT = """Heligoland is an island.

== History ==
Settled early.

=== 19th century ===
British until 1890.

== Geography ==

=== Climate ===
Maritime.

== See also ==
Other islands.

== References ==
A citation.

=== Notes ===
A footnote.
"""


def test_lead_and_nested_headings():
    out = split_sections(TEXT, DEFAULT_SKIP)
    assert out[0] == {"heading": None, "text": "Heligoland is an island."}
    assert {"heading": "History", "text": "Settled early."} in out
    assert {"heading": "History › 19th century", "text": "British until 1890."} in out
    assert {"heading": "Geography › Climate", "text": "Maritime."} in out


def test_empty_sections_and_boilerplate_with_their_subsections_are_dropped():
    headings = [s["heading"] for s in split_sections(TEXT, DEFAULT_SKIP)]
    assert "Geography" not in headings  # no body of its own
    assert not any(h and ("See also" in h or "References" in h or "Notes" in h) for h in headings)


def test_skip_none_keeps_everything_and_german_boilerplate_is_skipped_by_default():
    assert any(s["heading"] == "See also" for s in split_sections(TEXT, frozenset()))
    de = "Einleitung.\n\n== Geschichte ==\nAlt.\n\n== Einzelnachweise ==\nBeleg."
    assert [s["heading"] for s in split_sections(de, DEFAULT_SKIP)] == [None, "Geschichte"]


def test_no_text_means_no_sections():
    assert split_sections("", DEFAULT_SKIP) == [] and split_sections("  \n ", DEFAULT_SKIP) == []


def test_formulas_are_indexed_as_their_tex_without_the_mathml_tokens():
    extract = ("A right triangle has\n\n  \n    \n      \n        a\n        2\n      \n      +\n        c\n      \n"
               "    \n    {\\displaystyle a^{2}+c}\n  \nas its sides.\n\n== Proof ==\nf⁡x holds.")
    assert split_sections(extract, frozenset()) == [
        {"heading": None, "text": "A right triangle has\n\n$a^{2}+c$\n\nas its sides."},
        {"heading": "Proof", "text": "fx holds."}]
