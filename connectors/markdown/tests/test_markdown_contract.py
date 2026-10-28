import json
import os
import re
import subprocess
import sys
from pathlib import Path

import jsonschema

from passageway.protocol import Connector
from passageway.testing.contract import check_connector

README = Path(__file__).resolve().parents[1] / "README.md"
SCHEMA = Path(__file__).resolve().parents[3] / "docs" / "reference" / "connector-protocol.schema.json"


def notes(root):
    (root / "guides").mkdir()
    (root / "a.md").write_text("---\ntitle: Alpha\n---\n# Alpha\nAbout lighthouses.\n\n## Care\nPaint them. See [b](guides/b.md).")
    (root / "guides" / "b.md").write_text("# Beta\nAbout harbours.")


def command():
    return [sys.executable, "-m", "passageway_connector_markdown"]


def test_the_connector_passes_the_shared_contract_as_a_real_subprocess(tmp_path):
    notes(tmp_path)
    connector = Connector("markdown", command(), env={"FOLDER": str(tmp_path)})
    check_connector(connector)
    items = {i.id: i for i in connector.fetch(["a.md", "guides/b.md"])}
    assert items["a.md"].links == ("guides/b.md",) and items["a.md"].title == "Alpha"


def test_non_ascii_survives_a_subprocess_whose_stdout_is_ascii(tmp_path):
    (tmp_path / "a.md").write_text("# Köln Süd\n\nGröße und Maße.", encoding="utf-8")
    connector = Connector("markdown", command(), env={"FOLDER": str(tmp_path), "PYTHONIOENCODING": "ascii"})
    item = connector.fetch(["a.md"])[0]
    assert item.title == "Köln Süd" and item.sections[0].text == "Größe und Maße."


def test_the_output_validates_against_the_published_json_schema(tmp_path):
    notes(tmp_path)
    schema = json.loads(SCHEMA.read_text())

    def valid(name, record):
        return jsonschema.Draft202012Validator({"$ref": f"#/$defs/{name}", "$defs": schema["$defs"]}).is_valid(record)

    def lines(mode, stdin=""):
        out = subprocess.run(command() + [mode], env={**os.environ, "FOLDER": str(tmp_path)}, input=stdin,
                             capture_output=True, text=True, check=True).stdout
        return [json.loads(line) for line in out.splitlines()]

    assert lines("check") and all(valid("check", r) for r in lines("check"))
    assert lines("list") and all(valid("listRecord", r) for r in lines("list"))
    items = lines("fetch", '{"id": "a.md"}\n{"id": "guides/b.md"}\n')
    assert len(items) == 2 and all(valid("item", r) for r in items)


def test_every_setting_is_in_the_readme():
    code = (Path(__file__).resolve().parents[1] / "passageway_connector_markdown" / "connector.py").read_text()
    names = sorted(set(re.findall(r'(?:env\.get|_list|_int)\(\s*(?:env,\s*)?"([A-Z_]+)"', code)))
    assert len(names) >= 4, names  # the pattern must actually find the settings
    readme = README.read_text()
    for name in names:
        assert f"`{name}`" in readme, f"{name} is read by the markdown connector but missing from its README"
