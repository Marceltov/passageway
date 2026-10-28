import pytest

from passageway.chunk import Chunk
from passageway.embed import HashEmbedder
from passageway.index import Index, ItemRecord


def rec(item_id="a", title="Alpha", version="1", weight=1.0, links=()):
    return ItemRecord(item_id, title, f"http://x/{item_id}", version, weight, ["Ops"], ["decision"], None, list(links))


@pytest.fixture
def emb():
    return HashEmbedder()


@pytest.fixture
def idx(tmp_path, emb):
    return Index(tmp_path / "i.db", emb.name, emb.dim)


def put(idx, emb, record, *texts):
    chunks = [Chunk("H", t, i) for i, t in enumerate(texts)]
    idx.upsert_item(record, chunks, emb.embed_passages([f"{record.title}: {t}" for t in texts]))


def test_roundtrip_and_versions(idx, emb):
    put(idx, emb, rec("a", version="3"), "rotate the signing certificate", "second section")
    got = idx.item("a")
    assert (got.title, got.version, got.weight, got.path, got.labels) == ("Alpha", "3", 1.0, ["Ops"], ["decision"])
    assert idx.versions() == {"a": "3"} and idx.counts() == (1, 2)


def test_item_without_sections_is_still_recorded(idx, emb):
    put(idx, emb, rec("empty", version="9"))
    assert idx.versions() == {"empty": "9"} and idx.counts() == (1, 0)


def test_fts_and_vector_search_find_the_section(idx, emb):
    put(idx, emb, rec("a"), "rotate the signing certificate every year")
    put(idx, emb, rec("b", "Beta"), "cafeteria opens at noon")
    assert idx.fts_search("signing certificate")[0].item_id == "a"
    q = emb.embed_queries(["signing certificate"])[0]
    assert idx.vec_search(q, 1)[0].item_id == "a"


def test_upsert_replaces_sections_and_delete_removes_everything(idx, emb):
    put(idx, emb, rec("a"), "old words zebra")
    put(idx, emb, rec("a", version="2"), "new words")
    assert not idx.fts_search("zebra") and idx.versions() == {"a": "2"}
    idx.delete_item("a")
    assert idx.counts() == (0, 0) and idx.item("a") is None and not idx.fts_search("new")


def test_links_return_only_indexed_targets(idx, emb):
    put(idx, emb, rec("a", links=["b", "gone"]), "text a")
    put(idx, emb, rec("b", "Beta"), "text b")
    assert idx.links("a") == [("b", "Beta", "http://x/b")]


def test_changed_embedder_requires_rebuild(tmp_path, emb):
    first = Index(tmp_path / "i.db", "model-1", emb.dim)
    put(first, emb, rec("a"), "text")
    assert not first.needs_rebuild()
    other = Index(tmp_path / "i.db", "model-2", emb.dim)
    assert other.needs_rebuild()
    other.reset()
    assert other.counts() == (0, 0) and not other.needs_rebuild()
