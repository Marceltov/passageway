import http.server
import json
import os
import re
import subprocess
import sys
import threading
from pathlib import Path

import httpx
import jsonschema
import pytest

from passageway.protocol import Connector
from passageway.testing.contract import check_connector

README = Path(__file__).resolve().parents[1] / "README.md"
SCHEMA = Path(__file__).resolve().parents[3] / "docs" / "reference" / "connector-protocol.schema.json"


@pytest.fixture
def api(github):
    """The fake GitHub API on a real localhost server, so the connector runs as a real subprocess."""

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            reply = github.handler(httpx.Request("GET", f"http://fake{self.path}", headers=dict(self.headers)))
            self.send_response(reply.status_code)
            for name, value in reply.headers.items():
                if name.lower() not in ("content-length", "transfer-encoding"):
                    self.send_header(name, value)
            self.send_header("Content-Length", str(len(reply.content)))
            self.end_headers()
            self.wfile.write(reply.content)

        def log_message(self, *args):
            pass

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()


def command():
    return [sys.executable, "-m", "passageway_connector_github"]


def env(api, **more):
    return {"REPOS": "acme/docs", "API_URL": api, **more}


def test_the_connector_passes_the_shared_contract_as_a_real_subprocess(api):
    connector = Connector("github", command(), env=env(api))
    check_connector(connector)
    items = {i.id: i for i in connector.fetch(["acme/docs/guide/setup.md"])}
    assert items["acme/docs/guide/setup.md"].title == "Setup"


def test_the_output_validates_against_the_published_json_schema(api):
    schema = json.loads(SCHEMA.read_text())

    def valid(name, record):
        return jsonschema.Draft202012Validator({"$ref": f"#/$defs/{name}", "$defs": schema["$defs"]}).is_valid(record)

    def lines(mode, stdin=""):
        out = subprocess.run(command() + [mode], env={**os.environ, **env(api, FILES="*.md|*.py")}, input=stdin,
                             capture_output=True, text=True, check=True).stdout
        return [json.loads(line) for line in out.splitlines()]

    assert lines("check") and all(valid("check", r) for r in lines("check"))
    assert lines("list") and all(valid("listRecord", r) for r in lines("list"))
    items = lines("fetch", '{"id": "acme/docs/guide/setup.md"}\n{"id": "acme/docs/src/app.py"}\n')
    assert len(items) == 2 and all(valid("item", i) for i in items)


def test_every_setting_is_in_the_readme():
    code = (Path(__file__).resolve().parents[1] / "passageway_connector_github" / "connector.py").read_text()
    names = sorted(set(re.findall(r'(?:env\.get|names|whole|flag|seconds|globs)\(\s*(?:env,\s*)?"([A-Z_]+)"', code)))
    assert len(names) >= 8, names  # the pattern must actually find the settings
    readme = README.read_text()
    for name in names:
        assert f"`{name}`" in readme, f"{name} is read by the github connector but missing from its README"


def test_the_example_in_the_readme_is_what_the_connector_really_produces(api, github):
    readme = README.read_text()
    github.repos["acme/docs"]["files"]["guide/setup.md"] = re.search(r"```markdown\n(.*?)```", readme, re.S).group(1)
    shown = json.loads(re.search(r"```json\n(.*?)```", readme, re.S).group(1))
    out = subprocess.run(command() + ["fetch"], env={**os.environ, **env(api)}, input='{"id": "acme/docs/guide/setup.md"}\n',
                         capture_output=True, text=True, check=True).stdout
    real = json.loads(out)
    for key, value in shown.items():
        assert real[key] == value, f"the README shows {key} = {value!r} but the connector prints {real[key]!r}"
