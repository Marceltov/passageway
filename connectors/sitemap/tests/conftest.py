import io
import json

import httpx
import pytest

from passageway_connector_sitemap.connector import Sitemap

SITE = "https://site.example"


def html(title, body):
    return f"<html><head><title>{title}</title></head><body><nav>Menu Home About</nav><main>{body}</main><footer>Copyright</footer></body></html>"


class Web:
    """A fake website: url -> (status, content type, body); and a way to run the connector against it in-process."""

    def __init__(self):
        self.pages = {
            f"{SITE}/sitemap.xml": (200, "application/xml",
                                    f"<urlset><url><loc>{SITE}/</loc></url><url><loc>{SITE}/guide/setup</loc></url></urlset>"),
            f"{SITE}/": (200, "text/html", html("Home", '<h1>Welcome</h1><p>The start.</p><a href="/guide/setup">Setup</a>'
                                                '<a href="/hidden">Hidden</a><a href="https://other.example/x">Out</a>')),
            f"{SITE}/guide/setup": (200, "text/html", html("Setup", "<h1>Setup</h1><p>Install it.</p><h2>Linux</h2><p>Use apt.</p>"
                                                           "<pre>apt install x</pre>")),
            f"{SITE}/hidden": (200, "text/html", html("Hidden", "<h1>Hidden</h1><p>Not in the sitemap.</p>")),
        }
        self.requests = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        self.requests.append(url)
        status, kind, body = self.pages.get(url, (404, "text/plain", "not found"))
        return httpx.Response(status, headers={"Content-Type": kind}, text=body)

    def call(self, mode, stdin="", render=None, **settings):
        out, err = io.StringIO(), io.StringIO()
        env = {"SITEMAP": f"{SITE}/sitemap.xml", "PAUSE": "0", **settings}
        code = Sitemap.run(["sitemap", mode], env, io.StringIO(stdin), out, err, transport=httpx.MockTransport(self.handler),
                           sleep=lambda s: None, **({"render": render} if render else {}))
        return code, [json.loads(line) for line in out.getvalue().splitlines()], err.getvalue()

    def ids(self, **settings):
        code, records, err = self.call("list", **settings)
        assert code == 0, err
        return [r["id"] for r in records]

    def fetch(self, *ids, **settings):
        code, records, err = self.call("fetch", "".join(json.dumps({"id": i}) + "\n" for i in ids), **settings)
        assert code == 0, err
        return {r["id"]: r for r in records}


@pytest.fixture
def web():
    return Web()
