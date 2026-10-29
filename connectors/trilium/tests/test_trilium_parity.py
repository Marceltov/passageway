"""Opt-in parity with trilium-recall on its public fixture: PASSAGEWAY_LIVE=1 and the default model present."""

import io
import json
import os
import sys
from pathlib import Path

import pytest

from passageway.eval.cli import main

pytestmark = pytest.mark.skipif(not os.environ.get("PASSAGEWAY_LIVE"), reason="set PASSAGEWAY_LIVE=1 to run with the real model")
CASES = Path(__file__).with_name("fixture-cases.toml")


def test_the_fixture_cases_score_at_least_what_trilium_recall_published(world, tmp_path):
    config = tmp_path / "passageway.toml"
    config.write_text(f'[embedder]\ndownload = false\n\n[[connector]]\nname = "fixture"\n'
                      f'command = ["{sys.executable}", "-m", "passageway_connector_trilium"]\n'
                      f'env = {{ URL = "{world.url}" }}\nsecrets = {{ TOKEN = "env:FIXTURE_TOKEN" }}\n')
    env = {k: v for k, v in os.environ.items() if not k.startswith("PASSAGEWAY_CONFIG")}
    env.update({"PASSAGEWAY_CONFIG": str(config), "FIXTURE_TOKEN": world.etapi.token})
    out, err = io.StringIO(), io.StringIO()
    code = main([str(CASES), "--out", str(tmp_path / "r"), "--include-cases"], env=env, stdout=out, stderr=err)
    assert code == 0, err.getvalue()
    report = json.loads((tmp_path / "r" / "report.json").read_text())
    m = report["metrics"]
    misses = [c["query"] for c in report["cases"] if c["expect_id"] and c["rank"] is None]
    assert m["hit_at_3"] >= 0.83, (m["hit_at_3"], misses)
    assert m["silence"] == 1.0, [c["query"] for c in report["cases"] if not c["expect_id"] and c["hits"]]
    print(f"parity: hit@3 {m['hit_at_3']:.2f} hit@1 {m['hit_at_1']:.2f} silence {m['silence']:.2f} p50 {m['p50_ms']} ms; misses {misses}")
