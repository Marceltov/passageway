---
status: accepted
date: 2026-10-30
decision-makers: Marcel Bruckner (the direction), Claude (the write-up)
---

# Several instances under one user, separated by convention

## Context and Problem Statement

Several Claude setups run side by side on one machine (personal, work, a customer), and each may see only some sources. They need their own passageway: their own connectors, index and password, and their own MCP connection. Some setups also need more than one of them (#71). How are instances told apart, and how hard is the line between them?

## Considered Options

* One setting, `PASSAGEWAY_INSTANCE=<name>`, that moves the default config and data folders to `passageway-<name>`, under the same operating-system user; each Claude connects to the instances the user chooses.
* The same, but each instance as its own operating-system user or container, so that one Claude cannot read another instance's password.
* No new setting: the skills set `PASSAGEWAY_CONFIG`, `PASSAGEWAY_DATA_DIR` and `PASSAGEWAY_MODEL_DIR` by hand for each instance.

## Decision Outcome

Chosen option: "one setting, under the same user". It keeps sources, indexes, passwords and connections apart, which is what the owner asked for; which Claude connects to which instance is the owner's responsibility, and the documentation says that under one user it is not a security boundary. One setting instead of three keeps the skills and the commands (`passageway init`, `eval`, `model`) short and hard to get half right. The built-in models stay in the shared data folder, so a second instance downloads nothing.

A Claude may connect to several instances: one hook file per instance (`passageway.json`, `passageway-<name>.json`) and one MCP server (`passageway`, `passageway-<name>`). The hook asks them all at once within its time limit and joins the passages; one that is down costs only its own.

### Consequences

* Good, because nothing changes for a single instance, and adding one is `PASSAGEWAY_INSTANCE=<name>` plus a port.
* Bad, because a Claude with a shell can read every instance's password file under the same user. A boundary that must hold needs a user or a container per instance, which the documentation points to.
