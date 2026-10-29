# passageway-connector-trilium

A [passageway](https://github.com/Marceltov/passageway#readme) connector for [Trilium Notes](https://github.com/TriliumNext/Notes): every text and code note of a Trilium server, read through its ETAPI with GET requests only. It is the trilium-recall sync as a connector, so an LLM wiki kept the trilium-llm-wiki way is understood, and any other Trilium works too.

## What it does

- **Each note is one item.** Its id is the note id, its version changes with the content, the title, the attributes or the place in the tree, and its link opens the note in Trilium.
- **Headings become sections:** `<h2>` and `<h3>` split a note into passages with their heading trail (`Setup › Linux`); lists, tables and code blocks are kept readable; a code note is split at blank lines. Long sections are cut at about 350 tokens.
- **Areas give weight.** The owned `#llmWikiPart` notes mark the areas: `wiki` and `schema` weigh 1.0, `sources` 0.8, the journal (`#calendarRoot`) 0.6, everything else 0.6; `locks`, `templates` and `views` are plumbing and are left out, as are archived notes.
- **Wiki labels become labels:** `area:wiki`, `type:<wikiType>`, `topic:<wikiTopic>`, `status:<wikiStatus>`.
- **Relations and links become related items:** `internalLink`, `relatesTo` and `wikiSource` relations the note owns, and the links in its text, point at other indexed notes; a source note links back to the summaries that cite it.
- **The path** is the titles of the ancestors below the area root, nearest last, so a hit says where in the tree the note is.
- **Edits to a note's content appear within a minute:** `changed` asks Trilium for the notes modified since the last poll, one small request when nothing changed. Trilium does not count an attribute or a move as a modification, so label changes, moves, renamed ancestors, deletions and archiving are settled at the next reconcile (every 30 minutes by default).
- **Cost:** `list` and each `fetch` batch read every note's metadata (one search per area root), because areas, paths and links need the whole tree; a Trilium with thousands of notes makes a full build take minutes. The content of a note is fetched once per version.

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
| `MAX_NOTE_BYTES` | `1048576` | A note whose content is larger is skipped with a warning at fetch (the core accepts 4 MiB per item line); it stays listed, so it is tried again at each reconcile |

## Not carried over from trilium-recall

trilium-recall showed a note's summary in place of its source when the summary matched almost as well. The core knows no source, so that rule has no place in it; here a summary and its source are items that link each other, and a hit shows the other as a related item. The connector's parity with trilium-recall is measured on trilium-recall's public fixture, a synthetic wiki with 17 questions served by the in-test ETAPI with the real model: hit@3 0.92 and silence 1.0 against trilium-recall's published 0.83 and 1.0 (`PASSAGEWAY_LIVE=1 uv run pytest connectors/trilium/tests/test_trilium_parity.py -s`). A check against a live Trilium and trilium-recall's private question set is still to be done by its owner.

## Test

```bash
uv run pytest connectors/trilium                                   # offline, against an in-test ETAPI with the fixture wiki
PASSAGEWAY_LIVE=1 uv run pytest connectors/trilium/tests/test_trilium_parity.py   # the fixture cases with the real model
```
