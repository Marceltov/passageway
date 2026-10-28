import io
import json
import os
import subprocess
import sys

import pytest
import yaml

from snapshot import snapshot

ARTICLE = ("Backpropagation computes gradients.\n\n== History ==\nInvented early.\n\n=== Rediscovery ===\nLater.\n\n"
           "== References ==\nA citation.\n\n== Einzelnachweise ==\nNo.")


def run(wiki_server, tmp_path, out="out", **settings):
    url, _ = wiki_server
    env = {"API_URL": url, "PAGE_URL": "https://wiki.example/wiki/", "LANGUAGE": "en", "PAUSE_SECONDS": "0",
           "OUT": str(tmp_path / out), **settings}
    stdout, stderr = io.StringIO(), io.StringIO()
    code = snapshot(env, stdout, stderr, sleep=lambda s: None)
    return code, stdout.getvalue(), stderr.getvalue()


def front_matter(path):
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n")
    head, body = text[4:].split("\n---\n", 1)
    return yaml.load(head, Loader=yaml.BaseLoader), body


@pytest.fixture
def articles(wiki_server):
    _, wiki = wiki_server
    wiki.add(1, "Backpropagation", ARTICLE, revid=111, ts="2026-09-14T08:21:05Z")
    wiki.add(2, "Autoencoder", "Short.", revid=222)
    wiki.add(3, "Convolutional neural network", "A much longer article about convolutions " * 5, revid=333)
    wiki.categories["Category:Deep learning"] = {"pages": [1, 2, 3], "subcats": []}
    return wiki


def test_every_article_becomes_a_markdown_file_with_front_matter(wiki_server, articles, tmp_path):
    code, _, err = run(wiki_server, tmp_path, CATEGORIES="Deep learning")
    assert code == 0, err
    meta, body = front_matter(tmp_path / "out" / "backpropagation.md")
    assert meta == {"title": "Backpropagation", "url": "https://wiki.example/wiki/Backpropagation",
                    "updated": "2026-09-14T08:21:05Z", "language": "en", "revision": "111",
                    "license": "CC BY-SA 4.0", "source": "Wikipedia"}
    assert (tmp_path / "out" / "convolutional-neural-network.md").is_file()


def test_sections_are_markdown_headings_and_boilerplate_is_left_out(wiki_server, articles, tmp_path):
    run(wiki_server, tmp_path, CATEGORIES="Deep learning")
    _, body = front_matter(tmp_path / "out" / "backpropagation.md")
    assert body.strip() == ("Backpropagation computes gradients.\n\n## History\n\nInvented early.\n\n"
                            "### Rediscovery\n\nLater.")
    assert "References" not in body and "Einzelnachweise" not in body and "# Backpropagation" not in body


def test_a_skipped_heading_skips_its_subsections_too(wiki_server, tmp_path):
    _, wiki = wiki_server
    wiki.add(1, "A", "Lead.\n\n== Notes ==\nx\n\n=== Sub ===\ny\n\n== Keep ==\nz")
    wiki.categories["Category:C"] = {"pages": [1], "subcats": []}
    run(wiki_server, tmp_path, CATEGORIES="C", SKIP_SECTIONS="notes")
    _, body = front_matter(tmp_path / "out" / "a.md")
    assert "Sub" not in body and "## Keep" in body


def test_limit_keeps_the_longest_articles_and_names_them(wiki_server, articles, tmp_path):
    code, out, _ = run(wiki_server, tmp_path, CATEGORIES="Deep learning", LIMIT="2")
    assert code == 0
    names = {p.name for p in (tmp_path / "out").glob("*.md")}
    assert "convolutional-neural-network.md" in names and "autoencoder.md" not in names  # the shortest is dropped
    assert "Convolutional neural network" in out and "Autoencoder" not in out


def test_ties_in_length_are_broken_by_title(wiki_server, tmp_path):
    _, wiki = wiki_server
    for i, title in enumerate(["Zeta", "Alpha", "Mid"], start=1):
        wiki.add(i, title, "Same length.")
    wiki.categories["Category:C"] = {"pages": [1, 2, 3], "subcats": []}
    run(wiki_server, tmp_path, CATEGORIES="C", LIMIT="2")
    assert sorted(p.name for p in (tmp_path / "out").glob("*.md")) == ["alpha.md", "mid.md"]


def test_titles_pick_exactly_those_articles(wiki_server, articles, tmp_path):
    run(wiki_server, tmp_path, TITLES="Autoencoder|Backpropagation")
    assert sorted(p.name for p in (tmp_path / "out").glob("*.md")) == ["autoencoder.md", "backpropagation.md"]


def test_attribution_lists_every_article_with_revision_and_history(wiki_server, articles, tmp_path):
    run(wiki_server, tmp_path, CATEGORIES="Deep learning")
    text = (tmp_path / "out" / "ATTRIBUTION.txt").read_text(encoding="utf-8")
    assert "CC BY-SA 4.0" in text and "https://creativecommons.org/licenses/by-sa/4.0/" in text
    assert "Backpropagation" in text and "https://wiki.example/wiki/Backpropagation" in text
    assert "revision 111" in text and "action=history" in text and "title=Backpropagation" in text
    assert text.count("action=history") == 3


def test_it_refuses_to_overwrite_a_folder_with_files_in_it_unless_forced(wiki_server, articles, tmp_path):
    (tmp_path / "out").mkdir()
    (tmp_path / "out" / "autoencoder.md").write_text("mine")
    code, _, err = run(wiki_server, tmp_path, CATEGORIES="Deep learning")
    assert code == 2 and "FORCE" in err
    assert sorted(p.name for p in (tmp_path / "out").iterdir()) == ["autoencoder.md"]
    assert (tmp_path / "out" / "autoencoder.md").read_text() == "mine"
    code, _, _ = run(wiki_server, tmp_path, CATEGORIES="Deep learning", FORCE="1")
    assert code == 0 and (tmp_path / "out" / "autoencoder.md").read_text() != "mine"


def test_a_wiki_failure_writes_nothing(wiki_server, articles, tmp_path):
    wiki = articles
    wiki.status_errors = [500]  # not retried: 500 is not in the retry list
    code, _, err = run(wiki_server, tmp_path, CATEGORIES="Deep learning")
    assert code == 1 and err
    assert not (tmp_path / "out").exists() or list((tmp_path / "out").iterdir()) == []


def test_redirects_are_left_out(wiki_server, articles, tmp_path):
    articles.redirect_pages = {2}
    run(wiki_server, tmp_path, CATEGORIES="Deep learning")
    assert not (tmp_path / "out" / "autoencoder.md").exists()


def test_file_names_keep_letters_and_a_clash_gets_the_page_id(wiki_server, tmp_path):
    _, wiki = wiki_server
    wiki.add(10, "Künstliche Intelligenz", "Text.")
    wiki.add(11, "Künstliche  Intelligenz!", "Other text.")
    wiki.add(12, "AlphaGo: Zero", "Third.")
    wiki.categories["Category:C"] = {"pages": [10, 11, 12], "subcats": []}
    run(wiki_server, tmp_path, CATEGORIES="C", LANGUAGE="de")
    names = sorted(p.name for p in (tmp_path / "out").glob("*.md"))
    assert names == ["alphago-zero.md", "künstliche-intelligenz-11.md", "künstliche-intelligenz.md"]
    meta, _ = front_matter(tmp_path / "out" / "alphago-zero.md")  # a colon in the title survives the YAML
    assert meta["title"] == "AlphaGo: Zero" and meta["language"] == "de"


@pytest.mark.parametrize("settings,message", [
    ({"OUT": ""}, "OUT"),
    ({"LIMIT": "many"}, "LIMIT"),
    ({"LIMIT": "0"}, "LIMIT"),
    ({"CATEGORIES": ""}, "CATEGORIES"),  # no scope at all
])
def test_bad_settings_exit_2_and_write_nothing(wiki_server, articles, tmp_path, settings, message):
    base = {"CATEGORIES": "Deep learning", **settings}
    code, out, err = run(wiki_server, tmp_path, **base)
    assert code == 2 and message in err and not (tmp_path / "out").exists()


def test_the_files_are_what_the_markdown_connector_indexes(wiki_server, articles, tmp_path):
    run(wiki_server, tmp_path, CATEGORIES="Deep learning")
    out = subprocess.run([sys.executable, "-m", "passageway_connector_markdown", "fetch"],
                         env={**os.environ, "FOLDER": str(tmp_path / "out")}, input='{"id": "backpropagation.md"}\n',
                         capture_output=True, text=True, check=True).stdout
    item = json.loads(out)
    assert item["title"] == "Backpropagation" and item["url"] == "https://wiki.example/wiki/Backpropagation"
    assert item["updated"] == "2026-09-14T08:21:05Z"
    assert [(s["heading"], s["text"]) for s in item["sections"]] == [
        (None, "Backpropagation computes gradients."), ("History", "Invented early."),
        ("History › Rediscovery", "Later.")]
    listed = subprocess.run([sys.executable, "-m", "passageway_connector_markdown", "list"],
                            env={**os.environ, "FOLDER": str(tmp_path / "out")}, capture_output=True, text=True,
                            check=True).stdout
    assert "ATTRIBUTION" not in listed  # the attribution file is .txt: not indexed as a note


# ---- review findings ------------------------------------------------------------------------------

MATH = ("Backpropagation takes an input\n\n  \n    \n      \n        x\n      \n    \n    {\\displaystyle x}\n  \n"
        ": input (vector of features), and an output\n\n  \n    \n      \n        y\n      \n"
        "        ⁢\n        z\n    \n    {\\displaystyle yz}\n  \nof the network.")


def test_a_mathml_token_block_becomes_its_tex_between_dollar_signs():
    from snapshot import to_markdown
    out = to_markdown(MATH, frozenset())
    assert out == ("Backpropagation takes an input\n\n$x$\n\n: input (vector of features), and an output\n\n$yz$\n\nof the network.")


def test_invisible_operators_are_removed_and_other_indented_text_is_kept():
    from snapshot import to_markdown
    out = to_markdown("A⁡B and\n\n  an indented quote\n  second line\n\nend", frozenset())
    assert out == "AB and\n\n  an indented quote\n  second line\n\nend"


def test_a_display_style_formula_line_without_a_token_block_is_kept_as_tex():
    from snapshot import to_markdown
    assert to_markdown("Energy\n    {\\displaystyle E=mc^{2}}\nis", frozenset()) == "Energy\n$E=mc^{2}$\nis"


def test_a_folder_that_is_not_empty_is_refused_without_force_before_any_request(wiki_server, articles, tmp_path):
    (tmp_path / "out").mkdir()
    (tmp_path / "out" / "ATTRIBUTION.txt").write_text("precious")
    before = len(articles.requests)
    code, _, err = run(wiki_server, tmp_path, TITLES="Autoencoder")
    assert code == 2 and "FORCE" in err and "not empty" in err
    assert len(articles.requests) == before  # nothing was fetched
    assert (tmp_path / "out" / "ATTRIBUTION.txt").read_text() == "precious"


def test_force_replaces_the_whole_folder_so_no_stale_articles_stay(wiki_server, articles, tmp_path):
    run(wiki_server, tmp_path, TITLES="Autoencoder|Backpropagation")
    code, _, err = run(wiki_server, tmp_path, TITLES="Backpropagation", FORCE="1")
    assert code == 0, err
    assert sorted(p.name for p in (tmp_path / "out").iterdir()) == ["ATTRIBUTION.txt", "backpropagation.md", "titles.txt"]
    assert (tmp_path / "out" / "ATTRIBUTION.txt").read_text().count("action=history") == 1


def test_a_failing_forced_run_leaves_the_old_folder_untouched(wiki_server, articles, tmp_path):
    run(wiki_server, tmp_path, TITLES="Autoencoder")
    articles.status_errors = [500]
    code, _, _ = run(wiki_server, tmp_path, TITLES="Backpropagation", FORCE="1")
    assert code == 1 and (tmp_path / "out" / "autoencoder.md").is_file()
    assert not (tmp_path / "out.tmp").exists()


def test_out_that_is_a_file_is_a_settings_error(wiki_server, articles, tmp_path):
    (tmp_path / "out").write_text("a file")
    code, _, err = run(wiki_server, tmp_path, TITLES="Autoencoder", FORCE="1")
    assert code == 2 and "OUT" in err


def test_the_chosen_titles_are_written_one_per_line(wiki_server, articles, tmp_path):
    run(wiki_server, tmp_path, CATEGORIES="Deep learning")
    assert (tmp_path / "out" / "titles.txt").read_text(encoding="utf-8").splitlines() == [
        "Autoencoder", "Backpropagation", "Convolutional neural network"]


def test_the_attribution_says_what_was_removed(wiki_server, articles, tmp_path):
    run(wiki_server, tmp_path, TITLES="Autoencoder")
    text = (tmp_path / "out" / "ATTRIBUTION.txt").read_text(encoding="utf-8")
    for word in ("tables", "images", "infoboxes", "formulas"):
        assert word in text.casefold()


def test_a_formula_block_with_empty_lines_between_its_tokens_is_one_formula():
    from snapshot import to_markdown
    block = "text\n\n        D\n        :\n\n            E\n\n        ]\n\n    {\\displaystyle D:E]}\n  \nmore"
    assert to_markdown(block, frozenset()) == "text\n\n$D:E]$\n\nmore"


def test_a_text_line_with_a_single_leading_space_is_not_part_of_a_formula_block():
    from snapshot import to_markdown
    text = "against any\n$\\mu$\n\n is deterministic, so there is no loss of generality\n\n        D\n        :\n\n    {\\displaystyle D:}\n  \n. Next"
    assert to_markdown(text, frozenset()) == ("against any\n$\\mu$\n\n is deterministic, so there is no loss of generality\n\n"
                                              "$D:$\n\n. Next")
