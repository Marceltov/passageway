"""The public question set stays what its header says it is."""

import collections
import re
from pathlib import Path

import pytest

from passageway.eval.cases import load_cases

CORPUS = Path(__file__).resolve().parents[1]
CASES, TARGETS = load_cases(CORPUS / "questions.toml")
ANSWERABLE = [c for c in CASES if c.answerable]
GERMAN = {"was", "wie", "der", "die", "das", "ein", "eine", "und", "ist", "mit", "wird", "um", "im", "zu", "wofür", "warum",
          "welche", "ich", "einen", "dem", "den", "des", "auf", "bei", "von", "nach"}
ENGLISH = {"what", "how", "the", "a", "is", "of", "and", "to", "in", "does", "do", "are", "that", "so", "can", "it", "its", "i",
           "an", "one", "on", "by", "for", "with"}


def is_german(query: str) -> bool:
    words = re.findall(r"\w+", query.casefold())
    return sum(w in GERMAN for w in words) > sum(w in ENGLISH for w in words)


def test_a_hundred_questions_seventy_with_answers_and_thirty_without():
    assert len(CASES) == 100 and len(ANSWERABLE) == 70
    assert not TARGETS  # targets are a gate for one's own CI, not part of a published set


def test_the_groups_are_the_documented_ones_with_the_documented_sizes():
    groups = collections.Counter(c.group for c in CASES)
    assert set(groups) == {"definition", "how-why", "paraphrase", "cross-language", "near-topic", "off-topic"}
    assert groups["near-topic"] == groups["off-topic"] == 15
    assert all(c.group in {"near-topic", "off-topic"} for c in CASES if not c.answerable)
    assert all(c.group not in {"near-topic", "off-topic"} for c in ANSWERABLE)
    assert min(groups["definition"], groups["how-why"], groups["paraphrase"], groups["cross-language"]) >= 12


def test_queries_are_unique_and_plain_text():
    queries = [c.query for c in CASES]
    assert len(set(queries)) == 100 and all(10 < len(q) < 200 for q in queries)


def test_the_answers_are_exact_ids_of_articles_that_exist():
    existing = {p.name for lang in ("en", "de") for p in (CORPUS / lang).glob("*.md")}
    for case in ANSWERABLE:
        assert not case.expect and case.expect_id, case.query
        assert set(case.expect_id) <= existing, f"{case.query!r} names a file that is not in the corpus"
        assert len(set(case.expect_id)) == len(case.expect_id)


def test_no_question_names_a_language_or_a_source():
    for case in CASES:
        assert not re.search(r"\b(english|german|englisch|deutsch|wikipedia|corpus|korpus|source|quelle)\b", case.query, re.I), case.query


def test_both_languages_are_asked_in_both_kinds():
    german = [c for c in ANSWERABLE if is_german(c.query)]
    english = [c for c in ANSWERABLE if not is_german(c.query)]
    assert 28 <= len(german) <= 42 and 28 <= len(english) <= 42, (len(german), len(english))
    unanswerable = [c for c in CASES if not c.answerable]
    assert 10 <= sum(is_german(c.query) for c in unanswerable) <= 20


def test_a_cross_language_answer_exists_in_one_language_only():
    en = {p.name for p in (CORPUS / "en").glob("*.md")}
    de = {p.name for p in (CORPUS / "de").glob("*.md")}
    for case in (c for c in ANSWERABLE if c.group == "cross-language"):
        for item_id in case.expect_id:
            assert (item_id in en) != (item_id in de), f"{item_id} is in both languages: not a cross-language answer"
        in_en = any(i in en for i in case.expect_id)
        assert is_german(case.query) == in_en, f"{case.query!r}: the answer must be in the other language than the question"
