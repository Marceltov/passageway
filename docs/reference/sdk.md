# Connector SDK

`passageway-sdk` is a small Python package (no dependencies) that does the protocol plumbing of a [connector](connector-protocol.md), so that a connector is the logic of its source. It is a convenience for Python; the protocol stays the contract, and a connector in any language is written against that.

```python
from passageway_sdk import Connector, SettingsError, SourceError
```

## Connector

Subclass it and call `YourConnector.main()`.

| Member | What it does |
|---|---|
| `name` | Prefix of the messages on stderr, e.g. `"folder connector"`. |
| `__init__(self, env)` | Read and validate the settings from `env`; raise `SettingsError` if they are wrong. |
| `versions(self)` | **Required.** Every item that exists, as `{id: version}`. Answers `list` and, by default, `check`. |
| `fetch(self, ids)` | **Required.** The item record (a dict, see the protocol) for each requested id that still exists. |
| `changed(self, since)` | Optional. Items changed since `since`, a timezone-aware `datetime`. Leave it out if that is not cheap; `--since` is then not required. |
| `count(self)` | Optional. The number printed by `check`; by default `len(self.versions())`. |
| `expected_errors` | Optional tuple of exception types that mean "the source failed", exit 1 with the message, like `SourceError`. |

The method is called `versions`, not `list`, so that a `list[str]` annotation in your class keeps working.

## What it does for you

- Dispatches `check`, `list`, `fetch` and `changed --since T`; an unknown mode or a bad `--since` exits 2 with a usage message.
- Reads the ids for `fetch` from stdin and skips blank lines.
- **All or nothing:** the output is written only after the whole call succeeded, so a failure leaves stdout empty.
- **Exit codes:** `SettingsError` exits 2 and `SourceError` (or an `expected_errors` type) exits 1, each with `name: message` on stderr and no traceback. Any other exception is a bug in the connector: it propagates, the process exits 1 with a traceback, and stdout is still empty.
- Validates every item with the core's rules before printing it; an invalid item exits 1 and names the problem.
- Prints `check` as `{"ok": true, "count": n, "protocol": "1"}` and keeps the JSON ASCII-safe.

## Testing

`Connector.run(argv, env, stdin, stdout, stderr, **options)` runs one mode in-process and returns the exit code; `options` go to `__init__`. For the contract, run your script as a real subprocess with `passageway.testing.contract.check_connector`, as the [guide](../guides/write-a-connector.md) shows.
