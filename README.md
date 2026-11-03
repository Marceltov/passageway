# passageway

**The answer is hidden somewhere across your sources. passageway finds it.**

passageway searches all your sources at once, wiki, notes and documentation, and gives your agent exactly the passages that answer the question, each linked to its source.

- **On premise.** Your knowledge stays on your infrastructure.
- **Connected.** Confluence, Trilium, Markdown and Wikipedia work out of the box.
- **Open.** A documented protocol lets you add any source or embedding model, in any language.

Free for private use. Companies need a licence ([details](docs/licence.md)); trying it at work for fewer than 32 days is covered by the PolyForm Free Trial licence (`LICENSE-FREE-TRIAL`).

It serves the passages as one `recall` tool over MCP, stays silent when nothing is relevant enough, and does no generation: the calling agent reads the passages. An [eval harness](docs/guides/evaluate.md) (`passageway eval`) measures retrieval quality on your own questions, so you can publish the numbers.

- [Install and run](docs/install.md) and [configuration](docs/configuration.md)
- [How it works](docs/how-it-works.md)
- [What passageway stands for](docs/values.md): the yardstick for every change
- [Run it](docs/deploy.md) as a local service or as the container `ghcr.io/getpassageway/passageway`; in [Claude Code](docs/guides/claude-code.md), the plugin installs and connects it for you and brings the prompt hook
- [Write a connector](docs/guides/write-a-connector.md), the [connector protocol](docs/reference/connector-protocol.md) and the [Python SDK](docs/reference/sdk.md) that does its plumbing
- Bundled connectors: [Wikipedia](connectors/wikipedia/README.md), [Markdown](connectors/markdown/README.md), [llms.txt](connectors/llmstxt/README.md), [Sitemap](connectors/sitemap/README.md), [Trilium](connectors/trilium/README.md), [Confluence](connectors/confluence/README.md); bundled embedder: [OpenAI-compatible](embedders/openai/README.md)
- For AI agents: [skills and `llms-full.txt`](docs/guides/agents.md); in Claude Code, `/plugin marketplace add getpassageway/passageway` and `/plugin install passageway@passageway` give you the plugin, then `/passageway-install` sets everything up

Documentation: the pages in `docs/`, will be published at https://passageway.marceltov.de.

Status: early. The engine started as the recall engine of [trilium-recall](https://github.com/Marceltov/trilium-recall) and is being generalized. The code is source-available under the PolyForm Noncommercial License 1.0.0 (free for private use; companies need a licence), and the SDK is MIT; the Wikipedia articles of the sample corpus in `corpus/` are CC BY-SA 4.0 (see `corpus/LICENSE.md`).

## Contact

marcel@marceltov.de
