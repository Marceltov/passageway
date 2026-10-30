import io
import json
import subprocess
import sys

import numpy as np
import pytest

from passageway.embed import HashEmbedder
from passageway.eval.cli import main

DOCS = [
    {"id": "bp.md", "title": "Backpropagation", "url": "http://x/bp", "version": "1",
     "sections": [{"heading": "Overview", "text": "backpropagation computes gradients with the chain rule"}]},
    {"id": "ae.md", "title": "Autoencoder", "url": "http://x/ae", "version": "1",
     "sections": [{"heading": "Overview", "text": "an autoencoder compresses data into a latent code"}]},
]
CASES = '''
[targets]
hit_at_3 = 1.0
silence = 1.0

[[case]]
query = "how does backpropagation use the chain rule"
expect = ["Backpropagation"]
group = "ml"

[[case]]
query = "what compresses data into a latent code"
expect_id = ["ae.md"]
group = "ml"

[[case]]
query = "quarterly cafeteria pizza budget"
'''


class Setup:
    def __init__(self, tmp_path):
        self.tmp = tmp_path
        (tmp_path / "items.json").write_text(json.dumps(DOCS))
        self.config = tmp_path / "passageway.toml"
        self.config.write_text(
            '[embedder]\nmin_similarity = 0.3\ndownload = false\n\n[[connector]]\nname = "notes"\n'
            f'command = ["{sys.executable}", "-m", "passageway.testing.fake_connector"]\n'
            f'env = {{ FAKE_ITEMS = "{tmp_path / "items.json"}" }}\n')
        self.cases = tmp_path / "cases.toml"
        self.cases.write_text(CASES)
        self.live = tmp_path / "live"
        self.live.mkdir()
        self.env = {"PASSAGEWAY_CONFIG": str(self.config), "PASSAGEWAY_DATA_DIR": str(self.live),
                    "PASSAGEWAY_MODEL_DIR": str(tmp_path / "model")}

    def run(self, *args, cases=None, embedder=None, env=None):
        out, err = io.StringIO(), io.StringIO()
        code = main([str(cases or self.cases), *map(str, args)], env={**self.env, **(env or {})},
                    embedder=embedder or HashEmbedder(), stdout=out, stderr=err)
        return code, out.getvalue(), err.getvalue()


@pytest.fixture
def s(tmp_path):
    return Setup(tmp_path)


def test_a_run_prints_the_report_and_needs_no_password(s):
    code, out, err = s.run()
    assert code == 0, err
    assert out.startswith("# Retrieval evaluation") and "Hit@3" in out and "100.0%" in out and "hash-test" in out


def test_enforce_exits_1_below_the_targets_and_only_then(s):
    assert s.run("--enforce")[0] == 0
    s.cases.write_text(CASES.replace("[[case]]\nquery = \"quarterly", "[[case]]\nquery = \"backpropagation\"\n"
                                     "expect = [\"Nothing Like This\"]\n\n[[case]]\nquery = \"quarterly"))
    assert s.run("--enforce")[0] == 1
    assert s.run()[0] == 0  # without --enforce a miss is a result, not a failure


def test_enforce_without_targets_warns_and_passes(s):
    s.cases.write_text('[[case]]\nquery = "backpropagation"\nexpect = ["Backpropagation"]')
    code, _, err = s.run("--enforce")
    assert code == 0 and "[targets]" in err


@pytest.mark.parametrize("args,message", [
    (["--sweep", "a,b"], "--sweep"),
    (["--sweep", "0.5,1.5"], "--sweep"),
    (["--threshold", "2"], "--threshold"),
    (["--config", "/no/such/passageway.toml"], "not found"),
])
def test_bad_options_exit_2_and_say_which(s, args, message):
    code, out, err = s.run(*args)
    assert code == 2 and message in err and out == ""


def test_a_bad_cases_file_exits_2(s):
    s.cases.write_text('[[case]]\nquery = ""')
    code, _, err = s.run()
    assert code == 2 and "query" in err


def test_a_missing_model_exits_2_with_the_folder(s):
    out, err = io.StringIO(), io.StringIO()
    code = main([str(s.cases)], env=s.env, stdout=out, stderr=err)  # no embedder given: the real one is looked for
    assert code == 2 and str(s.tmp / "model") in err.getvalue()


def test_a_source_that_fails_to_sync_stops_the_run_with_its_error(s, tmp_path):
    s.config.write_text(s.config.read_text().replace("FAKE_ITEMS =", 'FAKE_FAIL = "list", FAKE_ITEMS ='))
    code, out, err = s.run("--out", tmp_path / "r")
    assert code == 1 and "notes" in err and "fake failure" in err
    assert out == "" and not (tmp_path / "r").exists()


def test_the_live_index_is_never_touched_by_default(s):
    s.run()
    assert list(s.live.iterdir()) == []


def test_data_dir_keeps_the_index_and_refuses_one_built_with_another_embedder(s, tmp_path):
    keep = tmp_path / "keep"
    assert s.run("--data-dir", keep)[0] == 0 and (keep / "notes.db").is_file()
    assert s.run("--data-dir", keep)[0] == 0  # reused

    class Other(HashEmbedder):
        name = "other-model"

    code, _, err = s.run("--data-dir", keep, embedder=Other())
    assert code == 2 and "other-model" in err and "hash-test" in err


def test_out_writes_json_and_markdown_that_hold_no_question(s, tmp_path):
    code, _, err = s.run("--out", tmp_path / "r")
    assert code == 0, err
    report = json.loads((tmp_path / "r" / "report.json").read_text())
    assert report["schema"] == 1 and report["metrics"]["cases"] == 3 and report["run"]["embedder"] == "hash-test"
    assert report["run"]["sources"]["notes"] == {"items": 2, "sections": 2}
    text = (tmp_path / "r" / "report.json").read_text() + (tmp_path / "r" / "report.md").read_text()
    assert "cafeteria" not in text and "Backpropagation" not in text and "chain rule" not in text


def test_include_cases_quotes_them(s, tmp_path):
    s.run("--out", tmp_path / "r", "--include-cases")
    assert "cafeteria" in (tmp_path / "r" / "report.md").read_text()
    assert len(json.loads((tmp_path / "r" / "report.json").read_text())["cases"]) == 3


def test_write_updates_the_page_and_records_the_history(s, tmp_path):
    page = tmp_path / "measurements.md"
    page.write_text("# Numbers\n\n<!-- passageway:results:start -->\n<!-- passageway:results:end -->\n")
    assert s.run("--write", page)[0] == 0
    first = page.read_text()
    assert "hash-test" in first and "### History" in first
    s.run("--write", page)
    assert len(json.loads((tmp_path / "measurements.history.json").read_text())) == 1


def test_a_page_without_markers_is_refused_before_anything_is_measured(s, tmp_path):
    page = tmp_path / "plain.md"
    page.write_text("no markers")
    s.config.write_text(s.config.read_text().replace("FAKE_ITEMS =", 'FAKE_FAIL = "list", FAKE_ITEMS ='))
    code, _, err = s.run("--write", page)
    assert code == 2 and "passageway:results:start" in err and "fake failure" not in err
    assert page.read_text() == "no markers"


TWO_TERMS = '''
[[case]]
query = "chain rule"
expect = ["Backpropagation"]
'''  # fewer than three matching words: only the similarity can let it through, so the threshold decides


def test_sweep_runs_the_questions_at_each_threshold(s, tmp_path):
    cases = tmp_path / "two-terms.toml"
    cases.write_text(TWO_TERMS)
    s.run("--sweep", "0.2,0.999", "--out", tmp_path / "r", cases=cases)
    report = json.loads((tmp_path / "r" / "report.json").read_text())
    rows = {row["threshold"]: row["metrics"] for row in report["sweep"]}
    assert rows[0.2]["hit_at_3"] == 1.0 and rows[0.999]["hit_at_3"] == 0.0 and rows[0.999]["false_silence"] == 1.0
    assert report["run"]["threshold"] == 0.3 and report["metrics"]["hit_at_3"] == 1.0  # the main run: the configured one


def test_threshold_overrides_the_configured_one_for_the_run(s, tmp_path):
    cases = tmp_path / "two-terms.toml"
    cases.write_text(TWO_TERMS)
    s.run("--threshold", "0.999", "--out", tmp_path / "r", cases=cases)
    report = json.loads((tmp_path / "r" / "report.json").read_text())
    assert report["run"]["threshold"] == 0.999 and report["metrics"]["hit_at_3"] == 0.0


def test_the_model_option_and_config_option_are_used(s, tmp_path):
    other = tmp_path / "other.toml"
    other.write_text(s.config.read_text())
    env = {k: v for k, v in s.env.items() if k != "PASSAGEWAY_CONFIG"}
    out, err = io.StringIO(), io.StringIO()
    assert main([str(s.cases), "--config", str(other)], env=env, embedder=HashEmbedder(), stdout=out, stderr=err) == 0


def test_passageway_eval_is_dispatched_by_the_server_entry_point(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))  # instances on the machine running the tests must not count
    monkeypatch.delenv("PASSAGEWAY_INSTANCE", raising=False)
    import passageway.eval.cli as cli
    import passageway.server as server
    seen = []
    monkeypatch.setattr(cli, "main", lambda argv: seen.append(argv) or 7)
    monkeypatch.setattr(sys, "argv", ["passageway", "eval", "cases.toml", "--enforce"])
    with pytest.raises(SystemExit) as stop:
        server.main()
    assert stop.value.code == 7 and seen == [["cases.toml", "--enforce"]]


def test_help_is_available_as_a_module():
    out = subprocess.run([sys.executable, "-m", "passageway.eval", "--help"], capture_output=True, text=True)
    assert out.returncode == 0 and "--sweep" in out.stdout and "--include-cases" in out.stdout


# ---- review findings ------------------------------------------------------------------------------

def test_paths_that_cannot_work_exit_2_before_the_run_not_with_a_traceback(s, tmp_path):
    a_file = tmp_path / "a-file"
    a_file.write_text("x")
    folder = tmp_path / "a-folder"
    folder.mkdir()
    for args, message in ((["--data-dir", a_file], "--data-dir"), (["--out", a_file], "--out"),
                          (["--write", folder], "--write")):
        code, out, err = s.run(*args)
        assert code == 2 and message in err and out == "", args
    code, _, err = s.run(cases=folder)
    assert code == 2 and "eval:" in err


def test_a_page_that_cannot_be_written_is_found_before_the_run(s, tmp_path):
    import os
    if os.geteuid() == 0:
        pytest.skip("root can write anything")
    page = tmp_path / "ro.md"
    page.write_text("<!-- passageway:results:start -->\n<!-- passageway:results:end -->\n")
    page.chmod(0o444)
    s.config.write_text(s.config.read_text().replace("FAKE_ITEMS =", 'FAKE_FAIL = "list", FAKE_ITEMS ='))
    try:
        code, _, err = s.run("--write", page)
    finally:
        page.chmod(0o644)
    assert code == 2 and "write" in err and "fake failure" not in err  # refused before any source was built


def test_an_empty_sweep_is_an_error(s):
    code, _, err = s.run("--sweep", "")
    assert code == 2 and "--sweep" in err


def test_a_kept_index_of_the_same_model_is_reused_even_if_it_must_be_rebuilt_for_another_reason(s, tmp_path):
    keep = tmp_path / "keep"
    assert s.run("--data-dir", keep)[0] == 0
    code, _, err = s.run("--data-dir", keep, embedder=HashEmbedder(dim=128))  # same name, other dimension: rebuilt
    assert code == 0, err


def test_the_servers_own_sync_logging_does_not_add_a_traceback_to_the_error(s, caplog):
    s.config.write_text(s.config.read_text().replace("FAKE_ITEMS =", 'FAKE_FAIL = "list", FAKE_ITEMS ='))
    assert s.run()[0] == 1
    assert not [r for r in caplog.records if r.name == "passageway.sync"]


def test_the_report_is_printed_before_the_files_are_written(s, tmp_path):
    out_dir = tmp_path / "r"
    code, out, _ = s.run("--out", out_dir)
    assert code == 0 and out.startswith("# Retrieval evaluation") and (out_dir / "report.md").is_file()


def test_an_embedder_that_fails_on_queries_fails_the_run_instead_of_reporting_silence(s, tmp_path):
    class FailingQueries(HashEmbedder):
        def embed_queries(self, texts):
            raise RuntimeError("rate limited")

    code, out, err = s.run("--out", tmp_path / "r", embedder=FailingQueries())
    assert code == 1 and "rate limited" in err and out == "" and not (tmp_path / "r").exists()


def test_help_mentions_the_compare_command():
    out = subprocess.run([sys.executable, "-m", "passageway.eval", "--help"], capture_output=True, text=True)
    assert "compare" in out.stdout
