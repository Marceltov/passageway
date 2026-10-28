"""Keeps one source's Index in step with its connector: full build, reconcile, incremental poll."""

import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from passageway.chunk import chunks, passage_text
from passageway.embed import Embedder
from passageway.index import Index, ItemRecord
from passageway.protocol import Connector, ConnectorError, Item

log = logging.getLogger(__name__)

POLL_MARGIN = timedelta(seconds=120)  # overlap between polls; items with an unchanged version are skipped
FETCH_BATCH = 50


@dataclass
class SyncStatus:
    last_ok: datetime | None = None
    last_error: str | None = None
    items: int = 0
    sections: int = 0


class Syncer:
    def __init__(self, name: str, connector: Connector, index: Index, embedder: Embedder,
                 *, max_delete_fraction: float = 0.3):
        self.name = name
        self.connector = connector
        self.index = index
        self.embedder = embedder
        self.status = SyncStatus()
        self._max_delete = max_delete_fraction
        self._cursor: datetime | None = None

    # -- applying ----------------------------------------------------------------------------

    def _apply(self, items: list[Item]) -> int:
        known = self.index.versions()
        changed = 0
        for item in items:
            if known.get(item.id) == item.version:
                continue
            parts = chunks(item)
            vectors = self.embedder.embed_passages([passage_text(item, c) for c in parts])
            self.index.upsert_item(
                ItemRecord(item.id, item.title, item.url, item.version, item.weight, list(item.path),
                           list(item.labels), item.updated, [link_id for link_id, _ in item.links]),
                parts, vectors)
            changed += 1
        return changed

    def _fetch_and_apply(self, ids: list[str]) -> int:
        return sum(self._apply(self.connector.fetch(ids[i:i + FETCH_BATCH])) for i in range(0, len(ids), FETCH_BATCH))

    def _guarded(self, work) -> int:
        started = datetime.now(UTC)
        try:
            changed = work()
        except Exception as e:  # never let one source's failure (a sqlite error too) stop the others
            self.status.last_error = f"{type(e).__name__}: {e}"
            log.warning("sync %s failed: %s", self.name, self.status.last_error, exc_info=not isinstance(e, ConnectorError))
            return 0
        self._cursor = started
        self.status.last_ok = started
        self.status.last_error = None
        self.status.items, self.status.sections = self.index.counts()
        return changed

    # -- public ------------------------------------------------------------------------------

    def full_build(self) -> None:
        def work():
            remote = self.connector.list_versions()  # list before reset: during an outage the old index keeps serving
            self.index.reset()
            return self._fetch_and_apply(list(remote))
        self._guarded(work)

    def reconcile(self) -> int:
        def work():
            remote = self.connector.list_versions()
            known = self.index.versions()
            gone = set(known) - set(remote)
            if gone and (len(gone) == len(known) or len(gone) / len(known) > self._max_delete):
                raise ConnectorError(f"refusing to delete {len(gone)} of {len(known)} items: "
                                     f"the listing looks incomplete")
            changed = self._fetch_and_apply([i for i, v in remote.items() if known.get(i) != v])
            for item_id in gone:
                self.index.delete_item(item_id)
            return changed + len(gone)
        return self._guarded(work)

    def poll(self) -> int:
        if self._cursor is None:
            return self.reconcile()
        since = self._cursor - POLL_MARGIN
        return self._guarded(lambda: self._apply(self.connector.changed(since)))
