import os

import pytest

from passageway import models
from tests.test_models import hub  # noqa: F401


def run(*args, env, capsys, monkeypatch):
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    code = models.main(list(args))
    out = capsys.readouterr()
    return code, out.out, out.err


def test_download_and_verify_through_the_command(hub, tmp_path, monkeypatch, capsys):
    base, preset, state, files = hub
    monkeypatch.setattr(models, "PRESETS", {"tiny": preset})
    env = {"PASSAGEWAY_DATA_DIR": str(tmp_path), "PASSAGEWAY_MODEL_HUB": base}
    code, out, err = run("download", "tiny", env=env, capsys=capsys, monkeypatch=monkeypatch)
    assert code == 0, err
    assert (tmp_path / "models" / "tiny" / "model.onnx").is_file() and "downloaded and verified" in out
    code, out, _ = run("download", "tiny", env=env, capsys=capsys, monkeypatch=monkeypatch)
    assert code == 0 and "already there" in out
    assert run("verify", "tiny", env=env, capsys=capsys, monkeypatch=monkeypatch)[0] == 0
    (tmp_path / "models" / "tiny" / "tokenizer.json").write_text("tampered")
    code, out, _ = run("verify", "tiny", env=env, capsys=capsys, monkeypatch=monkeypatch)
    assert code == 1 and "tokenizer.json" in out
    code, _, err = run("download", "nope", env=env, capsys=capsys, monkeypatch=monkeypatch)
    assert code == 2 and "nope" in err


def test_list_names_every_preset_and_the_default(capsys):
    assert models.main(["list"]) == 0
    out = capsys.readouterr().out
    assert all(name in out for name in models.PRESETS) and "(default)" in out and "not measured" in out


def test_the_command_looks_where_the_server_looks_for_the_default_preset(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("PASSAGEWAY_MODEL_DIR", raising=False)
    monkeypatch.setenv("PASSAGEWAY_DATA_DIR", str(tmp_path))
    code = models.main(["verify"])
    out = capsys.readouterr().out
    assert code == 1 and str(tmp_path / "models" / "e5-small") in out
