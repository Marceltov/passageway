"""passageway init: the configuration folder with a generated password and a passageway.toml to fill in."""

import os
import secrets
import sys
from pathlib import Path

from passageway.config import ConfigError, default_config_path, instance_name

SAMPLE = '''# passageway.toml: one [[connector]] per source. Secrets are references to environment variables, never values.
# Documentation: https://passageway.marceltov.de/configuration/

# [[connector]]
# name = "notes"
# command = ["{python}", "-m", "passageway_connector_markdown"]
# env = {{ FOLDER = "/path/to/your/notes" }}
'''


def main(argv: list[str], env=None, stdout=None) -> int:
    env = os.environ if env is None else env
    stdout = stdout or sys.stdout
    if argv:
        print("usage: passageway init  (creates the configuration folder with a generated password and a passageway.toml "
              "to fill in; it keeps what is there)", file=stdout)
        return 0 if argv in (["--help"], ["-h"]) else 2
    try:
        instance = instance_name(env)
    except ConfigError as e:
        print(f"init: {e}", file=stdout)
        return 2
    config = Path(env.get("PASSAGEWAY_CONFIG") or default_config_path(instance))
    folder = config.parent
    folder.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(folder, 0o700)
    except OSError:
        pass
    password = folder / "password"
    if password.exists():
        os.chmod(password, 0o600)
        print(f"{password}: already there, kept (readable only by you)", file=stdout)
    else:
        with open(os.open(password, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w") as f:
            f.write(secrets.token_hex(24) + "\n")
        print(f"{password}: generated (readable only by you)", file=stdout)
    if config.exists():
        print(f"{config}: already there, kept", file=stdout)
    else:
        config.write_text(SAMPLE.format(python=sys.executable))
        print(f"{config}: written, fill in your connectors", file=stdout)
    prefix = f"PASSAGEWAY_PORT=<a free port> " if instance else ""
    flag = f" --instance {instance}" if instance else ""
    print(f"\nThen start the server:\n  {prefix}PASSAGEWAY_LOGIN_PASSWORD_FILE={password} passageway{flag}", file=stdout)
    print("and connect Claude Code with /passageway-connect (https://passageway.marceltov.de/guides/claude-code/)", file=stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
