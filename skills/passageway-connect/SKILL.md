---
name: passageway-connect
description: "Connect Claude Code to a running passageway server: set its URL and password once, so the prompt hook adds relevant passages from the user's sources automatically and the recall MCP tool is registered. Use when the user wants to connect, check or remove the passageway hook or MCP server in Claude Code."
---

# Set up passageway in Claude Code

passageway is a retrieval server next to the user's sources (docs: https://passageway.marceltov.de/). It indexes them and answers "do the sources know something about this?" in milliseconds. Once connected, Claude Code gets two things:

- a **prompt hook** (`UserPromptSubmit`, shipped with this plugin) that sends each prompt to the server and adds up to three short passages to the context when something relevant exists, and nothing otherwise;
- the **`recall` MCP tool** (server name `passageway`), for searching on purpose mid-task.

**Documentation:** the index https://passageway.marceltov.de/llms.txt lists every page with its markdown address; the whole documentation is one file, https://passageway.marceltov.de/llms-full.txt. Before you act on something this skill only names (a connector's settings, a configuration key, a deploy step), fetch its page and work from it, not from memory.

The connection is two pieces, both written by this skill: the hook's config file `passageway.json` in the plugin data folder, and the MCP server registration. Never print the password.

## On claude.ai, the desktop app or Cowork

There is no hook and no `claude` CLI there. Add a custom connector (*Customize → Connectors → Add custom connector*) with the server's public HTTPS URL ending in `/mcp`. claude.ai opens the server's login page; the password is the server's `PASSAGEWAY_LOGIN_PASSWORD`. This needs `PASSAGEWAY_BASE_URL` set on the server: without it, the connector gets a 401 and no login page. Everything below applies to Claude Code.

Free text (a URL, a folder, a space key, a name) is asked in the chat, never through a choice prompt; a choice prompt is only for real alternatives (which source, which operation).

## Determine the operation

**Add** (default), **check**, or **remove**.

## Add

1. Ask for the server URL (for example `http://127.0.0.1:8082` for a local server, or `https://passageway.example` for a sidecar, no path) and the `PASSAGEWAY_LOGIN_PASSWORD` the server was started with. A local server set up with `passageway init` keeps it in `~/.config/passageway/password`: read it from there with a command, do not ask the user to paste it. If the user does not know it, it is in the server's environment (its compose file or secret store).
2. Check it: `curl -s <url>/health`. Expect JSON with `"status": "ok"` (or `"starting"` while the first index build runs). `"error"` names the misconfiguration; stop and report it. Nothing listening on a local URL means the server is not installed or not running: run `/passageway-install`, which installs it and runs it as a service (launchd or systemd) that reads the password from the file, then come back here. A `passageway.toml` without a `[[connector]]` serves an empty index: `/passageway-add-source` adds one.
3. Write the hook config, readable only by the user, into `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/plugin-data/passageway/` (the hook reads this folder as well as the plugin's own data folder). Put the password in a file first (`passageway init` already did, at `~/.config/passageway/password`), and read it from there, so that it is never typed:

   ```bash
   dir="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/plugin-data/passageway"
   (umask 077 && mkdir -p "$dir" && python3 -c 'import json,sys; json.dump({"url": sys.argv[1], "token": open(sys.argv[2]).read().strip()}, open(sys.argv[3], "w"))' "<url>" "$HOME/.config/passageway/password" "$dir/passageway.json" && chmod 600 "$dir/passageway.json")
   ```
4. Register the MCP server (user scope), again reading the password from the file:

   ```bash
   claude mcp add --transport http passageway "<url>/mcp" -H "Authorization: Bearer $(cat ~/.config/passageway/password)" -s user
   ```

5. Tell the user: the hook works from the next prompt in a new session; `recall` is available as a tool right away. A trilium-recall hook config (`plugin-data/trilium-recall/recall.json`) keeps working until it is replaced.

## Check

`curl -s <url>/health` for the server; `test -f "$dir/passageway.json"` (do not print it); `claude mcp list` shows `passageway`. Run `bash "${CLAUDE_PLUGIN_ROOT}/scripts/test-recall-hook.sh"` to check the hook itself against a stub.

## Remove

Delete `$dir/passageway.json` and run `claude mcp remove passageway -s user`. The server keeps running; this only disconnects Claude Code.
