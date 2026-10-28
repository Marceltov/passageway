import json
import sys

import pytest

from passageway.embed import HashEmbedder
from passageway.index import Index
from passageway.protocol import Connector
from passageway.sync import Syncer


def items(*ids, version="1"):
    return [{"id": i, "title": f"Doc {i}", "url": f"http://x/{i}", "version": version, "updated": "2026-10-28T10:00:00Z",
             "sections": [{"heading": "H", "text": f"body of {i} zebra{i}"}]} for i in ids]


class World:
    def __init__(self, tmp_path):
        self.file = tmp_path / "items.json"
        self.set([])
        self.env = {"FAKE_ITEMS": str(self.file)}

    def set(self, data):
        self.file.write_text(json.dumps(data))

    def connector(self, **env):
        return Connector("w", [sys.executable, "-m", "passageway.testing.fake_connector"], env={**self.env, **env})


@pytest.fixture
def world(tmp_path):
    return World(tmp_path)


@pytest.fixture
def idx(tmp_path):
    e = HashEmbedder()
    return Index(tmp_path / "i.db", e.name, e.dim)


def syncer(world, idx, **kw):
    return Syncer("w", world.connector(), idx, HashEmbedder(), **kw)


def test_full_build_indexes_everything_and_sets_status(world, idx):
    world.set(items("a", "b"))
    s = syncer(world, idx)
    s.full_build()
    assert idx.versions() == {"a": "1", "b": "1"} and idx.fts_search("zebraa")
    assert s.status.items == 2 and s.status.last_error is None and s.status.last_ok


def test_reconcile_deletes_gone_items_and_fetches_new_ones(world, idx):
    world.set(items("a", "b", "c", "d"))
    s = syncer(world, idx)
    s.full_build()
    world.set(items("a", "b", "c"))  # d is gone: 25 % is below the guard
    assert s.reconcile() == 1 and "d" not in idx.versions()
    world.set(items("a", "b", "c", "e"))
    assert s.reconcile() == 1 and idx.fts_search("zebrae")


def test_unchanged_versions_are_not_refetched(world, idx):
    world.set(items("a"))
    s = syncer(world, idx)
    s.full_build()
    assert s.reconcile() == 0


def test_deletion_guard_refuses_to_wipe_or_halve_the_index(world, idx):
    world.set(items("a", "b", "c", "d"))
    s = syncer(world, idx)
    s.full_build()
    world.set([])
    assert s.reconcile() == 0 and len(idx.versions()) == 4 and "refus" in s.status.last_error
    world.set(items("a", "b"))  # 50 % gone
    assert s.reconcile() == 0 and len(idx.versions()) == 4
    world.set(items("a", "b", "c"))  # 25 % gone is allowed
    assert s.reconcile() == 1 and len(idx.versions()) == 3


def test_poll_applies_changed_items_without_deleting(world, idx):
    world.set(items("a", "b"))
    s = syncer(world, idx)
    s.full_build()
    world.set([{**items("a")[0], "version": "2", "updated": "2099-01-01T00:00:00Z",
                "sections": [{"heading": "H", "text": "now narwhal"}]}])
    assert s.poll() == 1 and idx.versions()["a"] == "2" and idx.fts_search("narwhal")
    assert set(idx.versions()) == {"a", "b"}  # b not listed by poll: untouched


def test_failing_connector_keeps_the_old_index_and_reports(world, idx):
    world.set(items("a"))
    good = syncer(world, idx)
    good.full_build()
    bad = Syncer("w", world.connector(FAKE_FAIL="list"), idx, HashEmbedder())
    assert bad.reconcile() == 0
    assert "fake failure" in bad.status.last_error and idx.versions() == {"a": "1"}


def test_item_without_sections_is_stored_and_not_refetched(world, idx):
    world.set([{"id": "e", "title": "Empty", "url": "u", "version": "1", "sections": []}])
    s = syncer(world, idx)
    s.full_build()
    assert idx.versions() == {"e": "1"} and s.reconcile() == 0


def test_any_failure_is_recorded_and_never_raised(world, idx, monkeypatch):
    import sqlite3
    world.set(items("a"))
    s = syncer(world, idx)
    s.full_build()

    def boom():
        raise sqlite3.OperationalError("disk I/O error")

    monkeypatch.setattr(idx, "versions", boom)
    assert s.poll() == 0 and "disk I/O error" in s.status.last_error
