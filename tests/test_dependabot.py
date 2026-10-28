"""Pins the Dependabot setup to the standard in the wiki ("Dependabot in every repository")."""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


def test_every_ecosystem_the_repository_has_is_covered_with_the_standard_settings():
    config = yaml.safe_load((ROOT / ".github" / "dependabot.yml").read_text())
    assert config["version"] == 2 and set(config) == {"version", "updates"}  # no extra top-level keys
    updates = {u["package-ecosystem"]: u for u in config["updates"]}
    assert {"uv", "github-actions"} <= set(updates)  # uv.lock and the workflows
    if (ROOT / "Dockerfile").exists():
        assert "docker" in updates
    for name, u in updates.items():
        assert u["schedule"] == {"interval": "weekly", "day": "monday", "time": "05:00", "timezone": "Europe/Berlin"}, name
        assert u["cooldown"] == {"default-days": 14}, name
        assert u["open-pull-requests-limit"] == 5, name
        assert u["commit-message"] == {"prefix": "Dependencies"}, name
        assert u["labels"] == ["dependencies"], name
    assert updates["uv"]["groups"]["minor-and-patch"]["update-types"] == ["minor", "patch"]
    assert updates["github-actions"]["groups"]["actions"]["patterns"] == ["*"]


def test_the_automerge_workflow_only_touches_dependabot_patch_and_minor_bumps():
    text = (WORKFLOWS / "dependabot-automerge.yml").read_text()
    workflow = yaml.safe_load(text)
    assert workflow["permissions"] == {"contents": "write", "pull-requests": "write"}
    job = workflow["jobs"]["automerge"]
    assert job["if"] == "github.event.pull_request.user.login == 'dependabot[bot]'"
    merge = next(s for s in job["steps"] if "run" in s)
    assert merge["run"].startswith("gh pr merge --auto --merge")  # --auto waits for the required checks
    assert "semver-patch" in merge["if"] and "semver-minor" in merge["if"] and "semver-major" not in merge["if"]


def test_a_scheduled_audit_is_the_safety_net():
    workflow = yaml.safe_load((WORKFLOWS / "audit.yml").read_text())
    assert "schedule" in workflow[True] and "workflow_dispatch" in workflow[True]
    assert "pip-audit" in (WORKFLOWS / "audit.yml").read_text()


def test_claude_md_names_the_one_exception_to_merge_only_when_told():
    text = (ROOT / "CLAUDE.md").read_text()
    assert "dependabot-automerge.yml" in text and "Merge only when I say" in text
