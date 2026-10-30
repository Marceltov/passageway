---
name: passageway-install
description: "Install passageway on this machine and run it as a service that survives reboots: uv tool install with the connectors the user wants, passageway init for the password and the config, a launchd agent (macOS) or systemd user unit (Linux) that reads the password and the connectors' secrets from files only the user can read, then /health. Use when the user wants passageway on their machine, when /passageway-connect finds nothing listening locally, or to upgrade; on a machine that has it, it upgrades to the latest release."
---

# Install passageway and keep it running

passageway (docs: https://passageway.marceltov.de/) is a server next to the user's sources. This skill puts it on the machine and runs it as a user service, so that the user never starts it by hand. Never print a secret, never ask the user to paste one into the chat: the password lives in a file `passageway init` writes, and the connectors' tokens in one environment file the user fills in an editor.

**Documentation:** the index https://passageway.marceltov.de/llms.txt lists every page with its markdown address; the whole documentation is one file, https://passageway.marceltov.de/llms-full.txt. The pages for this skill: https://passageway.marceltov.de/install/ and https://passageway.marceltov.de/deploy/. Fetch them before acting when a step below does not match what you see.

Free text (a URL, a folder, a space key, a name) is asked in the chat, never through a choice prompt; a choice prompt is only for real alternatives (which source, which operation).

## Determine the operation

First look at what is there and what is current:

```bash
uv tool list --show-with | grep -A3 '^passageway '     # the installed version and its connectors, or nothing
curl -s https://api.github.com/repos/Marceltov/passageway/releases/latest | python3 -c "import json,sys; print(json.load(sys.stdin)['tag_name'])"
```

- **Not installed:** **install** (below), at the latest release.
- **Installed, older than the latest release:** **upgrade** (below). Say which version goes to which before you start; the user asked for this skill, so no further question is needed.
- **Installed and current:** say so, and check the service and `/health` instead (or hand over to `/passageway-status`).
- **Remove**, only when asked: stop and remove the service, `uv tool uninstall passageway`; the config folder stays.

`<tag>` below is the latest release, e.g. `v0.2.4`.

**Several instances** (https://passageway.marceltov.de/configuration/#several-instances). One installation can run several servers side by side, one per Claude setup, each with its own sources, password and port. `ls -d ~/.config/passageway*/` lists what exists: `~/.config/passageway/` is the default instance, `~/.config/passageway-<name>/` instance `<name>`. On a machine with only named instances there is no default: every command needs `--instance`. When the user wants a separate passageway for this Claude (work, a customer), ask for a name (lowercase letters, digits, hyphens) and install that instance: the installation (step 2) is shared, steps 3 to 7 are per instance, with these differences:

- Give every `passageway` command `--instance <name>`; `passageway --instance <name> init` writes `~/.config/passageway-<name>/`. A typo is an error that lists the instances there are.
- Pick a free port from 8083 up (`lsof -nP -iTCP:<port> -sTCP:LISTEN` prints nothing for a free one).
- The service is `de.marceltov.passageway.<name>` (file `~/Library/LaunchAgents/de.marceltov.passageway.<name>.plist`, log `~/Library/Logs/passageway-<name>.log`) or `passageway-<name>.service`. Its environment adds `PASSAGEWAY_INSTANCE=<name>` (services set the variable; the argument is for commands typed by hand) and `PASSAGEWAY_PORT=<port>`, and the password and env file paths use `passageway-<name>`.
- `/health` on that port names the instance under `instance`. Connect only this Claude to it; which Claude uses which instance is the user's responsibility, and each Claude keeps its connection in its own `CLAUDE_CONFIG_DIR`.

The built-in model is shared, so a second instance does not download it again.

## Install

1. `uv --version`; without uv: `curl -LsSf https://astral.sh/uv/install.sh | sh` (ask first, it changes the user's shell setup), or `brew install uv`.
2. Ask which sources to index (a folder of markdown, Trilium, Confluence, Wikipedia; several are fine) and install passageway with those connectors in one environment:

   ```bash
   uv tool install \
     --with 'passageway-connector-trilium @ git+https://github.com/Marceltov/passageway@<tag>#subdirectory=connectors/trilium' \
     --with 'passageway-connector-markdown @ git+https://github.com/Marceltov/passageway@<tag>#subdirectory=connectors/markdown' \
     git+https://github.com/Marceltov/passageway@<tag>
   ```

   The packages are `passageway-connector-<name>` under `connectors/<name>`, all from the same `<tag>`. The command replaces the set, so list every connector the user wants. `passageway --help` must then work.
3. `passageway init`: creates `~/.config/passageway/` with a generated `password` (0600) and a sample `passageway.toml`; rerunning keeps what is there.
4. Write the sources with `/passageway-add-source` (one `[[connector]]` each, secrets as `env:NAME` references). For every `NAME` referenced, add a line `NAME=` to `~/.config/passageway/env` (create it with `umask 077`, `chmod 600`), then ask the user to fill the values in that file with their editor, not in the chat. Leave the file out when no connector needs a secret.
5. Run it as a service.

   **macOS**, `~/Library/LaunchAgents/de.marceltov.passageway.plist` (the program path from `which passageway`; `uv tool dir` tells where the interpreter is, `PATH` must reach it):

   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
   <plist version="1.0">
   <dict>
     <key>Label</key><string>de.marceltov.passageway</string>
     <key>ProgramArguments</key>
     <array>
       <string>/bin/sh</string><string>-c</string>
       <string>f="$HOME/.config/passageway/env"; if [ -f "$f" ]; then set -a; . "$f"; set +a; fi; exec "$HOME/.local/bin/passageway"</string>
     </array>
     <key>EnvironmentVariables</key>
     <dict>
       <key>PASSAGEWAY_LOGIN_PASSWORD_FILE</key><string>/Users/you/.config/passageway/password</string>
       <key>PATH</key><string>/Users/you/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
     </dict>
     <key>RunAtLoad</key><true/>
     <key>KeepAlive</key><true/>
     <key>StandardOutPath</key><string>/Users/you/Library/Logs/passageway.log</string>
     <key>StandardErrorPath</key><string>/Users/you/Library/Logs/passageway.log</string>
   </dict>
   </plist>
   ```

   Then `launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/de.marceltov.passageway.plist`. Restart later with `launchctl kickstart -k gui/$(id -u)/de.marceltov.passageway`; stop with `launchctl bootout gui/$(id -u)/de.marceltov.passageway`. `plutil -lint` the file before loading it.

   **Linux**, `~/.config/systemd/user/passageway.service`:

   ```ini
   [Unit]
   Description=passageway
   After=network.target

   [Service]
   Environment=PASSAGEWAY_LOGIN_PASSWORD_FILE=%h/.config/passageway/password
   EnvironmentFile=-%h/.config/passageway/env
   ExecStart=%h/.local/bin/passageway
   Restart=on-failure

   [Install]
   WantedBy=default.target
   ```

   Then `systemctl --user daemon-reload && systemctl --user enable --now passageway`; `loginctl enable-linger "$USER"` keeps it running when the user is logged out. Restart later with `systemctl --user restart passageway`; the log is `journalctl --user -u passageway`.
6. Wait for `curl -s http://127.0.0.1:8082/health`: `"starting"` while the model is fetched (once, about 0.5 GB) and the first index is built, then `"ok"` with every source listed. `"error"` names the problem; the log has the rest. A missing value in the env file shows as a connector error naming the variable.
7. Connect Claude Code with `/passageway-connect` (it reads the password from the file). Tell the user what runs where: the service name, the config folder, the log, and that `/passageway-add-source` adds more sources later.

## Upgrade

1. Take the connectors from `uv tool list --show-with` (each `passageway-connector-<name>`) and run the `uv tool install` command from step 2 with exactly those, at `<tag>`, plus `--reinstall`. Leaving one out would uninstall it and break its source.
2. Restart the service of every instance (step 5; `ls -d ~/.config/passageway*/` lists them), since they all run from this installation. Nothing in their config folders changes.
3. Wait for `/health` to be `"ok"` again, check that `uv tool list` shows the new version, and tell the user: from which version to which, and the release notes link `https://github.com/Marceltov/passageway/releases/tag/<tag>`.
