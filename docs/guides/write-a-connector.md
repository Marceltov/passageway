# Write a connector

A connector is a program that answers three questions about a source: *what exists*, *what is in it*, and optionally *what changed*. It can be written in any language. This guide builds one in Python for a folder of text files.

## The connector

```python
#!/usr/bin/env python3
"""A passageway connector for a folder of .txt files. Setting: FOLDER."""
import hashlib
import json
import os
import sys
from pathlib import Path

folder = Path(os.environ["FOLDER"]).resolve()
files = sorted(p for p in folder.rglob("*.txt") if p.is_file())


def item_id(path):
    return path.relative_to(folder).as_posix()


def version(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def emit(record):
    print(json.dumps(record))


mode = sys.argv[1]
if mode == "check":
    emit({"ok": True, "count": len(files)})
elif mode == "list":
    for p in files:
        emit({"id": item_id(p), "version": version(p)})
elif mode == "fetch":
    wanted = {json.loads(line)["id"] for line in sys.stdin if line.strip()}
    for p in files:
        if item_id(p) in wanted:
            emit({"id": item_id(p), "title": p.stem, "url": p.as_uri(), "version": version(p),
                  "sections": [{"heading": None, "text": p.read_text(encoding="utf-8")}]})
# "changed" is optional: print nothing, and edits show up at the next reconcile.
```

passageway runs it as `<command> <mode>`:

| Mode | What it must print |
|---|---|
| `check` | `{"ok": true, "count": n}` |
| `list` | one `{"id", "version"}` line for **every** item that exists |
| `fetch` | an item record for each id it receives on stdin, for ids that still exist |
| `changed --since T` | optional: items changed since the UTC time `T` |

## Try it by hand

```bash
mkdir notes && echo "Lighthouses guide ships." > notes/a.txt
FOLDER=notes python folder_connector.py list
echo '{"id": "a.txt"}' | FOLDER=notes python folder_connector.py fetch
```

## Test it

passageway ships the checks every connector must pass. Call them from a pytest test:

```python
import sys
from pathlib import Path
from passageway.protocol import Connector
from passageway.testing.contract import check_connector

def test_folder_connector(tmp_path):
    (tmp_path / "a.txt").write_text("Lighthouses guide ships.")
    script = str(Path(__file__).with_name("folder_connector.py"))
    connector = Connector("notes", [sys.executable, script], env={"FOLDER": str(tmp_path)})
    check_connector(connector)
```

## Register it

```toml
[[connector]]
name = "notes"
command = ["/usr/bin/python3", "/path/to/folder_connector.py"]
env = { FOLDER = "/path/to/notes" }
```

## Rules that keep it correct

- **Ids are stable**, and unique within the connector.
- **The version changes when the content changes**, and only then. passageway fetches only items whose version differs from the one it has, so a version that changes on every call re-embeds everything every time.
- **`list` is the source of truth for deletions.** Print every existing item; an item missing from `list` is deleted. If your listing can be incomplete, exit non-zero instead of printing less.
- **`fetch` returns only requested ids**, and skips ids that no longer exist.
- **A failure means a non-zero exit and nothing worth keeping on stdout.** passageway stores nothing from a failed call. Write diagnostics to stderr, never secrets.
- **Optional fields** shape the ranking and the answer: `weight` (a multiplier), `path` (a breadcrumb), `labels`, `links` (ids of related items) and `updated`. See the [protocol reference](../reference/connector-protocol.md).
- **Secrets** come in through the environment from the `secrets` table in `passageway.toml`, never as arguments.
