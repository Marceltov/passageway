---
name: passageway-add-source
description: "Add a source to a running passageway: write the [[connector]] for a folder of markdown, Trilium, Confluence or Wikipedia into passageway.toml, with secrets as env: references, then restart and check /health. Use when the user wants passageway to index something, or when the index is empty after connecting Claude Code."
---

# Add a source to passageway

passageway indexes what its connectors report (docs: https://passageway.marceltov.de/configuration/). The configuration is one TOML file: `$PASSAGEWAY_CONFIG`, else `~/.config/passageway/passageway.toml` (`passageway init` writes a sample), `/config/passageway.toml` in the container. This skill edits that file; the server reads it at start, so every change ends with a restart. Never print a secret, never ask the user to paste one into the chat, never write a token or password into the file: a secret is a reference to an environment variable, `env:NAME`, and the variable is set where the server starts (the shell, the launchd plist, the compose file).

**Documentation:** the index https://passageway.marceltov.de/llms.txt lists every page with its markdown address; the whole documentation is one file, https://passageway.marceltov.de/llms-full.txt. Before you act on something this skill only names (a connector's settings, a configuration key, a deploy step), fetch its page and work from it, not from memory.

## Determine the operation

**Add a source** (default), or **show** what is configured (print the file with every `secrets` line masked).

## Add a source

1. Find the file: `echo "${PASSAGEWAY_CONFIG:-$HOME/.config/passageway/passageway.toml}"`; in a container it is the mounted `/config/passageway.toml` on the host. Read it: existing `[[connector]]` tables tell you the interpreter path and the style to keep. Connector names are unique, lowercase, `[a-z0-9_-]`.
2. Find the interpreter that has the connectors: a connector runs with an empty environment, so `python` on the `PATH` is not it. For a `uv tool install` it is `$(uv tool dir)/passageway/bin/python` (the sample written by `passageway init` already names it); in the image it is `python` (the venv is first on the `PATH`); otherwise `$(dirname "$(which passageway)")/python`. Check it: `<python> -c "import passageway_connector_markdown"`. An `ImportError` means the connector package is not installed; for a `uv tool` install, add it with `uv tool install --with 'passageway-connector-<name> @ git+https://github.com/Marceltov/passageway#subdirectory=connectors/<name>' git+https://github.com/Marceltov/passageway` (list every connector already in use, the command replaces the set).
3. Ask what to index, then write one table. The bundled connectors and their settings, from their own pages (read the page for the full table before writing):
   - **A folder of markdown** (https://passageway.marceltov.de/connectors/markdown/): `command = [<python>, "-m", "passageway_connector_markdown"]`, `env = { FOLDER = "/abs/path" }`; `INCLUDE`/`EXCLUDE` are glob patterns separated by `|`.
   - **Trilium Notes** (https://passageway.marceltov.de/connectors/trilium/): `"-m", "passageway_connector_trilium"`, `env = { URL = "http://host:8080" }` (plus `WEB_URL` when readers reach it under another name), `secrets = { TOKEN = "env:TRILIUM_TOKEN" }`; the token is an ETAPI token.
   - **Confluence Data Center** (https://passageway.marceltov.de/connectors/confluence/): `"-m", "passageway_connector_confluence"`, `env = { URL = "https://wiki.example.org", SPACES = "KEY1|KEY2" }`, `secrets = { TOKEN = "env:CONFLUENCE_TOKEN" }`; a personal access token.
   - **Wikipedia** (https://passageway.marceltov.de/connectors/wikipedia/): `"-m", "passageway_connector_wikipedia"`, `env = { LANGUAGE = "en", CATEGORIES = "Deep learning", CATEGORY_DEPTH = "1" }` or `TITLES = "A|B"`; no secret.
   - Something else: write a connector with `/create-passageway-connector`, then come back here.

   Every `env` value is a string. Example of a complete table:

   ```toml
   [[connector]]
   name = "notes"
   command = ["/Users/me/.local/share/uv/tools/passageway/bin/python", "-m", "passageway_connector_trilium"]
   env = { URL = "http://127.0.0.1:8080" }
   secrets = { TOKEN = "env:TRILIUM_TOKEN" }
   ```
4. For a `secrets` entry, the variable is set where the server starts: `~/.config/passageway/env` for the service (step 6), `environment:` in compose (https://passageway.marceltov.de/deploy/). Never ask for its value.
5. Check the file parses: `<python> -c 'import tomllib,sys; tomllib.load(open(sys.argv[1],"rb"))' <file>`.
6. If a `secrets` entry references a variable the server does not have yet, add `NAME=` to `~/.config/passageway/env` (0600; the service installed by `/passageway-install` reads it) and ask the user to fill the value in that file with their editor. Restart the server yourself: `launchctl kickstart -k gui/$(id -u)/de.marceltov.passageway` for the launchd service, `systemctl --user restart passageway` for systemd, `docker compose restart passageway` for the container; a server started by hand in a terminal is the user's to restart. Then `curl -s <url>/health`: `"starting"` while the first index build runs, then `"ok"` with the source listed; `"error"` names the problem (a missing variable, an unreachable source). A big source takes minutes on the first build.
7. Say what was added and suggest a question the `recall` tool should now answer.

## Show

The embedding model is not this skill's job: the `/passageway` guide says how to pick a preset or run any model (`[embedder]`).

Print the file with the values of every `secrets` entry replaced by `***` (they are references, but the habit matters), and `/health` for what the server runs with.
