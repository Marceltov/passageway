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

Dependabot opens one pull request a week that bumps the GitHub Actions the workflows use (`.github/dependabot.yml`). Those pull requests carry a `deps` prefix instead of an issue number.

## Releasing

A release is a tag. Bump `version` in the root `pyproject.toml`, merge it, then tag the commit:

```bash
git tag -a v0.2.0 -m "A one-line headline for the release"
git push origin v0.2.0
```

The `Release` workflow checks that the tag equals the version in `pyproject.toml`, runs the tests, and creates the GitHub release. Its notes are the tag message, the pull requests merged since the previous release, and install instructions. It then posts the same notes to a notefeed feed, once per tag, so running the workflow again never posts twice. The feed is configured with two repository secrets, `NOTEFEED_FEED` and `NOTEFEED_FEED_PASSWORD`; without them (a fork) nothing is posted.

To publish an existing tag again, run the workflow by hand from the Actions tab and give it the tag. This rewrites the release notes, so edits made by hand on GitHub are lost. The check compares the tag only with the root `pyproject.toml`; connector packages keep their own versions.
