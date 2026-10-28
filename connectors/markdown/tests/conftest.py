import io
import json

import pytest

from passageway_connector_markdown.connector import Markdown


class Folder:
    """A folder of notes and a way to run the connector on it in-process."""

    def __init__(self, root):
        self.root = root

    def write(self, name, text, *, binary=False):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text) if binary else path.write_text(text, encoding="utf-8")
        return path

    def call(self, mode, stdin="", *, extra=(), **settings):
        out, err = io.StringIO(), io.StringIO()
        env = {"FOLDER": str(self.root), **settings}
        code = Markdown.run(["markdown", mode, *extra], env, io.StringIO(stdin), out, err)
        return code, [json.loads(line) for line in out.getvalue().splitlines()], err.getvalue()

    def fetch(self, *ids, **settings):
        code, records, err = self.call("fetch", "".join(json.dumps({"id": i}) + "\n" for i in ids), **settings)
        assert code == 0, err
        return {r["id"]: r for r in records}

    def ids(self, **settings):
        code, records, err = self.call("list", **settings)
        assert code == 0, err
        return sorted(r["id"] for r in records)


@pytest.fixture
def folder(tmp_path):
    return Folder(tmp_path)
