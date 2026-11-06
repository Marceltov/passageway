#!/usr/bin/env bash
# Moves every version that scripts/check-version.sh compares to one number: the root and every package pyproject.toml, the plugin
# manifest and the general agent skill, plus the pins between the packages.
# Usage: scripts/bump-version.sh X.Y.Z   (run from the repository root, then `uv lock`)
set -euo pipefail

version=${1:-}
[[ "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || {
  echo "not a version (expected MAJOR.MINOR.PATCH): '$version'" >&2
  exit 1
}

python3 - "$version" <<'PY'
import glob
import re
import sys

version = sys.argv[1]


def edit(path, pattern, replacement, count=1):
    text = open(path).read()
    new, n = re.subn(pattern, replacement, text, count=count, flags=re.M)
    if n == 0:
        sys.exit(f"no version to change in {path}")
    open(path, "w").write(new)


for path in ["pyproject.toml", "sdk/pyproject.toml", *glob.glob("connectors/*/pyproject.toml"), *glob.glob("embedders/*/pyproject.toml")]:
    edit(path, r'^version = "[^"]*"', f'version = "{version}"')
for path in ["pyproject.toml", *glob.glob("connectors/*/pyproject.toml")]:
    # the pins between packages: exact in the core's extras, compatible-release for the SDK
    text = open(path).read()
    text = re.sub(r"(passageway-(?:connector|embedder)-[a-z]+)==[0-9.]+", rf"\1=={version}", text)
    text = re.sub(r"(passageway-sdk(?:\[[a-z,]+\])?)~=[0-9.]+", rf"\1~={version}", text)
    open(path, "w").write(text)
edit(".claude-plugin/plugin.json", r'^(\s*"version": )"[^"]*"', rf'\1"{version}"')
edit("skills/passageway/SKILL.md", r"^version: .*$", f"version: {version}")
PY
