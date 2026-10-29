import re

import pytest

from passageway.eval.cases import Case, CasesError, load_cases, matches
from passageway.rank import Hit


def write(tmp_path, text):
    path = tmp_path / "cases.toml"
    path.write_text(text)
    return path


def hit(title="Backpropagation", heading="History", url="https://en.wikipedia.org/wiki/Backpropagation", item_id="backpropagation.md"):
    return Hit("corpus-en", item_id, title, url, [], [], heading, "passage", 1.0, [])


def test_cases_and_targets_are_loaded(tmp_path):
    cases, targets = load_cases(write(tmp_path, '''
[targets]
hit_at_3 = 0.8
p95_ms = 300

[[case]]
query = "what is backpropagation"
expect = ["Backpropagation", "Backprop"]
group = "ml"

[[case]]
query = "exact"
expect_id = ["a.md"]

[[case]]
query = "what is on the cafeteria menu"
'''))
    assert targets == {"hit_at_3": 0.8, "p95_ms": 300.0}
    assert cases == [Case("what is backpropagation", ("Backpropagation", "Backprop"), (), "ml"),
                     Case("exact", (), ("a.md",), None),
                     Case("what is on the cafeteria menu", (), (), None)]
    assert [c.answerable for c in cases] == [True, True, False]


@pytest.mark.parametrize("text,message", [
    ("", "no [[case]]"),
    ('[[case]]\nexpect = ["x"]', "query"),
    ('[[case]]\nquery = ""', "query"),
    ('[[case]]\nquery = 5', "query"),
    ('[[case]]\nquery = "q"\nexpect = "x"', "expect"),
    ('[[case]]\nquery = "q"\nexpect = [1]', "expect"),
    ('[[case]]\nquery = "q"\nexpect = [""]', "expect"),
    ('[[case]]\nquery = "q"\nexpect_id = "a"', "expect_id"),
    ('[[case]]\nquery = "q"\ngroup = 3', "group"),
    ('[[case]]\nquery = "q"\nexpet = ["typo"]', "expet"),
    ('[[case]]\nquery = "q"\n[targets]\nhit_at_9 = 1', "hit_at_9"),
    ('[[case]]\nquery = "q"\n[targets]\nhit_at_3 = "high"', "hit_at_3"),
    ('[[case]]\nquery = "q"\n[targets]\nhit_at_3 = 1.5', "hit_at_3"),
    ('[[case]]\nquery = "q"\n[targets]\np95_ms = -1', "p95_ms"),
    ('[[case]]\nquery = "q"\n[surprise]\nx = 1', "surprise"),
    ("this is not toml", "cases.toml"),
])
def test_a_bad_cases_file_is_refused_with_a_message_that_names_the_problem(tmp_path, text, message):
    with pytest.raises(CasesError, match=re.escape(message)):
        load_cases(write(tmp_path, text))


def test_a_missing_file_is_a_cases_error(tmp_path):
    with pytest.raises(CasesError, match="not found"):
        load_cases(tmp_path / "nope.toml")


def test_the_second_case_is_named_in_the_error(tmp_path):
    with pytest.raises(CasesError, match="case 2"):
        load_cases(write(tmp_path, '[[case]]\nquery = "ok"\n\n[[case]]\nquery = ""'))


def test_expect_matches_title_heading_or_url_ignoring_case():
    case = Case("q", ("backpropagation",), (), None)
    assert matches(hit(), case)
    assert matches(hit(title="Other", heading="Backpropagation in practice", url="http://x"), case)
    assert matches(hit(title="Other", heading="H", url="https://x/wiki/BACKPROPAGATION"), case)
    assert not matches(hit(title="Other", heading="H", url="http://x"), case)


def test_the_title_is_matched_as_a_substring():
    assert matches(hit(title="Long short-term memory"), Case("q", ("short-term",), (), None))


def test_expect_id_matches_the_exact_id_only():
    case = Case("q", (), ("backpropagation.md",), None)
    assert matches(hit(), case)
    assert not matches(hit(item_id="backpropagation.md.bak"), case)
    assert not matches(hit(item_id="x/backpropagation.md"), case)


def test_either_kind_of_entry_accepts_a_hit():
    case = Case("q", ("nothing like this",), ("backpropagation.md",), None)
    assert matches(hit(), case)
