import io
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
