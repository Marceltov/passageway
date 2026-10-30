"""The command line: --instance on every command, instances that must exist, and the version."""
import importlib.metadata
import os

import pytest

from passageway import server
from passageway.config import ConfigError, instance_problem, take_instance_argument


@pytest.mark.parametrize("argv,rest,name", [
    (["--instance", "apple"], [], "apple"),
    (["--instance=apple", "eval", "cases.toml"], ["eval", "cases.toml"], "apple"),
    (["eval", "cases.toml", "--instance", "apple", "--sweep", "0.8"], ["eval", "cases.toml", "--sweep", "0.8"], "apple"),
    (["init"], ["init"], None),
])
def test_the_instance_argument_is_taken_from_anywhere_in_the_command(argv, rest, name):
    assert take_instance_argument(argv) == (rest, name)


@pytest.mark.parametrize("argv", [["--instance"], ["--instance", "--sweep"], ["--instance", "Bad Name"]])
def test_a_missing_or_malformed_instance_argument_is_an_error(argv):
    with pytest.raises(ConfigError, match="--instance"):
        take_instance_argument(argv)


def _home(tmp_path, *instances, default=False):
    for name in instances:
        (tmp_path / ".config" / f"passageway-{name}").mkdir(parents=True)
        (tmp_path / ".config" / f"passageway-{name}" / "passageway.toml").write_text("")
    if default:
        (tmp_path / ".config" / "passageway").mkdir(parents=True)
        (tmp_path / ".config" / "passageway" / "passageway.toml").write_text("")


def test_an_unknown_instance_names_the_ones_that_exist(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    _home(tmp_path, "apple", "personal")
    problem = instance_problem({"PASSAGEWAY_INSTANCE": "aple"})
    assert "aple" in problem and "apple, personal" in problem and "passageway --instance aple init" in problem
    assert instance_problem({"PASSAGEWAY_INSTANCE": "apple"}) is None


def test_no_instance_and_no_default_config_says_which_instances_exist(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    _home(tmp_path, "apple", "personal")
    assert "--instance" in instance_problem({}) and "apple, personal" in instance_problem({})
    assert instance_problem({"PASSAGEWAY_CONFIG": str(tmp_path / "x.toml")}) is None  # an explicit config file wins


def test_a_machine_with_only_the_default_or_nothing_is_fine(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    assert instance_problem({}) is None  # nothing at all: load_config says what is missing, as before
    _home(tmp_path, "apple", default=True)
    assert instance_problem({}) is None


def test_the_argument_wins_over_the_variable_and_reaches_the_command(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("PASSAGEWAY_INSTANCE", "personal")
    _home(tmp_path, "apple", "personal")
    seen = {}
    import passageway.eval.cli as cli
    monkeypatch.setattr(cli, "main", lambda argv: seen.update(argv=argv, instance=os.environ["PASSAGEWAY_INSTANCE"]) or 0)
    monkeypatch.setattr("sys.argv", ["passageway", "--instance", "apple", "eval", "cases.toml"])
    with pytest.raises(SystemExit) as stop:
        server.main()
    assert stop.value.code == 0 and seen == {"argv": ["cases.toml"], "instance": "apple"}


def test_an_unknown_instance_stops_the_command_before_it_starts(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("PASSAGEWAY_INSTANCE", raising=False)
    _home(tmp_path, "apple")
    monkeypatch.setattr("sys.argv", ["passageway", "--instance", "aple"])
    with pytest.raises(SystemExit) as stop:
        server.main()
    assert stop.value.code == 2 and "apple" in capsys.readouterr().err


def test_init_creates_a_named_instance_from_the_argument(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("PASSAGEWAY_INSTANCE", raising=False)
    monkeypatch.setattr("sys.argv", ["passageway", "init", "--instance", "work"])
    with pytest.raises(SystemExit) as stop:
        server.main()
    assert stop.value.code == 0 and (tmp_path / ".config" / "passageway-work" / "password").exists()
    assert "--instance work" in capsys.readouterr().out


def test_the_usage_names_the_instance_argument():
    assert "--instance NAME" in server.USAGE


def test_the_version_comes_from_the_installed_package_unless_app_version_says_otherwise(monkeypatch):
    monkeypatch.delenv("APP_VERSION", raising=False)
    assert server.version() == importlib.metadata.version("passageway") != "dev"
    monkeypatch.setenv("APP_VERSION", "9.9.9")
    assert server.version() == "9.9.9"
