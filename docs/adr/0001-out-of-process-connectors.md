---
status: accepted
date: 2026-10-28
decision-makers: Marcel Bruckner
---

# Sources are out-of-process connectors speaking JSON Lines

## Context and Problem Statement

passageway must index many kinds of sources (notes, wikis, document stores) without the core knowing any of them, and anyone should be able to add a source in any language. How does the core obtain items from a source?

## Decision Drivers

* The core must stay free of source-specific code and dependencies.
* Third parties must be able to write a connector without touching the core.
* A broken or hanging connector must not take the server, or the other sources, down.
* Credentials for one source must not be visible to another source or to the core's own password.

## Considered Options

* In-process Python plugins (a connector class loaded by the core).
* Out-of-process executables that print JSON Lines, started per call by the core.
* A long-running connector service per source, called over HTTP.

## Decision Outcome

Chosen option: "out-of-process executables that print JSON Lines" (the transport is weighed against gRPC and others in [ADR 0003](0003-json-lines-over-a-subprocess-stays.md)), because it is the only option that gives language independence, process isolation and a single mechanism for bundled and third-party connectors at the cost of one process start per call.

The core runs `<command> <mode>` for `check`, `list`, `fetch` and `changed`. Each call starts with an empty environment plus the connector's own settings and the secrets it names, reads one JSON object per line, and stores nothing unless the process exits successfully. A timeout kills the connector's whole process group. A reconcile that would delete more than a configured share of a source is refused.

### Consequences

* Good, because the core needs no source dependencies and a connector can be written in any language.
* Good, because a crash, hang or oversized output fails one call and leaves the index as it was.
* Good, because bundled connectors are tested by the same contract suite third parties can use.
* Bad, because every call pays a process start, so `changed` polling must be cheap to start.
* Bad, because the protocol is now a public interface; changing it later means versioning it (`PASSAGEWAY_PROTOCOL`).

### Confirmation

`passageway.testing.contract.check_connector` and `tests/test_protocol.py` exercise the contract against real subprocesses, including limits, timeouts, secret masking and environment isolation.
