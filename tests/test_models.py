"""Model presets, their download with checksums, and the device choice."""

import hashlib
import json
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from passageway.models import PRESETS, ModelError, Preset, choose_device, download, files_missing, verify

HEX = re.compile(r"[0-9a-f]{64}")


def test_every_preset_pins_a_revision_and_a_checksum_for_every_file():
    assert {"multilingual-e5-small", "multilingual-e5-base", "jina-v2-base-de"} <= set(PRESETS)
    labels = set()
    for name, preset in PRESETS.items():
        assert preset.name == name and re.fullmatch(r"[0-9a-f]{40}", preset.revision), name
        assert preset.files and all(HEX.fullmatch(sha) for _, sha in preset.files.values()), name
        assert preset.tokenizer in ("sentencepiece", "tokenizers") and preset.pooling == "mean" and preset.dim >= 1
        assert preset.label not in labels, "embedder names must differ between presets"
        labels.add(preset.label)
    assert PRESETS["multilingual-e5-small"].label == "multilingual-e5-small-int8"  # the name the index already records
    assert PRESETS["multilingual-e5-small"].min_similarity == 0.845


# ---- a fake huggingface.co ----------------------------------------------------------------------

@pytest.fixture
def hub(tmp_path):
    files = {"onnx/model.onnx": b"ONNX" * 1000, "tokenizer.json": b'{"version": "1.0"}'}
    state = {"fail_after": None, "requests": []}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            state["requests"].append(self.path)
            name = self.path.split("/resolve/")[-1].split("/", 1)[1] if "/resolve/" in self.path else ""
            if name not in files:
                self.send_response(404)
                self.end_headers()
                return
            body = files[name]
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body if state["fail_after"] is None else body[: state["fail_after"]])

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True).start()
    sha = {k: hashlib.sha256(v).hexdigest() for k, v in files.items()}
    preset = Preset("tiny", "org/tiny", "a" * 40, {"model.onnx": ("onnx/model.onnx", sha["onnx/model.onnx"]),
                                                     "tokenizer.json": ("tokenizer.json", sha["tokenizer.json"])},
                    "tokenizers", "", "", 512, "mean", 8, None, "tiny-test")
    yield f"http://127.0.0.1:{server.server_port}", preset, state, files
    server.shutdown()


def test_download_fetches_the_pinned_files_verifies_them_and_names_the_folder(hub, tmp_path):
    base, preset, state, files = hub
    folder = tmp_path / "models" / "tiny"
    download(preset, folder, base_url=base)
    assert (folder / "model.onnx").read_bytes() == files["onnx/model.onnx"]
    assert (folder / "tokenizer.json").read_bytes() == files["tokenizer.json"]
    assert all("/org/tiny/resolve/" + "a" * 40 + "/" in r for r in state["requests"])
    assert files_missing(preset, folder) == [] and verify(preset, folder) == []
    assert not list(tmp_path.glob("models/*.tmp*"))  # nothing left behind


def test_a_wrong_checksum_is_refused_and_leaves_nothing(hub, tmp_path):
    base, preset, state, files = hub
    bad = Preset(**{**preset.__dict__, "files": {"model.onnx": ("onnx/model.onnx", "0" * 64),
                                                 "tokenizer.json": preset.files["tokenizer.json"]}})
    folder = tmp_path / "models" / "tiny"
    with pytest.raises(ModelError, match="checksum"):
        download(bad, folder, base_url=base)
    assert not folder.exists() and not list((tmp_path / "models").glob("*"))


def test_a_truncated_download_is_refused_and_leaves_nothing(hub, tmp_path):
    base, preset, state, _ = hub
    state["fail_after"] = 100
    folder = tmp_path / "models" / "tiny"
    with pytest.raises(ModelError):
        download(preset, folder, base_url=base)
    assert not folder.exists()


def test_a_missing_file_on_the_hub_is_a_model_error(hub, tmp_path):
    base, preset, _, _ = hub
    bad = Preset(**{**preset.__dict__, "files": {"model.onnx": ("onnx/nope.onnx", "0" * 64)}})
    with pytest.raises(ModelError, match="404"):
        download(bad, tmp_path / "m", base_url=base)


def test_an_existing_complete_folder_is_not_downloaded_again(hub, tmp_path):
    base, preset, state, _ = hub
    folder = tmp_path / "models" / "tiny"
    download(preset, folder, base_url=base)
    before = len(state["requests"])
    download(preset, folder, base_url=base)
    assert len(state["requests"]) == before


def test_verify_names_the_file_that_is_wrong(hub, tmp_path):
    base, preset, _, _ = hub
    folder = tmp_path / "models" / "tiny"
    download(preset, folder, base_url=base)
    (folder / "tokenizer.json").write_text("tampered")
    assert verify(preset, folder) == ["tokenizer.json"]
    (folder / "model.onnx").unlink()
    assert files_missing(preset, folder) == ["model.onnx"]


# ---- the device ---------------------------------------------------------------------------------

def test_the_device_choice():
    assert choose_device("cpu", ["CoreMLExecutionProvider", "CPUExecutionProvider"], "darwin", "arm64") == ["CPUExecutionProvider"]
    assert choose_device("auto", ["CoreMLExecutionProvider", "CPUExecutionProvider"], "darwin", "arm64") == [
        "CoreMLExecutionProvider", "CPUExecutionProvider"]
    assert choose_device("auto", ["CPUExecutionProvider"], "darwin", "arm64") == ["CPUExecutionProvider"]
    assert choose_device("auto", ["CoreMLExecutionProvider", "CPUExecutionProvider"], "linux", "x86_64") == ["CPUExecutionProvider"]
    assert choose_device("coreml", ["CoreMLExecutionProvider", "CPUExecutionProvider"], "darwin", "arm64") == [
        "CoreMLExecutionProvider", "CPUExecutionProvider"]
    with pytest.raises(ModelError, match="coreml"):
        choose_device("coreml", ["CPUExecutionProvider"], "linux", "x86_64")
