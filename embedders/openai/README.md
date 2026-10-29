# passageway-embedder-openai

A [passageway](https://github.com/Marceltov/passageway#readme) embedder for services that speak the OpenAI embeddings API: **Ollama**, **LM Studio**, **vLLM**, **OpenAI** itself, and **Voyage** (whose API differs in one field). It speaks the [embedder protocol](https://passageway.marceltov.de/reference/embedder-protocol/), so passageway runs it as `kind = "command"` and the core does not change.

**Where your text goes:** every indexed passage and every question is sent to the service at `BASE_URL`. With a local Ollama or LM Studio that is your own machine; with OpenAI or Voyage it is a third party, under their terms. passageway's default stays local; this embedder is your explicit choice.

## Configure

```toml
[embedder]
kind = "command"
command = ["/path/to/python", "-m", "passageway_embedder_openai"]
env = { BASE_URL = "http://localhost:11434/v1", MODEL = "nomic-embed-text" }   # Ollama
min_similarity = 0.75                       # measure it: passageway eval --sweep

# OpenAI
# env = { MODEL = "text-embedding-3-small" }
# secrets = { API_KEY = "env:OPENAI_API_KEY" }

# Voyage
# env = { PROVIDER = "voyage", MODEL = "voyage-3" }
# secrets = { API_KEY = "env:VOYAGE_API_KEY" }
```

| Setting | Default | Meaning |
|---|---|---|
| `MODEL` | required | The embedding model the service serves |
| `BASE_URL` | `https://api.openai.com/v1`, or Voyage's for `PROVIDER = "voyage"` | The service; `POST {BASE_URL}/embeddings` is called |
| `API_KEY` | | Sent as `Authorization: Bearer`. Required for api.openai.com and api.voyageai.com, usually not for a local server. Put it in `secrets`, never in `env` |
| `PROVIDER` | `openai` | `openai` for every OpenAI-compatible service, `voyage` for Voyage, which wants `input_type` (`query` or `document`) with each request |
| `QUERY_PREFIX`, `PASSAGE_PREFIX` | | Text put in front of every question or passage; e5-style models served locally want `query: ` and `passage: ` |
| `DIMENSIONS` | | Sent as `dimensions`, for models that can shorten their vectors (OpenAI's text-embedding-3); also answers the dimension without a probe |
| `TIMEOUT` | `60` | Seconds per request |
| `NAME` | `<provider>:<model>@<host>` | The embedder's name as the index records it; change it when the model behind a name changes |

`min_similarity` belongs to the model: similarity scales differ, so measure it with [`passageway eval --sweep`](https://passageway.marceltov.de/guides/evaluate/) before relying on it.

## Behaviour

- **The dimension** is learned at start by embedding one word (`passageway`), unless `DIMENSIONS` is set.
- **Retries:** 429 and 5xx answers and network errors are retried with backoff (honouring `Retry-After`, at most 30 s), five attempts in all. Any other HTTP error, and giving up, is an error reply to the core for that request; the process stays up.
- **The key** is never printed: it is masked in every error.
- **Voyage** is written from its public API documentation and tested against a fake of it, not against the live service.
- **Batches:** the core sends at most `batch_size` texts per request (32 by default); the services accept far more, so raise it for a cloud model if you like.

## Install

```bash
uv tool install \
  --with 'passageway-embedder-openai @ git+https://github.com/Marceltov/passageway#subdirectory=embedders/openai' \
  git+https://github.com/Marceltov/passageway
```

and use that environment's interpreter in `command` (`$(uv tool dir)/passageway/bin/python`), as for a connector.

## Test

```bash
uv run pytest embedders/openai        # offline, against an in-test embeddings API
```
