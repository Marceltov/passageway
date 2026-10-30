import json
import sys

import pytest
from fastmcp import Client
from starlette.testclient import TestClient

from passageway.config import Config, ConnectorConfig
from passageway.embed import HashEmbedder
from passageway.rank import RankParams
from passageway.server import Engine, build_app, build_error_app, build_mcp

OK = {"Authorization": "Bearer secret"}
BAD = {"Authorization": "Bearer wrong"}
DOC = {"id": "d1", "title": "Proxmox swap", "url": "http://x/d1", "version": "1",
       "sections": [{"heading": "OOM", "text": "the proxmox host swap setting makes the OOM killer fire"}]}


def make_engine(tmp_path, data, fail=None):
    items = tmp_path / "items.json"
    items.write_text(json.dumps(data))
    env = {"FAKE_ITEMS": str(items), **({"FAKE_FAIL": fail} if fail else {})}
    cc = ConnectorConfig("notes", (sys.executable, "-m", "passageway.testing.fake_connector"), env, {})
    config = Config(password="secret", connectors=[cc], data_dir=tmp_path, model_dir=tmp_path)
    engine = Engine(config, HashEmbedder())
    engine.params = RankParams(min_cos=0.2)
    engine.sync_all_once()
    return engine


@pytest.fixture
def engine(tmp_path):
    return make_engine(tmp_path, [DOC])


@pytest.fixture
def client(engine):
    with TestClient(build_app(engine, background=False)) as c:
        yield c


def test_health_is_open_and_reports_sources(client):
    body = client.get("/health").json()
    assert body["status"] == "ok" and body["sources"]["notes"]["items"] == 1


def test_health_degrades_when_a_connector_fails(tmp_path):
    engine = make_engine(tmp_path, [DOC], fail="list")
    with TestClient(build_app(engine, background=False)) as c:
        body = c.get("/health", headers=OK).json()
    assert body["status"] in ("degraded", "starting") and "fake failure" in str(body["sources"]["notes"]["last_error"])


def test_open_health_hides_connector_error_text(tmp_path):
    engine = make_engine(tmp_path, [DOC], fail="list")
    with TestClient(build_app(engine, background=False)) as c:
        open_body = c.get("/health")
    assert "fake failure" not in open_body.text and open_body.json()["sources"]["notes"]["last_error"]


def test_hook_requires_the_bearer_token(client):
    assert client.post("/recall", json={"prompt": "x"}).status_code == 401
    assert client.post("/recall", json={"prompt": "x"}, headers=BAD).status_code == 401


def test_hook_returns_context_and_remembers_the_session(client):
    body = {"prompt": "proxmox swap OOM killer", "session_id": "s1"}
    first = client.post("/recall", json=body, headers=OK).json()
    assert first["hits"] == ["d1"] and "http://x/d1" in first["context"]
    again = client.post("/recall", json=body, headers=OK).json()
    assert again["hits"] == [] and again["context"] == ""


def test_hook_skips_confirmations_and_validates_the_body(client):
    assert client.post("/recall", json={"prompt": "ok"}, headers=OK).json()["skipped"] == "confirmation"
    assert client.post("/recall", content="nope", headers=OK).status_code == 400


async def test_mcp_tool_returns_passages_and_nothing(engine):
    async with Client(build_mcp(engine)) as c:
        hit = (await c.call_tool("recall", {"query": "proxmox swap OOM killer"})).data
        none = (await c.call_tool("recall", {"query": "zebra quantum"})).data
        unknown = (await c.call_tool("recall", {"query": "x", "source": "nope"})).data
    assert "Proxmox swap" in hit and "Nothing relevant" in none and "Unknown source" in unknown


def test_health_is_indented_for_people_reading_it_with_curl(client):
    assert client.get("/health").text.startswith('{\n  "status"')
    with TestClient(build_error_app("bad config")) as c:
        assert c.get("/health").text.startswith('{\n  "status"')


def test_health_names_the_instance(engine):
    engine.config.instance = "work"
    with TestClient(build_app(engine, background=False)) as c:
        assert c.get("/health").json()["instance"] == "work"


def test_error_app_reports_the_problem():
    with TestClient(build_error_app("bad config")) as c:
        assert c.get("/health").status_code == 503 and c.post("/recall", json={}).status_code == 503


def two_source_engine(tmp_path):
    """Source `a` is healthy; source `b` has an index built with another embedder dimension and a failing connector."""
    from passageway.index import Index
    items = tmp_path / "items.json"
    items.write_text(json.dumps([DOC]))
    Index(tmp_path / "b.db", "other-embedder", 8)  # a stale index left by an earlier embedder
    cmd = (sys.executable, "-m", "passageway.testing.fake_connector")
    config = Config(password="secret", data_dir=tmp_path, model_dir=tmp_path, connectors=[
        ConnectorConfig("a", cmd, {"FAKE_ITEMS": str(items)}, {}),
        ConnectorConfig("b", cmd, {"FAKE_ITEMS": str(items), "FAKE_FAIL": "list"}, {})])
    engine = Engine(config, HashEmbedder())
    engine.params = RankParams(min_cos=0.2)
    engine.sync_all_once()
    return engine


def test_a_stale_source_does_not_break_recall_for_the_others(tmp_path):
    engine = two_source_engine(tmp_path)
    assert [h.item_id for h in engine.recall("proxmox swap OOM killer")] == ["d1"]


def test_reconcile_rebuilds_a_source_that_never_had_a_good_first_sync(tmp_path):
    from passageway.protocol import Connector
    engine = two_source_engine(tmp_path)
    items = tmp_path / "items.json"
    engine.syncers["b"].connector = Connector("b", [sys.executable, "-m", "passageway.testing.fake_connector"],
                                              env={"FAKE_ITEMS": str(items)})
    engine.reconcile_once()
    assert engine.ready["b"] and engine.syncers["b"].index.counts()[0] == 1
    assert engine.syncers["b"].status.last_error is None


# ---- the embedder as seen by the server ------------------------------------------------------------

def test_a_relevance_gate_of_zero_is_a_setting_not_an_absence(tmp_path):
    items = tmp_path / "items.json"
    items.write_text(json.dumps([DOC]))
    cc = ConnectorConfig("notes", (sys.executable, "-m", "passageway.testing.fake_connector"), {"FAKE_ITEMS": str(items)}, {})
    engine = Engine(Config(password="s", connectors=[cc], data_dir=tmp_path, model_dir=tmp_path, min_similarity=0.0), HashEmbedder())
    assert engine.params.min_cos == 0.0


class FailingQueries(HashEmbedder):
    def embed_queries(self, texts):
        raise RuntimeError("rate limited")


def test_an_embedder_that_fails_on_queries_is_an_error_not_silence(tmp_path):
    items = tmp_path / "items.json"
    items.write_text(json.dumps([DOC]))
    cc = ConnectorConfig("notes", (sys.executable, "-m", "passageway.testing.fake_connector"), {"FAKE_ITEMS": str(items)}, {})
    engine = Engine(Config(password="s", connectors=[cc], data_dir=tmp_path, model_dir=tmp_path), FailingQueries())
    engine.sync_all_once()
    from passageway.embed import EmbedderError
    with pytest.raises(EmbedderError, match="rate limited"):
        engine.recall("proxmox swap")
    body = engine.health()
    assert body["status"] == "degraded" and "rate limited" in body["embedder"]["last_error"]
    assert body["embedder"]["name"] == "hash-test" and body["embedder"]["dim"] == 384


def test_the_query_is_embedded_once_per_recall_not_once_per_source(tmp_path):
    items = tmp_path / "items.json"
    items.write_text(json.dumps([DOC]))
    env = {"FAKE_ITEMS": str(items)}
    ccs = [ConnectorConfig(n, (sys.executable, "-m", "passageway.testing.fake_connector"), env, {}) for n in ("a", "b", "c")]
    counting = HashEmbedder()
    calls = []
    real = counting.embed_queries
    counting.embed_queries = lambda texts: calls.append(texts) or real(texts)
    engine = Engine(Config(password="s", connectors=ccs, data_dir=tmp_path, model_dir=tmp_path), counting)
    engine.sync_all_once()
    engine.recall("proxmox swap")
    assert len(calls) == 1


def test_open_health_hides_the_embedders_error_text(tmp_path):
    items = tmp_path / "items.json"
    items.write_text(json.dumps([DOC]))
    cc = ConnectorConfig("notes", (sys.executable, "-m", "passageway.testing.fake_connector"), {"FAKE_ITEMS": str(items)}, {})
    engine = Engine(Config(password="secret", connectors=[cc], data_dir=tmp_path, model_dir=tmp_path), FailingQueries())
    engine.sync_all_once()
    with pytest.raises(Exception):
        engine.recall("x")
    with TestClient(build_app(engine, background=False)) as c:
        open_body = c.get("/health").json()
        auth_body = c.get("/health", headers=OK).json()
    assert "rate limited" not in json.dumps(open_body) and open_body["embedder"]["last_error"]
    assert "rate limited" in auth_body["embedder"]["last_error"]


def test_the_error_page_does_not_show_what_a_failing_embedder_printed():
    from passageway.config import ConfigError
    from passageway.embed import EmbedderStartError
    from passageway.server import public_message
    private = EmbedderStartError("embedder 'default': connecting to https://gpu-box.internal:8443 as svc failed: 401",
                                 public="the embedder 'default' could not start; see the server log")
    assert "gpu-box" not in public_message(private) and "could not start" in public_message(private)
    assert public_message(ConfigError("PASSAGEWAY_LOGIN_PASSWORD is not set")) == "PASSAGEWAY_LOGIN_PASSWORD is not set"


async def test_mcp_status_tool_is_the_health_report_with_the_errors(tmp_path):
    engine = make_engine(tmp_path, [DOC], fail="list")
    async with Client(build_mcp(engine)) as c:
        status = json.loads((await c.call_tool("status", {})).data)
    assert status["status"] == "degraded" and "fake failure" in status["sources"]["notes"]["last_error"]
    assert status["version"] and status["embedder"]["name"] and status["sources"]["notes"]["items"] == 0  # list failed: nothing indexed


async def test_error_app_status_tool_names_the_problem():
    from passageway.server import build_error_mcp
    async with Client(build_error_mcp("bad config")) as c:
        status = json.loads((await c.call_tool("status", {})).data)
        tools = {t.name for t in await c.list_tools()}
    assert status == {"status": "error", "error": "bad config", "version": status["version"]} and tools == {"recall", "status"}
