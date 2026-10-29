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
    assert code == 0 and replies == [{"name": f"openai:nomic-embed-text@127.0.0.1", "dim": 16, "protocol": "1"}]
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


def test_giving_up_after_five_attempts_is_an_error_reply(env, api_server):
    _, api = api_server
    api.status_errors = [503] * 5
    _, replies, _ = run(env, [{"op": "embed", "kind": "query", "texts": ["x"]}])
    assert "error" in replies[0] and "503" in replies[0]["error"] and len(api.requests) == 5


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
