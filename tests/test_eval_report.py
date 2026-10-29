import json
import platform

import pytest

from passageway.eval.cases import Case
from passageway.eval.report import ReportError, build_report, machine_line, render_markdown, write_block
from passageway.eval.run import CaseResult
from passageway.rank import Hit

SECRET = ["zebrafish", "quokka", "narwhal"]  # words that only the questions, titles and URLs contain


def hit(title="A quokka article", heading="The narwhal section", url="https://wiki.example/quokka", item_id="q.md"):
    return Hit("notes", item_id, title, url, [], [], heading, "passage", 1.0, [])


def results():
    answered = Case("what is a zebrafish", ("quokka",), (), "animals")
    silent = Case("zebrafish cafeteria menu", (), (), "animals")
    return [CaseResult(answered, [hit()], 1, 12.5, 4.0), CaseResult(silent, [], None, 8.0, 3.0),
            CaseResult(Case("missed", ("narwhal",), (), None), [], None, 9.0, 3.0)]


RUN = {"date": "2026-10-29T10:00:00Z", "passageway": "0.1.0", "embedder": "hash-test", "dim": 384, "threshold": 0.845,
       "machine": "Darwin arm64, Python 3.14.3", "index_seconds": 1.5,
       "sources": {"notes": {"items": 3, "sections": 7}}}


def report(**kw):
    args = {"run": RUN, "results": results(), "targets": {"hit_at_3": 0.5, "silence": 1.0}, "sweep": None,
            "include_cases": False}
    return build_report(**{**args, **kw})


def test_the_report_has_the_run_the_metrics_the_groups_and_the_targets():
    r = report()
    assert r["schema"] == 1 and r["run"] == RUN
    assert r["metrics"]["cases"] == 3 and r["metrics"]["hit_at_3"] == 0.5
    assert r["groups"]["animals"]["cases"] == 2
    assert [(t["name"], t["passed"]) for t in r["targets"]] == [("hit_at_3", True), ("silence", True)]
    assert "sweep" not in r and "cases" not in r


def test_a_sweep_adds_one_row_of_metrics_per_threshold():
    sweep = [(0.80, results()), (0.90, results()[:2])]
    r = report(sweep=sweep)
    assert [row["threshold"] for row in r["sweep"]] == [0.80, 0.90]
    assert r["sweep"][1]["metrics"]["cases"] == 2


def test_an_aggregate_report_holds_no_question_title_heading_or_url():
    r = report(sweep=[(0.8, results())])
    text = json.dumps(r) + render_markdown(r)
    for word in SECRET:
        assert word not in text.lower(), f"{word!r} leaked into an aggregate-only report"
    assert "https://wiki.example" not in text


def test_with_cases_the_report_quotes_them_and_that_is_the_only_difference():
    r = report(include_cases=True)
    text = json.dumps(r) + render_markdown(r)
    assert "zebrafish" in text and "quokka" in text
    assert r["cases"][0] == {"query": "what is a zebrafish", "group": "animals", "expect": ["quokka"], "expect_id": [],
                             "rank": 1, "ms": 12.5, "hits": [{"title": "A quokka article", "heading": "The narwhal section"}]}
    plain = report()
    assert {k: v for k, v in r.items() if k != "cases"} == plain


def test_the_markdown_has_readable_tables_and_n_a_for_what_was_not_measured():
    md = render_markdown(report(targets={"hit_at_3": 0.9}))
    assert md.startswith("# Retrieval evaluation")
    assert "hash-test" in md and "0.845" in md and "Darwin arm64, Python 3.14.3" in md
    assert "50.0%" in md and "12.5 ms" in md  # shares as percentages, latency in milliseconds
    assert "fail" in md.lower() and "hit_at_3" in md
    only_answerable = render_markdown(report(results=results()[:1], targets={}))
    assert "n/a" in only_answerable  # silence has no unanswerable question behind it


def test_the_heading_can_be_left_out_for_a_page_that_has_its_own():
    assert not render_markdown(report(), heading=False).startswith("#")


def test_the_machine_line_names_the_system_and_python_but_not_the_host(monkeypatch):
    monkeypatch.setattr(platform, "system", lambda: "Darwin")
    monkeypatch.setattr(platform, "machine", lambda: "arm64")
    monkeypatch.setattr(platform, "python_version", lambda: "3.14.3")
    monkeypatch.setattr(platform, "node", lambda: "marcels-macbook")
    line = machine_line()
    assert line == "Darwin arm64, Python 3.14.3" and "macbook" not in line


# ---- --write ---------------------------------------------------------------------------------------

PAGE = "# Measurements\n\nIntro text.\n\n<!-- passageway:results:start -->\nSTALE RESULTS\n<!-- passageway:results:end -->\n\nFooter.\n"


@pytest.fixture
def page(tmp_path):
    path = tmp_path / "measurements.md"
    path.write_text(PAGE)
    return path


def test_write_replaces_only_the_block_between_the_markers(page):
    write_block(page, report())
    text = page.read_text()
    assert text.startswith("# Measurements\n\nIntro text.\n\n<!-- passageway:results:start -->\n")
    assert text.endswith("<!-- passageway:results:end -->\n\nFooter.\n") and "STALE RESULTS" not in text
    assert "hash-test" in text and "# Retrieval evaluation" not in text


def test_write_twice_gives_the_same_file_and_one_history_entry(page):
    write_block(page, report())
    first = page.read_text()
    write_block(page, report())
    assert page.read_text() == first
    history = json.loads((page.parent / "measurements.history.json").read_text())
    assert len(history) == 1 and history[0]["embedder"] == "hash-test" and history[0]["hit_at_3"] == 0.5


def test_a_run_with_another_threshold_or_date_is_a_new_history_entry(page):
    write_block(page, report())
    write_block(page, report(run={**RUN, "threshold": 0.9}))
    write_block(page, report(run={**RUN, "date": "2026-11-01T09:00:00Z"}))
    history = json.loads((page.parent / "measurements.history.json").read_text())
    assert len(history) == 3
    assert page.read_text().count("0.9") >= 1


def test_the_block_ends_with_the_last_ten_runs_newest_first(page):
    for day in range(1, 13):
        write_block(page, report(run={**RUN, "date": f"2026-10-{day:02d}T10:00:00Z"}))
    text = page.read_text()
    rows = [line for line in text.splitlines() if line.startswith("| 2026-10-")]
    assert len(rows) == 10 and rows[0].startswith("| 2026-10-12") and rows[-1].startswith("| 2026-10-03")
    assert len(json.loads((page.parent / "measurements.history.json").read_text())) == 12  # the file keeps them all


@pytest.mark.parametrize("text", ["no markers here", "<!-- passageway:results:end -->\n<!-- passageway:results:start -->\n",
                                  "<!-- passageway:results:start -->\nonly the start"])
def test_a_page_without_both_markers_in_order_is_refused_and_left_alone(tmp_path, text):
    path = tmp_path / "page.md"
    path.write_text(text)
    with pytest.raises(ReportError, match="passageway:results:start"):
        write_block(path, report())
    assert path.read_text() == text and not (tmp_path / "page.history.json").exists()


def test_a_missing_page_is_a_report_error(tmp_path):
    with pytest.raises(ReportError, match="not found"):
        write_block(tmp_path / "nope.md", report())


# ---- review findings ------------------------------------------------------------------------------

def test_the_targets_table_shows_the_measured_value_the_way_the_metrics_table_does():
    md = render_markdown(report(targets={"hit_at_3": 0.667, "p95_ms": 100.0}))
    row = next(line for line in md.splitlines() if line.startswith("| hit_at_3"))
    assert "50.0%" in row and "66.7%" in row and "0.3333" not in md and "0.5000" not in md
    assert "12.5 ms" in next(line for line in md.splitlines() if line.startswith("| p95_ms"))


def test_the_sweep_table_says_that_three_shared_words_pass_any_threshold():
    md = render_markdown(report(sweep=[(0.8, results())]))
    assert "three or more words" in md


def test_a_crlf_page_stays_crlf(page):
    page.write_bytes(PAGE.replace("\n", "\r\n").encode())
    write_block(page, report())
    raw = page.read_bytes()
    assert b"\r\n" in raw and b"\n" not in raw.replace(b"\r\n", b"")
    assert raw.startswith(b"# Measurements\r\n\r\nIntro text.")


def test_markers_inside_a_code_fence_are_documentation_not_the_place_for_the_results(tmp_path):
    path = tmp_path / "page.md"
    path.write_text("How to use it:\n\n```markdown\n<!-- passageway:results:start -->\n<!-- passageway:results:end -->\n```\n\n"
                    "<!-- passageway:results:start -->\n<!-- passageway:results:end -->\n")
    write_block(path, report())
    text = path.read_text()
    assert "```markdown\n<!-- passageway:results:start -->\n<!-- passageway:results:end -->\n```" in text
    assert text.index("hash-test") > text.index("```\n\n<!--")


def test_a_second_pair_of_markers_is_an_error_not_silently_ignored(tmp_path):
    path = tmp_path / "page.md"
    twice = "<!-- passageway:results:start -->\n<!-- passageway:results:end -->\n"
    path.write_text(twice + "\n" + twice)
    with pytest.raises(ReportError, match="more than once"):
        write_block(path, report())
    assert path.read_text() == twice + "\n" + twice


def test_an_end_marker_before_the_start_does_not_hide_a_valid_pair(tmp_path):
    path = tmp_path / "page.md"
    path.write_text("<!-- passageway:results:end -->\ntext\n<!-- passageway:results:start -->\n<!-- passageway:results:end -->\n")
    write_block(path, report())
    assert "hash-test" in path.read_text()


def test_a_page_that_is_a_folder_is_a_report_error(tmp_path):
    with pytest.raises(ReportError, match="read"):
        write_block(tmp_path, report())


@pytest.mark.parametrize("content", ['{"a": 1}', '[{"date": "2026-01-01"}]', '[1, 2]', '"text"'])
def test_a_history_file_of_the_wrong_shape_is_a_report_error_and_is_left_alone(page, content):
    history = page.parent / "measurements.history.json"
    history.write_text(content)
    with pytest.raises(ReportError, match="history"):
        write_block(page, report())
    assert history.read_text() == content and page.read_text() == PAGE


def test_a_page_that_cannot_be_written_leaves_no_history_behind(page):
    import os
    if os.geteuid() == 0:
        pytest.skip("root can write anything")
    page.chmod(0o444)
    try:
        with pytest.raises(ReportError, match="write"):
            write_block(page, report())
    finally:
        page.chmod(0o644)
    assert not (page.parent / "measurements.history.json").exists()
