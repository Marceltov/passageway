#!/usr/bin/env bash
# A release tag must be vMAJOR.MINOR.PATCH and equal the version in pyproject.toml, in the plugin manifest
# (.claude-plugin/plugin.json), in the general agent skill (skills/passageway/SKILL.md) and in the SDK (sdk/pyproject.toml):
# they ship together.
# Usage: scripts/check-version.sh vX.Y.Z   (run from the repository root)
set -euo pipefail

tag=${1:-}
[[ "$tag" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]] || {
  echo "not a release tag (expected vMAJOR.MINOR.PATCH): '$tag'" >&2
  exit 1
}
version=$(python3 -c 'import tomllib; print(tomllib.load(open("pyproject.toml", "rb"))["project"]["version"])')
[ "v$version" = "$tag" ] || {
  echo "tag $tag does not match the version $version in pyproject.toml" >&2
  exit 1
}

plugin=$(python3 -c 'import json; print(json.load(open(".claude-plugin/plugin.json"))["version"])')
[ "v$plugin" = "$tag" ] || {
  echo "tag $tag does not match the version $plugin in .claude-plugin/plugin.json" >&2
  exit 1
}
skill=$(awk '/^---$/ {n++; next} n == 1 && /^version:/ {gsub(/["\047]/, "", $2); print $2; exit}' skills/passageway/SKILL.md)
[ "v$skill" = "$tag" ] || {
  echo "tag $tag does not match the version '$skill' in skills/passageway/SKILL.md" >&2
  exit 1
}
sdk=$(python3 -c 'import tomllib; print(tomllib.load(open("sdk/pyproject.toml", "rb"))["project"]["version"])')
[ "v$sdk" = "$tag" ] || {
  echo "tag $tag does not match the version $sdk in sdk/pyproject.toml" >&2
  exit 1
}
