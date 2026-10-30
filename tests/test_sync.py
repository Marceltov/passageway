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


def test_small_sources_can_lose_one_item_but_not_everything(world, idx):
    world.set(items("a", "b", "c"))
    s = syncer(world, idx)
    s.full_build()
    world.set(items("a", "b"))  # 1 of 3 is above 30 %, but one item is never a bulk delete
    assert s.reconcile() == 1 and set(idx.versions()) == {"a", "b"}
    world.set([])  # all of a source with two or more items is refused
    assert s.reconcile() == 0 and set(idx.versions()) == {"a", "b"} and "refus" in s.status.last_error


def test_a_single_item_source_can_lose_its_item(world, idx):
    world.set(items("a"))
    s = syncer(world, idx)
    s.full_build()
    world.set([])
    assert s.reconcile() == 1 and idx.versions() == {} and s.status.last_error is None


def test_a_full_build_loads_the_version_map_once_not_per_batch(world, idx, monkeypatch):
    world.set(items(*[f"i{n}" for n in range(120)]))  # three fetch batches
    calls = []
    original = idx.versions
    monkeypatch.setattr(idx, "versions", lambda: calls.append(1) or original())
    syncer(world, idx).full_build()
    assert len(calls) == 1 and len(original()) == 120


def test_a_source_that_speaks_another_protocol_is_refused_at_start_and_keeps_its_old_index(world, idx):
    world.set(items("a"))
    syncer(world, idx).full_build()
    world.set(items("a", "b"))
    wrong = Syncer("w", world.connector(FAKE_PROTOCOL="2"), idx, HashEmbedder())
    wrong.full_build()
    assert "protocol" in wrong.status.last_error and wrong.status.last_ok is None
    assert idx.versions() == {"a": "1"}  # neither reset nor fetched


def test_the_start_asks_check_once_and_polls_and_reconciles_do_not(world, idx, monkeypatch):
    world.set(items("a"))
    s = syncer(world, idx)
    calls = []
    real = s.connector.check
    monkeypatch.setattr(s.connector, "check", lambda: calls.append(1) or real())
    s.full_build()
    s.reconcile()
    s.poll()
    assert len(calls) == 1


def _failing_fetch(s, monkeypatch, bad):
    import passageway.sync
    from passageway.protocol import ConnectorError
    monkeypatch.setattr(passageway.sync, "FETCH_BATCH", 1)
    asked, real = [], s.connector.fetch

    def fetch(ids):
        asked.append(ids[0])
        if ids[0] in bad:
            raise ConnectorError(f"connector 'w': fetch exited with status 1 ({ids[0]})")
        return real(ids)
    monkeypatch.setattr(s.connector, "fetch", fetch)
    return asked


def test_a_failing_fetch_batch_does_not_stop_the_batches_after_it(world, idx, monkeypatch):
    world.set(items("a", "b", "c", "d"))
    s = syncer(world, idx)
    _failing_fetch(s, monkeypatch, {"b"})
    s.full_build()
    assert set(idx.versions()) == {"a", "c", "d"}
    assert "(b)" in s.status.last_error and "1 of 4" in s.status.last_error and s.status.last_ok is None


def test_two_failing_fetch_batches_in_a_row_stop_the_fetch(world, idx, monkeypatch):
    world.set(items("a", "b", "c", "d"))
    s = syncer(world, idx)
    asked = _failing_fetch(s, monkeypatch, {"b", "c"})
    s.full_build()
    assert asked == ["a", "b", "c"] and set(idx.versions()) == {"a"} and "(b)" in s.status.last_error


def test_a_running_fetch_reports_how_far_it_is(world, idx, monkeypatch):
    world.set(items("a", "b", "c"))
    s = syncer(world, idx)
    import passageway.sync
    monkeypatch.setattr(passageway.sync, "FETCH_BATCH", 1)
    seen, real = [], s.connector.fetch

    def fetch(ids):
        seen.append((s.status.fetched, s.status.to_fetch))
        return real(ids)
    monkeypatch.setattr(s.connector, "fetch", fetch)
    s.full_build()
    assert seen == [(0, 3), (1, 3), (2, 3)]
    assert (s.status.fetched, s.status.to_fetch) == (None, None)
