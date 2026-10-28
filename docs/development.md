# Development

```bash
git clone https://github.com/Marceltov/passageway
cd passageway
uv sync                # installs the core and every connector package
uv run pytest -q       # the whole suite, offline
```

## Layout

The repository is a uv workspace: the core package `passageway` at the root and one self-contained package per connector under `connectors/`, each with its own `pyproject.toml`, tests and README. See [ADR 0002](adr/0002-connectors-as-workspace-packages.md).

## Tests

- `uv run pytest -q` runs everything offline. Connector tests run the connector as a real subprocess against an in-test server and through `passageway.testing.contract.check_connector`.
- Opt-in live tests hit real services: `PASSAGEWAY_LIVE=1 uv run pytest connectors/wikipedia/tests/test_wikipedia_live.py`.
- `tests/test_docs.py` keeps these docs honest: it fails when a setting is added to the code without being documented, and it runs the example connector from the guide.

## Docs

```bash
uvx --with mkdocs-material==9.7.7 --with 'mkdocs<2' mkdocs serve           # live preview
uvx --with mkdocs-material==9.7.7 --with 'mkdocs<2' mkdocs build --strict   # what CI runs
```

## Changes

Every change starts from an issue and goes through a pull request; the CI build must pass, including the strict docs build. Decisions that future contributors will ask about get an ADR in `docs/adr/`.
