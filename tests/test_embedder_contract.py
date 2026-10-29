import itertools
import sys

import numpy as np
import pytest

from passageway.embed import HashEmbedder
from passageway.embed_command import CommandEmbedder
from passageway.testing.embedder_contract import check_embedder


def test_the_hash_embedder_passes():
    check_embedder(HashEmbedder())


def test_a_command_embedder_passes_as_a_real_subprocess():
    embedder = CommandEmbedder("fake", [sys.executable, "-m", "passageway.testing.fake_embedder"])
    try:
        check_embedder(embedder)
    finally:
        embedder.close()


class Broken(HashEmbedder):
    """A hash embedder with one thing wrong."""

    def __init__(self, fault):
        super().__init__(32)
        self.fault = fault
        self.calls = itertools.count()

    def _embed(self, texts):
        out = super()._embed(texts)
        if self.fault == "random":
            return super()._embed([f"{t} {next(self.calls)}" for t in texts])
        if self.fault == "constant":
            return np.tile(super()._embed(["same"])[0], (len(texts), 1))
        if self.fault == "wrong-dim":
            return out[:, :-1]
        if self.fault == "not-unit":
            return out * 2
        if self.fault == "nan":
            out[:, 0] = np.nan
            return out
        if self.fault == "empty":
            return np.ones((1, self.dim), dtype=np.float32) if not texts else out
        if self.fault == "batch-dependent":
            moved = out + (0.5 if len(texts) > 1 else 0.0) * np.eye(len(texts), self.dim, dtype=np.float32)
            return moved / np.linalg.norm(moved, axis=1, keepdims=True)  # still unit length: only the batch matters
        return out

    embed_queries = _embed
    embed_passages = _embed


@pytest.mark.parametrize("fault,message", [
    ("random", "deterministic"), ("constant", "tell"), ("wrong-dim", "dim"), ("not-unit", "unit"),
    ("nan", "finite"), ("empty", "empty|0"), ("batch-dependent", "batch"),
])
def test_what_the_check_catches(fault, message):
    with pytest.raises(AssertionError, match=message):
        check_embedder(Broken(fault))
