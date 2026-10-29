"""Hybrid ranking: FTS5 + vectors fused by reciprocal rank, scaled by item weight, gated by relevance."""

import re
from dataclasses import dataclass
from pathlib import PurePosixPath

import numpy as np

from passageway.embed import Embedder
from passageway.index import Index, SectionHit, fold, query_terms

EMBED_QUERY_CHARS = 2000
PASSAGE_CHARS = 240
GENERIC_PATH_PARTS = {"root", "home", "src", "app", "repo", "repos", "code", "projects", "workspace", "users",
                      "tmp", "git", "dev", "work"}


@dataclass
class RankParams:
    rrf_k: int = 60
    cos_weight: float = 1.0
    rrf_weight: float = 20.0
    context_boost: float = 0.05
    # e5 similarities sit in a narrow band: live matches 0.85-0.94, unrelated questions 0.79-0.86.
    min_cos: float = 0.845
    bm25_rescue_min_terms: int = 3
    top_n: int = 3
    max_links: int = 3
    candidates: int = 50


@dataclass
class Hit:
    source: str
    item_id: str
    title: str
    url: str
    labels: list[str]
    path: list[str]
    heading: str
    passage: str
    score: float
    links: list[tuple[str, str]]  # (title, url) of related indexed items


@dataclass
class _Candidate:
    section: SectionHit
    cos: float = 0.0
    rrf: float = 0.0
    matched_terms: int = 0


def context_terms(cwd: str | None) -> list[str]:
    """Words from the last two meaningful folder names of the working directory.

    The engine cannot see the client's filesystem, so this works on the path string only.
    """
    if not cwd:
        return []
    parts = [p for p in reversed(PurePosixPath(cwd).parts) if p not in ("/", "") and p.lower() not in GENERIC_PATH_PARTS]
    out: list[str] = []
    for part in parts[:2]:
        for word in re.split(r"[-_.\s]+", part.lower()):
            if word and word not in GENERIC_PATH_PARTS and word not in out:
                out.append(word)
    return out


def _passage(text: str, words: list[str]) -> str:
    if len(text) <= PASSAGE_CHARS:
        return text
    folded = fold(text)
    starts = [m.start() for t in words if (m := re.search(rf"\b{re.escape(t)}\b", folded))]
    anchor = min(starts) if starts else 0
    start = max(0, anchor - PASSAGE_CHARS // 3)
    end = min(len(text), start + PASSAGE_CHARS)
    start = max(0, end - PASSAGE_CHARS)
    # Snap to word boundaries.
    if start > 0:
        space = text.find(" ", start)
        start = space + 1 if 0 <= space < anchor else start
    if end < len(text):
        space = text.rfind(" ", start, end)
        end = space if space > start else end
    return ("…" if start > 0 else "") + text[start:end].strip() + ("…" if end < len(text) else "")


def embed_query(embedder: Embedder, query: str) -> np.ndarray:
    return embedder.embed_queries([query[:EMBED_QUERY_CHARS]])[0]


def _gather(index: Index, embedder: Embedder, query: str, params: RankParams,
            qvec: np.ndarray | None = None) -> tuple[dict[int, _Candidate], np.ndarray]:
    if qvec is None:
        qvec = embed_query(embedder, query)
    candidates: dict[int, _Candidate] = {}
    for rank_, hit in enumerate(index.fts_search(query, params.candidates)):
        c = candidates.setdefault(hit.section_id, _Candidate(hit))
        c.rrf += 1 / (params.rrf_k + rank_ + 1)
        c.matched_terms = hit.matched_terms
    for rank_, hit in enumerate(index.vec_search(qvec, params.candidates)):
        c = candidates.setdefault(hit.section_id, _Candidate(hit))
        c.rrf += 1 / (params.rrf_k + rank_ + 1)
    vectors = index.section_vectors(list(candidates))
    for sid, c in candidates.items():
        if sid in vectors:
            c.cos = float(vectors[sid] @ qvec)
    return candidates, qvec


def rank(source: str, index: Index, embedder: Embedder, query: str, cwd: str | None = None,
         params: RankParams = RankParams(), limit: int = 3, qvec: np.ndarray | None = None) -> list[Hit]:
    words = query_terms(query)
    candidates, _ = _gather(index, embedder, query, params, qvec)
    if not candidates:
        return []
    ctx = context_terms(cwd)
    records: dict[str, object] = {}

    def record(item_id: str):
        if item_id not in records:
            records[item_id] = index.item(item_id)
        return records[item_id]

    best: dict[str, tuple[float, _Candidate]] = {}
    for c in candidates.values():
        rec = record(c.section.item_id)
        if rec is None:
            continue
        score = rec.weight * (params.cos_weight * c.cos + params.rrf_weight * c.rrf)
        if ctx and any(t in fold(" ".join([rec.title, *rec.path, *rec.labels])) for t in ctx):
            score += params.context_boost
        if rec.item_id not in best or score > best[rec.item_id][0]:
            best[rec.item_id] = (score, c)

    hits: list[Hit] = []
    for item_id, (score, c) in sorted(best.items(), key=lambda kv: -kv[1][0]):
        if len(hits) >= min(limit, params.top_n):
            break
        if not (c.cos >= params.min_cos or c.matched_terms >= params.bm25_rescue_min_terms):
            continue
        rec = record(item_id)
        hits.append(Hit(source, item_id, rec.title, rec.url, rec.labels, rec.path, c.section.heading,
                        _passage(c.section.text, words), score, []))

    shown = {h.item_id for h in hits}
    candidate_items = {c.section.item_id for c in candidates.values()}
    for hit in hits:
        related = [(i, t, u) for i, t, u in index.links(hit.item_id) if i not in shown]
        for _, title, url in sorted(related, key=lambda r: (r[0] not in candidate_items, r[0]))[:params.max_links]:
            hit.links.append((title, url))
    return hits
