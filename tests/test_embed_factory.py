import logging
import sys

import pytest

from passageway.config import Config, ConfigError, EmbedderConfig
from passageway.embed import HashEmbedder, build_embedder

FAKE = (sys.executable, "-m", "passageway.testing.fake_embedder")


def conf(tmp_path, model_dir=None):
    return Config(password="", connectors=[], data_dir=tmp_path, model_dir=model_dir or tmp_path)


def test_a_command_embedder_is_built_from_its_configuration(tmp_path):
    cfg = EmbedderConfig("command", FAKE, {"FAKE_EMBED_NAME": "from-config", "FAKE_EMBED_DIM": "16"}, {}, 0.8, 8, 30.0)
    embedder = build_embedder(cfg, conf(tmp_path))
    try:
        assert (embedder.name, embedder.dim) == ("from-config", 16)
        assert embedder._batch == 8 and embedder._timeout == 30.0
    finally:
        embedder.close()


def test_a_command_that_cannot_start_is_a_config_error_naming_the_cause(tmp_path):
    cfg = EmbedderConfig("command", ("/no/such/program",), min_similarity=0.8)
    with pytest.raises(ConfigError, match="/no/such/program"):
        build_embedder(cfg, conf(tmp_path))
    cfg = EmbedderConfig("command", FAKE, {"FAKE_EMBED_FAIL": "start"}, {}, 0.8)
    with pytest.raises(ConfigError, match="fake start failure"):
        build_embedder(cfg, conf(tmp_path))


def test_without_min_similarity_a_command_embedder_gets_a_warning(tmp_path, caplog):
    with caplog.at_level(logging.WARNING, logger="passageway.embed"):
        build_embedder(EmbedderConfig("command", FAKE), conf(tmp_path)).close()
    assert any("min_similarity" in r.getMessage() and "--sweep" in r.getMessage() for r in caplog.records)
    caplog.clear()
    with caplog.at_level(logging.WARNING, logger="passageway.embed"):
        build_embedder(EmbedderConfig("command", FAKE, min_similarity=0.8), conf(tmp_path)).close()
    assert not caplog.records


def test_the_onnx_model_is_looked_for_in_the_configured_folder_else_the_default_one(tmp_path):
    with pytest.raises(ConfigError, match=str(tmp_path / "default-dir")):
        build_embedder(EmbedderConfig("onnx", download=False), conf(tmp_path, tmp_path / "default-dir"))
    with pytest.raises(ConfigError, match=str(tmp_path / "own-dir")):
        build_embedder(EmbedderConfig("onnx", model_dir=tmp_path / "own-dir", download=False), conf(tmp_path, tmp_path / "default-dir"))


def test_a_label_names_the_embedder_in_errors(tmp_path):
    with pytest.raises(ConfigError, match="bge"):
        build_embedder(EmbedderConfig("command", FAKE, {"FAKE_EMBED_FAIL": "start"}, {}, 0.8), conf(tmp_path), label="bge")
    assert isinstance(HashEmbedder(), object)
