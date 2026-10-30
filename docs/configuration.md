# Configuration

## passageway.toml

Default location `~/.config/passageway/passageway.toml`, or the path in `PASSAGEWAY_CONFIG`. One `[[connector]]` entry is one source with its own index file, so two servers of the same kind are two entries with the same `command`. Secrets are references to environment variables, never values. In Claude Code, `/passageway-add-source` from the [plugin](guides/claude-code.md) writes the entry for you.

```toml
[embedder]
min_similarity = 0.845          # optional: the relevance gate for the model in use

[[connector]]
name = "notes"                  # starts with a-z or 0-9, then a-z, 0-9, _ or -; it names the index file
command = ["/path/to/python", "-m", "passageway.testing.fake_connector"]
env = { FAKE_ITEMS = "/path/to/items.json" }
secrets = { TOKEN = "env:NOTES_TOKEN" }
timeout = 300                   # seconds per call
max_line_bytes = 4194304        # longest line a connector may print
max_output_bytes = 67108864     # most output one call may produce
max_delete_fraction = 0.3       # a reconcile that would delete more than this share is refused
```

A connector runs with an empty environment (only `PATH` and `HOME`, plus its `env` table and named secrets), so `python` on `PATH` is usually not the interpreter that has passageway installed. For the example above use the tool's own interpreter, `$(uv tool dir)/passageway/bin/python`.

See the [connector protocol](reference/connector-protocol.md) for what a connector prints and the [Wikipedia connector](connectors/wikipedia.md) for a bundled one.

## The embedder

Without an `[embedder]` section passageway uses its built-in default, the multilingual e5-small, and fetches it once (pinned to a revision, every file verified by checksum) when it is missing. `model` picks another built-in preset:

```toml
[embedder]
model = "jina-v2-base-de"       # see `passageway model list`
device = "auto"                 # auto | cpu | coreml
download = true                 # fetch the pinned files when missing (false for an air-gapped machine)
```

 To use another model, point `[embedder]` at a program that speaks the [embedder protocol](reference/embedder-protocol.md); the bundled [OpenAI-compatible embedder](embedders/openai.md) is one, for Ollama, LM Studio, vLLM, OpenAI and Voyage:

```toml
[embedder]
kind = "command"                # "onnx" (the default) or "command"
command = ["/path/to/python", "/path/to/my_embedder.py"]
env = { MODEL = "bge-m3" }
secrets = { API_KEY = "env:EMBED_KEY" }
min_similarity = 0.80           # the relevance gate for this model
batch_size = 32                 # texts per request
timeout = 60                    # seconds per request
```

| Key | Kinds | Meaning |
|---|---|---|
| `kind` | both | `onnx` is the built-in model; `command` runs your program as one long-lived process |
| `min_similarity` | both | The relevance gate, from 0 to 1. Similarity scales differ between models, so measure it with [`passageway eval --sweep`](guides/evaluate.md); a `command` embedder without it gets the built-in model's value and a warning |
| `model` | `onnx` | A built-in preset: `multilingual-e5-small` (the default), `multilingual-e5-base`, `jina-v2-base-de`; `passageway model list` shows them with their measured relevance gate |
| `device` | `onnx` | `auto` (CPU) or `cpu`; `coreml` is opt-in on a Mac, measured four times slower on these int8 models and giving different vectors, so only for your own experiments |
| `download` | `onnx` | `true` fetches the preset's files from huggingface.co (or the mirror in `PASSAGEWAY_MODEL_HUB`) when they are missing or fail their checksum, once, before the server answers; `false` makes a missing model an error, with `passageway model download <preset>` as the step to run |
| `model_dir` | `onnx` | Where the preset's files are. Default: `PASSAGEWAY_MODEL_DIR` for the default preset (itself `<data dir>/models/e5-small`), else `<data dir>/models/<preset>`; `passageway model` uses the same rule. Set, it wins over `PASSAGEWAY_MODEL_DIR` and `--model-dir` |
| `command`, `env`, `secrets` | `command` | The program, its settings and named secrets (references to environment variables), run with an empty environment like a connector |
| `batch_size`, `timeout` | `command` | At most this many texts per request (1 to 1024); seconds per request, after which the process is killed. The first request, which loads the model, is under the same limit |

A typo in a key is an error. Changing the embedder rebuilds every index at the next start, because vectors of different models cannot be compared.

To compare models, add `[embedders.NAME]` tables with the same keys. The server ignores them; [`passageway eval compare`](guides/evaluate.md#compare-embedding-models) runs your questions with each:

```toml
[embedders.e5]
kind = "onnx"

[embedders.bge]
kind = "command"
command = ["/path/to/python", "/path/to/my_embedder.py"]
min_similarity = 0.80
```

## Environment

| Variable | Default | Meaning |
|---|---|---|
| `PASSAGEWAY_LOGIN_PASSWORD` | required | Static Bearer token, and the OAuth login page's password |
| `PASSAGEWAY_LOGIN_PASSWORD_FILE` | unset | A file holding the password, read when the variable is unset; `passageway init` writes one (see [Run it](deploy.md)) |
| `PASSAGEWAY_INSTANCE` | unset | Names one of [several instances](#several-instances) on this machine; it moves the default config and data folders to `passageway-<name>`. For a service; on the command line `--instance NAME` says the same and wins |
| `PASSAGEWAY_CONFIG` | `~/.config/passageway/passageway.toml` | Connector file |
| `PASSAGEWAY_BASE_URL` | unset | Public https URL; set, it turns on OAuth for `/mcp` |
| `PASSAGEWAY_DATA_DIR` | `~/Library/Application Support/passageway` on macOS, `~/.local/share/passageway` elsewhere | Index files and OAuth state |
| `PASSAGEWAY_MODEL_DIR` | `<data dir>/models/e5-small` | The embedding model |
| `PASSAGEWAY_HOST`, `PASSAGEWAY_PORT` | `127.0.0.1`, `8082` | Where to listen |
| `PASSAGEWAY_POLL_SECONDS`, `PASSAGEWAY_RECONCILE_SECONDS` | `60`, `1800` | Change polling and full reconcile |
| `PASSAGEWAY_TOOL_DESCRIPTION`, `PASSAGEWAY_INSTRUCTIONS` | neutral text | What MCP clients read about the `recall` tool |
| `PASSAGEWAY_LOG_LEVEL` | `INFO` | |
| `APP_VERSION` | the installed version | Version string shown by `/health` and `status`; set it only to override the package's version |

## Several instances

Several Claude setups side by side (yours, your work's, a customer's) can each have their own passageway, with their own sources, index and password. Give each instance a name and a port of its own:

```bash
passageway --instance work init
PASSAGEWAY_PORT=8083 PASSAGEWAY_LOGIN_PASSWORD_FILE=~/.config/passageway-work/password passageway --instance work
passageway --instance work eval cases.toml
```

The instance reads `~/.config/passageway-work/passageway.toml` and keeps its index in the data folder with `-work` appended (`~/Library/Application Support/passageway-work` on macOS). The built-in models stay in the shared data folder, so they are downloaded once. `/health` names the instance. Every command takes `--instance NAME`, anywhere on the line; a service sets `PASSAGEWAY_INSTANCE` instead, and the argument wins when both are there. An instance must exist: `--instance wrok` is an error that lists the instances there are, and only `init` creates one. Without an instance nothing changes, unless the machine has only named instances: then a bare `passageway` or `passageway eval` asks you to pick one rather than run against an empty default. In Claude Code, `/passageway-install` asks for the name, picks a free port and runs each instance as its own service.

Each Claude setup connects to the instances you choose, one or several: their hook files and MCP registrations live in its own `CLAUDE_CONFIG_DIR`, so `/passageway-connect` run in that setup touches no other. The hook asks every connected instance at once and joins their passages; the `recall` tool of instance `work` is the MCP server `passageway-work`. This keeps sources, indexes and connections apart; it is not a security boundary. Under one operating-system user, a Claude with a shell can read another instance's password file and call its port, so which Claude connects to which instance is up to you. For a boundary that holds, run each instance as its own user or in its own [container](deploy.md).

## Certificates

Every HTTPS request passageway makes, from the core's model download and from the bundled connectors and embedder, checks the server's certificate against your operating system's trust store: the Keychain on macOS, the certificate store on Windows, `/etc/ssl` on Linux. A server whose certificate comes from a company or internal CA works as soon as that CA is trusted there, the way Safari and curl see it; no exported bundle in `SSL_CERT_FILE` is needed. Only the Confluence connector can turn checking off, with `VERIFY_TLS = false`.

## Rebuilding a source

Each source is one file, `<data dir>/<name>.db`, and it can always be rebuilt from the connector: stop the server, delete the file, start it again. Do this after changing the embedding model, after removing a connector from the config (its items stay searchable until then), and when the deletion guard keeps refusing a legitimate bulk delete (it refuses to remove more than `max_delete_fraction` of a source, and always allows a single item; it also refuses to empty a source of two or more items).

## Health

`GET /health` is open so a health check can use it. It reports each source's item count and whether it is failing; the error text itself is shown only when the request carries the Bearer password. The same report, errors included, is the MCP tool `status`, so a connected client asks the server itself instead of curl; a server started with a broken configuration answers `{"status": "error", "error": ...}` from both.
