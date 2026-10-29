"""Opt-in: the built-in presets with their real files (PASSAGEWAY_LIVE=1 and the models downloaded)."""

import os
import time
from pathlib import Path

import numpy as np
import pytest

from passageway.config import Config, EmbedderConfig
from passageway.embed import build_embedder, model_folder
from passageway.models import PRESETS, files_missing
from passageway.testing.embedder_contract import check_embedder

pytestmark = pytest.mark.skipif(not os.environ.get("PASSAGEWAY_LIVE"), reason="set PASSAGEWAY_LIVE=1 to run against the real models")


def _config():
    data = Path(os.environ.get("PASSAGEWAY_DATA_DIR") or Path.home() / "Library/Application Support/passageway")
    return Config(password="", connectors=[], data_dir=data, model_dir=Path(os.environ.get("PASSAGEWAY_MODEL_DIR") or data / "models" / "e5-small"))


@pytest.mark.parametrize("name", sorted(PRESETS))
def test_each_preset_loads_passes_the_contract_and_tells_german_from_english_apart(name):
    config = _config()
    cfg = EmbedderConfig(model=name, download=False, device="cpu")
    if files_missing(PRESETS[name], model_folder(cfg, config)):
        pytest.skip(f"{name} is not downloaded")
    started = time.perf_counter()
    embedder = build_embedder(cfg, config)
    load = time.perf_counter() - started
    check_embedder(embedder)
    assert (embedder.name, embedder.dim) == (PRESETS[name].label, PRESETS[name].dim)
    q = embedder.embed_queries(["Wie funktioniert Backpropagation?"])[0]
    p = embedder.embed_passages(["Backpropagation computes the gradient of the loss with respect to each weight by the chain rule.",
                                 "Ein Leuchtturm steht an der Küste und warnt Schiffe vor Untiefen."])
    assert float(q @ p[0]) > float(q @ p[1]), name  # the German question is closer to the English answer than to the lighthouse
    print(f"{name}: load {load:.1f} s, cos(answer) {float(q @ p[0]):.3f}, cos(lighthouse) {float(q @ p[1]):.3f}")


def test_coreml_gives_the_same_vectors_as_cpu_within_tolerance():
    import onnxruntime as ort
    if "CoreMLExecutionProvider" not in ort.get_available_providers():
        pytest.skip("no CoreML here")
    config = _config()
    cpu = build_embedder(EmbedderConfig(download=False, device="cpu"), config)
    coreml = build_embedder(EmbedderConfig(download=False, device="coreml"), config)
    texts = ["Lighthouses guide ships safely into the harbour at night.", "Backpropagation computes gradients."]
    a, b = cpu.embed_passages(texts), coreml.embed_passages(texts)
    assert np.allclose(a, b, atol=2e-2), np.abs(a - b).max()
