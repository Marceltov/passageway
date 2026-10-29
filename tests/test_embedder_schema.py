import json
import os
import re
import subprocess
import sys
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = json.loads((ROOT / "docs" / "reference" / "embedder-protocol.schema.json").read_text())


def valid(name, message) -> bool:
    return jsonschema.Draft202012Validator({"$ref": f"#/$defs/{name}", "$defs": SCHEMA["$defs"]}).is_valid(message)


def test_the_schema_is_a_valid_draft_2020_12_schema_with_every_message():
    jsonschema.Draft202012Validator.check_schema(SCHEMA)
    assert {"infoRequest", "infoReply", "embedRequest", "embedReply", "errorReply"} <= set(SCHEMA["$defs"])


def test_the_messages():
    assert valid("infoRequest", {"op": "info"}) and not valid("infoRequest", {"op": "embed"})
    assert valid("infoReply", {"name": "bge-m3", "dim": 1024}) and valid("infoReply", {"name": "m", "dim": 8, "protocol": "1"})
    assert not valid("infoReply", {"name": "", "dim": 8}) and not valid("infoReply", {"name": "m", "dim": 0})
    assert not valid("infoReply", {"name": "m", "dim": 8, "protocol": "2"}) and not valid("infoReply", {"name": "m"})
    assert valid("embedRequest", {"op": "embed", "kind": "query", "texts": ["a", "b"]})
    assert valid("embedRequest", {"op": "embed", "kind": "passage", "texts": []})
    assert not valid("embedRequest", {"op": "embed", "kind": "other", "texts": ["a"]})
    assert not valid("embedRequest", {"op": "embed", "kind": "query", "texts": [1]})
    assert valid("embedReply", {"vectors": [[0.1, 0.2], [0.3, 0.4]]}) and valid("embedReply", {"vectors": []})
    assert not valid("embedReply", {"vectors": [["a"]]}) and not valid("embedReply", {"vectors": [0.1]})
    assert valid("errorReply", {"error": "out of memory"}) and not valid("errorReply", {"error": 5})


def test_a_real_embedder_process_speaks_the_schema():
    proc = subprocess.Popen([sys.executable, "-m", "passageway.testing.fake_embedder"], stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, text=True, cwd=ROOT, env={**os.environ, "FAKE_EMBED_DIM": "8"})
    try:
        def ask(message, reply_type, request_type):
            assert valid(request_type, message)
            proc.stdin.write(json.dumps(message) + "\n")
            proc.stdin.flush()
            reply = json.loads(proc.stdout.readline())
            assert valid(reply_type, reply), reply
            return reply

        info = ask({"op": "info"}, "infoReply", "infoRequest")
        assert info["dim"] == 8
        out = ask({"op": "embed", "kind": "query", "texts": ["alpha", "beta"]}, "embedReply", "embedRequest")
        assert len(out["vectors"]) == 2 and len(out["vectors"][0]) == 8
    finally:
        proc.stdin.close()
        proc.wait(timeout=10)


def test_the_reference_page_exists_links_the_schema_and_its_examples_validate():
    page = (ROOT / "docs" / "reference" / "embedder-protocol.md").read_text()
    assert "embedder-protocol.schema.json" in page
    blocks = re.findall(r"```json\n(.*?)```", page, re.S)
    assert blocks
    examples = [json.loads(line) for block in blocks for line in block.splitlines() if line.strip().startswith("{")]
    assert len(examples) >= 4 and all(
        any(valid(name, example) for name in ("infoRequest", "infoReply", "embedRequest", "embedReply", "errorReply"))
        for example in examples)
