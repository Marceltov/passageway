import pytest

from passageway.chunk import Chunk
from passageway.embed import HashEmbedder
from passageway.index import Index, ItemRecord
from passageway.rank import RankParams, rank

PARAMS = RankParams(min_cos=0.2)


@pytest.fixture
def emb():
    return HashEmbedder()


@pytest.fixture
def idx(tmp_path, emb):
    index = Index(tmp_path / "i.db", emb.name, emb.dim)

    def put(item_id, title, text, weight=1.0, links=(), path=()):
        rec = ItemRecord(item_id, title, f"http://x/{item_id}", "1", weight, list(path), [], None, list(links))
        index.upsert_item(rec, [Chunk("H", text, 0)], emb.embed_passages([f"{title}: {text}"]))

    index.put = put
    return index


def test_finds_the_matching_item_and_stays_silent_otherwise(idx, emb):
    idx.put("a", "Certificates", "rotate the signing certificate every year")
    idx.put("b", "Lunch", "pasta and salad on friday")
    hits = rank("s", idx, emb, "rotate signing certificate", params=PARAMS)
    assert [h.item_id for h in hits] == ["a"] and hits[0].url == "http://x/a" and hits[0].source == "s"
    assert rank("s", idx, emb, "zebra quantum", params=PARAMS) == []


def test_item_weight_reorders_equal_matches(idx, emb):
    idx.put("low", "Same words", "restart the proxmox host after the swap change", weight=0.6)
    idx.put("high", "Same words", "restart the proxmox host after the swap change", weight=1.0)
    assert [h.item_id for h in rank("s", idx, emb, "restart proxmox host swap", params=PARAMS)][0] == "high"


def test_one_hit_per_item_and_limit(idx, emb):
    for i in range(5):
        idx.put(f"i{i}", f"Doc {i}", "deploy the cluster with the helm chart")
    hits = rank("s", idx, emb, "deploy cluster helm chart", params=PARAMS, limit=2)
    assert len(hits) == 2 and len({h.item_id for h in hits}) == 2


def test_links_point_at_indexed_related_items_not_shown_as_hits(idx, emb):
    idx.put("a", "Alpha", "unique quokka words here", links=["b"])
    idx.put("b", "Beta", "something else entirely about trains")
    hit = rank("s", idx, emb, "unique quokka words", params=PARAMS)[0]
    assert hit.links == [("Beta", "http://x/b")]


def test_path_and_heading_reach_the_hit(idx, emb):
    idx.put("a", "Alpha", "quokka words", path=["Ops", "Sec"])
    hit = rank("s", idx, emb, "quokka words", params=PARAMS)[0]
    assert hit.path == ["Ops", "Sec"] and hit.heading == "H"
