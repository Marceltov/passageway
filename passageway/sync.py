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

    def _apply(self, items: list[Item], known: dict[str, str]) -> int:
        changed = 0
        for item in items:
            if known.get(item.id) == item.version:
                continue
            parts = chunks(item)
            vectors = self.embedder.embed_passages([passage_text(item, c) for c in parts])
            self.index.upsert_item(
                ItemRecord(item.id, item.title, item.url, item.version, item.weight, list(item.path),
                           list(item.labels), item.updated, list(item.links)),
                parts, vectors)
            changed += 1
        return changed

    def _fetch_and_apply(self, ids: list[str]) -> int:
        known = self.index.versions()  # once: the batches are disjoint, so it cannot go stale between them
        batches = [ids[i:i + FETCH_BATCH] for i in range(0, len(ids), FETCH_BATCH)]
        changed, errors, in_a_row = 0, [], 0
        for batch in batches:
            # a batch stores all or nothing; one that fails (a page that never loads) must not keep the rest
            # out, but two in a row mean the source is down: stop rather than wait out a timeout per batch
            try:
                fetched = self.connector.fetch(batch)
            except ConnectorError as e:
                errors.append(e)
                in_a_row += 1
                if in_a_row == 2:
                    break
                continue
            in_a_row = 0
            changed += self._apply(fetched, known)
        if errors:
            stopped = ", stopped after two in a row" if in_a_row == 2 else ""
            raise ConnectorError(f"{errors[0]} ({len(errors)} of {len(batches)} fetch batches failed{stopped})")
        return changed

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
            self.connector.check()  # once per start: refuses a connector that speaks another protocol version
            remote = self.connector.list_versions()  # list before reset: during an outage the old index keeps serving
            self.index.reset()
            return self._fetch_and_apply(list(remote))
        self._guarded(work)

    def reconcile(self) -> int:
        def work():
            remote = self.connector.list_versions()
            known = self.index.versions()
            gone = set(known) - set(remote)
            # One item is never a bulk delete; losing everything from a source of two or more is.
            if gone and (len(gone) > max(1, self._max_delete * len(known)) or (len(gone) == len(known) > 1)):
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
        return self._guarded(lambda: self._apply(self.connector.changed(since), self.index.versions()))
