#!/usr/bin/env bash
# Compare the built-in models on the sample corpus with the questions in corpus/questions.toml and update the results block
# in docs/models.md (and its history). Needs the three presets downloaded: passageway model download <preset>.
# Extra arguments go to `passageway eval compare`; --no-write runs without touching the page.
set -euo pipefail
cd "$(dirname "$0")/.."

python=$(uv run python -c 'import sys; print(sys.executable)')
config=$(mktemp)
trap 'rm -f "$config"' EXIT
cat > "$config" <<TOML
[embedder]
download = false

[embedders.e5-base]
model = "multilingual-e5-base"
download = false

[embedders.jina-de]
model = "jina-v2-base-de"
download = false

[[connector]]
name = "corpus-en"
command = ["$python", "-m", "passageway_connector_markdown"]
env = { FOLDER = "$PWD/corpus/en" }

[[connector]]
name = "corpus-de"
command = ["$python", "-m", "passageway_connector_markdown"]
env = { FOLDER = "$PWD/corpus/de" }
TOML

write=(--write docs/models.md)
args=()
for arg in "$@"; do
  if [ "$arg" = "--no-write" ]; then write=(); else args+=("$arg"); fi
done

# a wide sweep: Jina's similarities lie around 0.5 for a match, e5's around 0.85
PASSAGEWAY_CONFIG="$config" uv run passageway eval compare corpus/questions.toml \
  --sweep 0.4,0.45,0.5,0.52,0.54,0.55,0.56,0.58,0.6,0.65,0.7,0.75,0.8,0.81,0.82,0.83,0.84,0.845,0.85,0.86,0.87,0.88,0.9 \
  ${write[@]+"${write[@]}"} ${args[@]+"${args[@]}"}
