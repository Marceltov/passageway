import io
import json

import httpx
import pytest

from passageway_connector_llmstxt.connector import LlmsTxt

DOCS = """# Install

Run the installer.

## Linux

Use the package manager.

# Configure

Set the token in the settings file.

```
# not a heading
```
"""


class Sites:
    """A fake web: path -> (status, body); and a way to run the connector against it in-process."""

    def __init__(self):
        self.pages = {"https://docs.example/llms-full.txt": DOCS}
        self.requests = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(str(request.url))
        body = self.pages.get(str(request.url))
        return httpx.Response(404) if body is None else httpx.Response(200, text=body)

    def call(self, mode, stdin="", **settings):
        out, err = io.StringIO(), io.StringIO()
        env = {"URLS": "https://docs.example", **settings}
        code = LlmsTxt.run(["llmstxt", mode], env, io.StringIO(stdin), out, err, transport=httpx.MockTransport(self.handler),
                           sleep=lambda s: None)
        return code, [json.loads(line) for line in out.getvalue().splitlines()], err.getvalue()

    def fetch(self, *ids, **settings):
        code, records, err = self.call("fetch", "".join(json.dumps({"id": i}) + "\n" for i in ids), **settings)
        assert code == 0, err
        return {r["id"]: r for r in records}


@pytest.fixture
def sites():
    return Sites()
