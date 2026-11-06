import os
from pathlib import Path

import numpy as np
import pytest

from passageway.embed import HashEmbedder, OnnxEmbedder

MODEL_DIR = Path(os.environ.get("RECALL_TEST_MODEL_DIR", Path(__file__).parents[2] / ".models" / "e5-small"))


def test_hash_embedder_shape_and_norm():
    v = HashEmbedder().embed_passages(["proxmox lxc swap", "a"])
    assert v.shape == (2, 384) and v.dtype == np.float32
    assert np.allclose(np.linalg.norm(v, axis=1), 1)


def test_hash_embedder_overlap_scores_higher():
    e = HashEmbedder()
    q = e.embed_queries(["proxmox swap"])[0]
    a, b = e.embed_passages(["proxmox lxc swap limit", "pizza dough recipe"])
    assert q @ a > q @ b


def test_hash_embedder_empty_text_is_finite():
    v = HashEmbedder().embed_queries([""])
    assert np.isfinite(v).all()


@pytest.mark.skipif(not (MODEL_DIR / "model.onnx").exists(), reason="model not fetched")
def test_onnx_cross_lingual():
    e = OnnxEmbedder(MODEL_DIR)
    assert e.dim == 384 and e.name == "multilingual-e5-small-int8"
    q = e.embed_queries(["Wie viel Arbeitsspeicher hat der Container?"])[0]
    a, b = e.embed_passages(["The container has 2 GB of RAM and no swap.", "Pizza dough needs 48 hours."])
    assert q @ a > q @ b
    assert np.isclose(np.linalg.norm(a), 1, atol=1e-4)


@pytest.mark.skipif(not (MODEL_DIR / "model.onnx").exists(), reason="model not fetched")
def test_onnx_truncates_long_input():
    e = OnnxEmbedder(MODEL_DIR)
    v = e.embed_queries(["word " * 5000])
    assert v.shape == (1, 384) and np.isfinite(v).all()


def test_token_budget_batches():
    from passageway.embed import token_batches
    lengths = [512, 10, 512, 20, 30, 512, 40]
    batches = token_batches(lengths, budget=1024)
    assert sorted(i for b in batches for i in b) == list(range(7))
    assert all(len(b) * max(lengths[i] for i in b) <= 1024 for b in batches)
    assert len(batches) <= 3


@pytest.mark.skipif(not (MODEL_DIR / "model.onnx").exists(), reason="model not fetched")
def test_onnx_batching_keeps_order():
    e = OnnxEmbedder(MODEL_DIR)
    texts = ["long " * 400, "short a", "medium text " * 30, "short b"]
    together = e.embed_passages(texts)
    alone = np.stack([e.embed_passages([t])[0] for t in texts])
    # Dynamic int8 quantisation shifts values a little with batch composition; order must hold.
    similarity = together @ alone.T
    assert (np.diag(similarity) > 0.99).all() and (similarity.argmax(axis=1) == np.arange(4)).all()


@pytest.mark.skipif(not (MODEL_DIR / "model.onnx").exists(), reason="model not fetched")
def test_onnx_counts_a_passage_as_the_model_sees_it_without_cutting():
    e = OnnxEmbedder(MODEL_DIR)
    assert e.max_tokens == 512
    short, long_ = e.count_passages(["Hallo Welt", "Wort " * 2000])
    assert 4 < short < 12  # "passage: Hallo Welt" with <s> and </s>
    assert long_ > 2000  # counted in full, not at the cut


@pytest.mark.skipif(not (MODEL_DIR / "model.onnx").exists(), reason="model not fetched")
def test_onnx_refuses_a_passage_over_its_limit_instead_of_cutting_it():
    from passageway.embed import EmbedderError

    e = OnnxEmbedder(MODEL_DIR)
    with pytest.raises(EmbedderError, match="over the model's limit of 512"):
        e.embed_passages(["short", "Wort " * 2000])
    assert e.embed_queries(["Wort " * 2000]).shape == (1, 384)  # a question is cut, as before


def test_the_hash_embedder_does_not_count():
    assert HashEmbedder().max_tokens is None
