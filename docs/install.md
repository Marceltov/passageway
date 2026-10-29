# Install and run

passageway runs as a small server on your machine. You give it connectors, it indexes what they report, and an MCP client such as Claude Code asks it for passages.

## 1. Install

```bash
uv tool install \
  --with 'passageway-connector-wikipedia @ git+https://github.com/Marceltov/passageway#subdirectory=connectors/wikipedia' \
  git+https://github.com/Marceltov/passageway
```

This installs passageway and the Wikipedia connector into one environment. A connector is a separate package, so add `--with` for every bundled connector you want to run. The [Markdown](connectors/markdown.md), [Trilium](connectors/trilium.md) and [Confluence](connectors/confluence.md) connectors are installed the same way, with `connectors/markdown`, `connectors/trilium` or `connectors/confluence` as the subdirectory and the packages `passageway-connector-markdown`, `passageway-connector-trilium` and `passageway-connector-confluence`.

## 2. The embedding model

This is the built-in model. To use another one, see [the embedder](configuration.md#the-embedder).

passageway embeds text with the multilingual `e5-small` model in ONNX form, about 120 MB. The server fetches it on first start when it is missing, pinned to a revision and verified by checksum, into `<data dir>/models/e5-small` (or `PASSAGEWAY_MODEL_DIR`). The first start waits for that download before it answers, so `/health` is reachable only afterwards. To fetch it yourself, or to prepare a machine without network access (download on another machine, copy the folder over, set `download = false`):

```bash
passageway model list                 # the built-in presets
passageway model download             # the default, multilingual-e5-small
passageway model download jina-v2-base-de
```

Another preset or model is a line in `passageway.toml`, see [the embedder](configuration.md#the-embedder).

## 3. Say what to index

Create `~/.config/passageway/passageway.toml` with one `[[connector]]` per source. This one indexes a small corner of English Wikipedia:

```toml
[[connector]]
name = "deep-learning"
command = ["/path/to/python", "-m", "passageway_connector_wikipedia"]
env = { LANGUAGE = "en", CATEGORIES = "Deep learning", CATEGORY_DEPTH = "0" }
```

A connector runs with an empty environment, so `python` on your `PATH` is usually not the interpreter that has passageway installed. Use the tool's own interpreter, `$(uv tool dir)/passageway/bin/python`, which is the environment from step 1. See [Configuration](configuration.md) for every setting and the [Wikipedia connector](connectors/wikipedia.md) for its options.

## 4. Start it

```bash
PASSAGEWAY_LOGIN_PASSWORD=choose-one passageway
```

The first start indexes every source, which can take a few minutes. Watch it with:

```bash
curl http://127.0.0.1:8082/health
```

`"status": "ok"` means every source is built, `"starting"` means one still is, and `"degraded"` means a source is failing. Add `-H 'Authorization: Bearer choose-one'` to the request to see why; a missing connector package, a wrong `command` path and an unreachable service all show up there.

## 5. Connect a client

Point an MCP client at `http://127.0.0.1:8082/mcp` and authenticate with `Authorization: Bearer choose-one`. The server offers one tool, `recall`: ask it a question and it returns up to three short passages with links, or says that nothing relevant is indexed.

For remote access with a login page instead of a static token, set `PASSAGEWAY_BASE_URL`; see [How it works](how-it-works.md#authentication).
