import functools
import http.server
import json
import os
import re
import subprocess
import sys
import threading
from pathlib import Path

import jsonschema
import pytest

from passageway.protocol import Connector
from passageway.testing.contract import check_connector

README = Path(__file__).resolve().parents[1] / "README.md"
SCHEMA = Path(__file__).resolve().parents[3] / "docs" / "reference" / "connector-protocol.schema.json"
PAGE = "<html><head><title>{t}</title></head><body><nav>Menu</nav><main><h1>{t}</h1><p>Text of {t}.</p></main></body></html>"


class Site(str):
    def __new__(cls, url, root):
        site = super().__new__(cls, url)
        site.root = root
        return site


@pytest.fixture
def site(tmp_path):
    """A real web server on localhost with a sitemap and two pages, so the connector runs as a real subprocess."""
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(tmp_path))
    handler.log_message = lambda *args: None
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{server.server_port}"
    (tmp_path / "a.html").write_text(PAGE.format(t="Alpha"))
    (tmp_path / "b.html").write_text(PAGE.format(t="Beta"))
    (tmp_path / "sitemap.xml").write_text(f"<urlset><url><loc>{url}/a.html</loc></url><url><loc>{url}/b.html</loc></url></urlset>")
    yield Site(url, tmp_path)
    server.shutdown()


def command():
    return [sys.executable, "-m", "passageway_connector_sitemap"]


def env(site, **more):
    return {"SITEMAP": f"{site}/sitemap.xml", "PAUSE": "0", **more}


def test_the_connector_passes_the_shared_contract_as_a_real_subprocess(site):
    connector = Connector("sitemap", command(), env=env(site))
    check_connector(connector)
    assert {i.title for i in connector.fetch([f"{site}/a.html", f"{site}/b.html"])} == {"Alpha", "Beta"}


def test_the_output_validates_against_the_published_json_schema(site):
    schema = json.loads(SCHEMA.read_text())

    def valid(name, record):
        return jsonschema.Draft202012Validator({"$ref": f"#/$defs/{name}", "$defs": schema["$defs"]}).is_valid(record)

    def lines(mode, stdin=""):
        out = subprocess.run(command() + [mode], env={**os.environ, **env(site)}, input=stdin,
                             capture_output=True, text=True, check=True).stdout
        return [json.loads(line) for line in out.splitlines()]

    assert lines("check") and all(valid("check", r) for r in lines("check"))
    assert lines("list") and all(valid("listRecord", r) for r in lines("list"))
    items = lines("fetch", f'{{"id": "{site}/a.html"}}\n')
    assert len(items) == 1 and valid("item", items[0])


def test_every_setting_is_in_the_readme():
    code = (Path(__file__).resolve().parents[1] / "passageway_connector_sitemap" / "connector.py").read_text()
    names = sorted(set(re.findall(r'(?:env\.get|names|whole|flag|seconds)\(\s*(?:env,\s*)?"([A-Z_]+)"', code)))
    assert len(names) >= 8, names  # the pattern must actually find the settings
    readme = README.read_text()
    for name in names:
        assert f"`{name}`" in readme, f"{name} is read by the sitemap connector but missing from its README"


def test_the_example_in_the_readme_is_what_the_connector_really_produces(site):
    readme = README.read_text()
    page = re.search(r"```html\n(.*?)```", readme, re.S).group(1)
    shown = json.loads(re.search(r"```json\n(.*?)```", readme, re.S).group(1))
    (site.root / "guide").mkdir()
    (site.root / "guide" / "setup.html").write_text(page)
    out = subprocess.run(command() + ["fetch"], env={**os.environ, **env(site)},
                         input=f'{{"id": "{site}/guide/setup.html"}}\n', capture_output=True, text=True, check=True).stdout
    real = json.loads(out)
    for key, value in shown.items():
        assert real[key] == value, f"the README shows {key} = {value!r} but the connector prints {real[key]!r}"
