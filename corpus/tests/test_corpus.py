"""The committed corpus stays what its README and licence say it is."""

import re
import sys
from pathlib import Path

import pytest
import yaml

from passageway.protocol import Connector
from passageway.testing.contract import check_connector

CORPUS = Path(__file__).resolve().parents[1]
LANGUAGES = {"en": "https://en.wikipedia.org/wiki/", "de": "https://de.wikipedia.org/wiki/"}


def articles(language):
    return sorted((CORPUS / language).glob("*.md"))


def front_matter(path):
    head, body = path.read_text(encoding="utf-8")[4:].split("\n---\n", 1)
    return yaml.load(head, Loader=yaml.BaseLoader), body


@pytest.mark.parametrize("language", LANGUAGES)
def test_thirty_articles_per_language_each_with_its_source_and_licence(language):
    files = articles(language)
    assert len(files) == 30
    titles = set()
    for path in files:
        meta, body = front_matter(path)
        assert meta["language"] == language and meta["source"] == "Wikipedia" and meta["license"] == "CC BY-SA 4.0"
        assert meta["url"].startswith(LANGUAGES[language]) and re.fullmatch(r"\d+", meta["revision"]), path.name
        assert re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", meta["updated"]), path.name
        assert len(body.strip()) > 500, f"{path.name} has hardly any text"
        assert not re.search(r"^## (References|External links|Einzelnachweise|Weblinks|Literatur|Siehe auch)\b", body, re.M | re.I)
        titles.add(meta["title"])
    assert len(titles) == 30


@pytest.mark.parametrize("language", LANGUAGES)
def test_the_attribution_names_every_article_with_revision_and_history(language):
    text = (CORPUS / language / "ATTRIBUTION.txt").read_text(encoding="utf-8")
    assert "CC BY-SA 4.0" in text and "https://creativecommons.org/licenses/by-sa/4.0/" in text
    for path in articles(language):
        meta, _ = front_matter(path)
        assert f"{meta['url']} (revision {meta['revision']}," in text, f"{path.name} is missing from the attribution"
    assert text.count("action=history") == 30


def test_the_licence_and_readme_say_what_the_files_are():
    licence = (CORPUS / "LICENSE.md").read_text()
    assert "CC BY-SA 4.0" in licence and "AGPL" in licence and "Changes made" in licence
    assert "deep learning" in (CORPUS / "README.md").read_text()


@pytest.mark.parametrize("language", LANGUAGES)
def test_the_markdown_connector_indexes_each_folder_and_not_the_attribution_file(language):
    connector = Connector(language, [sys.executable, "-m", "passageway_connector_markdown"],
                          env={"FOLDER": str(CORPUS / language)})
    check_connector(connector)
    ids = list(connector.list_versions())
    assert len(ids) == 30 and not any("ATTRIBUTION" in i for i in ids)
    items = connector.fetch(ids)
    assert all(item.sections for item in items)


def test_the_corpus_stays_small_enough_to_live_in_the_repository():
    total = sum(p.stat().st_size for p in CORPUS.rglob("*") if p.is_file() and "tests" not in p.parts)
    assert total < 4 * 1024 * 1024
