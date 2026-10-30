import io
import sys
import os
import stat

import pytest

from passageway.config import ConfigError, load_config
from passageway.init import main


def test_init_creates_the_folder_a_password_and_a_sample_and_is_safe_to_rerun(tmp_path):
    config = tmp_path / "cfg" / "passageway.toml"
    out = io.StringIO()
    assert main([], env={"PASSAGEWAY_CONFIG": str(config)}, stdout=out) == 0
    password = config.parent / "password"
    assert len(password.read_text().strip()) == 48 and stat.S_IMODE(password.stat().st_mode) == 0o600
    assert "[[connector]]" in config.read_text() and "PASSAGEWAY_LOGIN_PASSWORD_FILE" in out.getvalue()
    first = password.read_text()
    config.write_text("[[connector]]\nname = \"mine\"\ncommand = [\"x\"]\n")
    assert main([], env={"PASSAGEWAY_CONFIG": str(config)}, stdout=io.StringIO()) == 0
    assert password.read_text() == first and "mine" in config.read_text()  # nothing overwritten


def test_the_server_reads_the_password_from_the_file(tmp_path):
    config = tmp_path / "passageway.toml"
    config.write_text('[[connector]]\nname = "n"\ncommand = ["x"]\n')
    (tmp_path / "password").write_text("s3cret\n")
    cfg = load_config({"PASSAGEWAY_CONFIG": str(config), "PASSAGEWAY_LOGIN_PASSWORD_FILE": str(tmp_path / "password"),
                       "PASSAGEWAY_DATA_DIR": str(tmp_path)})
    assert cfg.password == "s3cret"
    cfg = load_config({"PASSAGEWAY_CONFIG": str(config), "PASSAGEWAY_LOGIN_PASSWORD": "direct",
                       "PASSAGEWAY_LOGIN_PASSWORD_FILE": str(tmp_path / "password"), "PASSAGEWAY_DATA_DIR": str(tmp_path)})
    assert cfg.password == "direct"  # the variable wins
    with pytest.raises(ConfigError, match="PASSAGEWAY_LOGIN_PASSWORD_FILE"):
        load_config({"PASSAGEWAY_CONFIG": str(config), "PASSAGEWAY_LOGIN_PASSWORD_FILE": str(tmp_path / "nope"),
                     "PASSAGEWAY_DATA_DIR": str(tmp_path)})


def test_init_fixes_the_mode_of_a_kept_password_and_refuses_an_empty_one(tmp_path):
    config = tmp_path / "passageway.toml"
    config.write_text('[[connector]]\nname = "n"\ncommand = ["x"]\n')
    password = tmp_path / "password"
    password.write_text("kept\n")
    password.chmod(0o644)
    assert main([], env={"PASSAGEWAY_CONFIG": str(config)}, stdout=io.StringIO()) == 0
    assert stat.S_IMODE(password.stat().st_mode) == 0o600 and password.read_text() == "kept\n"
    password.write_text("")
    with pytest.raises(ConfigError, match="empty"):
        load_config({"PASSAGEWAY_CONFIG": str(config), "PASSAGEWAY_LOGIN_PASSWORD_FILE": str(password), "PASSAGEWAY_DATA_DIR": str(tmp_path)})
    assert main(["--help"], env={"PASSAGEWAY_CONFIG": str(config)}, stdout=io.StringIO()) == 0
    assert main(["--bogus"], env={"PASSAGEWAY_CONFIG": str(config)}, stdout=io.StringIO()) == 2


@pytest.mark.parametrize("arg,code", [("--help", 0), ("-h", 0), ("serve", 2)])
def test_passageway_help_prints_the_usage_instead_of_serving(arg, code, capsys, tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    import passageway.server as server
    sys.argv = ["passageway", arg]
    with pytest.raises(SystemExit) as stop:
        server.main()
    out = capsys.readouterr()
    assert stop.value.code == code
    assert "PASSAGEWAY_LOGIN_PASSWORD_FILE" in out.out + out.err and "init" in out.out + out.err


def test_init_for_an_instance_creates_its_own_folder(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    out = io.StringIO()
    assert main([], env={"PASSAGEWAY_INSTANCE": "work"}, stdout=out) == 0
    assert (tmp_path / ".config" / "passageway-work" / "password").is_file()
    assert "PASSAGEWAY_PORT=" in out.getvalue() and "passageway --instance work" in out.getvalue()
    assert main([], env={"PASSAGEWAY_INSTANCE": "Bad Name"}, stdout=io.StringIO()) == 2
