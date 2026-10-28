import pytest

from fake_mediawiki import FakeWiki, serve


@pytest.fixture
def wiki_server():
    wiki = FakeWiki()
    server = serve(wiki)
    yield f"http://127.0.0.1:{server.server_port}/w/api.php", wiki
    server.shutdown()
