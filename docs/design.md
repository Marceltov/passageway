# Design

The design passageway was started from, as decided on 2026-10-28. It is the reference for the parts that are not built yet (the embedder protocol, the eval harness, the Trilium and Confluence connectors, the sidecar image). What is built is described in the pages of the guide; where the two differ, the guide and the [roadmap](roadmap.md) are current and this page is the original intent.

## Goal

passageway is an open-source retrieval service for Claude. It indexes documents from sources, finds the best short passages for a question with keyword plus embedding search, and serves them over MCP as one `recall` tool. It does no generation: the calling model reads the passages. It stays silent when nothing is relevant enough.

The core is **completely source-agnostic**. Anyone can write a connector (any language) or an embedder and configure it. The project also makes retrieval quality **measurable**: users run an eval harness against their own connectors and question corpus and publish the results in their own docs.

## Provenance and licence

- Built on the author's own `trilium-recall` engine (AGPL-3.0-or-later). The code was copied into a new repository with **fresh git history**; passageway is licensed AGPL-3.0-or-later as well. The last commit with all the Trilium code is the tag `trilium-engine-import`.
- The connector protocol, the embedder protocol and the eval harness are specified in this document. The Confluence connector is written from the public Confluence REST documentation.
- Published as `github.com/Marceltov/passageway`.

## Decisions

| Topic | Decision |
|---|---|
| Name | **passageway** (repo `Marceltov/passageway`, CLI `passageway`, env prefix `PASSAGEWAY_`, packages `passageway`, `passageway-connector-<name>`, `passageway-embedder-<name>`). The MCP tool keeps the name `recall`, because it is what the calling model learns to use. The earlier name `recall` was dropped: it clashes with Windows Recall, with the recall@k metric the eval harness reports, and with an unrelated PyPI package. |
| Source-agnostic core | The core speaks only the connector protocol and the embedder protocol. Source-specific knowledge (areas, wiki types, breadcrumbs) reaches the core as optional fields on the item record. |
| Connectors | Out-of-process executables speaking JSON Lines; bundled and third-party connectors are identical. |
| Embedding models | Configurable: built-in generic `onnx` embedder with presets, plus an out-of-process `command` embedder. |
| Deployments | Sidecar/remote (container, OAuth) and local (process on localhost, bearer). Same code; only defaults and settings differ. |
| Repository | One repo, uv workspace. Core package `passageway`; every connector and embedder is a self-contained folder with its own `pyproject.toml`, tests, README and dependencies. Connectors own their tests. |
| Eval | First-class feature: `passageway eval` with sweep, compare and publishable, aggregate-only reports. |

## Repository layout

```
passageway/                          github.com/Marceltov/passageway
  pyproject.toml                     uv workspace root
  passageway/                        core package
    server.py      MCP `recall` tool (fastmcp), /health, /recall hook endpoint
    auth.py        bearer always; OAuth (mcp-login-oauth) when PASSAGEWAY_BASE_URL is set
    sync.py        drives connectors: reconcile and poll
    protocol.py    connector protocol: launch, JSON Lines, limits, deletion guard
    index.py       one SQLite file per source: sections, FTS5, sqlite-vec
    rank.py        hybrid ranking, relevance gate, item weight
    embed.py       embedder interface; built-in `onnx` and `command`
    hook.py        prompt skip rules and per-session memory (Claude Code hook)
    eval/          run, sweep, compare, report
    sdk.py         helpers for connector authors; contract test suite
  connectors/
    wikipedia/  trilium/  confluence/  markdown/        each: pyproject, code, tests, README
  embedders/
    openai/                                              OpenAI-compatible, covers Voyage
  plugin/          Claude Code plugin: hook and setup skill
  docs/            generic documentation and ADRs
  Dockerfile       the sidecar image
```

## Deployments

| | Sidecar / remote | Local |
|---|---|---|
| Runs as | Container next to the source, behind an HTTPS proxy | A process on the user's machine |
| Clients | claude.ai and Claude Code over the network | Claude Code on the same machine, `http://127.0.0.1:<port>/mcp` |
| Inbound auth | `PASSAGEWAY_BASE_URL` set turns on OAuth for `/mcp`; the static bearer stays for the hook | No base URL: bearer password only |
| Defaults | Binds `0.0.0.0`, data in `/data`, model baked into the image, CPU | Binds `127.0.0.1`, data in the user's data dir, model downloaded on first start, `device = auto` (CoreML on a Mac) |
| Connectors | Run inside the container; the image ships the bundled ones | Local processes; any executable works |

No stdio MCP mode: the index and sync loop must outlive client sessions. Local v1 is minimal: `uv tool install`, `passageway serve`, a generated password stored in the config directory, and a documented launchd example. Homebrew packaging and a service installer come later. Third-party connectors in the container need a derived image or a mount; the docs describe a derived image.

## Configuration

Core settings are environment variables (password, base URL, host, port, data dir, poll and reconcile intervals, tool description, instructions). Structured settings live in one TOML file, `passageway.toml`, in the config directory or a mounted path. Secrets are references, not values: `env:NAME`, resolved from the core's environment and handed only to the connector that names them.

```toml
[embedder]
kind = "onnx"
model = "intfloat/multilingual-e5-small"
min_similarity = 0.845

[[connector]]
name = "notes"
command = ["python", "-m", "passageway_connector_trilium"]
env = { URL = "https://trilium.example.com" }
secrets = { TOKEN = "env:TRILIUM_NOTES_TOKEN" }
```

One `[[connector]]` entry is one source with its own index file, so two Trilium servers are two entries with the same `command`.

## Connector protocol (v1)

The core runs `<command> <mode>`. stdout is one JSON object per line. stderr goes to the log with secrets masked. A non-zero exit fails the call.

| Mode | Input | Output |
|---|---|---|
| `check` | none | `{"ok": true, "count": 42}` |
| `list` | none | `{"id", "version"}` for every existing item |
| `fetch` | `{"id"}` lines on stdin | an item record per requested id that still exists |
| `changed --since <UTC ISO>` | none | an item record per item changed since then; optional, a connector that cannot answer cheaply prints nothing and its edits appear at the next reconcile |

Item record:

```json
{"id": "abc", "title": "Rotating certificates", "url": "https://…", "version": "3f2a",
 "sections": [{"heading": "Steps", "text": "Rotate the signing cert every year…"}],
 "weight": 1.0, "path": ["Ops", "Security"], "links": ["def"],
 "labels": ["decision"], "updated": "2026-10-28T09:00:00Z"}
```

- Required: `id`, `title`, `url`, `version`, `sections` (may be empty; a section has optional `heading` and required `text`).
- Optional: `weight` (multiplier on the ranking score, default 1.0), `path` (breadcrumb), `links` (ids of related items, shown with a hit when they are indexed), `labels` (short tags), `updated`.
- The core builds the embedded text as `title › path › heading: text` and splits any section over a size cap at paragraph boundaries, so a connector cannot send an oversize section.
- `version` is any string that changes when the content changes; the core fetches only items whose version differs.
- The connector receives an empty environment plus `PATH`, `HOME`, `PASSAGEWAY_PROTOCOL=1`, its `env` table and its named secrets. It never sees the core's password or another connector's secrets.
- A call succeeds completely or stores nothing.
- `list` decides deletions. The deletion guard refuses to remove more than 30 % of a source (configurable, and never less than one item) or all of a source that has two or more items, and reports an error instead.
- A failing connector never stops other sources; its already indexed items stay searchable. Line size, call size and timeout have configurable defaults.

## Embedder protocol (v1) and models

A model needs prefixes, pooling, a token limit, a dimension and a **relevance threshold**: similarity scales differ between models, so the threshold is tied to the model and is measured, not guessed. The index records the embedder name and dimension; a change rebuilds the index.

- **`onnx` (built in):** `onnxruntime` plus Hugging Face `tokenizers`. A model is a Hugging Face repo id or a local folder with `model.onnx` and `tokenizer.json`. Prefixes, pooling, max length, device (`auto | cpu | coreml`) and `min_similarity` are config. Presets ship for e5-small multilingual (default) and a German-focused model such as `jinaai/jina-embeddings-v2-base-de`; preset thresholds are calibrated on the project's public Wikipedia corpus and documented as a starting point. A custom model without a threshold produces a warning at start.
- **`command`:** one long-lived process kept running by the core, JSON Lines on stdin and stdout. `{"op":"info"}` returns `{"name","dim"}`; `{"op":"embed","kind":"query"|"passage","texts":[…]}` returns `{"vectors":[[…]]}`. The core L2-normalises, batches, enforces a timeout and restarts a dead process. Prefixes and pooling are the embedder's business.
- **`embedders/openai`:** an OpenAI-compatible HTTP embedder with an optional field mapping, covering Ollama, LM Studio, vLLM, OpenAI and Voyage (Anthropic offers no embedding model; Voyage is its recommended partner). The Voyage request format is verified when this is built. Cloud embedders send all indexed text and queries to a third party; the default stays local and the docs say so.

## Ranking and hook

Hybrid ranking carried over from trilium-recall: FTS5 and vector search fused by reciprocal rank, a hard relevance gate (`min_similarity`, plus a keyword rescue), item `weight` as multiplier, up to three passages per answer, nothing when below the gate. The Trilium-specific parts (areas, wiki type, topics, status, summary-for-source substitution) move into the Trilium connector, expressed as `weight`, `path`, `links` and `labels`. The Claude Code prompt hook (`/recall` endpoint, skip rules for slash commands, confirmations and bare follow-ups, per-session memory of what was already injected) is generic and stays in the core, keyed on item ids.

## Eval harness

Corpus (TOML written by the user):

```toml
[targets]            # optional, for --enforce
hit_at_3 = 0.8
silence = 0.8
p95_ms = 300

[[case]]
query = "how do I rotate the signing certificate"
expect = ["Rotating certificates"]   # substrings of title, heading or URL
group = "ops"                        # optional
# expect_id = ["abc"] matches exact item ids

[[case]]
query = "what is the cafeteria menu"  # no expect: the index must stay silent
```

Commands, in-process against the configured index (no running server needed):

- `passageway eval cases.toml`: hit@1, hit@3, MRR, silence on unanswerable questions, false silence on answerable ones, latency p50 and p95 including the embedding share. A warm-up query is not counted.
- `--sweep 0.5,0.6,0.7`: repeat at several thresholds, the way to set `min_similarity`.
- `passageway eval compare cases.toml --embedder <name>…`: re-embed a copy of the index with each candidate and report quality, model load time and index time; the live index is untouched.
- `--enforce`: exit 1 below `[targets]`, for CI.
- It refuses to run against an index built with a different embedder than configured, and says so.

Publishing:

- `--out DIR` writes `report.json` (schema version; run metadata: date, machine, passageway version, embedder, threshold, counts) and `report.md`.
- `--write docs/measurements.md` replaces the block between `<!-- passageway:results:start -->` and `<!-- passageway:results:end -->` in the user's own page, idempotently, and appends to a history file rendered as a run table.
- **Aggregate-only by default:** no questions, no returned titles, no per-case rows. Per-case tables require `--include-cases`, since they quote what is in the user's sources.
- No charts in v1.

## Wikipedia connector and the public corpus

The first real connector, and the public demo and measurement corpus. Scope: a category with a depth limit, a list of titles, a language (German and English test multilingual embedding), or a geographic area (latitude, longitude, radius). The revision id is the version; the recent-changes feed backs `changed`; sections come from the article headings. It sends a descriptive User-Agent and respects Wikimedia's rate limits. The project ships a public question set for a small fixed scope, including unanswerable questions, so the project's own measurements are reproducible by anyone. Content is CC BY-SA: dumps are never committed, only the connector and the questions.

## Testing

- Core: trilium-recall's tests move over where they still apply (index, rank, text, config, OAuth, sessions, skip rules), running against a hash embedder and a fake connector script, with no model download and no network.
- Contract suites in the core's SDK, one for connectors and one for embedders: records, limits, exit codes, "fetch returns only requested ids", all-or-nothing, deletion guard. **Each connector owns its tests** (fixtures, unit tests, the contract suite, optional live tests), living in its own folder.
- Trilium connector: trilium-recall's fake ETAPI fixtures, the opt-in live container test, and a parity check that ranking quality matches trilium-recall on the same notes.
- Wikipedia: recorded HTTP fixtures offline; live runs opt-in.
- Confluence: recorded fixtures only.
- Eval: metric math, sweep, compare on the hash embedder, and a guard test that an aggregate-only report contains no query text and no titles.
- CI (GitHub Actions): one job per package, strict docs build, Docker image build with a smoke start.

## Build order

Each step is its own pull request. The [roadmap](roadmap.md) shows which are done.

0. **Bootstrap:** `git init` with fresh history, trilium-recall engine files copied in, `LICENSE`, README, CI skeleton, repo published as `Marceltov/passageway`.
1. **Core refactor:** connector protocol, sync driver, one index per source, item `weight`, hash embedder, fake connector and the connector contract suite. The engine runs end to end on the fake connector.
2. **Wikipedia connector** and the public demo scope.
3. **Trilium connector:** `trilium.py`, sync logic and HTML sectioning leave the engine; parity check.
4. **Embedders:** generalize `onnx` with presets, then `command` and `embedders/openai` (Voyage).
5. **Eval harness:** run, sweep, compare, report, `--write`; the public Wikipedia question set and the project's own published measurements.
6. **Confluence connector.**
7. **Hook, plugin, docs site, sidecar image, local quickstart.**
8. **Markdown connector.**
9. Outside this repo: trilium-recall points to passageway.

## Open items

- **Confluence flavor (needed at step 6):** Cloud, Data Center/Server, or both. Auth and API paths differ.
- Preset thresholds for e5-small and Jina are calibrated at step 5 on the Wikipedia corpus, not carried over from any earlier measurement.

## Non-goals

- Generation or answering: passageway returns passages only.
- A reranker, stdio MCP, per-connector access control (everything indexed is searchable by every caller of `recall`), charts in eval reports, Homebrew packaging and a service installer in v1.
- Purging a removed connector's items automatically: dropping its index file does that, and the docs say so.
