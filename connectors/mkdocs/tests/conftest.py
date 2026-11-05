import io
import json

import httpx
import pytest

from passageway_connector_mkdocs.connector import MkDocs

SITE = "https://docs.example"

# the shape Material for MkDocs writes: a page entry (its text before the first heading) and one entry per section, HTML in text
INDEX = {
    "config": {"lang": ["en"], "separator": "[\\s\\-]+"},
    "docs": [
        {"location": "", "title": "Home", "text": "<p>Welcome to the docs.</p>"},
        {"location": "guide/setup/", "title": "Setup", "text": "<p>How to set it up.</p>"},
        {"location": "guide/setup/#linux", "title": "Linux",
         "text": "<p>Use the <code>apt</code> package.</p><pre><code>apt install example\n</code></pre>"},
        {"location": "guide/setup/#windows", "title": "Windows", "text": ""},
        {"location": "changelog/", "title": "Changelog", "text": "<p>Version 2 fixes the installer.</p>"},
    ],
}


class Sites:
    """A fake web: url -> JSON body; and a way to run the connector against it in-process."""

    def __init__(self):
        self.index = INDEX
        self.pages = {f"{SITE}/search/search_index.json": INDEX}
        self.requests = []
        self.status = 200

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(str(request.url))
        body = self.pages.get(str(request.url))
        if body is None:
            return httpx.Response(404)
        return httpx.Response(self.status, text=body if isinstance(body, str) else json.dumps(body))

    def call(self, mode, stdin="", **settings):
        out, err = io.StringIO(), io.StringIO()
        env = {"URLS": SITE, **settings}
        code = MkDocs.run(["mkdocs", mode], env, io.StringIO(stdin), out, err, transport=httpx.MockTransport(self.handler),
                          sleep=lambda s: None)
        return code, [json.loads(line) for line in out.getvalue().splitlines()], err.getvalue()

    def versions(self, **settings):
        code, records, err = self.call("list", **settings)
        assert code == 0, err
        return {r["id"]: r["version"] for r in records}

    def fetch(self, *ids, **settings):
        code, records, err = self.call("fetch", "".join(json.dumps({"id": i}) + "\n" for i in ids), **settings)
        assert code == 0, err
        return {r["id"]: r for r in records}


@pytest.fixture
def sites():
    return Sites()
