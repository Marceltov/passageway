import json
import sys

from starlette.testclient import TestClient

from passageway.config import load_config
from passageway.embed import HashEmbedder
from passageway.rank import RankParams
from passageway.server import Engine, build_app


def test_config_file_to_hook_answer(tmp_path):
    items = tmp_path / "items.json"
    items.write_text(json.dumps([
        {"id": "a", "title": "Certificates", "url": "http://x/a", "version": "1", "weight": 1.0,
         "path": ["Ops"], "sections": [{"heading": "Rotation", "text": "rotate the signing certificate every year"}]},
        {"id": "b", "title": "Lunch", "url": "http://x/b", "version": "1",
         "sections": [{"heading": None, "text": "pasta and salad on friday"}]}]))
    toml = tmp_path / "passageway.toml"
    toml.write_text(f'''
[[connector]]
name = "docs"
command = ["{sys.executable}", "-m", "passageway.testing.fake_connector"]
env = {{ FAKE_ITEMS = "{items}" }}
''')
    config = load_config({"PASSAGEWAY_LOGIN_PASSWORD": "pw", "PASSAGEWAY_CONFIG": str(toml),
                          "PASSAGEWAY_DATA_DIR": str(tmp_path / "data")})
    engine = Engine(config, HashEmbedder())
    engine.params = RankParams(min_cos=0.2)
    engine.sync_all_once()
    with TestClient(build_app(engine, background=False)) as c:
        answer = c.post("/recall", json={"prompt": "how do I rotate the signing certificate"},
                        headers={"Authorization": "Bearer pw"}).json()
        silent = c.post("/recall", json={"prompt": "what is the best pizza topping anywhere"},
                        headers={"Authorization": "Bearer pw"}).json()
        health = c.get("/health").json()
    assert answer["hits"] == ["a"] and "Ops › Rotation" in answer["context"]
    assert silent["hits"] == [] and health["status"] == "ok"
