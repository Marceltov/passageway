import io
import json
import os
import sys
import time

import pytest

from passageway.eval.cli import main

DOCS = [
    {"id": "bp.md", "title": "Backpropagation", "url": "http://x/bp", "version": "1",
     "sections": [{"heading": "Overview", "text": "backpropagation computes gradients with the chain rule"}]},
    {"id": "ae.md", "title": "Autoencoder", "url": "http://x/ae", "version": "1",
     "sections": [{"heading": "Overview", "text": "an autoencoder compresses data into a latent code"}]},
]
CASES = '''
[[case]]
query = "how does backpropagation use the chain rule"
expect_id = ["bp.md"]
group = "ml"

[[case]]
query = "what compresses data into a latent code"
expect_id = ["ae.md"]
group = "ml"

[[case]]
query = "quarterly cafeteria pizza budget"
group = "off"
'''
PAGE = "# Numbers\n\n<!-- passageway:results:start -->\n<!-- passageway:results:end -->\n"


class Setup:
    def __init__(self, tmp_path):
        self.tmp = tmp_path
        (tmp_path / "items.json").write_text(json.dumps(DOCS))
        self.log = tmp_path / "embed.log"
        py = sys.executable

        def command(name, dim):
            return (f'command = ["{py}", "-m", "passageway.testing.fake_embedder"]\n'
                    f'env = {{ FAKE_EMBED_NAME = "{name}", FAKE_EMBED_DIM = "{dim}", FAKE_EMBED_LOG = "{self.log}" }}\n')

        self.config = tmp_path / "passageway.toml"
        self.config.write_text(
            '[embedder]\nkind = "command"\n' + command("default-model", 64) + 'min_similarity = 0.3\n\n'
            '[embedders.small]\nkind = "command"\n' + command("small-model", 8) + 'min_similarity = 0.5\n\n'
            '[embedders.big]\nkind = "command"\n' + command("big-model", 128) + 'min_similarity = 0.2\n\n'
            f'[[connector]]\nname = "notes"\ncommand = ["{py}", "-m", "passageway.testing.fake_connector"]\n'
            f'env = {{ FAKE_ITEMS = "{tmp_path / "items.json"}" }}\n')
        self.cases = tmp_path / "cases.toml"
        self.cases.write_text(CASES)
        self.live = tmp_path / "live"
        self.live.mkdir()
        self.env = {"PASSAGEWAY_CONFIG": str(self.config), "PASSAGEWAY_DATA_DIR": str(self.live),
                    "PASSAGEWAY_MODEL_DIR": str(tmp_path / "model")}

    def run(self, *args, env=None):
        out, err = io.StringIO(), io.StringIO()
        code = main(["compare", str(self.cases), *map(str, args)], env={**self.env, **(env or {})}, stdout=out, stderr=err)
        return code, out.getvalue(), err.getvalue()

    def report(self, *args):
        out = self.tmp / "r"
        code, _, err = self.run("--out", out, *args)
        assert code == 0, err
        return json.loads((out / "report.json").read_text())


@pytest.fixture
def s(tmp_path):
    return Setup(tmp_path)


def test_every_candidate_gets_a_row_with_its_model_its_gate_and_its_times(s):
    code, out, err = s.run()
    assert code == 0, err
    assert out.startswith("# Embedder comparison")
    for label, model, dim, gate in (("default", "default-model", "64", "0.3"), ("small", "small-model", "8", "0.5"),
                                    ("big", "big-model", "128", "0.2")):
        row = next(line for line in out.splitlines() if line.startswith(f"| {label}"))
        assert model in row and f"| {dim} |" in row and f"| {gate} |" in row, row
    assert "Load" in out and "Index" in out and "Hit@3" in out and "(" in out  # times, and the intervals


def test_the_json_report_has_the_run_and_one_entry_per_candidate(s):
    report = s.report()
    assert report["schema"] == 1 and report["kind"] == "compare"
    assert report["run"]["passageway"] and report["run"]["machine"] and report["questions"]["cases"] == 3
    by = {c["label"]: c for c in report["candidates"]}
    assert list(by) == ["default", "big", "small"]  # the server's embedder first, then the candidates by name
    assert (by["small"]["embedder"], by["small"]["dim"], by["small"]["threshold"]) == ("small-model", 8, 0.5)
    for c in report["candidates"]:
        assert c["load_seconds"] >= 0 and c["index_seconds"] >= 0 and c["metrics"]["cases"] == 3
        assert c["sources"]["notes"] == {"items": 2, "sections": 2} and "ml" in c["groups"]


def test_each_candidate_runs_at_its_own_threshold_unless_told_otherwise(s):
    assert [c["threshold"] for c in s.report()["candidates"]] == [0.3, 0.2, 0.5]
    assert {c["threshold"] for c in s.report("--threshold", "0.9")["candidates"]} == {0.9}


def test_the_chosen_candidates_only(s):
    report = s.report("--embedder", "small", "--embedder", "default")
    assert [c["label"] for c in report["candidates"]] == ["small", "default"]  # in the order asked


def test_a_comparison_needs_two_embedders_and_known_names(s):
    code, _, err = s.run("--embedder", "small")
    assert code == 2 and "at least two" in err
    code, _, err = s.run("--embedder", "small", "--embedder", "nope")
    assert code == 2 and "nope" in err and "big" in err and "default" in err  # the known names
    text = s.config.read_text()
    only_default = s.tmp / "only.toml"  # no candidates configured: only the server's own embedder
    only_default.write_text(text.split("[embedders.small]")[0] + "[[connector]]" + text.split("[[connector]]")[1])
    code, _, err = s.run("--config", only_default)
    assert code == 2 and "[embedders" in err


def test_every_candidate_has_a_fresh_throwaway_index_and_the_live_one_is_untouched(s):
    code, _, err = s.run()  # one shared folder would be refused: the models differ
    assert code == 0, err
    assert list(s.live.iterdir()) == []


def test_a_sweep_adds_rows_for_every_candidate(s):
    report = s.report("--sweep", "0.2,0.9")
    for c in report["candidates"]:
        assert [row["threshold"] for row in c["sweep"]] == [0.2, 0.9]
    md = (s.tmp / "r" / "report.md").read_text()
    assert md.count("Relevance threshold") == 3


def test_the_report_holds_no_question_title_or_url(s):
    s.run("--out", s.tmp / "r", "--sweep", "0.5")
    text = (s.tmp / "r" / "report.json").read_text() + (s.tmp / "r" / "report.md").read_text()
    for word in ("cafeteria", "Backpropagation", "chain rule", "http://x"):
        assert word not in text


def test_write_updates_the_page_and_records_one_history_line_per_candidate(s):
    page = s.tmp / "measurements.md"
    page.write_text(PAGE)
    assert s.run("--write", page)[0] == 0
    first = page.read_text()
    assert "default-model" in first and "big-model" in first and "small-model" in first and "### History" in first
    history = json.loads((s.tmp / "measurements.history.json").read_text())
    assert sorted(e["embedder"] for e in history) == ["big-model", "default-model", "small-model"]
    assert s.run("--write", page)[0] == 0
    assert len(json.loads((s.tmp / "measurements.history.json").read_text())) == 3  # the same day replaces


def test_a_page_without_markers_is_refused_before_any_embedder_is_started(s):
    page = s.tmp / "plain.md"
    page.write_text("no markers")
    code, _, err = s.run("--write", page)
    assert code == 2 and "passageway:results:start" in err and not s.log.exists()


def test_an_embedder_that_cannot_start_stops_the_comparison_with_its_name(s):
    s.config.write_text(s.config.read_text().replace('FAKE_EMBED_NAME = "small-model"',
                                                     'FAKE_EMBED_FAIL = "start", FAKE_EMBED_NAME = "small-model"'))
    code, out, err = s.run()
    assert code == 2 and "small" in err and "fake start failure" in err and out == ""


def test_a_source_that_fails_to_sync_stops_it_with_exit_1(s):
    s.config.write_text(s.config.read_text().replace("FAKE_ITEMS =", 'FAKE_FAIL = "list", FAKE_ITEMS ='))
    code, _, err = s.run()
    assert code == 1 and "notes" in err


def test_the_embedder_processes_are_gone_when_it_is_over(s):
    assert s.run()[0] == 0
    time.sleep(0.3)
    pids = {json.loads(line)["pid"] for line in s.log.read_text().splitlines()}
    assert len(pids) >= 3
    for pid in pids:
        with pytest.raises(ProcessLookupError):
            os.kill(pid, 0)


def test_help_and_bad_options(s):
    code, _, err = s.run("--threshold", "2")
    assert code == 2 and "--threshold" in err
    code, _, err = s.run("--sweep", "a")
    assert code == 2 and "--sweep" in err
