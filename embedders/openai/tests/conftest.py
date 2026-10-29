import pytest

from fake_openai import FakeApi, serve


@pytest.fixture
def api_server():
    api = FakeApi()
    server = serve(api)
    yield f"http://127.0.0.1:{server.server_port}/v1", api
    server.shutdown()
