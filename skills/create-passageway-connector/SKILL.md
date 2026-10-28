---
name: create-passageway-connector
description: "Create a passageway connector, a small program that lists the items of a source and prints their text as JSON Lines. Use when the user wants passageway to index a new source such as a folder, an API, a database or a wiki."
---

# Create a passageway connector

A connector is any program that tells passageway what exists in a source, what is in it and, optionally, what changed. passageway runs it as `<command> <mode>`, reads one JSON object per line from stdout, and stores nothing from a call that fails. Reference: https://passageway.marceltov.de/reference/connector-protocol/. The whole documentation as one file: https://passageway.marceltov.de/llms-full.txt.

## Steps

1. **Understand the source before writing code.** Ask: what is one item (a file, a page, a ticket)? What stable id does it have? What changes when its content changes (that is the version: a hash, a revision id, a modified time)? How is it read (files, an API, a database)? Which credentials does it need, and under which environment variable names? Never ask for the values.
2. **Start from this example**, a connector for a folder of text files. Language is free; Python is easiest because the contract check is Python.

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

3. **Adapt it.** Keep the four modes. Choose the id and the version as decided in step 1. Cut an item into sections that are natural units (a heading and its text); passageway splits very long ones itself. Optional fields shape the ranking and the answer: `weight` (a multiplier, default 1.0), `path` (a breadcrumb), `labels`, `links` (ids of related items) and `updated`.

   In Python you can drop the plumbing (mode dispatch, stdin ids, all-or-nothing output, exit codes, item validation) with `passageway-sdk`: subclass `Connector`, implement `versions()` and `fetch(ids)`, call `main()`. The same folder connector with the SDK, the install line and the API are in https://passageway.marceltov.de/guides/write-a-connector/ and https://passageway.marceltov.de/reference/sdk/. Show the user the plain script if they want to see the protocol, and offer the SDK version for Python.
4. **Test it with the shared contract check.** It runs `check`, `list`, `fetch` and `changed` against your connector and checks the rules below.

```python
import sys
from pathlib import Path
from passageway.protocol import Connector
from passageway.testing.contract import check_connector

def test_my_connector(tmp_path):
    (tmp_path / "a.txt").write_text("A note about lighthouses.")
    script = str(Path(__file__).with_name("my_connector.py"))
    check_connector(Connector("mine", [sys.executable, script], env={"FOLDER": str(tmp_path)}))
```

   `passageway` must be importable where pytest runs: `uv add --dev git+https://github.com/Marceltov/passageway`, or run `uv run --with git+https://github.com/Marceltov/passageway pytest`.

   For a connector in another language, run each mode by hand and compare with the rules.
5. **Register it** in `~/.config/passageway/passageway.toml`:

```toml
[[connector]]
name = "mine"                       # starts with a-z or 0-9, then a-z, 0-9, _ or -; it names the index file
command = ["/path/to/python", "/path/to/my_connector.py"]
env = { FOLDER = "/path/to/notes" }
secrets = { TOKEN = "env:MY_TOKEN" }   # references to environment variables, never values
```

   A connector runs with an empty environment except `PATH` and `HOME`, so use an absolute interpreter path, and name every variable it needs in `env` or `secrets`.
6. **Run it and check `GET /health`.** The human starts the server and runs the request; you read the output, never the password. `degraded` means the connector failed; the human adds the bearer header to see the error text and tells you what it says.

## Rules that keep it correct

- Ids are stable and unique within the connector.
- The version changes exactly when the content changes. passageway fetches only items whose version differs, so a version that changes on every call re-embeds everything every time.
- `list` is the truth for deletions: print every existing item. If the listing can be incomplete, exit non-zero instead of printing less. passageway refuses a reconcile that would delete more than a set share of a source.
- `fetch` prints only the ids it is asked for and skips ids that no longer exist.
- A failure is a non-zero exit. Anything on stdout is then discarded; diagnostics go to stderr.
- `changed` is optional. Without it, edits appear at the next reconcile (every 30 minutes by default).
- Never print, log or hard-code a secret, and never ask the human to paste one into the chat. Credentials arrive through the environment. The human starts the server and runs authenticated commands.
