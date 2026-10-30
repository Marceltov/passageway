import io
import json
import re
import sys
from pathlib import Path

import pytest

from passageway_embedder_openai.embedder import Embedder, SettingsError

README = Path(__file__).resolve().parents[1] / "README.md"


def run(env, requests):
    stdin = io.StringIO("".join(json.dumps(r) + "\n" for r in requests))
    out, err = io.StringIO(), io.StringIO()
    code = Embedder.run(env, stdin, out, err, sleep=lambda s: None)
    return code, [json.loads(line) for line in out.getvalue().splitlines()], err.getvalue()


@pytest.fixture
def env(api_server):
    url, _ = api_server
    return {"BASE_URL": url, "MODEL": "nomic-embed-text"}


def test_info_learns_the_dimension_by_embedding_a_probe_and_names_model_and_host(env, api_server):
    _, api = api_server
    code, replies, _ = run(env, [{"op": "info"}])
    assert code == 0 and replies[0]["dim"] == 16 and replies[0]["protocol"] == "1"
    assert replies[0]["name"].startswith("openai:nomic-embed-text@127.0.0.1:")
    assert len(api.requests) == 1 and api.requests[0]["body"]["input"] == ["passageway"]


def test_embed_posts_the_texts_and_returns_the_vectors_in_order(env, api_server):
    _, api = api_server
    code, replies, _ = run(env, [{"op": "embed", "kind": "passage", "texts": ["alpha beta", "gamma"]}])
    assert code == 0 and len(replies[0]["vectors"]) == 2
    assert api.requests[-1]["path"] == "/v1/embeddings" and api.requests[-1]["body"] == {"model": "nomic-embed-text", "input": ["alpha beta", "gamma"]}
    from fake_openai import vector
    assert replies[0]["vectors"] == [vector("alpha beta", 16), vector("gamma", 16)]  # sorted by index, as sent


def test_the_api_key_goes_in_the_authorization_header_and_nowhere_else(env, api_server):
    _, api = api_server
    run({**env, "API_KEY": "sk-secret"}, [{"op": "embed", "kind": "query", "texts": ["x"]}])
    assert api.requests[-1]["headers"]["Authorization"] == "Bearer sk-secret"
    run(env, [{"op": "embed", "kind": "query", "texts": ["x"]}])
    assert "Authorization" not in api.requests[-1]["headers"]  # a local server needs none


def test_prefixes_are_added_per_kind(env, api_server):
    _, api = api_server
    run({**env, "QUERY_PREFIX": "query: ", "PASSAGE_PREFIX": "passage: "},
        [{"op": "embed", "kind": "query", "texts": ["q"]}, {"op": "embed", "kind": "passage", "texts": ["p"]}])
    assert [r["body"]["input"] for r in api.requests[-2:]] == [["query: q"], ["passage: p"]]


def test_dimensions_is_sent_and_answers_info_without_a_probe(env, api_server):
    _, api = api_server
    code, replies, _ = run({**env, "DIMENSIONS": "8"}, [{"op": "info"}, {"op": "embed", "kind": "query", "texts": ["x"]}])
    assert code == 0 and replies[0]["dim"] == 8 and len(replies[1]["vectors"][0]) == 8
    assert len(api.requests) == 1 and api.requests[0]["body"]["dimensions"] == 8


def test_voyage_sends_input_type_and_defaults_to_its_own_url(env, api_server):
    _, api = api_server
    run({**env, "PROVIDER": "voyage", "MODEL": "voyage-3"},
        [{"op": "embed", "kind": "query", "texts": ["q"]}, {"op": "embed", "kind": "passage", "texts": ["p"]}])
    assert [r["body"]["input_type"] for r in api.requests[-2:]] == ["query", "document"]
    _, replies, _ = run({**env, "PROVIDER": "voyage", "MODEL": "voyage-3"}, [{"op": "info"}])
    assert replies[0]["name"].startswith("voyage:voyage-3@")
    from passageway_embedder_openai.embedder import parse_settings
    assert parse_settings({"PROVIDER": "voyage", "MODEL": "voyage-3", "API_KEY": "k"}).base_url == "https://api.voyageai.com/v1"
    assert parse_settings({"MODEL": "text-embedding-3-small", "API_KEY": "k"}).base_url == "https://api.openai.com/v1"


def test_a_name_override(env):
    _, replies, _ = run({**env, "NAME": "my-ollama-nomic"}, [{"op": "info"}])
    assert replies[0]["name"] == "my-ollama-nomic"


def test_a_failing_request_is_an_error_reply_and_the_process_goes_on(env, api_server):
    _, api = api_server
    code, replies, _ = run({**env, "MODEL": "no-such-model"},
                           [{"op": "embed", "kind": "query", "texts": ["x"]}, {"op": "info"}])
    assert code == 0 and "error" in replies[0] and "no-such-model" in replies[0]["error"] and "404" in replies[0]["error"]
    assert "error" in replies[1]


def test_the_key_never_appears_in_an_error(env, api_server):
    _, api = api_server
    api.status_errors = [401]
    _, replies, err = run({**env, "API_KEY": "sk-secret"}, [{"op": "embed", "kind": "query", "texts": ["x"]}])
    assert "sk-secret" not in json.dumps(replies) + err and "401" in replies[0]["error"]


def test_429_and_5xx_are_retried_with_backoff_and_retry_after(env, api_server):
    _, api = api_server
    api.status_errors = [429, 503, 502]
    api.retry_after = "0"
    code, replies, _ = run(env, [{"op": "embed", "kind": "query", "texts": ["x"]}])
    assert code == 0 and "vectors" in replies[0] and len(api.requests) == 4


def test_giving_up_at_the_deadline_is_an_error_reply(env, api_server):
    _, api = api_server
    api.status_errors = [503] * 1000
    _, replies, _ = run({**env, "TIMEOUT": "300"}, [{"op": "embed", "kind": "query", "texts": ["x"]}])
    assert "error" in replies[0] and "503" in replies[0]["error"] and "300 s" in replies[0]["error"]


def test_more_than_five_429s_are_waited_out_within_a_long_timeout(env, api_server):
    _, api = api_server
    api.status_errors = [429] * 8
    waited = []
    stdin = io.StringIO('{"op": "embed", "kind": "query", "texts": ["x"]}\n')
    out = io.StringIO()
    Embedder.run({**env, "TIMEOUT": "1000"}, stdin, out, io.StringIO(), sleep=waited.append)
    assert "vectors" in json.loads(out.getvalue()) and len(api.requests) == 9 and sum(waited) > 120


def test_a_retry_after_beyond_30_seconds_is_honoured_within_timeout(env, api_server):
    _, api = api_server
    api.status_errors, api.retry_after = [429], "200"
    waited = []
    stdin = io.StringIO('{"op": "embed", "kind": "query", "texts": ["x"]}\n')
    out = io.StringIO()
    Embedder.run({**env, "TIMEOUT": "1000"}, stdin, out, io.StringIO(), sleep=waited.append)
    assert "vectors" in json.loads(out.getvalue()) and waited == [200]


def test_a_server_that_is_not_there_is_an_error_reply_not_a_crash():
    _, replies, _ = run({"BASE_URL": "http://127.0.0.1:9/v1", "MODEL": "m"}, [{"op": "info"}])
    assert "error" in replies[0] and "127.0.0.1:9" in replies[0]["error"]


@pytest.mark.parametrize("env,message", [
    ({}, "MODEL"),
    ({"MODEL": "m", "BASE_URL": "ftp://x"}, "BASE_URL"),
    ({"MODEL": "m", "PROVIDER": "cohere"}, "PROVIDER"),
    ({"MODEL": "m", "BASE_URL": "http://localhost:11434/v1", "DIMENSIONS": "big"}, "DIMENSIONS"),
    ({"MODEL": "m", "BASE_URL": "http://localhost:11434/v1", "DIMENSIONS": "0"}, "DIMENSIONS"),
    ({"MODEL": "m", "BASE_URL": "http://localhost:11434/v1", "TIMEOUT": "soon"}, "TIMEOUT"),
    ({"MODEL": "m", "PROVIDER": "voyage"}, "API_KEY"),  # a cloud provider needs a key
    ({"MODEL": "m"}, "API_KEY"),  # api.openai.com too
])
def test_bad_settings_exit_2_with_a_message_and_no_output(env, message):
    stdin, out, err = io.StringIO('{"op": "info"}\n'), io.StringIO(), io.StringIO()
    assert Embedder.run(env, stdin, out, err) == 2
    assert out.getvalue() == "" and message in err.getvalue()


def test_an_empty_text_list_is_an_empty_reply_without_a_request(env, api_server):
    _, api = api_server
    _, replies, _ = run(env, [{"op": "embed", "kind": "query", "texts": []}])
    assert replies == [{"vectors": []}] and api.requests == []


def test_every_setting_is_in_the_readme():
    code = (Path(__file__).resolve().parents[1] / "passageway_embedder_openai" / "embedder.py").read_text()
    names = sorted(set(re.findall(r'env\.get\(\s*"([A-Z_]+)"', code)))
    assert len(names) >= 8, names
    readme = README.read_text()
    for name in names:
        assert f"`{name}`" in readme, f"{name} is read by the embedder but missing from its README"
    assert "third party" in readme or "third-party" in readme  # the privacy sentence


def test_the_contract_check_passes_as_a_real_subprocess(api_server):
    url, _ = api_server
    from passageway.embed_command import CommandEmbedder
    from passageway.testing.embedder_contract import check_embedder
    embedder = CommandEmbedder("openai", [sys.executable, "-m", "passageway_embedder_openai"],
                               env={"BASE_URL": url, "MODEL": "nomic-embed-text"})
    try:
        check_embedder(embedder)
        assert embedder.dim == 16
    finally:
        embedder.close()


# ---- review findings ------------------------------------------------------------------------------

def test_dimensions_is_checked_against_what_the_service_really_returns(env, api_server):
    _, api = api_server
    api.ignore_dimensions = True
    _, replies, _ = run({**env, "DIMENSIONS": "8"}, [{"op": "info"}, {"op": "embed", "kind": "query", "texts": ["x"]}])
    assert replies[0]["dim"] == 8 and "error" in replies[1] and "8" in replies[1]["error"] and "16" in replies[1]["error"]


def test_voyage_sends_output_dimension_not_dimensions(env, api_server):
    _, api = api_server
    run({**env, "PROVIDER": "voyage", "MODEL": "voyage-3", "DIMENSIONS": "8"}, [{"op": "embed", "kind": "query", "texts": ["x"]}])
    body = api.requests[-1]["body"]
    assert body.get("output_dimension") == 8 and "dimensions" not in body


def test_the_whole_request_including_retries_stays_within_timeout(env, api_server):
    _, api = api_server
    api.status_errors = [503] * 5
    api.retry_after = "100"
    waited = []
    stdin = io.StringIO('{"op": "embed", "kind": "query", "texts": ["x"]}\n')
    out, err = io.StringIO(), io.StringIO()
    Embedder.run({**env, "TIMEOUT": "2"}, stdin, out, err, sleep=lambda s: waited.append(s))
    reply = json.loads(out.getvalue())
    assert "error" in reply and "503" in reply["error"]
    assert sum(waited) <= 2 and len(api.requests) <= 3  # it gave up within the budget, not after five long waits


def test_retry_after_is_honoured_and_clamped(env, api_server):
    _, api = api_server
    api.status_errors = [429]
    api.retry_after = "3"
    waited = []
    stdin = io.StringIO('{"op": "embed", "kind": "query", "texts": ["x"]}\n')
    Embedder.run({**env, "TIMEOUT": "30"}, stdin, io.StringIO(), io.StringIO(), sleep=lambda s: waited.append(s))
    assert waited == [3.0]
    for value in ("-5", "nan", "Wed, 21 Oct 2015 07:28:00 GMT"):
        api.status_errors = [429]
        api.retry_after = value
        waited.clear()
        stdin = io.StringIO('{"op": "embed", "kind": "query", "texts": ["x"]}\n')
        out = io.StringIO()
        Embedder.run({**env, "TIMEOUT": "30"}, stdin, out, io.StringIO(), sleep=lambda s: waited.append(s))
        assert "vectors" in json.loads(out.getvalue()) and len(waited) == 1 and 0 <= waited[0] <= 30


def test_a_connection_error_is_retried_but_a_read_timeout_is_not(env, api_server, monkeypatch):
    import httpx
    calls = []

    class Client:
        def __init__(self, *a, **k): pass
        def post(self, url, json, timeout=None):
            calls.append(json)
            raise (httpx.ConnectError("refused") if len(calls) < 3 else httpx.ReadTimeout("slow"))
    monkeypatch.setattr(httpx, "Client", Client)
    _, replies, _ = run(env, [{"op": "embed", "kind": "query", "texts": ["x"]}])
    assert "error" in replies[0] and "ReadTimeout" in replies[0]["error"] and len(calls) == 3  # 2 retries, then no retry


def test_a_key_quoted_by_the_service_is_masked(env, api_server):
    _, api = api_server
    api.echo_auth = True
    _, replies, _ = run({**env, "API_KEY": "sk-secret"}, [{"op": "embed", "kind": "query", "texts": ["x"]}])
    assert "sk-secret" not in json.dumps(replies) and "***" in replies[0]["error"]


def test_credentials_in_the_base_url_are_refused():
    out, err = io.StringIO(), io.StringIO()
    assert Embedder.run({"MODEL": "m", "BASE_URL": "http://user:pw@localhost:11434/v1"}, io.StringIO('{"op":"info"}\n'), out, err) == 2
    assert "API_KEY" in err.getvalue() and "pw" not in err.getvalue().replace("API_KEY", "")


@pytest.mark.parametrize("env_extra,message", [
    ({"DIMENSIONS": "²"}, "DIMENSIONS"), ({"TIMEOUT": "nan"}, "TIMEOUT"), ({"TIMEOUT": "inf"}, "TIMEOUT"),
    ({"API_KEY": "sk-’"}, "API_KEY"),
])
def test_more_settings_that_must_be_refused_cleanly(env_extra, message):
    out, err = io.StringIO(), io.StringIO()
    env = {"MODEL": "m", "BASE_URL": "http://localhost:11434/v1", **env_extra}
    assert Embedder.run(env, io.StringIO('{"op":"info"}\n'), out, err) == 2 and message in err.getvalue()


def test_a_redirect_and_a_base_url_ending_in_embeddings_give_clear_answers(env, api_server):
    url, api = api_server
    api.redirect_to = "https://elsewhere.example/v1/embeddings"
    _, replies, _ = run(env, [{"op": "info"}])
    assert "redirect" in replies[0]["error"] and "elsewhere.example" in replies[0]["error"]
    api.redirect_to = None
    from passageway_embedder_openai.embedder import parse_settings
    assert parse_settings({**env, "BASE_URL": url + "/embeddings"}).base_url == url


@pytest.mark.parametrize("body", [b'{"data": [{"index": 0, "embedding": "abc"}]}', b'{"data": [{"index": 0, "embedding": null}]}',
                                  b'{"data": [{"index": 0, "embedding": [NaN, 1.0]}]}', b'{"data": [{"index": 0, "embedding": []}]}',
                                  b"[" * 100000])
def test_a_service_answer_that_is_not_vectors_is_an_error_reply_not_a_crash(env, api_server, body):
    _, api = api_server
    api.bad_body = body
    code, replies, _ = run(env, [{"op": "embed", "kind": "query", "texts": ["x"]}, {"op": "info"}])
    assert code == 0 and len(replies) == 2 and all("error" in r for r in replies)


@pytest.mark.parametrize("request_", ['{"op": "embed", "kind": "query", "texts": "abc"}', '{"op": "embed", "kind": "other", "texts": ["a"]}',
                                      "[" * 100000])
def test_a_bad_request_line_is_an_error_reply_and_the_process_goes_on(env, request_):
    stdin = io.StringIO(request_ + '\n{"op": "info"}\n')
    out = io.StringIO()
    assert Embedder.run(env, stdin, out, io.StringIO(), sleep=lambda s: None) == 0
    replies = [json.loads(line) for line in out.getvalue().splitlines()]
    assert "error" in replies[0] and "dim" in replies[1]


def test_the_name_changes_with_the_prefixes_and_carries_the_port(env):
    plain = run(env, [{"op": "info"}])[1][0]["name"]
    prefixed = run({**env, "QUERY_PREFIX": "search_query: "}, [{"op": "info"}])[1][0]["name"]
    assert plain != prefixed and plain.startswith("openai:nomic-embed-text@127.0.0.1:") and prefixed.startswith(plain)
