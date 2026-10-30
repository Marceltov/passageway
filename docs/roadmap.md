---
hide:
  - toc
---

# Roadmap { .pw-center }

What is planned and what has shipped, from the [trilium-recall](https://github.com/Marceltov/trilium-recall) engine to a core that knows no source.
{: .pw-center .pw-lead }

<!-- roadmap -->

## Parked

Considered and wanted, not needed yet: publishing the SDK and the connectors to PyPI ([#28](https://github.com/Marceltov/passageway/issues/28), waits for a dependency that is not on PyPI); a reranker, and charts in evaluation reports, until a measurement shows what they would add ([V3](values.md#v3-numbers-are-measured-never-tuned)).

## Decided against

Generation or summarisation inside passageway (it returns passages only: [V4](values.md#v4-passages-not-answers)); stdio MCP, because the index and the sync loop must outlive a client session; per-connector access control, because one `recall` searches every source and the callers are one person's or one team's tools: index only what every caller may see; a service installer in v1.

## Keep it true

The timeline is rendered from [`docs/roadmap.yml`](https://github.com/Marceltov/passageway/blob/main/docs/roadmap.yml); on GitHub, read that file. Finish a step in the pull request that finishes it: set `status: done`, replace `when` with a `date`, add the link to its pull request, and move it to the top of the shipped entries. Change the file in the pull request that changes the plan.
