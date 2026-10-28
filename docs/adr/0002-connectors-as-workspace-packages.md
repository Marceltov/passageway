---
status: accepted
date: 2026-10-28
decision-makers: Marcel Bruckner
---

# One repository, each connector a self-contained workspace package

## Context and Problem Statement

passageway ships bundled connectors (Wikipedia, Trilium, Confluence, later others) next to the core. Where should they live, and who owns their tests and dependencies?

## Considered Options

* A repository per connector.
* One repository, one package, connectors as submodules of the core.
* One repository, a uv workspace: the core plus a self-contained package per connector.

## Decision Outcome

Chosen option: "one repository, a uv workspace", because the protocol is still changing and a change must land in the core, the contract check and every connector as one reviewed unit, while each connector keeps its own `pyproject.toml`, dependencies, tests and README.

A connector talks to the core only through the JSON Lines protocol and the shared contract check (`passageway.testing.contract`), so it can be split into its own repository later with `git subtree split` once the protocol is frozen, or when a connector gets its own maintainers or heavy dependencies. Third-party connectors already live outside this repository and follow the same recipe.

### Consequences

* Good, because the core stays free of connector dependencies and a connector's tests live and run with it.
* Good, because the layout is the template an outside connector author copies.
* Bad, because contributors need the workspace installed (`uv sync` does it; the connector is part of the default dev group).
* Bad, because one CI job covers all packages for now.
