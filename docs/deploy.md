# Run it: as a service or as a container

Two ways to keep passageway running. Both use the same code; only defaults differ. In Claude Code, `/passageway-install` from the [plugin](guides/claude-code.md) sets up the service below for you, with launchd or systemd.

## On your own machine

`passageway init` prepares the configuration folder once:

```bash
passageway init
```

It creates `~/.config/passageway/` with a generated `password` (readable only by you; the Bearer token for the hook and the tool), and a `passageway.toml` to fill in with your connectors if there is none yet. It prints the two things to do next: edit the file, and start the server with the password file:

```bash
PASSAGEWAY_LOGIN_PASSWORD_FILE=~/.config/passageway/password passageway
```

The server binds to `127.0.0.1:8082`, fetches the default model on first start, and answers at `http://127.0.0.1:8082/health`. Connect Claude Code with the [plugin](guides/claude-code.md).

### Keep it running with launchd (macOS)

Save this as `~/Library/LaunchAgents/de.marceltov.passageway.plist`, with the path of your `passageway` (`which passageway`):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>de.marceltov.passageway</string>
  <key>ProgramArguments</key>
  <array><string>/Users/you/.local/bin/passageway</string></array>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PASSAGEWAY_LOGIN_PASSWORD_FILE</key><string>/Users/you/.config/passageway/password</string>
    <key>PATH</key><string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
  </dict>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>/Users/you/Library/Logs/passageway.log</string>
  <key>StandardErrorPath</key><string>/Users/you/Library/Logs/passageway.log</string>
</dict>
</plist>
```

Then `launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/de.marceltov.passageway.plist`. The connectors run with an empty environment plus `PATH` and `HOME`, so the `PATH` above must reach the interpreter named in your `passageway.toml`. On Linux, a systemd user unit with the same two environment variables does the same (`EnvironmentFile=-%h/.config/passageway/env` is the place for the connectors' tokens). The plugin's `/passageway-install` skill writes either one for you, with a small wrapper that reads `~/.config/passageway/env` (`NAME=value` lines, readable only by you) so the tokens your connectors reference as `env:NAME` never appear in the plist.

## As a container

The image `ghcr.io/marceltov/passageway` is built from the repository's `Dockerfile` on every release, for amd64 and arm64: the server with every bundled connector and embedder, and the default model baked in and verified by checksum, so the container fetches nothing at start as long as it uses the default model (another preset is fetched into `/data/models` once). It runs as an unprivileged user.

```yaml
services:
  passageway:
    image: ghcr.io/marceltov/passageway:latest
    ports: ["8082:8082"]
    volumes:
      - passageway-data:/data
      - ./passageway.toml:/config/passageway.toml:ro
    environment:
      PASSAGEWAY_LOGIN_PASSWORD: ${PASSAGEWAY_LOGIN_PASSWORD}
      PASSAGEWAY_BASE_URL: https://passageway.example.org     # the public address, for claude.ai's login
      TRILIUM_TOKEN: ${TRILIUM_TOKEN}                         # whatever your connectors' secrets reference
volumes:
  passageway-data:
```

Inside the container the defaults are `PASSAGEWAY_HOST=0.0.0.0`, `PASSAGEWAY_DATA_DIR=/data`, `PASSAGEWAY_CONFIG=/config/passageway.toml` and `PASSAGEWAY_MODEL_DIR=/models/e5-small`; the health check calls `/health` every minute. The bundled connectors are installed, so a `command` of `["python", "-m", "passageway_connector_trilium"]` works as written (the venv's `python` is first on the `PATH`). A connector of your own needs a derived image that adds it, or a mount.

`:latest` moves only on pushed version tags, so a watcher that pulls `latest` installs each release on its own. The image is a few hundred megabytes, most of it the model and the ONNX runtime.
