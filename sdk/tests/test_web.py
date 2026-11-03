import httpx
import pytest
import truststore

from passageway_sdk import SourceError
from passageway_sdk.web import TooLarge, Web


def web(handler, **options):
    return Web("test-agent", transport=httpx.MockTransport(handler), sleep=lambda s: None, **options)


def ok(request):
    return httpx.Response(200, headers={"Content-Type": "text/html"}, text="hello")


def test_a_reply_has_status_text_and_content_type():
    reply = web(ok).get("https://x.example/")
    assert (reply.status, reply.text, reply.content_type) == (200, "hello", "text/html")


def test_the_user_agent_is_sent():
    seen = []
    web(lambda r: seen.append(r.headers["user-agent"]) or httpx.Response(200)).get("https://x.example/")
    assert seen == ["test-agent"]


def test_a_missing_page_is_a_reply_unless_it_is_required():
    handler = lambda r: httpx.Response(404)  # noqa: E731
    assert web(handler).get("https://x.example/").status == 404
    with pytest.raises(SourceError, match="404"):
        web(handler).get("https://x.example/", required=True)


@pytest.mark.parametrize("status", [429, 500, 503])
def test_a_busy_or_failing_server_fails_the_call(status):
    with pytest.raises(SourceError, match=str(status)):
        web(lambda r: httpx.Response(status)).get("https://x.example/")


def test_a_network_error_fails_the_call():
    def refuse(request):
        raise httpx.ConnectError("refused")

    with pytest.raises(SourceError, match="refused"):
        web(refuse).get("https://x.example/")


def test_a_reply_over_the_limit_is_too_large_and_the_limit_can_be_set_per_call():
    big = lambda r: httpx.Response(200, content=b"x" * 100)  # noqa: E731
    with pytest.raises(TooLarge):
        web(big, max_bytes=10).get("https://x.example/")
    assert len(web(big, max_bytes=10).get("https://x.example/", max_bytes=1000).text) == 100
    assert issubclass(TooLarge, SourceError)


def test_requests_are_spaced_by_the_pause():
    waits = []
    client = Web("a", pause=5, transport=httpx.MockTransport(ok), sleep=waits.append)
    client.get("https://x.example/")
    client.get("https://x.example/")
    assert len(waits) == 1 and 0 < waits[0] <= 5  # the first request does not wait


def test_https_uses_the_system_trust_store():
    assert isinstance(Web("a")._http._transport._pool._ssl_context, truststore.SSLContext)


def test_text_that_is_not_utf8_is_replaced_not_fatal():
    assert web(lambda r: httpx.Response(200, content=b"caf\xe9")).get("https://x.example/").text == "caf�"
