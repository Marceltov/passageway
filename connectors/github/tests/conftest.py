import base64
import hashlib
import io
import json
import re

import httpx
import pytest

from passageway_connector_github.connector import GitHub

API = "https://api.github.com"
CODE = "\n".join([f"def f{n}():\n    return {n}\n" for n in range(40)])  # 120 lines in 40 small functions


def sha(content: bytes) -> str:
    return hashlib.sha1(content).hexdigest()


class FakeGitHub:
    """A fake GitHub REST API over a few repositories; and a way to run the connector against it in-process."""

    def __init__(self):
        self.owners = {"acme": "Organization", "ann": "User"}
        self.repos = {
            "acme/docs": {"default_branch": "main", "fork": False, "archived": False, "private": False, "files": {
                "README.md": "# Acme docs\n\nStart here.\n",
                "guide/setup.md": "---\ntitle: x\n---\n# Setup\n\nInstall it.\n\n## Linux\n\nUse the package manager.\n",
                "guide/notes.markdown": "No heading here.\n",
                "src/app.py": CODE,
                "logo.png": b"\x89PNG\0\0binary",
            }},
            "acme/old": {"default_branch": "main", "fork": False, "archived": True, "private": False, "files": {"README.md": "# Old\n\nGone.\n"}},
            "acme/forked": {"default_branch": "main", "fork": True, "archived": False, "private": False, "files": {"README.md": "# Fork\n\nCopy.\n"}},
            "acme/secret": {"default_branch": "trunk", "fork": False, "archived": False, "private": True, "files": {"README.md": "# Secret\n\nHidden.\n"}},
            "ann/notes": {"default_branch": "main", "fork": False, "archived": False, "private": False, "files": {"ideas.md": "# Ideas\n\nMany.\n"}},
        }
        self.token = "t0ken"  # the token the fake accepts as ann's; a private repo needs it
        self.requests: list[httpx.Request] = []
        self.rate_limited = False
        self.down = False

    # -- the API --------------------------------------------------------------------------------

    def _visible(self, name: str, request: httpx.Request) -> bool:
        return not self.repos[name]["private"] or request.headers.get("authorization") == f"Bearer {self.token}"

    def _repo(self, name: str) -> dict:
        r = self.repos[name]
        return {"full_name": name, "name": name.split("/")[1], "owner": {"login": name.split("/")[0]},
                "default_branch": r["default_branch"], "fork": r["fork"], "archived": r["archived"], "private": r["private"],
                "html_url": f"https://github.com/{name}"}

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        if self.down:
            return httpx.Response(503)
        if self.rate_limited:
            return httpx.Response(403, headers={"x-ratelimit-remaining": "0", "x-ratelimit-reset": "1762430400"},
                                  json={"message": "API rate limit exceeded"})
        auth = request.headers.get("authorization")
        if auth and auth != f"Bearer {self.token}":
            return httpx.Response(401, json={"message": "Bad credentials"})
        # GitHub Enterprise Server serves the same API under /api/v3
        path, page = request.url.path.removeprefix("/api/v3"), int(request.url.params.get("page", "1"))
        if path == "/user":
            return httpx.Response(200, json={"login": "ann"}) if auth else httpx.Response(401, json={})
        if m := re.fullmatch(r"/users/([^/]+)", path):
            kind = self.owners.get(m.group(1))
            return httpx.Response(200, json={"login": m.group(1), "type": kind}) if kind else httpx.Response(404, json={})
        if m := re.fullmatch(r"/(?:orgs|users)/([^/]+)/repos|/user/repos", path):
            owner = m.group(1) if m.group(1) else "ann"
            names = [n for n in self.repos if n.split("/")[0] == owner and self._visible(n, request)]
            per = int(request.url.params.get("per_page", "30"))
            return httpx.Response(200, json=[self._repo(n) for n in names[(page - 1) * per:page * per]])
        if m := re.fullmatch(r"/repos/([^/]+/[^/]+)", path):
            name = m.group(1)
            return httpx.Response(200, json=self._repo(name)) if name in self.repos and self._visible(name, request) \
                else httpx.Response(404, json={"message": "Not Found"})
        if m := re.fullmatch(r"/repos/([^/]+/[^/]+)/git/trees/([^/]+)", path):
            name, branch = m.groups()
            if name not in self.repos or not self._visible(name, request) or branch != self.repos[name]["default_branch"]:
                return httpx.Response(404, json={"message": "Not Found"})
            tree = [{"path": p, "type": "blob", "sha": sha(c if isinstance(c, bytes) else c.encode()),
                     "size": len(c if isinstance(c, bytes) else c.encode())} for p, c in self.repos[name]["files"].items()]
            folders = sorted({p.rsplit("/", 1)[0] for p in self.repos[name]["files"] if "/" in p})
            tree += [{"path": f, "type": "tree", "sha": sha(f.encode())} for f in folders]
            return httpx.Response(200, json={"sha": "root", "tree": tree, "truncated": False})
        if m := re.fullmatch(r"/repos/([^/]+/[^/]+)/git/blobs/([0-9a-f]+)", path):
            name, wanted = m.groups()
            for content in self.repos.get(name, {}).get("files", {}).values():
                raw = content if isinstance(content, bytes) else content.encode()
                if sha(raw) == wanted:
                    return httpx.Response(200, json={"sha": wanted, "encoding": "base64",
                                                     "content": base64.encodebytes(raw).decode()})
            return httpx.Response(404, json={"message": "Not Found"})
        return httpx.Response(404, json={"message": "Not Found"})

    # -- the connector --------------------------------------------------------------------------

    def call(self, mode, stdin="", **settings):
        out, err = io.StringIO(), io.StringIO()
        env = {"REPOS": "acme/docs", **settings}
        code = GitHub.run(["github", mode], env, io.StringIO(stdin), out, err, transport=httpx.MockTransport(self.handler),
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
def github():
    return FakeGitHub()
