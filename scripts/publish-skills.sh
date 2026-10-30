#!/usr/bin/env bash
# Copies the agent skills into a built site as raw files; MkDocs would turn them into HTML pages.
# Usage: scripts/publish-skills.sh site
set -euo pipefail

site=${1:?usage: publish-skills.sh SITE_DIR}
root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

cp "$root/skills/passageway/SKILL.md" "$site/SKILL.md"
for skill in create-passageway-connector passageway-install passageway-connect passageway-add-source passageway-status; do
  mkdir -p "$site/skills/$skill"
  cp "$root/skills/$skill/SKILL.md" "$site/skills/$skill/SKILL.md"
done
