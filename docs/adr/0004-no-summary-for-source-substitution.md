---
status: accepted
date: 2026-10-29
decision-makers: Marcel Bruckner (the rule), Claude (the write-up under the goal of building the roadmap to the end)
---

# A summary is a linked item, not a stand-in for its source

## Context and Problem Statement

trilium-recall showed a note's summary in place of its source note when the summary's own best passage matched almost as well (within 0.05 of cosine similarity), so that a reader got the short page and a pointer to the long one. The Trilium connector carries trilium-recall's sync over to passageway, whose core knows no source ([V1](../values.md#v1-the-core-knows-no-source-and-no-model-beyond-its-default)). Where does that rule go?

## Considered Options

* A protocol field that marks an item as "stands for" another, and ranking code in the core that substitutes it.
* The connector decides at indexing time which of the two to index.
* Both are indexed as items that link each other; the core shows the other as a related item of a hit, as it does for every link.

## Decision Outcome

Chosen option: "both are items that link each other", because the first option is a field only one connector would use and ranking code that behaves differently for one source's notion of a summary, which V1 rules out, and the second loses the source's detail. The summary carries a `wikiSource` relation to its source, and the connector adds the reverse link to the source, so a hit on either shows the other among its related items.

The cost is measured, not assumed: on trilium-recall's public fixture the connector scores hit@3 0.92 and silence 1.0 against trilium-recall's published 0.83 and 1.0; the one miss is the fixture's summary question, which the old rule had answered through the summary. If a real question set shows the loss to matter, a generic mechanism (an item's `weight` already exists; a "prefer the shorter of two linked items" rule would be the next candidate) is the way to bring it back, for every source.

### Consequences

* Good, because the core stays free of Trilium's notion of a summary, and every connector gets the same link behaviour.
* Good, because the measurement that decides whether the rule is missed is public and repeatable.
* Bad, because a question answered by a source's long text may show the source rather than its summary, and the summary only as a related item.
