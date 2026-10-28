# passageway

Retrieval for Claude over MCP: connectors (out-of-process programs speaking JSON Lines) feed passages to a core that indexes and ranks them. Documentation: https://passageway.marceltov.de/ (the pages are in `docs/`).

## Commands

```bash
uv sync                                   # the core and every connector package
uv run pytest -q                          # the whole suite, offline
uvx --with mkdocs-material==9.7.7 --with mkdocs-llmstxt==0.5.1 --with 'mkdocs<2' mkdocs build --strict   # the docs, as CI builds them
PASSAGEWAY_LIVE=1 uv run pytest connectors/wikipedia/tests/test_wikipedia_live.py   # opt-in, hits Wikipedia
```

## Working in this repository

- Every change starts from an issue. Branches, commits and pull request titles carry `PASSAGEWAY #<issue>:` (the `/ccp:ship-pr` flow). Dependabot's carry `Dependencies:` instead.
- Tests first: write the failing test, watch it fail, then the code. `tests/test_docs.py` keeps the docs in step with the code.
- CI is the gate, and I decide when a branch is finished and when it is merged. A `/ccp:ship-pr` request is the go-ahead for push and PR only, not for the merge. Merge only when I say "merge". The one exception: Dependabot's patch and minor bumps merge by themselves once CI is green (`.github/workflows/dependabot-automerge.yml`); its majors wait for me like any other PR.
- Never print or write a secret into a file, a log or a commit. Credentials live in 1Password; GitHub secrets are set by piping from there.

## Releases

A `vX.Y.Z` tag is a release and must equal the version in `pyproject.toml`. The Release workflow creates the GitHub release and posts its notes to the notefeed feed; see `docs/development.md`.
