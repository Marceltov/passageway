---
name: passageway-status
description: "Is passageway fine? Checks the whole chain in order and says what to do: the server's own status tool (sources, counts, errors, model, version), the service that keeps it running, the hook's config and self-test, the MCP registration, and the log. Use when recall returns nothing it should, when the hook is silent, after a restart or an upgrade, or when the user asks whether passageway works."
---

# Is passageway fine?

Five links in the chain can fail, and the symptom is the same for all of them: Claude gets no passages. This skill walks the chain from the server outwards, stops at the first broken link, and says what to do about it. It prints no secret and quotes nothing from the user's sources beyond what `status` reports (names and counts).

**Documentation:** the index https://passageway.marceltov.de/llms.txt lists every page with its markdown address; the whole documentation is one file, https://passageway.marceltov.de/llms-full.txt. The pages for this skill: https://passageway.marceltov.de/configuration/#health and https://passageway.marceltov.de/guides/claude-code/.

Free text (a URL, a path) is asked in the chat, never through a choice prompt. Usually nothing needs asking: the URL is in the hook config.

**Several instances.** A machine may run several passageway servers side by side, one per Claude setup (https://passageway.marceltov.de/configuration/#several-instances). Instance `<name>` lives in `~/.config/passageway-<name>/` (its `passageway.toml`, `password` and `env`), listens on its own port, runs as the service `de.marceltov.passageway.<name>` (macOS, log `~/Library/Logs/passageway-<name>.log`) or `passageway-<name>` (Linux), and `/health` names it under `instance`. Wherever this skill says `~/.config/passageway`, the service, the log or port 8082, use the instance's. `ls -d ~/.config/passageway*/` lists them. Check every instance this Claude is connected to: one hook file each (`passageway.json`, `passageway-<name>.json`) whose URL's `/health` names it, and one MCP server each (`passageway`, `passageway-<name>`).

## The chain, in order

1. **The server, asked directly.** Call the MCP tool `status` (server `passageway`). It returns `status` (`ok`, `starting`, `degraded`, `error`), each source with `items`, `sections`, `last_ok` and `last_error`, the `embedder` with its `last_error`, and the `version`. Read it back in one line per source, plain words: "notes: 1,240 items, synced 3 minutes ago" or "wiki: failing since 09:10: <the error>". If the tool itself is not available, the MCP registration is the broken link: go to step 4, then come back.
   - `starting`: the first index build or a model download is running; say so and how to watch it (the log, step 5). Not an error.
   - `degraded` with a source error: the connector cannot reach its source or a secret is missing. The error names it (a host, a 401, a variable). A missing variable means `~/.config/passageway/env` lacks the line: `/passageway-add-source` writes it. After the fix, restart (step 2) and ask `status` again.
   - `degraded` with an embedder error: the model failed to load or the embedder program died; the log has the traceback.
   - `error`: the configuration did not load; the message says which key. Fix `passageway.toml`, restart.
2. **The service.** Local server: `launchctl print gui/$(id -u)/de.marceltov.passageway | head -20` (macOS; look at `state` and `last exit code`) or `systemctl --user status passageway` (Linux). Not loaded at all: `/passageway-install` writes and starts it. Loaded but exiting: step 5. A container: `docker ps --filter name=passageway` and `docker inspect --format '{{.State.Health.Status}}' <name>`. Restart when a fix needs it: `launchctl kickstart -k gui/$(id -u)/de.marceltov.passageway`, `systemctl --user restart passageway`, `docker compose restart passageway`.
3. **The hook.** `test -f "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/plugin-data/passageway/passageway.json"` (or in `$CLAUDE_PLUGIN_DATA`); do not print it. Missing: `/passageway-connect`. Then `bash "${CLAUDE_PLUGIN_ROOT}/scripts/test-recall-hook.sh"`: every line `ok` means the script itself is sound; a `FAIL` names what broke. Then the real thing: `curl -s -o /dev/null -w '%{http_code}' -H "Authorization: Bearer $(cat ~/.config/passageway/password)" -H 'Content-Type: application/json' -d '{"prompt": "status check"}' <url>/recall` must be `200`; `401` is a password that does not match the server's (the hook config holds an old one: `/passageway-connect` again).
4. **The MCP registration.** `claude mcp list` shows `passageway` with its URL. Missing: `/passageway-connect`. Present but the `recall` tool is absent in this session: the session started before the registration; a new session picks it up.
5. **The log.** `tail -50 ~/Library/Logs/passageway.log` (launchd), `journalctl --user -u passageway -n 50` (systemd), `docker logs --tail 50 <name>`. Read for the last `ERROR` or traceback and say it in one line. `/health` without the Bearer token hides the error text on purpose; the log and `status` have it.

## When all five are fine

Say so with the numbers from `status`, and the two reasons recall can still return nothing: the question has no close passage in the sources (the relevance gate is doing its job; `/passageway-evaluate` measures it), or the hook already showed that passage in this session (it does not repeat a hit within a session).

## Also

- `curl -s <url>/health` is the same report without the error texts and needs no token: for a monitor, or when the MCP tool is not reachable.
- After an upgrade, `status.version` must be the new version; if not, the service runs the old binary: restart it.
