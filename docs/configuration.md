# Configuration

## passageway.toml

Default location `~/.config/passageway/passageway.toml`, or the path in `PASSAGEWAY_CONFIG`. One `[[connector]]` entry is one source with its own index file, so two servers of the same kind are two entries with the same `command`. Secrets are references to environment variables, never values.

```toml
[embedder]
min_similarity = 0.845          # optional: the relevance gate for the model in use

[[connector]]
name = "notes"                  # a-z, 0-9, _ and -; it names the index file
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

## Environment

| Variable | Default | Meaning |
|---|---|---|
| `PASSAGEWAY_LOGIN_PASSWORD` | required | Static Bearer token, and the OAuth login page's password |
| `PASSAGEWAY_CONFIG` | `~/.config/passageway/passageway.toml` | Connector file |
| `PASSAGEWAY_BASE_URL` | unset | Public https URL; set, it turns on OAuth for `/mcp` |
| `PASSAGEWAY_DATA_DIR` | `~/Library/Application Support/passageway` on macOS, `~/.local/share/passageway` elsewhere | Index files and OAuth state |
| `PASSAGEWAY_MODEL_DIR` | `<data dir>/models/e5-small` | The embedding model |
| `PASSAGEWAY_HOST`, `PASSAGEWAY_PORT` | `127.0.0.1`, `8082` | Where to listen |
| `PASSAGEWAY_POLL_SECONDS`, `PASSAGEWAY_RECONCILE_SECONDS` | `60`, `1800` | Change polling and full reconcile |
| `PASSAGEWAY_TOOL_DESCRIPTION`, `PASSAGEWAY_INSTRUCTIONS` | neutral text | What MCP clients read about the `recall` tool |
| `PASSAGEWAY_LOG_LEVEL` | `INFO` | |
| `APP_VERSION` | `dev` | Version string shown by `/health`; a release build sets it |

## Rebuilding a source

Each source is one file, `<data dir>/<name>.db`, and it can always be rebuilt from the connector: stop the server, delete the file, start it again. Do this after changing the embedding model, after removing a connector from the config (its items stay searchable until then), and when the deletion guard keeps refusing a legitimate bulk delete (it refuses to remove more than `max_delete_fraction` of a source, and always allows a single item; it also refuses to empty a source of two or more items).

## Health

`GET /health` is open so a health check can use it. It reports each source's item count and whether it is failing; the error text itself is shown only when the request carries the Bearer password.
