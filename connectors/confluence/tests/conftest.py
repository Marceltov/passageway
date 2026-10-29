import io
import json

import pytest

from fake_confluence import FakeConfluence, seed, serve
from passageway_connector_confluence.connector import Confluence


class World:
    def __init__(self):
        self.api = FakeConfluence()
        seed(self.api)
        self.server = serve(self.api)
        self.url = f"http://127.0.0.1:{self.server.server_port}"

    def env(self, **extra):
        return {"URL": self.url, "SPACES": "OPS|HR", "TOKEN": self.api.token, "PAUSE_SECONDS": "0", **extra}

    def call(self, mode, stdin="", *, extra=(), **settings):
        out, err = io.StringIO(), io.StringIO()
        code = Confluence.run(["confluence", mode, *extra], self.env(**settings), io.StringIO(stdin), out, err, sleep=lambda s: None)
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
