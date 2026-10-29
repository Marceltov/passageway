import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_every_environment_variable_the_server_reads_is_documented():
    config = (ROOT / "passageway" / "config.py").read_text()
    server = (ROOT / "passageway" / "server.py").read_text()
    documented = (ROOT / "docs" / "configuration.md").read_text()
    names = set(re.findall(r"PASSAGEWAY_[A-Z_]+", config)) | set(re.findall(r'environ\.get\(\s*"([A-Z][A-Z_]+)"', server))
    assert len(names) >= 10  # the patterns must actually find the variables
    for name in sorted(names):
        assert name in documented, f"{name} is read by the server but missing from docs/configuration.md"


def test_every_wikipedia_setting_is_in_its_readme():
    code = (ROOT / "connectors/wikipedia/passageway_connector_wikipedia/connector.py").read_text()
    readme = (ROOT / "connectors/wikipedia/README.md").read_text()
    names = sorted(set(re.findall(r'(?:env\.get|_list|_int)\(\s*(?:env,\s*)?"([A-Z_]+)"', code)))
    assert len(names) >= 9  # the pattern must actually find the settings
    for name in names:
        assert f"`{name}`" in readme, f"{name} is read by the Wikipedia connector but missing from its README"


def test_every_nav_page_exists():
    nav = (ROOT / "mkdocs.yml").read_text()
    pages = re.findall(r"^\s+- (?:[^:\n]+: )?([\w/.-]+\.md)$", nav, re.M)
    assert len(pages) >= 10
    for page in pages:
        assert (ROOT / "docs" / page).is_file(), f"mkdocs.yml lists {page}, which does not exist"


def _guide_script(tmp_path):
    guide = (ROOT / "docs" / "guides" / "write-a-connector.md").read_text()
    blocks = re.findall(r"```python\n(.*?)```", guide, re.S)
    assert blocks, "the guide must contain the example connector as a python block"
    script = tmp_path / "folder_connector.py"
    script.write_text(blocks[0])
    return script


def test_the_guide_example_works_with_a_relative_folder_as_the_guide_runs_it(tmp_path):
    import os
    import subprocess
    import sys

    script = _guide_script(tmp_path)
    (tmp_path / "notes").mkdir()
    (tmp_path / "notes" / "a.txt").write_text("Lighthouses guide ships.")
    done = subprocess.run([sys.executable, str(script), "fetch"], input='{"id": "a.txt"}\n', text=True,
                          capture_output=True, cwd=tmp_path, env={**os.environ, "FOLDER": "notes"})
    assert done.returncode == 0, done.stderr
    assert "a.txt" in done.stdout


def test_the_example_connector_in_the_guide_passes_the_contract(tmp_path):
    import sys

    from passageway.protocol import Connector
    from passageway.testing.contract import check_connector

    script = _guide_script(tmp_path)
    notes = tmp_path / "notes"
    (notes / "sub").mkdir(parents=True)
    (notes / "a.txt").write_text("Alpha note about lighthouses.")
    (notes / "sub" / "b.txt").write_text("Beta note about harbours.")
    connector = Connector("folder", [sys.executable, str(script)], env={"FOLDER": str(notes)})
    check_connector(connector)
    assert {i.title for i in connector.fetch(["a.txt", "sub/b.txt"])} == {"a", "b"}


def test_every_entry_point_in_the_agents_table_is_a_link():
    guide = (ROOT / "docs" / "guides" / "agents.md").read_text()
    table = guide.split("| Entry point |", 1)[1].split("\n\n", 1)[0]
    rows = [line for line in table.splitlines()[2:] if line.startswith("|")]  # skip the header's separator row
    assert len(rows) >= 3, "the table must list the entry points"
    for row in rows:
        first_cell = row.split("|")[1]
        assert re.search(r"\]\(https://passageway\.marceltov\.de/\S+\)", first_cell), f"no link in: {first_cell.strip()}"


def test_the_roadmap_is_a_page_of_the_site_with_its_data_beside_it():
    assert (ROOT / "docs" / "roadmap.yml").is_file() and (ROOT / "docs" / "roadmap.md").is_file()


def test_no_public_file_names_the_work_project():
    """The employer's internal project must never appear in the repository (code, docs, skills, workflows, issues' source)."""
    needle = "cq" + "se"  # spelled in two parts so that this file does not match itself
    public = [*ROOT.glob("docs/**/*.md"), *ROOT.glob("docs/**/*.yml"), *ROOT.glob("docs/**/*.json"), *ROOT.glob("tests/**/*.py"), *ROOT.glob("docs_hooks/*.py"), *ROOT.glob("skills/**/*.md"), *ROOT.glob("connectors/**/*.md"),
              *ROOT.glob("connectors/**/*.py"), *ROOT.glob("passageway/**/*.py"), *ROOT.glob("sdk/**/*.py"), *ROOT.glob("sdk/**/*.md"), *ROOT.glob("embedders/**/*.py"), *ROOT.glob("embedders/**/*.md"), *ROOT.glob("corpus/*.md"), *ROOT.glob("corpus/*.py"), *ROOT.glob("corpus/*.toml"), *ROOT.glob("corpus/*.sh"), *ROOT.glob("corpus/tests/*.py"), *ROOT.glob("scripts/*"),
              *ROOT.glob(".github/**/*.yml"), ROOT / "README.md", ROOT / "CLAUDE.md", ROOT / "pyproject.toml", ROOT / "mkdocs.yml"]
    offenders = [str(p.relative_to(ROOT)) for p in public
                 if p.is_file() and "superpowers" not in p.parts and needle in p.read_text(errors="ignore").lower()]
    assert not offenders, f"the work project is named in: {offenders}"


def test_the_sdk_example_in_the_guide_is_short_and_passes_the_contract(tmp_path):
    import sys

    from passageway.protocol import Connector
    from passageway.testing.contract import check_connector

    guide = (ROOT / "docs" / "guides" / "write-a-connector.md").read_text()
    blocks = re.findall(r"```python\n(.*?)```", guide, re.S)
    sdk_block = next(b for b in blocks if "passageway_sdk" in b)
    assert len([line for line in sdk_block.splitlines() if line.strip()]) <= 32  # "a folder connector in about 30 lines"
    script = tmp_path / "folder_sdk.py"
    script.write_text(sdk_block)
    notes = tmp_path / "notes"
    (notes / "sub").mkdir(parents=True)
    (notes / "a.txt").write_text("Alpha note about lighthouses.")
    (notes / "sub" / "b.txt").write_text("Beta note about harbours.")
    connector = Connector("folder", [sys.executable, str(script)], env={"FOLDER": str(notes)})
    check_connector(connector)
    assert {i.title for i in connector.fetch(["a.txt", "sub/b.txt"])} == {"a", "b"}


def test_the_sdk_is_versioned_with_the_core_and_documented():
    import tomllib
    core = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]
    sdk = tomllib.loads((ROOT / "sdk" / "pyproject.toml").read_text())["project"]["version"]
    assert sdk == core, "the SDK ships with the protocol: bump both together"
    assert "sdk.md" in (ROOT / "mkdocs.yml").read_text()


def test_the_guide_tells_how_to_run_and_register_an_sdk_connector():
    guide = (ROOT / "docs" / "guides" / "write-a-connector.md").read_text()
    assert "uv add git+" not in guide  # fails for a lone script: there is no pyproject.toml
    assert "uv run --with 'passageway-sdk @ git+" in guide  # trying it by hand
    assert "$(uv tool dir)/passageway/bin/python" in guide  # registering it: the interpreter that has the SDK


def test_the_corpus_licence_is_stated_where_the_code_licence_is():
    assert "CC BY-SA 4.0" in (ROOT / "README.md").read_text()
    assert "CC BY-SA 4.0" in (ROOT / "mkdocs.yml").read_text()
    import tomllib
    build = tomllib.loads((ROOT / "pyproject.toml").read_text())["tool"]["hatch"]["build"]["targets"]
    assert "corpus" in build["sdist"]["exclude"]  # the AGPL package does not carry the CC BY-SA text


def test_the_cases_example_in_the_evaluation_guide_is_a_valid_cases_file(tmp_path):
    from passageway.eval.cases import load_cases
    guide = (ROOT / "docs" / "guides" / "evaluate.md").read_text()
    blocks = re.findall(r"```toml\n(.*?)```", guide, re.S)
    example = next(b for b in blocks if "[[case]]" in b)
    path = tmp_path / "cases.toml"
    path.write_text(example)
    cases, targets = load_cases(path)
    assert len(cases) >= 3 and targets, "the guide's example shows questions, one that must stay silent, and targets"
    assert any(not c.answerable for c in cases) and any(c.answerable for c in cases)


def test_the_evaluation_guide_states_what_a_reader_could_get_wrong():
    guide = (ROOT / "docs" / "guides" / "evaluate.md").read_text()
    for needle in ("three or more words", "group labels", "live data folder", "on a line of its own", "95% interval",
                   "version", "has no `[targets]`"):
        assert needle in guide, f"the evaluation guide should say: {needle}"


def test_the_embedder_example_in_the_protocol_reference_passes_the_contract(tmp_path):
    import sys

    from passageway.embed_command import CommandEmbedder
    from passageway.testing.embedder_contract import check_embedder

    page = (ROOT / "docs" / "reference" / "embedder-protocol.md").read_text()
    script = next(b for b in re.findall(r"```python\n(.*?)```", page, re.S) if "def embed(" in b)
    assert len([line for line in script.splitlines() if line.strip()]) <= 30
    path = tmp_path / "my_embedder.py"
    path.write_text(script)
    embedder = CommandEmbedder("example", [sys.executable, str(path)])
    try:
        check_embedder(embedder)
        assert (embedder.name, embedder.dim) == ("toy-hash-64", 64)
    finally:
        embedder.close()


def test_the_configuration_page_documents_every_key_of_an_embedder():
    from passageway.config import _COMMAND_KEYS, _ONNX_KEYS
    page = (ROOT / "docs" / "configuration.md").read_text()
    for key in sorted(_COMMAND_KEYS | _ONNX_KEYS):
        assert f"`{key}`" in page, f"the embedder key {key} is not documented in docs/configuration.md"
    assert "[embedders." in page and "embedder-protocol.md" in page


def test_the_guide_names_every_option_of_the_compare_command():
    from passageway.eval.compare import _parser as compare_parser
    guide = (ROOT / "docs" / "guides" / "evaluate.md").read_text()
    section = guide.split("## Compare embedding models")[1].split("\n## ")[0]
    options = [o for a in compare_parser()._actions for o in a.option_strings if o.startswith("--") and o != "--help"]
    assert len(options) >= 6
    for option in options:
        assert f"`{option}" in section, f"{option} is an option of passageway eval compare but the guide does not mention it"


def test_the_guide_names_every_option_of_the_command():
    from passageway.eval.cli import _parser
    guide = (ROOT / "docs" / "guides" / "evaluate.md").read_text()
    options = [o for a in _parser()._actions for o in a.option_strings if o.startswith("--") and o != "--help"]
    assert len(options) >= 8
    for option in options:
        assert f"`{option}" in guide, f"{option} is an option of passageway eval but the guide does not mention it"


# ---- the values page (a standing rule: docs/values.md is the yardstick every change is judged against) ----------------

def test_the_values_page_has_numbered_points_in_three_groups_each_with_what_it_rules_out():
    page = (ROOT / "docs" / "values.md").read_text()
    assert page.startswith("# What passageway stands for")
    for group in ("## Lines never crossed", "## What you can rely on", "## Principles that follow", "## Changing this page"):
        assert group in page, f"the values page needs the section {group}"
    points = re.findall(r"^### V(\d+)\. (.+)$", page, re.M)
    numbers = [int(n) for n, _ in points]
    assert numbers == list(range(1, len(numbers) + 1)) and len(numbers) >= 8, "points are numbered V1, V2, … across the groups"
    sections = re.split(r"^### V\d+\. .+$", page, flags=re.M)[1:]
    for (number, title), body in zip(points, sections):
        assert "**Rules out:**" in body, f"V{number} {title!r} has no Rules out line"
        assert "**ADRs:**" in body, f"V{number} {title!r} has no ADRs line"
    adrs = {p.stem.split("-")[0] for p in (ROOT / "docs" / "adr").glob("*.md")}
    for cited in re.findall(r"\*\*ADRs:\*\* ([^\n]+)", page):
        for number in re.findall(r"\b(\d{4})\b", cited):
            assert number in adrs, f"the values page cites ADR {number}, which does not exist"


def test_the_values_page_is_right_after_home_in_the_nav_and_in_the_llms_file():
    config = (ROOT / "mkdocs.yml").read_text()
    nav = config.split("nav:")[1].split("theme:")[0]
    assert re.search(r"- Home: index\.md\n\s+- [^\n]*values\.md", nav), "values.md comes right after Home"
    assert re.search(r"Start: \[index\.md, values\.md", config)


def test_claude_md_says_changes_are_judged_against_the_values():
    text = (ROOT / "CLAUDE.md").read_text()
    assert "docs/values.md" in text and "names the point" in text


def test_every_open_roadmap_item_links_its_issue_and_the_value_it_serves():
    import yaml
    data = yaml.safe_load((ROOT / "docs" / "roadmap.yml").read_text())
    values = (ROOT / "docs" / "values.md").read_text()
    anchors = {f"v{n}-" + re.sub(r"[^a-z0-9 -]", "", title.lower()).replace(" ", "-")
               for n, title in re.findall(r"^### V(\d+)\. (.+)$", values, re.M)}
    for entry in data["items"]:
        if entry["status"] == "done":
            continue
        labels = [link["label"] for link in entry.get("links", [])]
        assert any(label.startswith("#") for label in labels), f"roadmap item {entry['id']} links no issue"
        value_links = [link for link in entry.get("links", []) if re.fullmatch(r"V\d+", link["label"])]
        assert value_links, f"roadmap item {entry['id']} names no value it serves"
        for link in value_links:
            anchor = link["url"].split("#")[-1]
            assert anchor in anchors, f"roadmap item {entry['id']} links {link['url']}, but no value heading gives that anchor"
