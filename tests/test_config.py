import pytest

from passageway.config import ConfigError, load_config

TOML = '''
[embedder]
min_similarity = 0.7

[[connector]]
name = "notes"
command = ["python", "-m", "x"]
env = { URL = "http://t" }
secrets = { TOKEN = "env:NOTES_TOKEN" }
timeout = 60
'''


def env_for(tmp_path, toml=TOML, **extra):
    path = tmp_path / "passageway.toml"
    path.write_text(toml)
    return {"PASSAGEWAY_LOGIN_PASSWORD": "pw", "PASSAGEWAY_CONFIG": str(path), "NOTES_TOKEN": "tok", **extra}


def test_loads_connectors_with_resolved_secrets(tmp_path):
    cfg = load_config(env_for(tmp_path))
    c = cfg.connectors[0]
    assert (c.name, c.command, c.env, c.secrets, c.timeout) == (
        "notes", ("python", "-m", "x"), {"URL": "http://t"}, {"TOKEN": "tok"}, 60.0)
    assert cfg.min_similarity == 0.7 and cfg.host == "127.0.0.1" and cfg.port == 8082


def test_password_is_required(tmp_path):
    env = env_for(tmp_path)
    del env["PASSAGEWAY_LOGIN_PASSWORD"]
    with pytest.raises(ConfigError, match="PASSAGEWAY_LOGIN_PASSWORD"):
        load_config(env)


def test_missing_config_file_and_empty_connector_list(tmp_path):
    with pytest.raises(ConfigError, match="passageway.toml"):
        load_config({"PASSAGEWAY_LOGIN_PASSWORD": "pw", "PASSAGEWAY_CONFIG": str(tmp_path / "none.toml")})
    with pytest.raises(ConfigError, match="no connectors"):
        load_config(env_for(tmp_path, "[embedder]\nmin_similarity = 0.5\n"))


def test_secret_reference_to_a_missing_variable_names_connector_and_variable(tmp_path):
    env = env_for(tmp_path)
    del env["NOTES_TOKEN"]
    with pytest.raises(ConfigError, match=r"notes.*NOTES_TOKEN"):
        load_config(env)


def test_secrets_must_be_references(tmp_path):
    bad = TOML.replace('"env:NOTES_TOKEN"', '"plaintext"')
    with pytest.raises(ConfigError, match="env:"):
        load_config(env_for(tmp_path, bad))


@pytest.mark.parametrize("name", ["../x", "a/b", "A", "", "-x", "a b"])
def test_connector_names_are_safe_file_names(tmp_path, name):
    with pytest.raises(ConfigError, match="name"):
        load_config(env_for(tmp_path, TOML.replace('name = "notes"', f'name = "{name}"')))


def test_duplicate_names_and_bad_command(tmp_path):
    with pytest.raises(ConfigError, match="duplicate"):
        load_config(env_for(tmp_path, TOML + '\n[[connector]]\nname = "notes"\ncommand = ["x"]\n'))
    with pytest.raises(ConfigError, match="command"):
        load_config(env_for(tmp_path, TOML.replace('command = ["python", "-m", "x"]', 'command = "python"')))


def test_base_url_must_be_a_valid_issuer(tmp_path):
    with pytest.raises(ConfigError, match="PASSAGEWAY_BASE_URL"):
        load_config(env_for(tmp_path, PASSAGEWAY_BASE_URL="http://example.com/path?x=1"))
    assert load_config(env_for(tmp_path, PASSAGEWAY_BASE_URL="https://r.example.com/")).base_url == "https://r.example.com"


def test_integers_and_text_overrides(tmp_path):
    cfg = load_config(env_for(tmp_path, PASSAGEWAY_PORT="9000", PASSAGEWAY_TOOL_DESCRIPTION="Finds things.",
                              PASSAGEWAY_INSTRUCTIONS="Use me."))
    assert (cfg.port, cfg.tool_description, cfg.instructions) == (9000, "Finds things.", "Use me.")
    with pytest.raises(ConfigError, match="PASSAGEWAY_PORT"):
        load_config(env_for(tmp_path, PASSAGEWAY_PORT="x"))


def test_protocol_limits_and_guard_are_configurable_per_connector(tmp_path):
    toml = TOML.replace("timeout = 60", "timeout = 60\nmax_line_bytes = 1000\nmax_output_bytes = 5000\nmax_delete_fraction = 0.5")
    c = load_config(env_for(tmp_path, toml)).connectors[0]
    assert (c.max_line_bytes, c.max_output_bytes, c.max_delete_fraction) == (1000, 5000, 0.5)
    d = load_config(env_for(tmp_path)).connectors[0]
    assert (d.max_line_bytes, d.max_output_bytes, d.max_delete_fraction) == (4 * 1024 * 1024, 64 * 1024 * 1024, 0.3)


@pytest.mark.parametrize("line", ['timeout = "abc"', "max_line_bytes = -1", 'max_output_bytes = "x"',
                                  "max_delete_fraction = 2", "max_delete_fraction = true"])
def test_bad_numbers_are_config_errors(tmp_path, line):
    with pytest.raises(ConfigError, match="notes"):
        load_config(env_for(tmp_path, TOML.replace("timeout = 60", line)))


def test_a_single_connector_table_is_a_config_error_not_a_traceback(tmp_path):
    with pytest.raises(ConfigError, match=r"\[\[connector\]\]"):
        load_config(env_for(tmp_path, TOML.replace("[[connector]]", "[connector]")))
