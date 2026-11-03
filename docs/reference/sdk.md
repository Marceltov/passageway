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
| `warn(self, message)` | Report something odd on stderr without failing the call. |
| `expected_errors` | Optional tuple of exception types that mean "the source failed", exit 1 with the message, like `SourceError`. |

The method is called `versions`, not `list`, so that a `list[str]` annotation in your class keeps working.

## What it does for you

- Dispatches `check`, `list`, `fetch` and `changed --since T`; an unknown mode or a bad `--since` exits 2 with a usage message.
- Reads the ids for `fetch` from stdin and skips blank lines.
- **All or nothing:** the output is written only after the whole call succeeded, so a failure leaves stdout empty.
- **Exit codes:** `SettingsError` exits 2 and `SourceError` (or an `expected_errors` type) exits 1, each with `name: message` on stderr and no traceback. Any other exception is a bug in the connector: it propagates, the process exits 1 with a traceback, and stdout is still empty.
- Validates every item with the core's rules before printing it; an invalid item exits 1 and names the problem.
- Prints `check` as `{"ok": true, "count": n, "protocol": "1"}` and keeps the JSON ASCII-safe.

## Markdown helpers

For connectors whose source is (or converts to) markdown:

| Function | What it does |
|---|---|
| `split_markdown(text, skip_first_h1=False)` | The sections of a document: one per heading at any level (`#` to `######`), with the heading as the trail of its parents (`Setup › Linux`). Text before the first heading is a section without a heading; a `#` inside a fenced code block is not a heading; sections without text are dropped. With `skip_first_h1` the first `# heading`, the title, is left out of the trail. |
| `first_h1(text)` | The text of the first level-1 heading outside code, or `None`. Use it as the title. |
| `strip_code(text)` | The text without fenced code blocks and inline code, for finding the links a document really contains. |

`Connector.warn(message)` reports something odd (a skipped file) on stderr as `name: warning: message` without failing the call.

## Testing

`Connector.run(argv, env, stdin, stdout, stderr, **options)` runs one mode in-process and returns the exit code; `options` go to `__init__`. For the contract, run your script as a real subprocess with `passageway.testing.contract.check_connector`, as the [guide](../guides/write-a-connector.md) shows.

## Settings helpers

`passageway_sdk.settings` reads the connector's settings, which arrive as strings in `env`. Each raises `SettingsError` with the setting's name when the value is wrong.

| Function | What it does |
|---|---|
| `names(env, key)` | A list setting: values separated by `\|`, blanks dropped. |
| `whole(env, key, default, low=1)` | A whole number of at least `low`. |
| `flag(env, key, default)` | `true` or `false`, in any case. |
| `seconds(env, key, default)` | A number of seconds that is not negative. |

## Web client

`passageway_sdk.web` is for connectors that read a website. It needs the extra, so the SDK itself keeps no dependencies: `passageway-sdk[web]` installs `httpx` and `truststore`.

`Web(user_agent, pause=0.2, timeout=30.0, max_bytes=2_000_000)` has one method, `get(url, required=False, max_bytes=None)`, which returns a `Reply(status, text, content_type)`. It verifies HTTPS against the operating system's trust store, follows redirects, waits `pause` seconds between requests and refuses a reply over the size limit with `TooLarge` (a `SourceError`). A failure to reach the server, a `5xx` or a `429` raises `SourceError`, so a source that is down fails the call and never looks empty; any other status, such as a `404`, is returned for the connector to judge, or raised with `required=True`.

*The SDK is MIT licensed ([licence](LICENSE)).*
