#!/usr/bin/env bash
# Posts release notes to a notefeed feed, once per tag: a re-run finds the note by its tag and does nothing.
# Usage: scripts/post-to-notefeed.sh vX.Y.Z notes.md
# Environment: NOTEFEED_FEED (without it nothing is posted, so forks work), NOTEFEED_FEED_PASSWORD,
#              NOTEFEED_URL (default https://notefeed.me), GITHUB_REPOSITORY.
set -euo pipefail

tag=${1:?usage: post-to-notefeed.sh vX.Y.Z notes.md}
notes=${2:?usage: post-to-notefeed.sh vX.Y.Z notes.md}
[ -n "${NOTEFEED_FEED:-}" ] || { echo "No NOTEFEED_FEED, not posting"; exit 0; }

repo=${GITHUB_REPOSITORY:?GITHUB_REPOSITORY is not set}
repo=${repo#*/}
feed="${NOTEFEED_URL:-https://notefeed.me}/api/v1/feeds/$NOTEFEED_FEED/notes"
password=${NOTEFEED_FEED_PASSWORD:-}

posted=$(curl -fsS -H "X-Feed-Password: $password" "$feed?tag=$repo-$tag&limit=1" | jq '.notes | length')
[ "$posted" = 0 ] || { echo "$repo $tag is already on notefeed"; exit 0; }

curl -fsS -o /dev/null \
  -H "Content-Type: text/markdown" \
  -H "X-Feed-Password: $password" \
  -H "X-Note-Title: $repo ${tag#v}" \
  -H "X-Note-Tags: release,$repo,$repo-$tag" \
  --data-binary @"$notes" "$feed"
echo "Posted $repo $tag to notefeed"
