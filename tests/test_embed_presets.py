"""The built-in embedder with presets: tokenisation per kind, the model folder, the download at start, the threshold."""

import json
import logging
import sys

import numpy as np
import pytest

from passageway.config import Config, ConfigError, EmbedderConfig
from passageway.embed import OnnxEmbedder, build_embedder, model_folder
from passageway.models import PRESETS, Preset


@pytest.fixture
def word_tokenizer(tmp_path):
    from tokenizers import Tokenizer
    from tokenizers.models import WordLevel
    from tokenizers.pre_tokenizers import Whitespace
    from tokenizers.processors import TemplateProcessing
    vocab = {"[PAD]": 0, "[CLS]": 1, "[SEP]": 2, "[UNK]": 3, "wie": 4, "geht": 5, "es": 6}
    tok = Tokenizer(WordLevel(vocab, unk_token="[UNK]"))
    tok.pre_tokenizer = Whitespace()
    tok.post_processor = TemplateProcessing(single="[CLS] $A [SEP]", special_tokens=[("[CLS]", 1), ("[SEP]", 2)])
    path = tmp_path / "tokenizer.json"
    tok.save(str(path))
    return path


def test_the_tokenizers_kind_encodes_with_special_tokens_truncation_and_the_pad_id(tmp_path, word_tokenizer):
    preset = Preset("t", "x/y", "a" * 40, {}, "tokenizers", "", "", 5, "mean", 8, None, "t")
    enc = OnnxEmbedder._tokenizer(preset, tmp_path)
    ids, mask = enc(["wie geht es", "wie", "wie geht es wie geht es"])
    assert ids.tolist()[0] == [1, 4, 5, 6, 2] and mask.tolist()[0] == [1, 1, 1, 1, 1]
    assert ids.tolist()[1] == [1, 4, 2, 0, 0] and mask.tolist()[1] == [1, 1, 1, 0, 0]  # padded with [PAD]
    assert len(ids[2]) == 5 and mask.tolist()[2] == [1, 1, 1, 1, 1]  # truncated to max_tokens


def test_the_sentencepiece_kind_keeps_the_xlm_r_ids(tmp_path):
    preset = PRESETS["multilingual-e5-small"]
    folder = model_folder(EmbedderConfig(), Config(password="", connectors=[], data_dir=tmp_path, model_dir=tmp_path / "e5"))
    assert folder == tmp_path / "e5"  # the default preset keeps PASSAGEWAY_MODEL_DIR
    assert model_folder(EmbedderConfig(model="jina-v2-base-de"), Config(password="", connectors=[], data_dir=tmp_path,
                                                                        model_dir=tmp_path / "e5")) == tmp_path / "models" / "jina-v2-base-de"
    assert model_folder(EmbedderConfig(model="jina-v2-base-de", model_dir=tmp_path / "own"),
                        Config(password="", connectors=[], data_dir=tmp_path, model_dir=tmp_path / "e5")) == tmp_path / "own"
    assert preset.tokenizer == "sentencepiece"


def test_prefixes_come_from_the_preset():
    class Fake(OnnxEmbedder):
        def __init__(self, preset):
            self.preset = preset
            self.seen = []

        def _embed(self, texts):
            self.seen.append(texts)
            return np.zeros((len(texts), 2), dtype=np.float32)

    e5 = Fake(PRESETS["multilingual-e5-small"])
    e5.embed_queries(["q"]); e5.embed_passages(["p"])
    assert e5.seen == [["query: q"], ["passage: p"]]
    jina = Fake(PRESETS["jina-v2-base-de"])
    jina.embed_queries(["q"]); jina.embed_passages(["p"])
    assert jina.seen == [["q"], ["p"]]


def test_a_missing_model_is_downloaded_at_start_when_allowed_and_an_error_otherwise(tmp_path, monkeypatch):
    fetched = []
    monkeypatch.setattr("passageway.embed.download", lambda preset, folder, **kw: fetched.append((preset.name, folder)) or True)
    monkeypatch.setattr("passageway.embed.files_missing", lambda preset, folder: [] if fetched else ["model.onnx"])
    monkeypatch.setattr("passageway.embed.verify", lambda preset, folder: [])
    monkeypatch.setattr("passageway.embed.OnnxEmbedder", lambda folder, preset, device: ("loaded", preset.name, device))
    config = Config(password="", connectors=[], data_dir=tmp_path, model_dir=tmp_path / "e5")
    assert build_embedder(EmbedderConfig(model="jina-v2-base-de", device="cpu"), config) == ("loaded", "jina-v2-base-de", "cpu")
    assert fetched == [("jina-v2-base-de", tmp_path / "models" / "jina-v2-base-de")]
    fetched.clear()
    with pytest.raises(ConfigError, match="passageway model download jina-v2-base-de"):
        build_embedder(EmbedderConfig(model="jina-v2-base-de", download=False), config)


def test_a_model_with_a_wrong_checksum_is_refused_unless_it_may_be_fetched_again(tmp_path, monkeypatch):
    monkeypatch.setattr("passageway.embed.files_missing", lambda preset, folder: [])
    monkeypatch.setattr("passageway.embed.verify", lambda preset, folder: ["model.onnx"])
    monkeypatch.setattr("passageway.embed.OnnxEmbedder", lambda folder, preset, device: "loaded")
    fetched = []
    monkeypatch.setattr("passageway.embed.download", lambda preset, folder, **kw: fetched.append(folder) or True)
    config = Config(password="", connectors=[], data_dir=tmp_path, model_dir=tmp_path / "e5")
    with pytest.raises(ConfigError, match="checksum"):
        build_embedder(EmbedderConfig(download=False), config)
    assert build_embedder(EmbedderConfig(), config) == "loaded" and fetched == [tmp_path / "e5"]


def test_the_engine_takes_the_relevance_gate_from_the_model_unless_configured(tmp_path):
    from passageway.embed import HashEmbedder
    from passageway.server import Engine
    gated = HashEmbedder()
    gated.min_similarity = 0.5
    assert Engine(Config(password="", connectors=[], data_dir=tmp_path, model_dir=tmp_path), gated).params.min_cos == 0.5
    assert Engine(Config(password="", connectors=[], data_dir=tmp_path, model_dir=tmp_path, min_similarity=0.7), gated).params.min_cos == 0.7


def test_a_preset_without_a_measured_gate_warns(tmp_path, caplog, monkeypatch):
    monkeypatch.setattr("passageway.embed.files_missing", lambda preset, folder: [])
    monkeypatch.setattr("passageway.embed.verify", lambda preset, folder: [])
    monkeypatch.setattr("passageway.embed.OnnxEmbedder", lambda folder, preset, device: type("E", (), {"min_similarity": None})())
    config = Config(password="", connectors=[], data_dir=tmp_path, model_dir=tmp_path / "e5")
    with caplog.at_level(logging.WARNING, logger="passageway.embed"):
        build_embedder(EmbedderConfig(model="multilingual-e5-base"), config)
    assert any("min_similarity" in r.getMessage() for r in caplog.records)


def test_a_download_error_of_any_kind_is_a_config_error(tmp_path, monkeypatch):
    from passageway.models import ModelError
    monkeypatch.setattr("passageway.embed.files_missing", lambda preset, folder: ["model.onnx"])
    monkeypatch.setattr("passageway.embed.verify", lambda preset, folder: [])

    def boom(preset, folder, **kw):
        raise ModelError("disk full")
    monkeypatch.setattr("passageway.embed.download", boom)
    with pytest.raises(ConfigError, match="disk full"):
        build_embedder(EmbedderConfig(), Config(password="", connectors=[], data_dir=tmp_path, model_dir=tmp_path / "e5"))


def test_the_warning_for_an_unmeasured_gate_says_what_it_means(tmp_path, caplog, monkeypatch):
    monkeypatch.setattr("passageway.embed.files_missing", lambda preset, folder: [])
    monkeypatch.setattr("passageway.embed.verify", lambda preset, folder: [])
    monkeypatch.setattr("passageway.embed.OnnxEmbedder", lambda folder, preset, device: type("E", (), {"min_similarity": None})())
    with caplog.at_level(logging.WARNING, logger="passageway.embed"):
        build_embedder(EmbedderConfig(model="jina-v2-base-de"), Config(password="", connectors=[], data_dir=tmp_path, model_dir=tmp_path / "e5"))
    message = next(r.getMessage() for r in caplog.records)
    assert "almost nothing" in message and "min_similarity" in message and "--sweep" in message
