# Claude Code: the hook and the plugin

Claude Code can use passageway in two ways, and the plugin sets up both:

- **The `recall` tool** over MCP, which the model calls when it decides to search. The server sends instructions on connect that say when to call it.
- **A prompt hook** (`UserPromptSubmit`) that sends every prompt to the server and adds up to three short passages to the context when the sources have something, and nothing otherwise. The hook exists because a model only calls a tool when it thinks it needs one, and skips it when it believes it knows the answer; the hook does not ask.

## Install the plugin

```bash
/plugin marketplace add Marceltov/passageway
/plugin install passageway@passageway
```

This gives you the hook, `/passageway-install` that installs the server on this machine and runs it as a service, the `/passageway-connect` skill that connects it, `/passageway-add-source` that writes a source into `passageway.toml`, the `/passageway` guide and `/create-passageway-connector`. Run `/passageway-install` for a local server, or `/passageway-connect` for one that already runs, and give it the server's URL; it checks `/health`, writes the hook's config and registers the MCP server. A fresh `passageway.toml` has no source yet: `/passageway-add-source` writes the `[[connector]]` for a folder of markdown, Trilium, Confluence or Wikipedia, with secrets as `env:` references, and tells you how to restart. Never paste the password into the chat: the skill reads it from `~/.config/passageway/password` for a local server, or you pass it through a variable.

## How the hook behaves

- It reads `passageway.json` (`{"url", "token"}`) from the plugin's data folder or from `${CLAUDE_CONFIG_DIR:-~/.claude}/plugin-data/passageway/`, where the connect skill writes it, readable only by you. A `recall.json` left by trilium-recall is used until it is replaced.
- It posts the prompt (the first 20,000 characters), the session id and the working directory to `POST /recall`. The password and the prompt go through files only you can read, never on a command line.
- It waits at most 1.5 s. A slow or broken server, no config, a bad answer: no output, exit 0. It never blocks a prompt.
- What comes back is the rendered passages (`context`), which it hands to Claude as additional context. The server remembers per session what it already showed, so a passage is not repeated.
- `bash "$CLAUDE_PLUGIN_ROOT/scripts/test-recall-hook.sh"` checks the hook against a stub server: a hit, no hit, errors, a slow server, a huge prompt, both config folders, and that neither the password nor the prompt shows up in the process table; `scripts/test-recall-hook.sh` in the repository is the same file.

## Without the plugin

The hook is one shell script, `scripts/recall-hook.sh`; any hook runner can call it with the Claude Code hook input on stdin. The MCP registration is one command:

```bash
claude mcp add --transport http passageway "http://127.0.0.1:8082/mcp" -H "Authorization: Bearer $(cat ~/.config/passageway/password)" -s user
```

On claude.ai, the desktop app or Cowork there is no hook: add the server's public HTTPS URL ending in `/mcp` as a custom connector and log in with the password (the server needs `PASSAGEWAY_BASE_URL` for that login page, see [Install](../install.md)).
