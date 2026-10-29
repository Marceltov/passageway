"""The public question set stays what its header says it is."""

import collections
import re
from pathlib import Path

import pytest
import yaml

from passageway.eval.cases import load_cases

CORPUS = Path(__file__).resolve().parents[1]
CASES, TARGETS = load_cases(CORPUS / "questions.toml")
ANSWERABLE = [c for c in CASES if c.answerable]
GERMAN = {"was", "wie", "der", "die", "das", "ein", "eine", "und", "ist", "mit", "wird", "um", "im", "zu", "wofür", "warum",
          "welche", "ich", "einen", "dem", "den", "des", "auf", "bei", "von", "nach", "es", "gibt", "sich"}
ENGLISH = {"what", "how", "the", "a", "is", "of", "and", "does", "do", "are", "that", "it", "its", "an", "one", "why", "who",
           "can", "i", "my", "to"}

# A cross-language question has its only good article in the other language. For each one: words that must not be part of
# a heading in the other language's folder (a section about the topic would be an explanation there).
AUDIT = {
    "Was ist Batch-Normalisierung?": ["batch norm", "batch-norm", "batchnorm"],
    "Wie funktioniert ein Diffusionsmodell?": ["diffusion"],
    "Was ist ein Residual Network?": ["residual"],
    "Was sind Hyperparameter?": ["hyperparam"],
    "What is a Boltzmann machine?": ["boltzmann"],
    "What is a self-organizing map?": ["self-organi", "self organi", "kohonen"],
    "What is model collapse when models are trained on AI-generated data?": ["model collapse"],
}


def is_german(query: str) -> bool:
    words = re.findall(r"\w+", query.casefold())
    umlauts = 2 * sum(ch in "äöüß" for ch in query)
    return sum(w in GERMAN for w in words) + umlauts > sum(w in ENGLISH for w in words)


def front_matter(path: Path) -> dict:
    head = path.read_text(encoding="utf-8")[4:].split("\n---\n", 1)[0]
    return yaml.load(head, Loader=yaml.BaseLoader)


def test_a_hundred_questions_seventy_with_answers_and_thirty_without():
    assert len(CASES) == 100 and len(ANSWERABLE) == 70
    assert not TARGETS  # targets are a gate for one's own CI, not part of a published set


def test_the_groups_are_the_documented_ones_with_the_documented_sizes():
    assert dict(collections.Counter(c.group for c in CASES)) == {
        "definition": 25, "how-why": 20, "paraphrase": 18, "cross-language": 7, "near-topic": 15, "off-topic": 15}
    assert all(c.group in {"near-topic", "off-topic"} for c in CASES if not c.answerable)
    assert all(c.group not in {"near-topic", "off-topic"} for c in ANSWERABLE)


def test_queries_are_unique_and_plain_text():
    queries = [c.query for c in CASES]
    assert len(set(queries)) == 100 and all(10 < len(q) < 200 for q in queries)


def test_the_answers_are_files_or_addresses_of_articles_that_exist():
    files = {p.name for lang in ("en", "de") for p in (CORPUS / lang).glob("*.md")}
    urls = [front_matter(p)["url"] for lang in ("en", "de") for p in (CORPUS / lang).glob("*.md")]
    for case in ANSWERABLE:
        assert case.expect_id, case.query
        assert set(case.expect_id) <= files, f"{case.query!r} names a file that is not in the corpus"
        assert len(set(case.expect_id)) == len(case.expect_id)
        for entry in case.expect:  # an address fragment, to accept one language's article of a shared file name
            assert any(entry in url for url in urls), f"{case.query!r}: {entry!r} is not part of an article's address"


def test_no_question_names_a_language_or_a_source():
    for case in CASES:
        assert not re.search(r"\b(english|german|englisch|deutsch|wikipedia|corpus|korpus|source|quelle)\b", case.query, re.I), case.query


def test_both_languages_are_asked_in_both_kinds():
    german = [c for c in ANSWERABLE if is_german(c.query)]
    english = [c for c in ANSWERABLE if not is_german(c.query)]
    assert 28 <= len(german) <= 42 and 28 <= len(english) <= 42, (len(german), len(english))
    unanswerable = [c for c in CASES if not c.answerable]
    assert 12 <= sum(is_german(c.query) for c in unanswerable) <= 20


def test_a_cross_language_answer_exists_in_the_other_language_only():
    en = {p.name for p in (CORPUS / "en").glob("*.md")}
    de = {p.name for p in (CORPUS / "de").glob("*.md")}
    cross = [c for c in ANSWERABLE if c.group == "cross-language"]
    assert {c.query for c in cross} == set(AUDIT), "every cross-language question needs its audit words in this test"
    for case in cross:
        for item_id in case.expect_id:
            assert (item_id in en) != (item_id in de), f"{item_id} is in both languages: not a cross-language answer"
        answer_in_en = any(i in en for i in case.expect_id) or any("en.wikipedia.org" in e for e in case.expect)
        assert is_german(case.query) == answer_in_en, f"{case.query!r}: the answer must be in the other language"


@pytest.mark.parametrize("query", sorted(AUDIT))
def test_the_questions_own_language_has_no_section_about_a_cross_language_topic(query):
    # the answer is in the other language, so the folder to audit is the one in the language of the question
    audited = CORPUS / ("de" if is_german(query) else "en")
    for path in sorted(audited.glob("*.md")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("#"):
                assert not any(w in line.casefold() for w in AUDIT[query]), f"{path.name} has a section {line!r} about this topic"
