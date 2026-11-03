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


# ---- a client for an API: base address, headers, TLS switch, redirects, retries, other methods ----------------------------

from passageway_sdk.web import HttpError, Retry  # noqa: E402


def test_a_base_url_and_default_headers_apply_to_every_request():
    seen = []
    client = web(lambda r: seen.append((str(r.url), r.headers["authorization"])) or httpx.Response(200),
                 base_url="https://api.example/v1", headers={"Authorization": "Bearer t"}, pause=0)
    client.get("/notes", params={"q": "a b"})
    assert seen == [("https://api.example/v1/notes?q=a+b", "Bearer t")]


def test_a_server_error_carries_its_status():
    with pytest.raises(HttpError) as raised:
        web(lambda r: httpx.Response(503)).get("https://x.example/")
    assert raised.value.status == 503 and isinstance(raised.value, SourceError)
    with pytest.raises(HttpError) as raised:
        web(lambda r: httpx.Response(401)).get("https://x.example/", required=True)
    assert raised.value.status == 401


def test_turning_tls_checking_off_is_an_explicit_switch():
    assert Web("a", verify=False)._http._transport._pool._ssl_context.verify_mode == ssl_none()


def ssl_none():
    import ssl

    return ssl.CERT_NONE


def test_redirects_are_followed_unless_refused():
    def handler(request):
        return httpx.Response(302, headers={"Location": "https://y.example/"}) if request.url.host == "x.example" else httpx.Response(200)

    assert web(handler).get("https://x.example/").status == 200
    assert web(handler, follow_redirects=False).get("https://x.example/").status == 302


def test_a_post_sends_json_and_a_reply_reads_as_json():
    seen = []

    def handler(request):
        seen.append((request.method, request.content))
        return httpx.Response(200, json={"ok": True})

    reply = web(handler).request("POST", "https://x.example/", json={"a": 1})
    assert seen == [("POST", b'{"a":1}')] and reply.json() == {"ok": True}


def test_a_retry_policy_waits_for_a_busy_server_and_then_succeeds():
    replies = iter([httpx.Response(429, headers={"Retry-After": "7"}), httpx.Response(503), httpx.Response(200, text="ok")])
    waits = []
    client = Web("a", pause=0, retry=Retry(), transport=httpx.MockTransport(lambda r: next(replies)), sleep=waits.append)
    assert client.get("https://x.example/").text == "ok"
    assert waits[0] == 7 and 0 < waits[1] <= 60  # Retry-After is honoured, otherwise a backoff


def test_a_retry_policy_gives_up_after_its_budget():
    waits = []
    client = Web("a", pause=0, retry=Retry(budget=10, max_backoff=4), transport=httpx.MockTransport(lambda r: httpx.Response(503)),
                 sleep=waits.append)
    with pytest.raises(HttpError, match="503"):
        client.get("https://x.example/")
    assert 0 < sum(waits) <= 10


def test_without_a_retry_policy_nothing_is_retried():
    calls = []
    with pytest.raises(HttpError):
        web(lambda r: calls.append(1) or httpx.Response(503)).get("https://x.example/")
    assert len(calls) == 1
