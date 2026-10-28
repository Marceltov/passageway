import sys

from passageway.protocol import Connector
from passageway.testing.contract import check_connector


def test_the_connector_passes_the_shared_contract_as_a_real_subprocess(wiki_server):
    url, wiki = wiki_server
    wiki.add(1, "Heligoland", "Island text.\n\n== History ==\nOld.", revid=11)
    wiki.add(2, "Cape Arkona", "Cape text.", revid=22)
    wiki.categories["Category:Lighthouses"] = {"pages": [1, 2], "subcats": []}
    connector = Connector("wikipedia", [sys.executable, "-m", "passageway_connector_wikipedia"],
                          env={"API_URL": url, "PAGE_URL": "http://wiki.example/wiki/", "CATEGORIES": "Lighthouses",
                               "PAUSE_SECONDS": "0"})
    check_connector(connector)
    assert {i.title for i in connector.fetch(["1", "2"])} == {"Heligoland", "Cape Arkona"}


def test_non_ascii_titles_and_text_survive_a_subprocess_whose_stdout_is_ascii(wiki_server):
    url, wiki = wiki_server
    wiki.add(5, "Köln Süd", "Größe und Maße.\n\n== Geschichte ==\nAlt.", revid=5)
    wiki.categories["Category:Orte"] = {"pages": [5], "subcats": []}
    connector = Connector("wikipedia", [sys.executable, "-m", "passageway_connector_wikipedia"],
                          env={"API_URL": url, "PAGE_URL": "http://wiki.example/wiki/", "CATEGORIES": "Orte",
                               "PAUSE_SECONDS": "0", "PYTHONIOENCODING": "ascii"})  # a locale without UTF-8
    item = connector.fetch(["5"])[0]
    assert item.title == "Köln Süd" and item.sections[0].text == "Größe und Maße."


def test_the_output_validates_against_the_published_json_schema(wiki_server):
    import json
    import subprocess
    from pathlib import Path

    import jsonschema

    schema = json.loads((Path(__file__).resolve().parents[3] / "docs/reference/connector-protocol.schema.json").read_text())

    def valid(name, record):
        return jsonschema.Draft202012Validator({"$ref": f"#/$defs/{name}", "$defs": schema["$defs"]}).is_valid(record)

    url, wiki = wiki_server
    wiki.add(1, "Heligoland", "Island text.\n\n== History ==\nOld.", revid=11)
    wiki.categories["Category:Lighthouses"] = {"pages": [1], "subcats": []}
    import os
    env = {**os.environ, "API_URL": url, "PAGE_URL": "http://wiki.example/wiki/", "CATEGORIES": "Lighthouses",
           "PAUSE_SECONDS": "0"}

    def lines(mode, stdin=""):
        out = subprocess.run([sys.executable, "-m", "passageway_connector_wikipedia", mode], env=env, input=stdin,
                             capture_output=True, text=True, check=True).stdout
        return [json.loads(line) for line in out.splitlines()]

    assert all(valid("check", r) for r in lines("check")) and lines("check")
    assert all(valid("listRecord", r) for r in lines("list")) and lines("list")
    items = lines("fetch", '{"id": "1"}\n')
    assert items and all(valid("item", r) for r in items)
