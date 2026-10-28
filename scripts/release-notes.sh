#!/usr/bin/env bash
# Prints the release notes for a tag: the annotated tag's message, the pull requests merged since the
# previous release (GitHub's generated list) and how to install it.
# Usage: scripts/release-notes.sh vX.Y.Z   (needs git and gh; GITHUB_REPOSITORY and GH_TOKEN in the environment)
set -euo pipefail

tag=${1:?usage: release-notes.sh vX.Y.Z}
repo=${GITHUB_REPOSITORY:?GITHUB_REPOSITORY is not set}

git show-ref --verify -q "refs/tags/$tag" || { echo "no such tag: $tag" >&2; exit 1; }

# Only an annotated tag has a message of its own; a lightweight tag would show its commit's message.
# The subject and body are taken separately so that a signed tag's signature block is left out.
if git rev-parse -q --verify "refs/tags/$tag^{tag}" >/dev/null 2>&1; then
  message=$(git for-each-ref "refs/tags/$tag" --format='%(contents:subject)%0a%0a%(contents:body)')
  [ -z "$message" ] || printf '%s\n\n' "$message"
fi

# The release right before this one, in version order, bounds the generated list. Only vX.Y.Z tags count:
# a pre-release or a stray v* tag must not become "the previous release".
previous=$(git tag --list 'v*' --sort=v:refname | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+$' | grep -xF -B1 -- "$tag" | head -1 || true)
[ "$previous" != "$tag" ] || previous=""
args=(-f "tag_name=$tag")
[ -z "$previous" ] || args+=(-f "previous_tag_name=$previous")
gh api "repos/$repo/releases/generate-notes" "${args[@]}" --jq .body

sed -e "s|__REPO__|$repo|g" -e "s|__TAG__|$tag|g" <<'NOTES'

## Install

```bash
uv tool install \
  --with 'passageway-connector-wikipedia @ git+https://github.com/__REPO__@__TAG__#subdirectory=connectors/wikipedia' \
  git+https://github.com/__REPO__@__TAG__
```

Documentation: https://passageway.marceltov.de/
NOTES
