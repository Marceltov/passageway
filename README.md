# passageway

Retrieval for Claude over MCP. passageway indexes what your **connectors** report, finds the best short passages for a question with keyword plus embedding search, and serves them as one `recall` tool. It stays silent when nothing is relevant enough. It does no generation: the calling model reads the passages.

The core knows no source. A connector is any executable that lists items and returns their text as JSON Lines; anyone can write one. An eval harness (coming) measures retrieval quality on your own questions so you can publish the numbers.

- [Install and configure](docs/install.md)
- [Connector protocol](docs/connectors.md)
- Bundled connectors: [Wikipedia](connectors/wikipedia/README.md)

Status: early. The engine started as the recall engine of [trilium-recall](https://github.com/Marceltov/trilium-recall) and is being generalized. Licensed AGPL-3.0-or-later.

## Contact

marcel@marceltov.de
