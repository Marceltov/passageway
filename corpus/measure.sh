#!/usr/bin/env bash
# Measure retrieval quality on the sample corpus with the questions in corpus/questions.toml and update the results block
# in docs/measurements.md (and its history). Needs the embedding model: see docs/install.md (PASSAGEWAY_MODEL_DIR).
# Extra arguments go to `passageway eval`, e.g. corpus/measure.sh --include-cases --out /tmp/report
set -euo pipefail
cd "$(dirname "$0")/.."

python=$(uv run python -c 'import sys; print(sys.executable)')
config=$(mktemp)
trap 'rm -f "$config"' EXIT
# one connector per language folder: a question is answered from both together, as it would be in real use
cat > "$config" <<TOML
[[connector]]
name = "corpus-en"
command = ["$python", "-m", "passageway_connector_markdown"]
env = { FOLDER = "$PWD/corpus/en" }

[[connector]]
name = "corpus-de"
command = ["$python", "-m", "passageway_connector_markdown"]
env = { FOLDER = "$PWD/corpus/de" }
TOML

PASSAGEWAY_CONFIG="$config" uv run passageway eval corpus/questions.toml \
  --sweep 0.80,0.81,0.82,0.83,0.84,0.85,0.86,0.87,0.88,0.89,0.90 --write docs/measurements.md "$@"
