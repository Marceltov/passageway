---
status: accepted
date: 2026-11-06
decision-makers: Marcel Bruckner (the direction), Claude (the write-up)
---

# Pieces fit the model, counted by the embedder

## Context and Problem Statement

The core cut sections into pieces of at most 1,500 characters and the model read at most 512 tokens of each, silently dropping the rest. On German federal law (106,468 provisions) 7.2 % of the pieces were longer than the model reads and 4.6 % of the text never reached the vectors; in 7,334 pieces the text alone was too long, because legal German runs at about three characters per token (#140). Text that is indexed but not embedded is half-found, and nothing reported it. How does the core make sure every word it indexes is also embedded?

## Considered Options

* A smaller character cap
* The connector cuts its own pieces
* The core cuts by the model's token count, which the embedder supplies

## Decision Outcome

Chosen option: "the core cuts by the model's token count, which the embedder supplies", because only the embedder knows its tokenizer and its limit, and only a count from that tokenizer can promise that nothing is cut.

- `Embedder` has `max_tokens` and `count_passages(texts)`: the tokens the model sees for each passage, its prefix and special tokens included. The built-in models answer from their tokenizer; a command embedder may name `max_tokens` in `info` and then answers `count` (an additive change to protocol v1).
- The chunker fills each piece up to the limit, cut at blank lines, then lines, sentences and words, and a word longer than the budget by tokens. A title and path that would take more than half the budget are shortened for embedding only.
- A piece over the limit is an error (the chunker checks every piece, the built-in embedder refuses one), never a cut.
- An embedder that does not count keeps the 1,500-character cap; `/health` shows `max_tokens: null` for it.
- `CHUNKER_VERSION` 3 rebuilds every index.

### Consequences

* Good, because every word of a source is embedded, with the built-in models and with any embedder that counts.
* Good, because a connector still sends sections of any length and stays out of model questions (V1).
* Bad, because counting costs time at indexing: about 90 seconds for the 106,468 provisions, small next to embedding them.
* Bad, because an embedder that does not count is still not checked against its limit; it is told so rather than silently trusted.

## Pros and Cons of the Options

### A smaller character cap

* Good, because it changes one number.
* Bad, because no character cap fits every language and every tokenizer: it would still cut dense text and waste room on light text.

### The connector cuts its own pieces

* Bad, because a connector cannot know which model the core runs, and V1 keeps model knowledge out of sources.
