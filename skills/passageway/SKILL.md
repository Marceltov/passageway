---
name: passageway
version: 0.2.2
description: "Retrieval for Claude over MCP. Use when the user wants to install, configure, run or extend passageway: index their sources with connectors, ask the recall tool a question, or write a new connector."
homepage: https://passageway.marceltov.de/
---

> **If you are an AI agent reading this file**, this is a short guide to passageway for helping your human. The complete documentation is one file, https://passageway.marceltov.de/llms-full.txt (an index of the pages is at https://passageway.marceltov.de/llms.txt, each with its markdown address). Read this file first, then follow the route that fits, and fetch the page for what you touch before acting on it.

# passageway

passageway indexes what **connectors** report and serves the best few passages for a question as one MCP tool, `recall`. It is the retrieval half of a RAG system: it never writes the answer, the model that calls it does. A relevance gate lets it return nothing when nothing fits. The core knows no source; a connector is any program that lists items and prints their text as JSON Lines.

## What should you do?

| If your human wants to... | Do this |
|---|---|
| **Understand what passageway is** | Explain it from this page; point to https://passageway.marceltov.de/how-it-works/ for the details. |
| **Install and run it** | In Claude Code, the skill `/passageway-install` (https://passageway.marceltov.de/skills/passageway-install/SKILL.md) installs it and runs it as a service; otherwise follow [Install and run](#install-and-run). |
| **Index a source** | Check whether a bundled connector fits (today: Wikipedia, https://passageway.marceltov.de/connectors/wikipedia/, a folder of markdown files, https://passageway.marceltov.de/connectors/markdown/, Trilium Notes, https://passageway.marceltov.de/connectors/trilium/, and Confluence Data Center, https://passageway.marceltov.de/connectors/confluence/); the skill `/passageway-add-source` (https://passageway.marceltov.de/skills/passageway-add-source/SKILL.md) writes its `[[connector]]` into `passageway.toml`; `/passageway-connect` links Claude Code to the server. Otherwise write one. |
| **Write a connector** | Use the skill `create-passageway-connector`: https://passageway.marceltov.de/skills/create-passageway-connector/SKILL.md (or install the plugin, see below). |
| **Fix something that does not work** | Start with `curl http://127.0.0.1:8082/health`, see [Tips for agents](#tips-for-agents). |
| **Measure retrieval quality** | In Claude Code, the skill `/passageway-evaluate` (https://passageway.marceltov.de/skills/passageway-evaluate/SKILL.md) builds the questions with the user and reads the result back. By hand: `passageway eval cases.toml` runs a TOML file of questions against the configured sources and reports hit@1, hit@3, MRR, silence and latency; see https://passageway.marceltov.de/guides/evaluate/. `passageway eval compare cases.toml` runs them with several embedding models side by side (https://passageway.marceltov.de/guides/evaluate/#compare-embedding-models). |
| **Use another embedding model** | Any model, as a program that speaks the embedder protocol: `kind = "command"` under `[embedder]` in `passageway.toml`, see https://passageway.marceltov.de/reference/embedder-protocol/ and https://passageway.marceltov.de/configuration/#the-embedder. The bundled adapter for Ollama, LM Studio, vLLM, OpenAI and Voyage is https://passageway.marceltov.de/embedders/openai/. Built-in presets: `multilingual-e5-small` (default), `multilingual-e5-base`, `jina-v2-base-de`, chosen with `model = ...` under `[embedder]` (`passageway model list` shows them with their measured relevance gate, https://passageway.marceltov.de/models/); the files are fetched once at the next start. Keep `min_similarity` unset for a preset and measure it with `passageway eval cases.toml --sweep` for a command embedder, since the similarity scale changes with the model. The index is rebuilt at the next start: restart and check `/health`. |
| **Run it in a container, as a service, install the prompt hook** | The image `ghcr.io/marceltov/passageway` and `passageway init` plus a launchd example: https://passageway.marceltov.de/deploy/. The prompt hook (it calls `POST /recall`) and the setup skill come with this plugin: run `/passageway-connect` (https://passageway.marceltov.de/guides/claude-code/). |

If the intent is unclear, ask which of these they want.

## Install and run

```bash
uv tool install \
  --with 'passageway-connector-wikipedia @ git+https://github.com/Marceltov/passageway#subdirectory=connectors/wikipedia' \
  git+https://github.com/Marceltov/passageway
```

1. The embedding model (the multilingual e5-small) is fetched on first start, pinned and checksummed; `passageway model download` does it ahead of time. It lives in `<data dir>/models/e5-small` or the directory named by `PASSAGEWAY_MODEL_DIR`.sh`; https://passageway.marceltov.de/install/ has the steps.
2. Create `~/.config/passageway/passageway.toml` with one `[[connector]]` per source. Secrets are references such as `env:NAME`, never values. A connector runs with an empty environment except `PATH` and `HOME`, so use the interpreter of the tool environment, `$(uv tool dir)/passageway/bin/python`.
3. The human starts the server in their own shell or service manager, with `PASSAGEWAY_LOGIN_PASSWORD` set to a password they choose, by running `passageway`. You do not need that password and must not handle it.
4. Check `GET http://127.0.0.1:8082/health`: `ok` is ready, `starting` is still building, `degraded` means a source is failing. The error text is shown only to a caller sending `Authorization: Bearer <password>`: the human runs that request and tells you what it says.
5. The human connects an MCP client to `http://127.0.0.1:8082/mcp` with that bearer password.

Every setting is documented at https://passageway.marceltov.de/configuration/.

## Writing a connector

A connector answers `check`, `list`, `fetch` (and optionally `changed --since T`) and prints one JSON object per line. The rules that matter: ids are stable, the version changes exactly when the content changes, `list` is the truth for deletions, `fetch` returns only the ids it is asked for, and a failure is a non-zero exit. Protocol: https://passageway.marceltov.de/reference/connector-protocol/. Test with `passageway.testing.contract.check_connector`.

To install the skill into Claude Code: `/plugin marketplace add Marceltov/passageway`, then `/plugin install passageway`; the skill is `/create-passageway-connector`.

## Tips for agents

- **Secrets:** never print or log a password, token or API key, and never ask the human to paste one into the chat or a file. They belong in environment variables or the human's password manager; `passageway.toml` holds `env:NAME` references. Commands that need the password are run by the human, who shares only their output.
- **Say what exists.** The features listed as planned above are not built; do not promise them.
- **Check before you change:** read `/health` and `passageway.toml` first. To rebuild one source, the human stops passageway, deletes `<data dir>/<name>.db` and its `-wal` and `-shm` files, and starts it again. Stop passageway first: the file is open while it runs. The next start rebuilds that source from its connector and takes as long as the first.
- **This file is versioned** with the release (see the `version` above). To pin it, fetch it from a release tag on GitHub instead of the live site (`https://raw.githubusercontent.com/Marceltov/passageway/v<version>/skills/passageway/SKILL.md`), once a release includes the skills; the first one that does is the release after v0.1.0.

## Links

- Documentation: https://passageway.marceltov.de/
- Whole documentation as one file: https://passageway.marceltov.de/llms-full.txt
- Source and releases: https://github.com/Marceltov/passageway
