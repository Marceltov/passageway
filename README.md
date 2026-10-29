# passageway

Retrieval for Claude over MCP. passageway indexes what your **connectors** report, finds the best short passages for a question with keyword plus embedding search, and serves them as one `recall` tool. It stays silent when nothing is relevant enough. It does no generation: the calling model reads the passages.

The core knows no source. A connector is any executable that lists items and returns their text as JSON Lines; anyone can write one. An [eval harness](docs/guides/evaluate.md) (`passageway eval`) measures retrieval quality on your own questions, and compares embedding models, so you can publish the numbers.

- [Install and run](docs/install.md) and [configuration](docs/configuration.md)
- [How it works](docs/how-it-works.md)
- [What passageway stands for](docs/values.md): the yardstick for every change
- [Write a connector](docs/guides/write-a-connector.md), the [connector protocol](docs/reference/connector-protocol.md) and the [Python SDK](docs/reference/sdk.md) that does its plumbing
- Bundled connectors: [Wikipedia](connectors/wikipedia/README.md), [Markdown](connectors/markdown/README.md)
- For AI agents: [skills and `llms-full.txt`](docs/guides/agents.md); in Claude Code, `/plugin marketplace add Marceltov/passageway` gives you `/create-passageway-connector`

Documentation: the pages in `docs/`, will be published at https://passageway.marceltov.de.

Status: early. The engine started as the recall engine of [trilium-recall](https://github.com/Marceltov/trilium-recall) and is being generalized. The code is licensed AGPL-3.0-or-later; the Wikipedia articles of the sample corpus in `corpus/` are CC BY-SA 4.0 (see `corpus/LICENSE.md`).

## Contact

marcel@marceltov.de
