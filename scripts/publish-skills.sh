#!/usr/bin/env bash
# Copies the agent skills into a built site as raw files; MkDocs would turn them into HTML pages.
# Usage: scripts/publish-skills.sh site
set -euo pipefail

site=${1:?usage: publish-skills.sh SITE_DIR}
root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

mkdir -p "$site/skills/create-passageway-connector"
cp "$root/skills/passageway/SKILL.md" "$site/SKILL.md"
cp "$root/skills/create-passageway-connector/SKILL.md" "$site/skills/create-passageway-connector/SKILL.md"
