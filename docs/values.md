# What passageway stands for

passageway is a retrieval service for Claude: connectors feed it the text of your sources, it indexes them, and it serves the best short passages for a question as one `recall` tool. This page says what it will stay, whoever runs it and whatever it grows into. Everything else follows from it: the features, the design decisions in `docs/adr`, and the [roadmap](roadmap.md).

It is written for you, if you are deciding whether to trust passageway with your notes, your wiki or your company's documentation. It is also the yardstick for every change: a contribution, from a person or an AI, is judged against these points, and a review names the one it touches ("this breaks V2"). Each point says what it rules out, so that it can be used that way.

## Lines never crossed

These three come first. When a feature would be easier, or would read better in a benchmark, by bending one of them, the feature changes or is not built.

### V1. The core knows no source, and no model beyond its default

The core speaks two protocols and nothing else: connectors tell it what exists and what the text is, embedders turn text into vectors. A connector is a program of its own, in any language, and a bundled one has no privileges a third-party one lacks. Knowledge of a particular source (how Trilium nests notes, how Confluence pages are typed) reaches the core only as the plain fields of the item record: weight, path, labels, links. The core ships one built-in embedder, the multilingual e5-small model, as a default that works offline; it sits behind the same interface as a program speaking the embedder protocol, and any other model replaces it with one line of configuration.

**Rules out:** a source-specific import in the core, a branch for a bundled connector, ranking code that behaves differently for one model by name, a protocol field only one connector understands.

**ADRs:** 0001, 0002, 0003.

### V2. Nothing leaves your machine unless you send it

The built-in model runs locally and the index is a local file in passageway's data folder. The first start fetches the built-in model from huggingface.co, pinned to a revision and checksummed; that request tells Hugging Face your address and which model you chose, and nothing of your text or questions. Set `download = false` and copy the files in yourself to keep the server from ever contacting it. Text and questions go to a third party only when you configure an embedder that does, and the documentation says what it sends. passageway reports nothing home and never logs a prompt: a recall leaves one log line with the number of hits and the time, nothing of the question. A measurement report holds no question, title or address from your sources unless you ask for them.

**Rules out:** telemetry, a cloud model as the default, a report that quotes sources by default, logging prompts or passages, a check that calls a server to see whether a version is current.

**ADRs:** none yet; the [evaluate guide](guides/evaluate.md) states what a report holds.

### V3. Numbers are measured, never tuned

Retrieval quality is measured with a public harness on a public corpus and a public question set. The headline rates are published with their confidence intervals, and the whole threshold sweep is shown, not the best row. The question set and the measurements page are in git, so every change to a question or a number is visible; when a published figure turns out to be wrong, the correction is its own commit and the page says what changed. What the numbers cannot show is said next to them.

**Rules out:** a threshold chosen without showing the sweep, a question changed after seeing a result without a commit that says so, a headline rate without its interval, a measurement page that hides its history, a claim about quality that no published run supports.

**ADRs:** none yet; the [measurements page](measurements.md) is the practice.

## What you can rely on

Why you can trust passageway between your sources and your model: what it returns, what it keeps, and what happens when a piece breaks.

### V4. Passages, not answers

passageway returns short passages, each with its title, its place in the source and its link, and up to three of them. The model that asked writes the answer; passageway never does. When nothing passes the relevance gate, the answer is silence, which the `/recall` endpoint and the tool report as "the sources have nothing", not as an error.

**Rules out:** generation or summarisation inside passageway, a "best guess" below the gate, a passage without its source, more than a page of context per question.

**ADRs:** none yet; [How it works](how-it-works.md) describes the gate and the budget.

### V5. The index is disposable, the sources stay the truth

Everything indexed can be rebuilt from the connectors, so deleting an index file loses nothing, and passageway never writes to a source. A connector's listing decides what exists; a listing that would delete more than a configured share of a source (30 % by default), or all of it, is refused, because it is more likely incomplete than true.

**Rules out:** an index as the only copy of anything, a connector that writes, a migration that cannot be redone from the sources, silently emptying a source.

**ADRs:** 0001 records the deletion guard.

### V6. A broken piece breaks only itself

One source failing to sync fails only its own sync, and a hanging connector delays the others until its timeout; neither stops the server, and nothing hides: `/health` names what is failing, the already indexed items keep serving, and the embedder failing makes `recall` fail rather than fall silent, because silence would look like "nothing relevant".

**Rules out:** a server that crashes because a program it started misbehaved, errors swallowed into empty answers, a health check that says "ok" while a part is failing.

**ADRs:** 0001, 0003, 0008.

### V7. Secrets are references

Secrets in the configuration are `env:NAME` references, never values. Each connector and embedder runs with only `PATH` and `HOME` from the server's environment, plus its own settings and the secrets it names; it never sees another's, nor the server's password. Secrets are masked in logs and errors, and nothing in the documentation asks anyone to print one.

**Rules out:** a secret in `passageway.toml`, a connector that can read another's token, credentials in an error message or a log line, a setup step that pastes a key into a chat.

**ADRs:** 0001.

### V8. Self-hosted and open

passageway is AGPL-3.0-or-later and everything in its documentation runs on your own machine or your own container. There is no hosted service it depends on and no feature kept back for one. The sample corpus is Wikipedia text under CC BY-SA, and it says so.

**Rules out:** a feature that only a hosted version has, a license check, a dependency on a service of the author's, content whose license is not stated.

**ADRs:** none yet; the licence files are the practice.

## Principles that follow

### V9. Protocols are written down before others build on them

A protocol is a page, a JSON Schema and a contract check that anyone can run against their own program, and it carries a version. After v1, a change is a migration with a new version, never a quiet edit; a connector that speaks another version is refused with a message that says so.

**Rules out:** a field the core relies on that the page does not mention, a behaviour only the bundled connectors know about, breaking a third-party connector without a version bump.

**ADRs:** 0001, 0003.

### V10. Any language, in an afternoon

A connector is any executable that prints JSON Lines, and the documentation always shows the bare protocol before the Python SDK, so that nobody needs the core installed to write one. The SDK removes boilerplate; it never adds a capability the protocol lacks.

**Rules out:** a connector that must import the core, an SDK-only feature, a guide whose example does not run as a plain script.

**ADRs:** 0001, 0003.

### V11. One honest page beats three vague ones

The documentation says what exists today and what is coming, and tests keep the main things true: the connector and embedder examples in the guides run and pass the contract checks, every environment variable and every option of `passageway eval` is documented, the bundled connectors' and embedders' settings are in their READMEs, and the agent files say the same as the pages. When the roadmap and a page disagree, the page about what exists wins.

**Rules out:** documenting a planned feature as existing, an example that is not tested, a skill that denies what exists, a measurement quoted without its page.

**ADRs:** none yet; `tests/test_docs.py` and `tests/test_agent_files.py` are the practice.

## Changing this page

Points keep their numbers, so that reviews and issues citing them stay right; a point that no longer holds is marked as withdrawn rather than renumbered. A change needs the maintainer's approval and says why in its pull request. Weakening a line never crossed is a change to what passageway is, and is treated as one.
