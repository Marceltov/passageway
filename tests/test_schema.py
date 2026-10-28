"""The published JSON Schema and the hand-written validator in passageway/protocol.py agree on records (not on rules
that need the whole output, such as duplicate ids)."""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import jsonschema
import pytest

from passageway.protocol import parse_item

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_FILE = ROOT / "docs" / "reference" / "connector-protocol.schema.json"
SCHEMA = json.loads(SCHEMA_FILE.read_text())

GOOD = {"id": "a", "title": "T", "url": "http://x", "version": "1", "sections": []}


def _validator(name: str):
    jsonschema.Draft202012Validator.check_schema(SCHEMA)
    return jsonschema.Draft202012Validator({"$ref": f"#/$defs/{name}", "$defs": SCHEMA["$defs"]})


def _schema_accepts(name: str, record) -> bool:
    return _validator(name).is_valid(record)


def test_the_schema_is_a_valid_draft_2020_12_schema_with_every_message():
    jsonschema.Draft202012Validator.check_schema(SCHEMA)
    assert {"item", "check", "listRecord", "fetchRequest"} <= set(SCHEMA["$defs"])


ITEMS = [
    (GOOD, True),
    ({**GOOD, "sections": [{"heading": "H", "text": "x"}, {"text": "no heading"}]}, True),
    ({**GOOD, "weight": 0, "path": ["A"], "links": ["b"], "labels": ["l"], "updated": "2026-10-28T09:00:00Z"}, True),
    ({**GOOD, "weight": 2}, True),
    ({k: v for k, v in GOOD.items() if k != "id"}, False),
    ({**GOOD, "id": ""}, False),
    ({k: v for k, v in GOOD.items() if k != "sections"}, False),
    ({**GOOD, "sections": [{"heading": "H"}]}, False),
    ({**GOOD, "sections": [{"heading": 3, "text": "x"}]}, False),
    ({**GOOD, "weight": 3}, False),
    ({**GOOD, "weight": -1}, False),
    ({**GOOD, "weight": True}, False),
    ({**GOOD, "path": "A"}, False),
    ({**GOOD, "links": [""]}, False),
    ({**GOOD, "labels": [1]}, False),
    ({**GOOD, "updated": 5}, False),
    ({**GOOD, "version": 1}, False),
]


@pytest.mark.parametrize("record,valid", ITEMS)
def test_the_schema_and_parse_item_give_the_same_verdict(record, valid):
    assert _schema_accepts("item", record) is valid
    try:
        parse_item(record)
        parsed = True
    except ValueError:
        parsed = False
    assert parsed is valid


def test_unknown_fields_are_allowed_so_the_protocol_can_grow():
    assert _schema_accepts("item", {**GOOD, "something_new": 1})
    parse_item({**GOOD, "something_new": 1})


def test_the_other_messages():
    assert _schema_accepts("check", {"ok": True, "count": 3})
    assert _schema_accepts("check", {"ok": True, "count": 3, "protocol": "1"})
    assert not _schema_accepts("check", {"ok": True, "count": 3, "protocol": "2"})
    assert not _schema_accepts("check", {"ok": True, "count": True})
    assert not _schema_accepts("check", {"ok": True, "count": -1})
    assert not _schema_accepts("check", {"ok": False, "count": 3})
    assert not _schema_accepts("check", {"ok": True})
    assert _schema_accepts("listRecord", {"id": "a", "version": "1"})
    assert not _schema_accepts("listRecord", {"id": "a"})
    assert _schema_accepts("fetchRequest", {"id": "a"})
    assert not _schema_accepts("fetchRequest", {"id": ""})


def test_the_fake_connector_prints_what_the_schema_describes(tmp_path):
    items = tmp_path / "items.json"
    items.write_text(json.dumps([{**GOOD, "id": "a", "updated": "2026-01-01T00:00:00Z"}, {**GOOD, "id": "b"}]))
    env = {**os.environ, "FAKE_ITEMS": str(items)}

    def run(mode, *args, stdin=""):
        out = subprocess.run([sys.executable, "-m", "passageway.testing.fake_connector", mode, *args], env=env,
                             input=stdin, capture_output=True, text=True, check=True, cwd=ROOT).stdout
        return [json.loads(line) for line in out.splitlines()]

    assert all(_schema_accepts("check", r) for r in run("check"))
    assert all(_schema_accepts("listRecord", r) for r in run("list"))
    assert all(_schema_accepts("item", r) for r in run("fetch", stdin='{"id": "a"}\n{"id": "b"}\n'))
    assert all(_schema_accepts("item", r) for r in run("changed", "--since", "2000-01-01T00:00:00Z"))


def test_the_example_record_in_the_protocol_reference_validates():
    page = (ROOT / "docs" / "reference" / "connector-protocol.md").read_text()
    example = json.loads(re.search(r"```json\n(.*?)```", page, re.S).group(1))
    assert _schema_accepts("item", example)


def test_the_reference_links_to_the_schema():
    page = (ROOT / "docs" / "reference" / "connector-protocol.md").read_text()
    assert "connector-protocol.schema.json" in page
