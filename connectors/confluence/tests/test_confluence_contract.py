import json
import os
import subprocess
import sys
from pathlib import Path

import jsonschema

from passageway.protocol import Connector
from passageway.testing.contract import check_connector

SCHEMA = Path(__file__).resolve().parents[3] / "docs" / "reference" / "connector-protocol.schema.json"


def test_the_connector_passes_the_shared_contract_as_a_real_subprocess(world):
    connector = Connector("confluence", [sys.executable, "-m", "passageway_connector_confluence"],
                          env={"URL": world.url, "SPACES": "OPS|HR", "PAUSE_SECONDS": "0"}, secrets={"TOKEN": world.api.token})
    check_connector(connector)
    assert {i.title for i in connector.fetch(["101", "200"])} == {"Rotating certificates", "Cafeteria menu"}


def test_the_output_validates_against_the_published_json_schema(world):
    schema = json.loads(SCHEMA.read_text())

    def valid(name, record):
        return jsonschema.Draft202012Validator({"$ref": f"#/$defs/{name}", "$defs": schema["$defs"]}).is_valid(record)

    def lines(mode, stdin=""):
        out = subprocess.run([sys.executable, "-m", "passageway_connector_confluence", mode],
                             env={**os.environ, "URL": world.url, "SPACES": "OPS|HR", "TOKEN": world.api.token, "PAUSE_SECONDS": "0"},
                             input=stdin, capture_output=True, text=True, check=True).stdout
        return [json.loads(line) for line in out.splitlines()]

    assert all(valid("check", r) for r in lines("check"))
    listed = lines("list")
    assert listed and all(valid("listRecord", r) for r in listed)
    items = lines("fetch", "".join(json.dumps({"id": r["id"]}) + "\n" for r in listed))
    assert len(items) == len(listed) and all(valid("item", r) for r in items)
