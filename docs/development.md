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
- `corpus/` holds the frozen sample corpus and `corpus/snapshot.py`, the script that writes it; its tests run offline against the Wikipedia connector's fake MediaWiki and check the committed files ([Sample corpus](reference/corpus.md)).
- Opt-in live tests hit real services: `PASSAGEWAY_LIVE=1 uv run pytest connectors/wikipedia/tests/test_wikipedia_live.py`.
- `tests/test_docs.py` keeps these docs honest: it fails when a setting is added to the code without being documented, and it runs the example connector from the guide.

## Docs

```bash
uvx --with mkdocs-material==9.7.7 --with mkdocs-llmstxt==0.5.1 --with 'mkdocs<2' mkdocs serve           # live preview
uvx --with mkdocs-material==9.7.7 --with mkdocs-llmstxt==0.5.1 --with 'mkdocs<2' mkdocs build --strict   # what CI runs
```

The Roadmap page is rendered from `docs/roadmap.yml` by a small MkDocs hook (`docs_hooks/roadmap.py`), so adding or finishing a step is one entry in that file; `mkdocs serve` rebuilds the page when the file changes. Its icons are Material Design icons, named in the file.

The header bar has two extra links for AI agents (`SKILL.md` and `llms-full.txt`). Material has no setting for that, so `overrides/partials/header.html` is a copy of Material's own header template with one block added. When you change the pinned Material version, copy the new `header.html` from the package and re-add the block; a test fails if the version in the copy and the pinned one differ.

## Changes

Every change starts from an issue and goes through a pull request; the CI build must pass, including the strict docs build. Decisions that future contributors will ask about get an ADR in `docs/adr/`.

Dependabot keeps the dependencies and the GitHub Actions current (`.github/dependabot.yml`): security updates arrive at once; everything else waits two weeks after a release and comes grouped on Monday mornings, with the `Dependencies:` prefix instead of an issue number. Patch and minor bumps merge by themselves once the required checks are green; majors wait for review. A scheduled audit (`.github/workflows/audit.yml`) checks the locked runtime dependencies for known vulnerabilities every day.

## Releasing

A release is a tag. Bump `version` in the root `pyproject.toml`, merge it, then tag the commit:

```bash
git tag -a v0.2.0 -m "A one-line headline for the release"
git push origin v0.2.0
```

The `Release` workflow checks that the tag equals the version in `pyproject.toml`, runs the tests, and creates the GitHub release. Its notes are the tag message, the pull requests merged since the previous release, and install instructions. It then posts the same notes to a notefeed feed, once per tag, so running the workflow again never posts twice. The feed is configured with two repository secrets, `NOTEFEED_FEED` and `NOTEFEED_FEED_PASSWORD`; without them (a fork) nothing is posted.

To publish an existing tag again, run the workflow by hand from the Actions tab and give it the tag. This rewrites the release notes, so edits made by hand on GitHub are lost. The check compares the tag only with the root `pyproject.toml`; connector packages keep their own versions.
