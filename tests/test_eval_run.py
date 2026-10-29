import json
import sys

import pytest

from passageway.config import Config, ConnectorConfig
from passageway.embed import HashEmbedder
from passageway.eval.cases import Case
from passageway.eval.run import CaseResult, TimedEmbedder, check_targets, group_scores, run_cases, score
from passageway.rank import Hit, RankParams
from passageway.server import Engine


def hit(item_id="a.md", title="A"):
    return Hit("notes", item_id, title, "http://x", [], [], "H", "p", 1.0, [])


def result(expect, hits, ms=10.0, group=None, embed_ms=1.0):
    case = Case("q", tuple(expect), (), group)
    rank = next((i for i, h in enumerate(hits, 1) if h.title in expect), None) if expect else None
    return CaseResult(case, hits, rank, ms, embed_ms)


def test_score_metrics():
    results = [
        result(["A"], [hit(title="X"), hit(title="A")]),   # rank 2
        result(["B"], [hit(title="B")]),                   # rank 1
        result(["C"], []),                                 # false silence
        result([], []),                                    # silent, as it should be
        result([], [hit()], ms=400.0),                     # should have been silent
    ]
    m = score(results)
    assert (m["cases"], m["answerable"], m["unanswerable"]) == (5, 3, 2)
    assert m["hit_at_1"] == 1 / 3 and m["hit_at_3"] == 2 / 3 and m["mrr"] == (0.5 + 1 + 0) / 3
    assert m["silence"] == 0.5 and m["false_silence"] == 1 / 3
    assert m["p50_ms"] == 10.0 and m["p95_ms"] == 400.0


def test_a_rank_beyond_three_is_not_a_hit_at_three():
    r = result(["D"], [hit(title="A"), hit(title="B"), hit(title="C"), hit(title="D")])
    assert r.rank == 4 and score([r])["hit_at_3"] == 0.0 and score([r])["mrr"] == 0.25


def test_metrics_that_have_no_cases_behind_them_are_none_not_a_perfect_score():
    only_answerable = score([result(["A"], [hit(title="A")])])
    assert only_answerable["silence"] is None
    only_unanswerable = score([result([], [])])
    assert only_unanswerable["hit_at_3"] is None and only_unanswerable["mrr"] is None
    assert only_unanswerable["false_silence"] is None and only_unanswerable["silence"] == 1.0


def test_the_embedding_share_of_the_latency():
    m = score([result(["A"], [hit(title="A")], ms=10.0, embed_ms=4.0), result([], [], ms=30.0, embed_ms=6.0)])
    assert m["embed_ms"] == 5.0 and m["embed_share"] == 0.25


def test_groups_are_scored_separately_and_the_ungrouped_are_left_out():
    results = [result(["A"], [hit(title="A")], group="ml"), result(["B"], [], group="ml"),
               result([], [], group="other"), result(["Z"], [hit(title="Z")])]
    groups = group_scores(results)
    assert set(groups) == {"ml", "other"}
    assert groups["ml"]["hit_at_3"] == 0.5 and groups["other"]["silence"] == 1.0


def test_targets_are_minimums_except_false_silence_and_latency():
    metrics = {"hit_at_3": 0.8, "silence": 0.79, "false_silence": 0.1, "p95_ms": 300.0, "mrr": None}
    checks = {c["name"]: c for c in check_targets(metrics, {"hit_at_3": 0.8, "silence": 0.8, "false_silence": 0.1,
                                                           "p95_ms": 299.0, "mrr": 0.5})}
    assert checks["hit_at_3"]["passed"] and not checks["silence"]["passed"]
    assert checks["false_silence"]["passed"] and checks["false_silence"]["limit"] == "at most"
    assert not checks["p95_ms"]["passed"]
    assert not checks["mrr"]["passed"] and checks["mrr"]["value"] is None  # nothing measured: not a pass


DOCS = [
    {"id": "bp.md", "title": "Backpropagation", "url": "http://x/bp", "version": "1",
     "sections": [{"heading": "Overview", "text": "backpropagation computes gradients with the chain rule"}]},
    {"id": "ae.md", "title": "Autoencoder", "url": "http://x/ae", "version": "1",
     "sections": [{"heading": "Overview", "text": "an autoencoder compresses data into a latent code"}]},
]


@pytest.fixture
def engine(tmp_path):
    items = tmp_path / "items.json"
    items.write_text(json.dumps(DOCS))
    cc = ConnectorConfig("notes", (sys.executable, "-m", "passageway.testing.fake_connector"), {"FAKE_ITEMS": str(items)}, {})
    config = Config(password="", connectors=[cc], data_dir=tmp_path / "data", model_dir=tmp_path)
    (tmp_path / "data").mkdir()
    engine = Engine(config, TimedEmbedder(HashEmbedder()))
    engine.params = RankParams(min_cos=0.3)
    engine.sync_all_once()
    return engine


def test_run_cases_asks_the_engine_and_ranks_the_answers(engine):
    cases = [Case("how does backpropagation use the chain rule", ("Backpropagation",)),
             Case("what compresses data into a latent code", (), ("ae.md",)),
             Case("quarterly cafeteria pizza budget", ())]
    results = run_cases(engine, cases)
    assert [r.rank for r in results] == [1, 1, None]
    assert results[2].hits == [] and results[0].hits[0].item_id == "bp.md"
    assert all(r.ms > 0 for r in results) and all(r.embed_ms > 0 for r in results)
    assert all(r.embed_ms <= r.ms for r in results)


def test_a_warm_up_question_is_asked_but_not_counted(engine, monkeypatch):
    asked = []
    real = engine.recall
    monkeypatch.setattr(engine, "recall", lambda q, **kw: asked.append(q) or real(q, **kw))
    results = run_cases(engine, [Case("one backpropagation", ("Backpropagation",)), Case("two", ())])
    assert len(results) == 2 and len(asked) == 3 and asked[0] == asked[1]


def test_the_engine_is_asked_for_three_hits(engine, monkeypatch):
    limits = []
    real = engine.recall
    monkeypatch.setattr(engine, "recall", lambda q, **kw: limits.append(kw.get("limit")) or real(q, **kw))
    run_cases(engine, [Case("backpropagation", ("Backpropagation",))])
    assert set(limits) == {3}
