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
