# Install and run

passageway runs as a small server on your machine. You give it connectors, it indexes what they report, and an MCP client such as Claude Code asks it for passages.

## Two ways to install

<div class="grid cards" markdown>

- **For yourself**

    Free for private use. Follow this page: the plugin below, or the steps by hand.

- **For a company**

    The same software and the same steps. Using it at work needs a [licence](licence.md); try it for up to 31 days under the Free Trial licence first, with no conversation needed.

</div>

## In Claude Code

The [Claude Code plugin](guides/claude-code.md) does every step on this page for you. Install it first:

```bash
/plugin marketplace add getpassageway/passageway
/plugin install passageway@passageway
```

Then run `/passageway-install`. It asks which sources you want, installs passageway with their connectors, writes each source with `/passageway-add-source`, runs the server as a service that survives reboots, and connects Claude Code with `/passageway-connect`. Run it again later and it upgrades an existing installation to the latest release, with the same connectors. Later, `/passageway-add-source` adds a source and `/passageway-status` checks the whole chain when something is off. No password or token goes through the chat.

The steps below are the same setup by hand, for any other MCP client or if you want to see what the skills do.

```mermaid
flowchart LR
  A["1. Install"] --> B["2. Embedding model"] --> C["3. Say what to index"] --> D["4. Start it"] --> E["5. Connect a client"]
```

Five steps, in this order; each is a section below.

## 1. Install

```bash
uv tool install --python 3.14 "passageway[wikipedia]"
```

This installs passageway and the Wikipedia connector from PyPI into one environment. Each bundled connector is an extra, pinned to the same release: name every one you want to run, for example `"passageway[wikipedia,markdown,trilium]"`. The extras are `confluence`, `llmstxt`, `markdown`, `mkdocs`, `sitemap`, `trilium` and `wikipedia`, `openai` for the [OpenAI embedder](configuration.md#the-embedder), and `all` for everything. The command replaces the set, so to add one later run it again with all of them.

`--python 3.14` is needed while onnxruntime, which the built-in embedder runs on, has no wheels for Python 3.15; without it uv takes the newest Python on the machine and the install fails. Any of 3.12 to 3.14 works.

## 2. The embedding model

(`passageway init` prepares the configuration folder with a generated password; [Run it](deploy.md) has the service and container setups.)

This is the built-in embedder with its default model. To use another model or embedder, see [the embedder](configuration.md#the-embedder).

passageway embeds text with the multilingual `e5-small` model in ONNX form, about 120 MB. The server fetches it on first start when it is missing, pinned to a revision and verified by checksum, into `<data dir>/models/e5-small` (or `PASSAGEWAY_MODEL_DIR`). The first start waits for that download before it answers, so `/health` is reachable only afterwards. To fetch it yourself, or to prepare a machine without network access (download on another machine, copy the folder over, set `download = false`):

```bash
passageway model list                 # the model presets of the built-in embedder
passageway model download             # the default, multilingual-e5-small
passageway model download jina-v2-base-de
```

Another preset or model is a line in `passageway.toml`, see [the embedder](configuration.md#the-embedder).

## 3. Say what to index

In Claude Code, `/passageway-add-source` writes this for you.

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

`"status": "ok"` means every source is built, `"indexing"` means one is still building its first index (the server already answers from what is indexed), and `"degraded"` means a source is failing. Each source has its own `state` (`ok`, `indexing`, `failing`) and, while it fetches, `fetched` and `of`: how far the build is. Add `-H 'Authorization: Bearer choose-one'` to the request to see why; a missing connector package, a wrong `command` path and an unreachable service all show up there. In Claude Code, `/passageway-status` reads the same report and says what to do.

## 5. Connect a client

In Claude Code, `/passageway-connect` from the [plugin](guides/claude-code.md) does this and adds the prompt hook.

Point an MCP client at `http://127.0.0.1:8082/mcp` and authenticate with `Authorization: Bearer choose-one`. The server offers one tool, `recall`: ask it a question and it returns up to three short passages with links, or says that nothing relevant is indexed.

For remote access with a login page instead of a static token, set `PASSAGEWAY_BASE_URL`; see [How it works](how-it-works.md#authentication).
