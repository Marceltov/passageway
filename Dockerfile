# passageway as a sidecar container: the server, the bundled connectors and embedders, and the default model baked in.
#
# Multi-stage: resolve the workspace into a venv with uv, fetch the pinned model and verify its checksums, then ship
# only the venv, the model and the code on python-slim.
#
#   docker build -t passageway .
#   docker run -p 8082:8082 -v passageway-data:/data -v ./passageway.toml:/config/passageway.toml \
#     -e PASSAGEWAY_LOGIN_PASSWORD=... passageway

# ---- builder: the venv with every workspace package ----
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
ENV UV_PYTHON_PREFERENCE=only-system \
    UV_PYTHON_DOWNLOADS=never
# git: mcp-login-oauth is pinned by git tag. Builder stage only; the runtime image does not get it.
RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
COPY passageway/ passageway/
COPY sdk/ sdk/
COPY connectors/ connectors/
COPY embedders/ embedders/
RUN uv sync --frozen --no-dev --all-packages

# ---- model: the default preset, pinned to a revision, every file verified by checksum ----
FROM python:3.12-slim-bookworm AS model
COPY --from=builder /app /app
RUN /app/.venv/bin/passageway model download --model-dir /models/e5-small

# ---- runtime ----
FROM python:3.12-slim-bookworm
# curl is used by the container healthcheck.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=builder /app /app
COPY --from=model /models /models

ARG APP_VERSION=dev
# glibc keeps freed embedding buffers otherwise: these hold a full build at about 300 MB instead of 400.
ENV PATH="/app/.venv/bin:$PATH" \
    APP_VERSION=$APP_VERSION \
    MALLOC_ARENA_MAX=2 \
    MALLOC_TRIM_THRESHOLD_=65536 \
    PASSAGEWAY_MODEL_DIR=/models/e5-small \
    PASSAGEWAY_DATA_DIR=/data \
    PASSAGEWAY_CONFIG=/config/passageway.toml \
    PASSAGEWAY_HOST=0.0.0.0

VOLUME /data
EXPOSE 8082
HEALTHCHECK --interval=60s --timeout=5s --start-period=120s --retries=3 \
  CMD curl -sf -o /dev/null http://localhost:8082/health || exit 1
CMD ["passageway"]
