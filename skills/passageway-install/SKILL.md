---
name: passageway-install
description: "Install passageway on this machine and run it as a service that survives reboots: uv tool install with the connectors the user wants, passageway init for the password and the config, a launchd agent (macOS) or systemd user unit (Linux) that reads the password and the connectors' secrets from files only the user can read, then /health. Use when the user wants passageway on their machine, when /passageway-connect finds nothing listening locally, or to upgrade."
---

# Install passageway and keep it running

passageway (docs: https://passageway.marceltov.de/) is a server next to the user's sources. This skill puts it on the machine and runs it as a user service, so that the user never starts it by hand. Never print a secret, never ask the user to paste one into the chat: the password lives in a file `passageway init` writes, and the connectors' tokens in one environment file the user fills in an editor.

**Documentation:** the index https://passageway.marceltov.de/llms.txt lists every page with its markdown address; the whole documentation is one file, https://passageway.marceltov.de/llms-full.txt. The pages for this skill: https://passageway.marceltov.de/install/ and https://passageway.marceltov.de/deploy/. Fetch them before acting when a step below does not match what you see.

Free text (a URL, a folder, a space key, a name) is asked in the chat, never through a choice prompt; a choice prompt is only for real alternatives (which source, which operation).

## Determine the operation

**Install** (default), **upgrade** (same install command again, then restart), or **remove** (stop and remove the service, `uv tool uninstall passageway`; the config folder stays).

## Install

1. `uv --version`; without uv: `curl -LsSf https://astral.sh/uv/install.sh | sh` (ask first, it changes the user's shell setup), or `brew install uv`.
2. Ask which sources to index (a folder of markdown, Trilium, Confluence, Wikipedia; several are fine) and install passageway with those connectors in one environment:

   ```bash
   uv tool install \
     --with 'passageway-connector-trilium @ git+https://github.com/Marceltov/passageway#subdirectory=connectors/trilium' \
     --with 'passageway-connector-markdown @ git+https://github.com/Marceltov/passageway#subdirectory=connectors/markdown' \
     git+https://github.com/Marceltov/passageway
   ```

   The packages are `passageway-connector-<name>` under `connectors/<name>`. The command replaces the set, so list every connector the user wants. For a release, append `@v0.2.0` to the main URL (the latest tag: https://github.com/Marceltov/passageway/releases). `passageway --help` must then work.
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

The `uv tool install` command from step 2 with the same connectors (add `--reinstall` to force), then the restart command for the platform, then `/health` and its `version`.
