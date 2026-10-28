---
status: accepted
date: 2026-10-28
decision-makers: Marcel Bruckner
---

# JSON Lines over a subprocess stays, with a JSON Schema beside it

## Context and Problem Statement

[ADR 0001](0001-out-of-process-connectors.md) chose out-of-process connectors speaking JSON Lines, but never weighed a transport such as gRPC, and the planned embedder protocol would repeat it. Before the protocol is frozen at v1 and others build on it: is JSON Lines over a subprocess the right transport for connectors and for embedders?

## Decision Drivers

* Anyone should be able to write a connector in any language in minutes, and debug it by hand.
* A connector must be isolated: its own environment, killable, nothing stored from a failed call.
* No ports, certificates or service lifecycle to run next to the core, least of all in the sidecar container.
* Other languages should get a machine-readable contract.

## Considered Options

1. Keep JSON Lines over a subprocess and publish a JSON Schema for its messages.
2. Add a long-running mode over stdio with JSON-RPC, for connectors with an expensive start.
3. gRPC: a schema with generated stubs, streaming, health checks and connection reuse.
4. HTTP/REST or MCP as the connector transport.

## Decision Outcome

Chosen option: "keep JSON Lines over a subprocess and publish a JSON Schema" (option 1), for connectors and for embedders alike.

The cost that would argue against it is small. A start of the Wikipedia connector, with its `httpx` import, takes about 58 ms, and a bare Python start about 11 ms (median of ten runs on a laptop, 2026-10-28), while the poll runs once a minute. gRPC would add `grpcio` to the core and to Python connectors, a code generator per language, a port with TLS and authentication per connector and a lifecycle to manage, and a connector could no longer be tried with `echo`. Options 3 and 4 trade the property this project is built on for typed contracts that a schema gives anyway.

What changes with this decision:

* [`connector-protocol.schema.json`](../reference/connector-protocol.schema.json) describes every message (`check`, `list`, `fetch` in and out, `changed`). A test keeps it in step with the core's validator on a table of good and bad records, and the fake and Wikipedia connectors are validated against it.
* `check` may print `"protocol": "1"`. The contract check (`check_connector`) refuses a connector that announces another version, with a message that says so; a `check` without the field is taken to speak v1. The running server does not call `check` yet.
* The embedder protocol, which is planned (see the roadmap), uses the same transport. An embedder is designed as one long-lived process (`{"op":"info"}`, `{"op":"embed",…}`), which is exactly where a per-call start would hurt; it gets its own schema when it is built.

### Consequences

* Good, because the contract stays one page and one file, and a connector in any language can validate itself against the schema.
* Good, because nothing new has to run or be exposed.
* Bad, because there is no streaming, progress or cancellation other than killing the process, and no connection reuse; a connector with a slow start pays it every minute.
* Bad, because flow control is replaced by size limits per line and per call.

### More Information

If a connector ever needs a long-running mode, JSON-RPC over stdio (as LSP and MCP do) is the upgrade path: the same JSON in one process kept alive, optional, with the per-call mode as the default. It is not built because no connector needs it.
