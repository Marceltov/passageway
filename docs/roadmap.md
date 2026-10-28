# Roadmap

This page is the plan for growing passageway from the [trilium-recall](https://github.com/Marceltov/trilium-recall) engine into a source-agnostic core, and for where each part of trilium-recall ends up. It lives in the repository so that it is reviewed like code: tick a step in the pull request that finishes it, and change this page in the pull request that changes the plan.

## The idea

The core knows no source. Everything specific to a source (Trilium, Confluence, Wikipedia, a folder of markdown files) is a [connector](reference/connector-protocol.md) speaking the JSON Lines protocol, and everything specific to a model is an embedder. trilium-recall's ranking quality, prompt hook and plugin move over; trilium-recall itself then points here.

## Done

- [x] **Bootstrap.** The trilium-recall engine imported with a fresh history. The last commit that still has all the Trilium code is the tag `trilium-engine-import`.
- [x] **Core refactor.** The connector protocol, a generic index with item `weight`, `path`, `labels` and `links`, a protocol-driven sync with a deletion guard, `passageway.toml`, bearer and OAuth authentication, and the contract check connectors test themselves with.
- [x] **Wikipedia connector,** in English and German.
- [x] **Around the code.** The documentation site, a release workflow that posts to notefeed, Dependabot with auto-merge for patch and minor bumps, and the agent entry points (the plugin skills, `/SKILL.md`, `llms-full.txt`).

## Next, in this order

- [ ] **Markdown connector.** Indexes a folder of markdown files, with front matter. It is the base for the corpus below.
- [ ] **A frozen corpus.** A `snapshot` command in the Wikipedia connector writes articles as markdown files with front matter (title, language, URL, revision id, licence). A small English and German snapshot, about 30 articles each on one theme, is committed with an attribution file and its own licence note (CC BY-SA 4.0). Measurements are only reproducible against a corpus that does not change under the questions.
- [ ] **Evaluation harness.** `passageway eval` reports hit@1, hit@3, MRR, silence on unanswerable questions and latency. `--sweep` repeats the run over relevance thresholds, `compare` runs several embedding models on a copy of the index, and `--enforce` makes a CI job fail below targets. Reports are aggregate-only by default, with no questions and no titles, and `--write` puts them into the reader's own docs. A public question set for the corpus, in both languages.
- [ ] **Embedders.** The built-in `onnx` embedder generalised with presets (the multilingual e5-small as the default, a German-focused model such as Jina v2 base de) and a `device` setting (`auto`, `cpu`, `coreml`). An out-of-process `command` embedder (one long-lived process, JSON Lines) and a bundled OpenAI-compatible one, which covers Ollama, vLLM, OpenAI and Voyage. Relevance thresholds are recalibrated with the harness on the public corpus, not carried over from earlier measurements.
- [ ] **Trilium connector.** `trilium.py`, the sync logic, the area and label handling and the HTML-to-sections code leave the engine; they can be recovered from the tag above. The wiki-aware ranking is expressed through the item fields: `weight` for the wiki, source and journal areas, `path` for the page trail, `labels` for type, topics and status, `links` for related notes. One design question is open: trilium-recall shows a note's summary in place of its source note when the summary matches almost as well, and fields alone cannot express that. The parity target is ranking quality at least as good as trilium-recall on the same notes (its private evaluation: hit@3 0.86, silence 0.92), shown with fake-ETAPI fixtures and an opt-in live test against a throwaway Trilium.
- [ ] **Confluence connector,** written from the public REST documentation. A decision is needed first: Cloud, Data Center or both, because authentication and API paths differ.
- [ ] **Hook, plugin, sidecar image, quickstart.** The `/recall` endpoint with its skip rules and per-session memory exists. Still to move over from trilium-recall: the `UserPromptSubmit` hook script and its self-test, the setup skill, the sidecar Docker image (multi-stage build, the model baked in and verified by checksum, a health check, memory settings), and a minimal local quickstart (a generated password in the config directory and a documented launchd example).
- [ ] **trilium-recall adopts passageway.** After parity, trilium-recall becomes a thin distribution (a `passageway.toml` with the Trilium connector, its plugin, docs that point here) or is archived with a pointer. It is a breaking change for its users: `RECALL_*` becomes `PASSAGEWAY_*`, the tool's `instance` argument becomes `source`, and configuration moves to `passageway.toml`. It needs a migration guide.

## To decide before the protocol is frozen at v1

- [ ] [JSON Lines over a subprocess, or gRPC or another transport](https://github.com/Marceltov/passageway/issues/13), for connectors and for embedders, recorded in an ADR.
- [ ] [A connector SDK](https://github.com/Marceltov/passageway/issues/12), so that a connector is just its logic.

## Not goals

Generation (passageway returns passages only), a reranker, stdio MCP, per-connector access control, charts in evaluation reports, and a service installer in v1.
