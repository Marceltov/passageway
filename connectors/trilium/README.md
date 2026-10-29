# passageway-connector-trilium

A [passageway](https://github.com/Marceltov/passageway#readme) connector for [Trilium Notes](https://github.com/TriliumNext/Notes): every text and code note of a Trilium server, read through its ETAPI with GET requests only. It is the trilium-recall sync as a connector, so an LLM wiki kept the trilium-llm-wiki way is understood, and any other Trilium works too.

## What it does

- **Each note is one item.** Its id is the note id, its version changes with the content, the title, the attributes or the place in the tree, and its link opens the note in Trilium.
- **Headings become sections:** `<h2>` and `<h3>` split a note into passages with their heading trail (`Setup › Linux`); lists, tables and code blocks are kept readable; a code note is split at blank lines. Long sections are cut at about 350 tokens.
- **Areas give weight.** The owned `#llmWikiPart` notes mark the areas: `wiki` and `schema` weigh 1.0, `sources` 0.8, the journal (`#calendarRoot`) 0.6, everything else 0.6; `locks`, `templates` and `views` are plumbing and are left out, as are archived notes.
- **Wiki labels become labels:** `area:wiki`, `type:<wikiType>`, `topic:<wikiTopic>`, `status:<wikiStatus>`.
- **Relations and links become related items:** `internalLink`, `relatesTo` and `wikiSource` relations the note owns, and the links in its text, point at other indexed notes; a source note links back to the summaries that cite it.
- **The path** is the titles of the ancestors below the area root, nearest last, so a hit says where in the tree the note is.
- **Edits appear within a minute:** `changed` asks Trilium for the notes modified since the last poll; deletions, moves out of scope and archiving are settled at the next reconcile.

## Configure

Create an ETAPI token in Trilium under Options › ETAPI. Trilium's tokens can write, so keep it a secret reference; the connector only ever sends GET requests.

```toml
[[connector]]
name = "notes"
command = ["/path/to/python", "-m", "passageway_connector_trilium"]
env = { URL = "http://trilium:8080", WEB_URL = "https://notes.example.org" }
secrets = { TOKEN = "env:TRILIUM_TOKEN" }
```

| Setting | Default | Meaning |
|---|---|---|
| `URL` | required | The Trilium server as the connector reaches it (`/etapi` is added) |
| `TOKEN` | required | An ETAPI token, as a secret reference such as `env:TRILIUM_TOKEN` |
| `WEB_URL` | `URL` | The address links are made with, when readers reach Trilium under another name than the connector does |
| `TIMEOUT` | `30` | Seconds per request |

## Not carried over from trilium-recall

trilium-recall showed a note's summary in place of its source when the summary matched almost as well. The core knows no source, so that rule has no place in it; here a summary and its source are items that link each other, and a hit shows the other as a related item. The connector's parity with trilium-recall is measured on trilium-recall's public fixture (see [the measurements](https://passageway.marceltov.de/measurements/)).

## Test

```bash
uv run pytest connectors/trilium                                   # offline, against an in-test ETAPI with the fixture wiki
PASSAGEWAY_LIVE=1 uv run pytest connectors/trilium/tests/test_trilium_parity.py   # the fixture cases with the real model
```
