"""What every embedder must satisfy. Embedder authors call check_embedder from their own tests, on an object with
name, dim, embed_queries and embed_passages (a passageway.embed_command.CommandEmbedder around their program)."""

import numpy as np

PASSAGES = ["Lighthouses guide ships safely into the harbour at night.",
            "Bananas grow in warm climates and turn yellow when they ripen."]
QUERY = "ships near the harbour"


def check_embedder(embedder) -> None:
    assert isinstance(embedder.name, str) and embedder.name, "name must be a non-empty string"
    assert isinstance(embedder.dim, int) and embedder.dim >= 1, "dim must be a whole number from 1"
    dim = embedder.dim

    empty = embedder.embed_passages([])
    assert empty.shape == (0, dim), (f"no texts must give an empty array of shape (0, {dim}), got {empty.shape}: "
                                     "the dimension must match dim")

    out = embedder.embed_passages(PASSAGES)
    assert out.shape == (2, dim), f"expected shape (2, {dim}), got {out.shape}: the dimension must match dim"
    assert np.isfinite(out).all(), "vectors must hold finite numbers"
    assert np.allclose(np.linalg.norm(out, axis=1), 1.0, atol=1e-3), "vectors must have unit length"

    assert np.allclose(out, embedder.embed_passages(PASSAGES), atol=1e-4), \
        "the same texts must give the same vectors (an embedder must be deterministic)"
    alone = embedder.embed_passages(PASSAGES[:1])
    assert np.allclose(alone[0], out[0], atol=1e-3), "a text must give the same vector alone and in a batch"

    query = embedder.embed_queries([QUERY])
    assert query.shape == (1, dim), f"a query must give shape (1, {dim}), got {query.shape}"
    closer, farther = (float(query[0] @ out[0]), float(query[0] @ out[1]))
    assert closer > farther, ("an embedder must tell texts apart: a query about ships near the harbour must be closer to the "
                              f"passage about lighthouses ({closer:.3f}) than to the one about bananas ({farther:.3f})")
