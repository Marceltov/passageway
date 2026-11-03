---
hide:
  - navigation
  - toc
---

<div class="pw-hero" markdown>

# The answer is hidden somewhere across your sources. <span class="pw-teal">passageway</span> finds it.

<p class="pw-hero__lead">passageway searches all your sources at once, wiki, notes and documentation, and gives your agent exactly the passages that answer the question, each linked to its source.</p>

[Install and run](install.md){ .md-button .md-button--primary }
[Write a connector](guides/write-a-connector.md){ .md-button }

<div class="pw-hero__art" aria-hidden="true">
<svg viewBox="0 0 570 360" role="img" class="pw-anim">
<path class="pw-flow" d="M122,28 C205,28 205,180 270,180" id="pw-p0"/><path class="pw-flow" d="M122,104 C205,104 205,180 270,180" id="pw-p1"/><path class="pw-flow" d="M122,180 C205,180 205,180 270,180" id="pw-p2"/><path class="pw-flow" d="M122,256 C205,256 205,180 270,180" id="pw-p3"/><path class="pw-flow" d="M122,332 C205,332 205,180 270,180" id="pw-p4"/>
<path class="pw-flow pw-flow--out" d="M330,180 L436,180"/>
<g class="pw-node"><g transform="translate(0,11)"><rect width="122" height="34" rx="7"/><text x="61" y="22" text-anchor="middle">Confluence</text></g><g transform="translate(0,87)"><rect width="122" height="34" rx="7"/><text x="61" y="22" text-anchor="middle">Trilium</text></g><g transform="translate(0,163)"><rect width="122" height="34" rx="7"/><text x="61" y="22" text-anchor="middle">Markdown</text></g><g transform="translate(0,239)"><rect width="122" height="34" rx="7"/><text x="61" y="22" text-anchor="middle">Wikipedia</text></g><g transform="translate(0,315)"><rect width="122" height="34" rx="7"/><text x="61" y="22" text-anchor="middle">your connector</text></g></g>
<circle class="pw-dot" r="4.5"><animateMotion path="M122,28 C205,28 205,180 270,180" dur="4.5s" begin="-0.00s" repeatCount="indefinite">></animateMotion></circle><circle class="pw-dot" r="4.5"><animateMotion path="M122,28 C205,28 205,180 270,180" dur="4.5s" begin="-2.25s" repeatCount="indefinite">></animateMotion></circle><circle class="pw-dot" r="4.5"><animateMotion path="M122,104 C205,104 205,180 270,180" dur="4.5s" begin="-0.70s" repeatCount="indefinite">></animateMotion></circle><circle class="pw-dot" r="4.5"><animateMotion path="M122,104 C205,104 205,180 270,180" dur="4.5s" begin="-2.95s" repeatCount="indefinite">></animateMotion></circle><circle class="pw-dot" r="4.5"><animateMotion path="M122,180 C205,180 205,180 270,180" dur="4.5s" begin="-1.40s" repeatCount="indefinite">></animateMotion></circle><circle class="pw-dot" r="4.5"><animateMotion path="M122,180 C205,180 205,180 270,180" dur="4.5s" begin="-3.65s" repeatCount="indefinite">></animateMotion></circle><circle class="pw-dot" r="4.5"><animateMotion path="M122,256 C205,256 205,180 270,180" dur="4.5s" begin="-2.10s" repeatCount="indefinite">></animateMotion></circle><circle class="pw-dot" r="4.5"><animateMotion path="M122,256 C205,256 205,180 270,180" dur="4.5s" begin="-4.35s" repeatCount="indefinite">></animateMotion></circle><circle class="pw-dot" r="4.5"><animateMotion path="M122,332 C205,332 205,180 270,180" dur="4.5s" begin="-2.80s" repeatCount="indefinite">></animateMotion></circle><circle class="pw-dot" r="4.5"><animateMotion path="M122,332 C205,332 205,180 270,180" dur="4.5s" begin="-5.05s" repeatCount="indefinite">></animateMotion></circle><rect class="pw-dot pw-dot--out" width="14" height="9" x="-7" y="-4.5" rx="2"><animateMotion dur="2.4s" begin="0.0s" repeatCount="indefinite" path="M330,180 L436,180"/></rect><rect class="pw-dot pw-dot--out" width="14" height="9" x="-7" y="-4.5" rx="2"><animateMotion dur="2.4s" begin="-0.8s" repeatCount="indefinite" path="M330,180 L436,180"/></rect><rect class="pw-dot pw-dot--out" width="14" height="9" x="-7" y="-4.5" rx="2"><animateMotion dur="2.4s" begin="-1.6s" repeatCount="indefinite" path="M330,180 L436,180"/></rect>
<g transform="translate(270,150)"><rect class="pw-core" width="60" height="60" rx="13"/><path class="pw-arch" d="M18,44 V28 a12,12 0 0 1 24,0 V44"/></g>
<g class="pw-node" transform="translate(436,163)"><rect width="134" height="34" rx="7"/><text x="67" y="22" text-anchor="middle">your agent</text></g>
</svg>
</div>

</div>

<div class="grid cards" markdown>

- **On premise.** Your knowledge stays on your infrastructure.

    [Run it yourself](deploy.md)

- **Connected.** Confluence, Trilium, Markdown and Wikipedia work out of the box.

    [See the connectors](connectors/confluence.md)

- **Open.** A documented protocol lets you add any source or embedding model, in any language.

    [Read the protocol](reference/connector-protocol.md)

</div>

Free for private use. Companies need a licence. [Details](licence.md)

## How it fits together

```mermaid
flowchart LR
  S["<b>Your sources</b><br/>Confluence<br/>Trilium<br/>Markdown<br/>Wikipedia<br/>your own connector"]
  subgraph P["passageway, on your machine"]
    I[("Index<br/>keywords + vectors")] --> R["Ranking and<br/>relevance gate"]
  end
  S -- "JSON Lines" --> I
  R -- "passages with<br/>source links" --> G["<b>Your agent</b><br/>writes the answer"]
```

passageway is the retrieval half of a RAG system, served as an MCP tool. It does no generation: the agent that calls it reads the passages and writes the answer. [How it works](how-it-works.md)

<div class="grid cards" markdown>

- **The core knows no source.** A connector is any executable that prints items as JSON Lines.
- **Quiet on purpose.** A relevance gate returns nothing instead of padding a prompt with weak matches.
- **Measured.** Right article in the top three for 88.6% (95% interval 79–94%) of 70 questions on a sample corpus. [The method and its limits](measurements.md)

</div>

## Start

<div class="grid cards" markdown>

- [**Install in Claude Code**](install.md): the plugin sets up the server, the sources and the hook for you.
- [**Add a source**](connectors/markdown.md): [Markdown](connectors/markdown.md), [Trilium](connectors/trilium.md), [Confluence](connectors/confluence.md), [Wikipedia](connectors/wikipedia.md), [llms.txt](connectors/llmstxt.md), [Sitemap](connectors/sitemap.md).
- [**Measure your own notes**](guides/evaluate.md): `passageway eval` on your questions, and [choose a model](models.md).

</div>

[What passageway stands for](values.md) and the [roadmap](roadmap.md), for what is planned.
