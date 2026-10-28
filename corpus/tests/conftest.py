import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[1]))  # corpus/snapshot.py
sys.path.insert(0, str(HERE.parents[2] / "connectors" / "wikipedia" / "tests"))  # the connector's fake MediaWiki

from fake_mediawiki import FakeWiki, serve  # noqa: E402


@pytest.fixture
def wiki_server():
    wiki = FakeWiki()
    server = serve(wiki)
    yield f"http://127.0.0.1:{server.server_port}/w/api.php", wiki
    server.shutdown()
