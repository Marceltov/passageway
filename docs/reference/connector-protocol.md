# Connector protocol

A connector is any executable that lists items and returns their text as JSON Lines. passageway runs it, indexes the result and never needs to know the source. This page is the protocol reference (v1). A machine-readable version of the messages is the [JSON Schema](connector-protocol.schema.json); validate a connector's output against it from any language.

The core runs `<command> <mode>`. stdout is one JSON object per line. stderr goes to the log with secrets masked. A non-zero exit fails the call.

| Mode | Input | Output |
|---|---|---|
| `check` | none | `{"ok": true, "count": 42}`, optionally with `"protocol": "1"` (a connector that names another version is refused) |
| `list` | none | `{"id", "version"}` for every existing item |
| `fetch` | `{"id"}` lines on stdin | an item record per requested id that still exists |
| `changed --since <UTC ISO>` | none | an item record per item changed since then; optional, a connector that cannot answer cheaply prints nothing and its edits appear at the next reconcile |

Item record:

```json
{"id": "abc", "title": "Rotating certificates", "url": "https://…", "version": "3f2a",
 "sections": [{"heading": "Steps", "text": "Rotate the signing cert every year…"}],
 "weight": 1.0, "path": ["Ops", "Security"], "links": ["def"],
 "labels": ["decision"], "updated": "2026-10-28T09:00:00Z"}
```

- Required: `id`, `title`, `url`, `version`, `sections` (may be empty; a section has optional `heading` and required `text`).
- Optional: `weight` (multiplier on the ranking score, default 1.0), `path` (breadcrumb), `links` (ids of related items, shown with a hit when they are indexed), `labels` (short tags), `updated`.
- The core builds the embedded text as `title › path › heading: text` and splits any section over a size cap at paragraph boundaries, so a connector cannot send an oversize section.
- `version` is any string that changes when the content changes; the core fetches only items whose version differs.
- The connector receives an empty environment plus `PATH`, `HOME`, `PASSAGEWAY_PROTOCOL=1`, its `env` table and its named secrets. It never sees the core's password or another connector's secrets.
- A call succeeds completely or stores nothing.
- `list` decides deletions. The deletion guard refuses to remove more than 30 % of a source (configurable, and never less than one item) or all of a source that has two or more items, and reports an error instead.
- A failing connector never stops other sources; its already indexed items stay searchable. Line size, call size and timeout have configurable defaults.

## Try it

Save a list of item records (see above) as `items.json`, then:

    FAKE_ITEMS=items.json python -m passageway.testing.fake_connector list
    FAKE_ITEMS=items.json python -m passageway.testing.fake_connector check

and point a `[[connector]]` at that command in `passageway.toml` (see [Install](../install.md)). To test your own connector, call `passageway.testing.contract.check_connector(Connector("mine", [...]))` from a pytest test: it checks the rules above that a test can check.
