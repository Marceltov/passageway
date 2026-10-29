import io
import json

import pytest

from fake_etapi import FakeEtapi, seed_fixture, serve
from passageway_connector_trilium.connector import Trilium


class World:
    """A fake Trilium over HTTP with the fixture wiki, and a way to run the connector on it in-process."""

    def __init__(self):
        self.etapi = FakeEtapi()
        self.roots = seed_fixture(self.etapi)
        self.server = serve(self.etapi)
        self.url = f"http://127.0.0.1:{self.server.server_port}"

    def env(self, **extra):
        return {"URL": self.url, "TOKEN": self.etapi.token, **extra}

    def call(self, mode, stdin="", *, extra=(), **settings):
        out, err = io.StringIO(), io.StringIO()
        code = Trilium.run(["trilium", mode, *extra], self.env(**settings), io.StringIO(stdin), out, err)
        return code, [json.loads(line) for line in out.getvalue().splitlines()], err.getvalue()

    def ids(self, **settings):
        code, records, err = self.call("list", **settings)
        assert code == 0, err
        return {r["id"]: r["version"] for r in records}

    def fetch(self, *ids, **settings):
        code, records, err = self.call("fetch", "".join(json.dumps({"id": i}) + "\n" for i in ids), **settings)
        assert code == 0, err
        return {r["id"]: r for r in records}


@pytest.fixture
def world():
    w = World()
    yield w
    w.server.shutdown()
    w.server.server_close()
