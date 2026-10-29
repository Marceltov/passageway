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
    assert files_missing(bad, folder) == ["model.onnx", "tokenizer.json"] and not list((tmp_path / "models").glob("tiny.*"))


def test_a_truncated_download_is_refused_and_leaves_nothing(hub, tmp_path):
    base, preset, state, _ = hub
    state["fail_after"] = 100
    folder = tmp_path / "models" / "tiny"
    with pytest.raises(ModelError):
        download(preset, folder, base_url=base)
    assert files_missing(preset, folder) == ["model.onnx", "tokenizer.json"] and not list((tmp_path / "models").glob("tiny.*"))


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
    assert choose_device("auto", ["CPUExecutionProvider"], "darwin", "arm64") == ["CPUExecutionProvider"]
    assert choose_device("auto", ["CoreMLExecutionProvider", "CPUExecutionProvider"], "linux", "x86_64") == ["CPUExecutionProvider"]
    assert choose_device("coreml", ["CoreMLExecutionProvider", "CPUExecutionProvider"], "darwin", "arm64") == [
        "CoreMLExecutionProvider", "CPUExecutionProvider"]
    with pytest.raises(ModelError, match="coreml"):
        choose_device("coreml", ["CPUExecutionProvider"], "linux", "x86_64")


# ---- review findings ------------------------------------------------------------------------------

def test_download_never_deletes_what_else_is_in_the_folder(hub, tmp_path):
    base, preset, state, files = hub
    folder = tmp_path / "models" / "tiny"
    folder.mkdir(parents=True)
    (folder / "precious.txt").write_text("mine")
    (folder / "model.onnx").write_bytes(b"stale")
    download(preset, folder, base_url=base)
    assert (folder / "precious.txt").read_text() == "mine" and (folder / "model.onnx").read_bytes() == files["onnx/model.onnx"]


def test_a_symlinked_folder_works(hub, tmp_path):
    base, preset, _, _ = hub
    real = tmp_path / "elsewhere"
    real.mkdir()
    link = tmp_path / "models" / "tiny"
    link.parent.mkdir()
    link.symlink_to(real)
    download(preset, link, base_url=base)
    assert (real / "model.onnx").is_file() and verify(preset, link) == []


def test_two_downloads_of_one_preset_at_once_both_end_with_a_good_folder(hub, tmp_path):
    import threading
    base, preset, _, _ = hub
    folder = tmp_path / "models" / "tiny"
    errors = []

    def go():
        try:
            download(preset, folder, base_url=base)
        except Exception as e:  # noqa: BLE001
            errors.append(e)

    threads = [threading.Thread(target=go) for _ in range(3)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    assert errors == [] and files_missing(preset, folder) == [] and verify(preset, folder) == []
    assert not list((tmp_path / "models").glob("tiny.*"))  # no temp folders left


def test_an_unwritable_destination_is_a_model_error_not_a_traceback(hub, tmp_path):
    import os
    if os.geteuid() == 0:
        pytest.skip("root can write anywhere")
    base, preset, _, _ = hub
    parent = tmp_path / "ro"
    parent.mkdir()
    parent.chmod(0o500)
    try:
        with pytest.raises(ModelError, match="ro"):
            download(preset, parent / "tiny", base_url=base)
    finally:
        parent.chmod(0o700)


def test_auto_means_cpu_until_coreml_is_measured_as_faster_and_close_enough():
    assert choose_device("auto", ["CoreMLExecutionProvider", "CPUExecutionProvider"], "darwin", "arm64") == ["CPUExecutionProvider"]
    assert choose_device("coreml", ["CoreMLExecutionProvider", "CPUExecutionProvider"], "darwin", "arm64") == [
        "CoreMLExecutionProvider", "CPUExecutionProvider"]


def test_the_model_folder_rule_is_one_for_the_server_and_the_command(tmp_path, monkeypatch):
    from passageway.models import DEFAULT_PRESET, model_folder_for
    monkeypatch.delenv("PASSAGEWAY_MODEL_DIR", raising=False)
    assert model_folder_for(DEFAULT_PRESET, tmp_path, None) == tmp_path / "models" / "e5-small"  # where the server looks
    assert model_folder_for("jina-v2-base-de", tmp_path, None) == tmp_path / "models" / "jina-v2-base-de"
    assert model_folder_for(DEFAULT_PRESET, tmp_path, tmp_path / "own") == tmp_path / "own"
    monkeypatch.setenv("PASSAGEWAY_MODEL_DIR", str(tmp_path / "env"))
    assert model_folder_for(DEFAULT_PRESET, tmp_path, None) == tmp_path / "env"
    assert model_folder_for("jina-v2-base-de", tmp_path, None) == tmp_path / "models" / "jina-v2-base-de"


def test_the_hub_can_be_a_mirror_through_the_environment(hub, tmp_path, monkeypatch):
    base, preset, state, _ = hub
    monkeypatch.setenv("PASSAGEWAY_MODEL_HUB", base)
    download(preset, tmp_path / "models" / "tiny")  # no base_url given: the environment names the mirror
    assert state["requests"] and files_missing(preset, tmp_path / "models" / "tiny") == []
