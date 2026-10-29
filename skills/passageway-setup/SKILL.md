---
name: passageway-setup
description: "Connect Claude Code to a running passageway server: set its URL and password once, so the prompt hook adds relevant passages from the user's sources automatically and the recall MCP tool is registered. Use when the user wants to connect, check or remove the passageway hook or MCP server in Claude Code."
---

# Set up passageway in Claude Code

passageway is a retrieval server next to the user's sources (docs: https://passageway.marceltov.de/). It indexes them and answers "do the sources know something about this?" in milliseconds. Once connected, Claude Code gets two things:

- a **prompt hook** (`UserPromptSubmit`, shipped with this plugin) that sends each prompt to the server and adds up to three short passages to the context when something relevant exists, and nothing otherwise;
- the **`recall` MCP tool** (server name `passageway`), for searching on purpose mid-task.

The connection is two pieces, both written by this skill: the hook's config file `passageway.json` in the plugin data folder, and the MCP server registration. Never print the password.

## On claude.ai, the desktop app or Cowork

There is no hook and no `claude` CLI there. Add a custom connector (*Customize → Connectors → Add custom connector*) with the server's public HTTPS URL ending in `/mcp`. claude.ai opens the server's login page; the password is the server's `PASSAGEWAY_LOGIN_PASSWORD`. This needs `PASSAGEWAY_BASE_URL` set on the server: without it, the connector gets a 401 and no login page. Everything below applies to Claude Code.

## Determine the operation

**Add** (default), **check**, or **remove**.

## Add

1. Ask for the server URL (for example `http://127.0.0.1:8082` for a local server, or `https://passageway.example` for a sidecar, no path) and the `PASSAGEWAY_LOGIN_PASSWORD` the server was started with. A local server set up with `passageway init` keeps it in `~/.config/passageway/password`: read it from there with a command, do not ask the user to paste it. If the user does not know it, it is in the server's environment (its compose file or secret store).
2. Check it: `curl -s <url>/health`. Expect JSON with `"status": "ok"` (or `"starting"` while the first index build runs). `"error"` names the misconfiguration; stop and report it.
3. Write the hook config, readable only by the user. The plugin data folder is `$CLAUDE_PLUGIN_DATA`, falling back to `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/plugin-data/passageway`:

   ```bash
   dir="${CLAUDE_PLUGIN_DATA:-${CLAUDE_CONFIG_DIR:-$HOME/.claude}/plugin-data/passageway}"
   mkdir -p "$dir" && umask 077 && python3 -c 'import json,sys; json.dump({"url": sys.argv[1], "token": sys.argv[2]}, open(sys.argv[3], "w"))' "<url>" "<password>" "$dir/passageway.json"
   ```

   Pass the password through a variable or a file, never typed into the command line of the transcript.
4. Register the MCP server (user scope):

   ```bash
   claude mcp add --transport http passageway "<url>/mcp" -H "Authorization: Bearer <password>" -s user
   ```

5. Tell the user: the hook works from the next prompt in a new session; `recall` is available as a tool right away. A trilium-recall hook config (`plugin-data/trilium-recall/recall.json`) keeps working until it is replaced.

## Check

`curl -s <url>/health` for the server; `cat "$dir/passageway.json"` exists (do not print the token); `claude mcp list` shows `passageway`. Run `bash "${CLAUDE_PLUGIN_ROOT}/scripts/test-recall-hook.sh"` to check the hook itself against a stub.

## Remove

Delete `$dir/passageway.json` and run `claude mcp remove passageway -s user`. The server keeps running; this only disconnects Claude Code.
