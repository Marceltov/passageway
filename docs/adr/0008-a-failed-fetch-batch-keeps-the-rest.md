---
status: accepted
date: 2026-10-30
decision-makers: Marcel Bruckner (the direction), Claude (the write-up)
---

# A failed fetch batch does not keep the other batches out

## Context and Problem Statement

The core fetches changed items in batches of 50, and each `fetch` call stores everything or nothing. Until now the sync stopped at the first batch that failed. A page that fails on every run (one Confluence cannot render, or one that stays throttled) then failed its batch every time, and the items listed after it were never fetched: the source stayed partly indexed for good (#72, #78). How should one bad page cost less?

## Considered Options

* The core goes on after a failing batch and reports the first error at the end; two failures in a row stop it.
* The protocol lets `fetch` deliver the items it got and name the ones it could not, so even the failing batch stores its good items.
* A connector skips a page it cannot load and exits 0.

## Decision Outcome

Chosen option: "the core goes on after a failing batch", because it needs no protocol change (V9): every connector, bundled or not, benefits as it is, and a call still succeeds completely or stores nothing. Skipping in the connector was ruled out because the sync would report "ok" while a page is missing (V6). A per-item error in the protocol saves at most 49 items for one run, since the failed batch is fetched again at the next sync, and is not worth a protocol version.

### Consequences

* Good, because one bad page costs only its own batch, and `/health` still names the failure with a count (`1 of 4 fetch batches failed`).
* Good, because two failing batches in a row stop the fetch: a source that is down costs two call timeouts, not one per batch.
* Bad, because the good items in a failing batch wait for the next sync; if that matters, a per-item error is the next step and needs a protocol version.
* Only connector failures are skipped over. A failure in the index or the embedder still stops the sync at once, because it would repeat on every batch.
