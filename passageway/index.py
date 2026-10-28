"""One SQLite file per source: items, sections, FTS5, sqlite-vec vectors and links.

Fully rebuildable from the connector, so deleting the file is always safe.
"""

import contextlib
import json
import re
import sqlite3
import threading
import unicodedata
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import sqlite_vec

from passageway.chunk import Chunk

CHUNKER_VERSION = 2
SCHEMA_VERSION = 2
MAX_QUERY_TERMS = 64
# Function words in English and German: they match everywhere and say nothing about the topic.
STOPWORDS = frozenset("""
a an and are as at be been but by can could did do does doing for from had has have how i if in into is it
its me my no not of on or our please should so than that the their them then there these they this to
us was we were what when where which who why will with would you your yes ok okay let lets just also
make get got about like any some
der die das den dem des ein eine einen einem einer eines und oder aber ist sind war waren bin bist hat
haben hatte ich du er sie es wir ihr mich mir dich dir uns euch sich mein meine dein wie was wo wann warum
wer welche welcher welches nicht kein keine mit von zu zum zur auf an am im in aus bei nach vor fur uber
unter um als auch noch schon nur so dass da dann denn doch ja nein mal bitte kann konnen soll sollte muss
mache machen wird werden wurde
""".split())


@dataclass
class ItemRecord:
    item_id: str
    title: str
    url: str
    version: str
    weight: float
    path: list[str]
    labels: list[str]
    updated: str | None
    links: list[str]  # ids of related items


@dataclass
class SectionHit:
    section_id: int
    item_id: str
    heading: str
    text: str
    score: float  # bm25 (lower is better) for FTS hits, cosine similarity for vector hits
    matched_terms: int = 0  # distinct query terms found in the section (FTS hits only)


def fold(s: str) -> str:
    """Lower-case and strip diacritics, the way the FTS tokenizer (remove_diacritics 2) does."""
    decomposed = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in decomposed if not unicodedata.combining(c))


def terms(s: str) -> list[str]:
    return re.findall(r"\w+", fold(s))


def query_terms(s: str) -> list[str]:
    """Distinct content words of a query, in order."""
    return list(dict.fromkeys(t for t in terms(s) if t not in STOPWORDS))


class Index:
    def __init__(self, path: Path, embedder_name: str, dim: int):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._meta = {"embedder": embedder_name, "dim": str(dim),
                      "chunker": str(CHUNKER_VERSION), "schema": str(SCHEMA_VERSION)}
        self._dim = dim
        self.lock = threading.RLock()
        self._db = sqlite3.connect(self.path, check_same_thread=False, isolation_level=None)
        self._db.enable_load_extension(True)
        sqlite_vec.load(self._db)
        self._db.enable_load_extension(False)
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")
        if not self._stored_meta():
            self._create()

    @contextlib.contextmanager
    def _tx(self):
        """One transaction under the lock: commit on success, roll back on any error."""
        with self.lock:
            self._db.execute("BEGIN")
            try:
                yield
            except BaseException:
                self._db.execute("ROLLBACK")
                raise
            self._db.execute("COMMIT")

    # -- schema ------------------------------------------------------------------------------

    def _stored_meta(self) -> dict[str, str]:
        return dict(self._db.execute("SELECT key, value FROM meta").fetchall())

    def _create(self) -> None:
        with self._tx():
            db = self._db
            for table in ("items", "sections", "links", "sections_fts", "sections_vocab", "sections_vec"):
                db.execute(f"DROP TABLE IF EXISTS {table}")
            db.execute("""CREATE TABLE items (item_id TEXT PRIMARY KEY, title TEXT, url TEXT, version TEXT,
                          weight REAL, path TEXT, labels TEXT, updated TEXT)""")
            db.execute("""CREATE TABLE sections (id INTEGER PRIMARY KEY, item_id TEXT, ordinal INTEGER,
                          heading TEXT, text TEXT)""")
            db.execute("CREATE INDEX sections_item ON sections(item_id)")
            db.execute("CREATE TABLE links (src TEXT, dst TEXT)")
            db.execute("CREATE INDEX links_src ON links(src)")
            # '_' joins identifiers like wiki_type; '-' and '.' stay separators so "swap." matches "swap".
            db.execute("""CREATE VIRTUAL TABLE sections_fts USING fts5(title, heading, text,
                          tokenize="unicode61 remove_diacritics 2 tokenchars '_'")""")
            db.execute("CREATE VIRTUAL TABLE sections_vocab USING fts5vocab(sections_fts, row)")
            db.execute(f"""CREATE VIRTUAL TABLE sections_vec USING vec0(
                           embedding float[{self._dim}] distance_metric=cosine)""")
            db.execute("DELETE FROM meta")
            db.executemany("INSERT INTO meta VALUES (?, ?)", self._meta.items())

    def needs_rebuild(self) -> bool:
        return self._stored_meta() != self._meta

    def reset(self) -> None:
        self._create()

    # -- writes ------------------------------------------------------------------------------

    def _delete_sections(self, item_id: str) -> None:
        ids = [r[0] for r in self._db.execute("SELECT id FROM sections WHERE item_id = ?", (item_id,))]
        for sid in ids:
            self._db.execute("DELETE FROM sections_fts WHERE rowid = ?", (sid,))
            self._db.execute("DELETE FROM sections_vec WHERE rowid = ?", (sid,))
        self._db.execute("DELETE FROM sections WHERE item_id = ?", (item_id,))

    def upsert_item(self, rec: ItemRecord, chunks: list[Chunk], vectors: np.ndarray) -> None:
        assert len(chunks) == len(vectors)
        with self._tx():
            self._delete_sections(rec.item_id)
            self._db.execute("INSERT OR REPLACE INTO items VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                             (rec.item_id, rec.title, rec.url, rec.version, rec.weight,
                              json.dumps(rec.path), json.dumps(rec.labels), rec.updated))
            self._db.execute("DELETE FROM links WHERE src = ?", (rec.item_id,))
            self._db.executemany("INSERT INTO links VALUES (?, ?)", [(rec.item_id, dst) for dst in rec.links])
            for chunk, vector in zip(chunks, vectors):
                cur = self._db.execute(
                    "INSERT INTO sections (item_id, ordinal, heading, text) VALUES (?, ?, ?, ?)",
                    (rec.item_id, chunk.ordinal, chunk.heading, chunk.text))
                sid = cur.lastrowid
                self._db.execute("INSERT INTO sections_fts (rowid, title, heading, text) VALUES (?, ?, ?, ?)",
                                 (sid, rec.title, chunk.heading, chunk.text))
                self._db.execute("INSERT INTO sections_vec (rowid, embedding) VALUES (?, ?)",
                                 (sid, sqlite_vec.serialize_float32(np.asarray(vector, dtype=np.float32))))

    def delete_item(self, item_id: str) -> None:
        with self._tx():
            self._delete_sections(item_id)
            self._db.execute("DELETE FROM items WHERE item_id = ?", (item_id,))
            self._db.execute("DELETE FROM links WHERE src = ?", (item_id,))

    # -- reads -------------------------------------------------------------------------------

    def item(self, item_id: str) -> ItemRecord | None:
        with self.lock:
            row = self._db.execute("SELECT * FROM items WHERE item_id = ?", (item_id,)).fetchone()
            dst = [r[0] for r in self._db.execute("SELECT dst FROM links WHERE src = ?", (item_id,))]
        if row is None:
            return None
        return ItemRecord(row[0], row[1], row[2], row[3], row[4], json.loads(row[5]), json.loads(row[6]), row[7], dst)

    def versions(self) -> dict[str, str]:
        with self.lock:
            return dict(self._db.execute("SELECT item_id, version FROM items"))

    def counts(self) -> tuple[int, int]:
        with self.lock:
            return (self._db.execute("SELECT count(*) FROM items").fetchone()[0],
                    self._db.execute("SELECT count(*) FROM sections").fetchone()[0])

    def links(self, item_id: str) -> list[tuple[str, str, str]]:
        """(id, title, url) of the items this one links to that are indexed."""
        with self.lock:
            return self._db.execute(
                "SELECT i.item_id, i.title, i.url FROM links l JOIN items i ON i.item_id = l.dst "
                "WHERE l.src = ? ORDER BY i.item_id", (item_id,)).fetchall()

    def _query_terms(self, query: str) -> list[str]:
        unique = query_terms(query)
        if len(unique) <= MAX_QUERY_TERMS:
            return unique
        placeholders = ",".join("?" * len(unique))
        df = dict(self._db.execute(f"SELECT term, doc FROM sections_vocab WHERE term IN ({placeholders})", unique))
        known = [t for t in unique if t in df]
        return sorted(known, key=lambda t: df[t])[:MAX_QUERY_TERMS]

    def fts_search(self, query: str, k: int = 50) -> list[SectionHit]:
        with self.lock:
            terms_ = self._query_terms(query)
            if not terms_:
                return []
            match = " OR ".join(f'"{t}"' for t in terms_)
            rows = self._db.execute(
                """SELECT s.id, s.item_id, s.heading, s.text, bm25(sections_fts, 5.0, 2.0, 1.0) AS rank,
                          f.title, f.heading
                   FROM sections_fts f JOIN sections s ON s.id = f.rowid
                   WHERE sections_fts MATCH ? ORDER BY rank LIMIT ?""", (match, k)).fetchall()
        hits = []
        for sid, item_id, heading, text, rank, title, fts_heading in rows:
            present = set(terms(f"{title} {fts_heading} {text}"))
            hits.append(SectionHit(sid, item_id, heading, text, rank, sum(t in present for t in terms_)))
        return hits

    def vec_search(self, vector: np.ndarray, k: int = 50) -> list[SectionHit]:
        with self.lock:
            rows = self._db.execute(
                """SELECT s.id, s.item_id, s.heading, s.text, v.distance
                   FROM (SELECT rowid, distance FROM sections_vec WHERE embedding MATCH ? AND k = ?) v
                   JOIN sections s ON s.id = v.rowid ORDER BY v.distance""",
                (sqlite_vec.serialize_float32(np.asarray(vector, dtype=np.float32)), k)).fetchall()
        return [SectionHit(sid, item_id, heading, text, 1.0 - dist) for sid, item_id, heading, text, dist in rows]

    def item_sections(self, item_id: str) -> list[SectionHit]:
        """All sections of an item in order, as hits with score 0."""
        with self.lock:
            rows = self._db.execute("SELECT id, heading, text FROM sections WHERE item_id = ? ORDER BY ordinal",
                                    (item_id,)).fetchall()
        return [SectionHit(sid, item_id, heading, text, 0.0) for sid, heading, text in rows]

    def section_vectors(self, section_ids: list[int]) -> dict[int, np.ndarray]:
        if not section_ids:
            return {}
        with self.lock:
            placeholders = ",".join("?" * len(section_ids))
            rows = self._db.execute(f"SELECT rowid, embedding FROM sections_vec WHERE rowid IN ({placeholders})",
                                    section_ids).fetchall()
        return {sid: np.frombuffer(blob, dtype=np.float32) for sid, blob in rows}
