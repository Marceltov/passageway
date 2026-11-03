import tomllib
from pathlib import Path

import pytest
from packaging.requirements import Requirement

ROOT = Path(__file__).resolve().parent.parent
ROOT_PROJECT = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
VERSION = ROOT_PROJECT["version"]
CONNECTORS = sorted(p.name for p in (ROOT / "connectors").iterdir() if (p / "pyproject.toml").is_file())
EMBEDDERS = sorted(p.name for p in (ROOT / "embedders").iterdir() if (p / "pyproject.toml").is_file())
EXTRAS = {**{name: f"passageway-connector-{name}" for name in CONNECTORS},
          **{name: f"passageway-embedder-{name}" for name in EMBEDDERS}}
PACKAGE_DIRS = [".", *(f"connectors/{n}" for n in CONNECTORS), *(f"embedders/{n}" for n in EMBEDDERS), "sdk"]


def project(directory):
    return tomllib.loads((ROOT / directory / "pyproject.toml").read_text())["project"]


@pytest.mark.parametrize("extra", sorted(EXTRAS))
def test_each_extra_pins_its_package_to_the_root_version(extra):
    assert ROOT_PROJECT["optional-dependencies"][extra] == [f"{EXTRAS[extra]}=={VERSION}"]


def test_all_is_every_other_extra():
    extras = ROOT_PROJECT["optional-dependencies"]
    assert sorted(extras["all"]) == sorted(pin for key, pins in extras.items() if key != "all" for pin in pins)


def test_no_connector_or_embedder_is_a_plain_dependency():
    assert not [d for d in ROOT_PROJECT["dependencies"] if d.startswith(("passageway-connector-", "passageway-embedder-"))]


@pytest.mark.parametrize("name", CONNECTORS)
def test_every_connector_requires_the_sdk_at_the_root_version_compatibly(name):
    sdk = [Requirement(d) for d in project(f"connectors/{name}")["dependencies"] if d.startswith("passageway-sdk")]
    assert len(sdk) == 1 and str(sdk[0].specifier) == f"~={VERSION}"


@pytest.mark.parametrize("directory", PACKAGE_DIRS)
def test_every_package_has_a_readme_that_exists(directory):
    assert project(directory).get("readme") == "README.md" and (ROOT / directory / "README.md").is_file()
