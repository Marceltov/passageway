#!/usr/bin/env bash
# A release tag must be vMAJOR.MINOR.PATCH and equal the version in pyproject.toml.
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
