"""The agent entry points: the plugin skill, the root SKILL.md and the llms files stay true to the code and the docs."""

import glob
import json
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
GENERAL = ROOT / "skills" / "passageway" / "SKILL.md"
CONNECTOR = ROOT / "skills" / "create-passageway-connector" / "SKILL.md"


def frontmatter(path: Path) -> dict:
    text = path.read_text()
    assert text.startswith("---\n"), f"{path} must start with YAML frontmatter"
    return yaml.safe_load(text.split("---\n", 2)[1])


def project_version() -> str:
    return tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]


def python_block(path: Path) -> str:
    blocks = re.findall(r"```python\n(.*?)```", path.read_text(), re.S)
    assert blocks, f"{path} has no python block"
    return blocks[0]


# ---- plugin and skills --------------------------------------------------------------------------

def test_the_plugin_manifests_are_valid_and_versioned_with_the_project():
    plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
    assert plugin["name"] == "passageway" and plugin["version"] == project_version()
    assert plugin["license"] == "AGPL-3.0-or-later" and plugin["repository"].endswith("Marceltov/passageway")
    market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())
    assert market["plugins"][0]["name"] == "passageway" and market["plugins"][0]["source"] == "./"


def test_both_skills_have_frontmatter_and_their_names_match_their_folders():
    for path in (GENERAL, CONNECTOR):
        meta = frontmatter(path)
        assert meta["name"] == path.parent.name, path
        assert len(meta["description"]) > 40, f"{path}: the description is what makes the skill findable"
    assert frontmatter(GENERAL)["version"] == project_version()
    assert frontmatter(GENERAL)["homepage"] == "https://passageway.marceltov.de/"


def test_the_connector_skill_uses_the_guides_example_and_it_passes_the_contract(tmp_path):
    from passageway.protocol import Connector
    from passageway.testing.contract import check_connector

    assert python_block(CONNECTOR) == python_block(ROOT / "docs" / "guides" / "write-a-connector.md")
    script = tmp_path / "folder_connector.py"
    script.write_text(python_block(CONNECTOR))
    notes = tmp_path / "notes"
    (notes / "sub").mkdir(parents=True)
    (notes / "a.txt").write_text("Alpha note about lighthouses.")
    (notes / "sub" / "b.txt").write_text("Beta note about harbours.")
    check_connector(Connector("folder", [sys.executable, str(script)], env={"FOLDER": str(notes)}))


def test_no_skill_asks_the_agent_to_handle_a_secret():
    for path in (GENERAL, CONNECTOR):
        text = path.read_text().lower()
        assert "never print" in text and "never ask" in text, f"{path} must say how secrets are handled"
        assert not re.search(r"(api[_ -]?key|token|password)\s*[:=]\s*(?!\"?env:)\S{12,}", text), f"{path} contains a credential"


def test_the_general_skill_routes_to_the_connector_skill_and_the_llms_file():
    text = GENERAL.read_text()
    assert "create-passageway-connector" in text and "llms-full.txt" in text


# ---- publishing -----------------------------------------------------------------------------------

def test_publish_skills_copies_both_skills_into_the_site_raw(tmp_path):
    site = tmp_path / "site"
    site.mkdir()
    done = subprocess.run(["bash", str(ROOT / "scripts" / "publish-skills.sh"), str(site)], cwd=ROOT,
                          capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    assert (site / "SKILL.md").read_text() == GENERAL.read_text()
    assert (site / "skills" / "create-passageway-connector" / "SKILL.md").read_text() == CONNECTOR.read_text()


# ---- the llms files -------------------------------------------------------------------------------

class _Loader(yaml.SafeLoader):
    pass


_Loader.add_multi_constructor("tag:yaml.org,2002:python/", lambda loader, suffix, node: None)  # mkdocs' !!python/name tags


def _nav_pages(nav) -> set[str]:
    found = set()
    for entry in nav:
        if isinstance(entry, str):
            found.add(entry)
        elif isinstance(entry, dict):
            for value in entry.values():
                found |= {value} if isinstance(value, str) else _nav_pages(value)
    return found


def test_llmstxt_is_configured_and_covers_every_page_of_the_nav():
    config = yaml.load((ROOT / "mkdocs.yml").read_text(), Loader=_Loader)
    plugin = next(p["llmstxt"] for p in config["plugins"] if isinstance(p, dict) and "llmstxt" in p)
    assert plugin["full_output"] == "llms-full.txt"
    covered = set()
    for entries in plugin["sections"].values():
        for entry in entries:
            pattern = entry if isinstance(entry, str) else next(iter(entry))
            covered |= {os.path.relpath(p, ROOT / "docs") for p in glob.glob(str(ROOT / "docs" / pattern))}
    missing = {p for p in _nav_pages(config["nav"]) if p.endswith(".md")} - covered
    assert not missing, f"pages in the nav but not in llms-full.txt: {sorted(missing)}"


# ---- the release check ---------------------------------------------------------------------------

def _mini_repo(tmp_path, pyproject="1.0.0", plugin="1.0.0", skill="1.0.0", sdk="1.0.0"):
    (tmp_path / "sdk").mkdir()
    (tmp_path / "sdk" / "pyproject.toml").write_text(f'[project]\nname = "s"\nversion = "{sdk}"\n')
    (tmp_path / "pyproject.toml").write_text(f'[project]\nname = "x"\nversion = "{pyproject}"\n')
    (tmp_path / ".claude-plugin").mkdir()
    (tmp_path / ".claude-plugin" / "plugin.json").write_text(json.dumps({"name": "x", "version": plugin}))
    (tmp_path / "skills" / "passageway").mkdir(parents=True)
    (tmp_path / "skills" / "passageway" / "SKILL.md").write_text(f"---\nname: passageway\nversion: {skill}\n---\n")
    return tmp_path


def _check(cwd, tag="v1.0.0"):
    return subprocess.run(["bash", str(ROOT / "scripts" / "check-version.sh"), tag], cwd=cwd, capture_output=True, text=True)


def test_the_release_check_passes_when_pyproject_plugin_and_skill_agree(tmp_path):
    assert _check(_mini_repo(tmp_path)).returncode == 0


def test_the_release_check_fails_when_the_plugin_or_the_skill_disagrees(tmp_path):
    (tmp_path / "plugin").mkdir()
    (tmp_path / "skill").mkdir()
    bad_plugin = _check(_mini_repo(tmp_path / "plugin", plugin="0.9.0"))
    assert bad_plugin.returncode != 0 and "plugin.json" in bad_plugin.stderr
    bad_skill = _check(_mini_repo(tmp_path / "skill", skill="0.9.0"))
    assert bad_skill.returncode != 0 and "SKILL.md" in bad_skill.stderr


def test_the_release_check_fails_when_the_sdk_disagrees(tmp_path):
    bad_sdk = _check(_mini_repo(tmp_path, sdk="0.9.0"))
    assert bad_sdk.returncode != 0 and "sdk/pyproject.toml" in bad_sdk.stderr


def test_the_connector_skill_points_to_the_sdk():
    text = CONNECTOR.read_text()
    assert "passageway-sdk" in text and "reference/sdk" in text


# ---- review findings: what the skills must say ---------------------------------------------------

def test_the_general_skill_does_not_deny_what_exists():
    text = GENERAL.read_text()
    assert "passageway eval" in text and "/recall" in text, "the evaluation command and the hook endpoint exist and must be named"
    assert "not available yet" not in text, "everything the skill describes exists now; say so without denial"


def test_the_secrets_rule_names_who_handles_the_password():
    for path in (GENERAL, CONNECTOR):
        text = path.read_text().lower()
        assert "never print" in text and "never ask" in text, f"{path}: both halves of the secrets rule"
        assert "the human starts" in text or "the human runs" in text, f"{path}: the human, not the agent, handles the password"


def test_deleting_an_index_comes_with_its_guard():
    text = GENERAL.read_text()
    assert "Stop passageway" in text and "-wal" in text and "-shm" in text


def test_the_connector_skill_says_how_passageway_becomes_importable_in_the_tests():
    text = CONNECTOR.read_text()
    assert "importable" in text and "uv add --dev" in text


def test_the_general_skill_links_the_install_page_and_names_the_source_of_the_model():
    text = GENERAL.read_text()
    assert "https://passageway.marceltov.de/install/" in text and "passageway model download" in text


def test_the_pinning_example_is_not_a_dead_url():
    agents = (ROOT / "docs" / "guides" / "agents.md").read_text()
    assert "/v0.1.0/skills/" not in agents, "the v0.1.0 tag predates the skills; use a placeholder tag"
    assert "v<version>" in agents


def test_the_environment_is_described_as_the_code_passes_it():
    for path in (GENERAL, CONNECTOR):
        text = path.read_text()
        assert not re.search(r"empty environment(?! except `PATH` and `HOME`)", text), f"{path}: PATH and HOME are passed through"
        assert "`PATH` and `HOME`" in text


def test_the_plugin_description_and_the_docs_name_both_skills():
    plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
    assert "/passageway" in plugin["description"] and "/create-passageway-connector" in plugin["description"]
    assert "/passageway" in (ROOT / "docs" / "guides" / "agents.md").read_text()


def test_connector_names_are_described_as_the_config_checks_them():
    for path in (CONNECTOR, ROOT / "docs" / "configuration.md"):
        assert "starts with" in path.read_text(), f"{path}: a name must start with a letter or digit"


def test_the_release_step_names_say_what_they_check():
    assert "Tag matches pyproject.toml" not in (ROOT / ".github" / "workflows" / "release.yml").read_text()


# ---- the links in the header bar -----------------------------------------------------------------

def test_the_agent_links_sit_in_the_header_before_the_theme_toggle_and_the_search():
    config = yaml.load((ROOT / "mkdocs.yml").read_text(), Loader=_Loader)
    assert config["theme"]["custom_dir"] == "overrides"
    header = (ROOT / "overrides" / "partials" / "header.html").read_text()
    block = header.index('class="pw-header-links"')  # the element, not the comment that explains it
    assert header.index("md-header__title") < block < header.index("partials/palette.html") < header.index("partials/search.html")
    assert "SKILL.md" in header and "llms-full.txt" in header
    assert "config.site_url" in header, "the links come from site_url, not a hard-coded host"


def test_the_header_copy_names_the_material_version_it_was_copied_from_and_it_is_the_pinned_one():
    header = (ROOT / "overrides" / "partials" / "header.html").read_text()
    copied = re.search(r"mkdocs-material (\d+\.\d+\.\d+)", header)
    assert copied, "the override must say which Material version it was copied from"
    for workflow in (".github/workflows/pages.yml", ".github/workflows/checks.yml"):
        pinned = re.search(r"mkdocs-material==(\d+\.\d+\.\d+)", (ROOT / workflow).read_text()).group(1)
        assert copied.group(1) == pinned, f"{workflow} pins Material {pinned}, the header copy is from {copied.group(1)}"


def test_the_stylesheet_hides_the_links_where_the_header_has_no_room():
    css = (ROOT / "docs" / "stylesheets" / "extra.css").read_text()
    assert ".pw-header-links" in css and "min-width" in css.split(".pw-header-links", 1)[1]


# ---- the hook, the setup skill, the image ----------------------------------------------------------

def test_the_plugin_registers_the_prompt_hook_and_the_script_exists():
    hooks = json.loads((ROOT / "hooks" / "hooks.json").read_text())
    entry = hooks["hooks"]["UserPromptSubmit"][0]["hooks"][0]
    assert entry["type"] == "command" and "scripts/recall-hook.sh" in entry["command"] and entry["timeout"] <= 5
    assert os.access(ROOT / "scripts" / "recall-hook.sh", os.X_OK)


def test_the_hook_self_test_passes():
    out = subprocess.run(["bash", str(ROOT / "scripts" / "test-recall-hook.sh")], capture_output=True, text=True, timeout=120)
    assert out.returncode == 0, out.stdout + out.stderr
    assert "FAIL" not in out.stdout


def test_the_setup_skill_has_frontmatter_and_never_asks_to_paste_the_password():
    skill = ROOT / "skills" / "passageway-setup" / "SKILL.md"
    meta = frontmatter(skill)
    assert meta["name"] == "passageway-setup" and meta["description"]
    text = skill.read_text()
    assert "Never print the password" in text and "/health" in text and "claude mcp add" in text


def test_the_image_bakes_the_model_in_and_serves_on_all_interfaces():
    text = (ROOT / "Dockerfile").read_text()
    assert "passageway model download --model-dir /models/e5-small" in text
    assert "PASSAGEWAY_MODEL_DIR=/models/e5-small" in text and "PASSAGEWAY_HOST=0.0.0.0" in text and "HEALTHCHECK" in text
    assert "PASSWORD" not in text.replace("PASSAGEWAY_LOGIN_PASSWORD=...", "")  # no secret baked in
    release = (ROOT / ".github" / "workflows" / "release.yml").read_text()
    assert "ghcr.io" in release and "packages: write" in release and "--push" in release and "linux/arm64" in release
    checks = (ROOT / ".github" / "workflows" / "checks.yml").read_text()
    assert "docker build" in checks


def test_the_launchd_example_in_the_deploy_page_is_a_valid_plist():
    import plistlib
    page = (ROOT / "docs" / "deploy.md").read_text()
    xml = re.search(r"```xml\n(.*?)```", page, re.S).group(1)
    plist = plistlib.loads(xml.encode())
    assert plist["Label"] == "de.marceltov.passageway" and plist["KeepAlive"] is True
    assert "PASSAGEWAY_LOGIN_PASSWORD_FILE" in plist["EnvironmentVariables"]


def test_the_configure_skill_writes_passageway_toml_with_secrets_as_references():
    skill = ROOT / "skills" / "passageway-configure" / "SKILL.md"
    meta = frontmatter(skill)
    assert meta["name"] == "passageway-configure" and len(meta["description"]) > 40
    text = skill.read_text()
    for needed in ("[[connector]]", "[embedder]", "env:", "passageway model list", "/health", "Never print", "never ask",
                   "passageway_connector_markdown", "passageway_connector_trilium", "passageway_connector_confluence",
                   "passageway_connector_wikipedia", "PASSAGEWAY_CONFIG", "tomllib"):
        assert needed in text, needed
    assert not re.search(r"(api[_ -]?key|token|password)\s*[:=]\s*(?!\"?env:)\S{12,}", text.lower())
    # it is shipped, published with the other skills, and the setup skill and the guides point at it
    assert "/passageway-configure" in json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())["description"]
    assert "passageway-configure" in (ROOT / "scripts" / "publish-skills.sh").read_text()
    assert "/passageway-configure" in (ROOT / "docs" / "guides" / "claude-code.md").read_text()
    assert "/passageway-configure" in GENERAL.read_text()


def test_every_skill_says_where_the_documentation_is_and_how_to_read_it():
    for path in sorted((ROOT / "skills").glob("*/SKILL.md")):
        text = path.read_text()
        assert "https://passageway.marceltov.de/llms.txt" in text and "llms-full.txt" in text, path
