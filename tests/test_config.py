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


def test_the_password_is_optional_for_commands_that_do_not_serve(tmp_path):
    path = tmp_path / "passageway.toml"
    path.write_text('[[connector]]\nname = "n"\ncommand = ["x"]\n')
    config = load_config({"PASSAGEWAY_CONFIG": str(path), "PASSAGEWAY_DATA_DIR": str(tmp_path)}, require_password=False)
    assert config.password == "" and config.connectors[0].name == "n"
    with pytest.raises(ConfigError, match="PASSAGEWAY_LOGIN_PASSWORD"):
        load_config({"PASSAGEWAY_CONFIG": str(path), "PASSAGEWAY_DATA_DIR": str(tmp_path)})


# ---- embedders ------------------------------------------------------------------------------------

def embedder_env(tmp_path, embedder_toml, **extra):
    return env_for(tmp_path, embedder_toml + '\n[[connector]]\nname = "n"\ncommand = ["x"]\n', **extra)


def test_without_an_embedder_section_the_onnx_model_stays_the_default(tmp_path):
    cfg = load_config(env_for(tmp_path, '[[connector]]\nname = "n"\ncommand = ["x"]\n'))
    assert cfg.embedder.kind == "onnx" and cfg.embedder.min_similarity is None and cfg.embedders == {}


def test_min_similarity_alone_keeps_the_onnx_kind(tmp_path):
    cfg = load_config(env_for(tmp_path))
    assert cfg.embedder.kind == "onnx" and cfg.embedder.min_similarity == 0.7 == cfg.min_similarity


def test_a_command_embedder_is_configured_with_command_env_secrets_and_limits(tmp_path):
    cfg = load_config(embedder_env(tmp_path, '''
[embedder]
kind = "command"
command = ["/usr/bin/python3", "-m", "my_embedder"]
env = { MODEL = "bge" }
secrets = { API_KEY = "env:EMBED_KEY" }
min_similarity = 0.8
batch_size = 16
timeout = 30
''', EMBED_KEY="sekret"))
    e = cfg.embedder
    assert (e.kind, e.command, e.env, e.secrets, e.min_similarity, e.batch_size, e.timeout) == (
        "command", ("/usr/bin/python3", "-m", "my_embedder"), {"MODEL": "bge"}, {"API_KEY": "sekret"}, 0.8, 16, 30.0)
    assert cfg.min_similarity == 0.8  # the engine reads the gate from here


def test_a_command_embedder_has_sensible_defaults(tmp_path):
    e = load_config(embedder_env(tmp_path, '[embedder]\nkind = "command"\ncommand = ["x"]\n')).embedder
    assert (e.batch_size, e.timeout, e.min_similarity, e.env, e.secrets) == (32, 60.0, None, {}, {})


def test_candidates_for_compare_are_named_tables(tmp_path):
    cfg = load_config(embedder_env(tmp_path, '''
[embedders.e5]
kind = "onnx"
model_dir = "/models/e5"

[embedders.bge]
kind = "command"
command = ["x", "--model", "bge"]
min_similarity = 0.8
'''))
    assert set(cfg.embedders) == {"e5", "bge"}
    assert str(cfg.embedders["e5"].model_dir) == "/models/e5" and cfg.embedders["bge"].command == ("x", "--model", "bge")
    assert cfg.embedder.kind == "onnx"  # the server's own embedder is unaffected


@pytest.mark.parametrize("toml,message", [
    ('[embedder]\nkind = "magic"', "kind"),
    ('[embedder]\nkind = "command"', "command"),
    ('[embedder]\nkind = "command"\ncommand = []', "command"),
    ('[embedder]\nkind = "command"\ncommand = ["x", 3]', "command"),
    ('[embedder]\nkind = "onnx"\ncommand = ["x"]', "command"),
    ('[embedder]\nmin_similiarity = 0.8', "min_similiarity"),
    ('[embedder]\nmin_similarity = 1.5', "min_similarity"),
    ('[embedder]\nmin_similarity = "high"', "min_similarity"),
    ('[embedder]\nkind = "command"\ncommand = ["x"]\nbatch_size = 0', "batch_size"),
    ('[embedder]\nkind = "command"\ncommand = ["x"]\nbatch_size = 2000', "batch_size"),
    ('[embedder]\nkind = "command"\ncommand = ["x"]\ntimeout = 0', "timeout"),
    ('[embedder]\nkind = "command"\ncommand = ["x"]\nsecrets = { K = "literal" }', "secrets"),
    ('[embedder]\nkind = "command"\ncommand = ["x"]\nsecrets = { K = "env:NOT_SET_ANYWHERE" }', "NOT_SET_ANYWHERE"),
    ('[embedders."Bad Name"]\nkind = "onnx"', "name"),
    ('[embedders.default]\nkind = "onnx"', "default"),
    ('embedders = "nope"', "embedders"),
    ('[embedders.x]\nkind = "command"', "command"),
])
def test_a_bad_embedder_section_is_refused_with_a_message_that_names_the_problem(tmp_path, toml, message):
    with pytest.raises(ConfigError, match=message):
        load_config(embedder_env(tmp_path, toml))


@pytest.mark.parametrize("value", ["nan", "inf", "1e12"])
def test_an_embedder_timeout_must_be_a_usable_number_of_seconds(tmp_path, value):
    with pytest.raises(ConfigError, match="timeout"):
        load_config(embedder_env(tmp_path, f'[embedder]\nkind = "command"\ncommand = ["x"]\ntimeout = {value}'))


@pytest.mark.parametrize("value", ["nan", "1e12"])
def test_a_connector_timeout_must_be_a_usable_number_of_seconds(tmp_path, value):
    with pytest.raises(ConfigError, match="timeout"):
        load_config(env_for(tmp_path, f'[[connector]]\nname = "n"\ncommand = ["x"]\ntimeout = {value}\n'))


# ---- presets ----------------------------------------------------------------------------------------

def test_the_onnx_embedder_takes_a_preset_a_device_and_the_download_switch(tmp_path):
    e = load_config(embedder_env(tmp_path, '[embedder]\nmodel = "jina-v2-base-de"\ndevice = "cpu"\ndownload = false\n')).embedder
    assert (e.kind, e.model, e.device, e.download) == ("onnx", "jina-v2-base-de", "cpu", False)
    e = load_config(embedder_env(tmp_path, '[embedder]\nmin_similarity = 0.8\n')).embedder
    assert (e.model, e.device, e.download) == ("multilingual-e5-small", "auto", True)


@pytest.mark.parametrize("toml,message", [
    ('[embedder]\nmodel = "gpt-9"', "model"),
    ('[embedder]\ndevice = "gpu"', "device"),
    ('[embedder]\ndownload = "yes"', "download"),
    ('[embedder]\nkind = "command"\ncommand = ["x"]\nmodel = "jina-v2-base-de"', "model"),
])
def test_bad_preset_settings_are_refused(tmp_path, toml, message):
    with pytest.raises(ConfigError, match=message):
        load_config(embedder_env(tmp_path, toml))


def test_a_model_that_is_not_a_string_is_a_config_error(tmp_path):
    with pytest.raises(ConfigError, match="model"):
        load_config(embedder_env(tmp_path, '[embedder]\nmodel = ["x"]'))
