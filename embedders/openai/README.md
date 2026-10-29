# passageway-embedder-openai

A [passageway](https://github.com/Marceltov/passageway#readme) embedder for services that speak the OpenAI embeddings API: **Ollama**, **LM Studio**, **vLLM**, **OpenAI** itself, and **Voyage** (whose API differs in one field). It speaks the [embedder protocol](https://passageway.marceltov.de/reference/embedder-protocol/), so passageway runs it as `kind = "command"` and the core does not change.

**Where your text goes:** every indexed passage and every question is sent to the service at `BASE_URL`. With a local Ollama or LM Studio that is your own machine; with OpenAI or Voyage it is a third party, under their terms. passageway's default stays local; this embedder is your explicit choice.

## Configure

```toml
[embedder]
kind = "command"
command = ["/path/to/python", "-m", "passageway_embedder_openai"]
# Ollama: nomic-embed-text wants these prefixes; DIMENSIONS lets passageway start before Ollama does
env = { BASE_URL = "http://localhost:11434/v1", MODEL = "nomic-embed-text", DIMENSIONS = "768",
        QUERY_PREFIX = "search_query: ", PASSAGE_PREFIX = "search_document: " }
# min_similarity = ...                      # measure it for this model: passageway eval --sweep
timeout = 60                                # the core's limit per request; keep it above TIMEOUT below

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
| `BASE_URL` | `https://api.openai.com/v1`, or Voyage's for `PROVIDER = "voyage"` | The service; `POST {BASE_URL}/embeddings` is called (a trailing `/embeddings` is dropped). No credentials in the URL |
| `API_KEY` | | Sent as `Authorization: Bearer`. Required for api.openai.com and api.voyageai.com, usually not for a local server. Put it in `secrets`, never in `env` |
| `PROVIDER` | `openai` | `openai` for every OpenAI-compatible service, `voyage` for Voyage, which wants `input_type` (`query` or `document`) with each request |
| `QUERY_PREFIX`, `PASSAGE_PREFIX` | | Text put in front of every question or passage; e5-style models served locally want `query: ` and `passage: ` |
| `DIMENSIONS` | | The vector length. Set, it answers `info` without a probe, so passageway can start while the service is still down; it is also sent as `dimensions` (`output_dimension` for Voyage) for models that can shorten their vectors. The first answer is checked against it |
| `TIMEOUT` | `50` | Seconds for one request including its retries. Keep the core's `timeout` for this embedder above it, or the core kills the process before this program can report what went wrong |
| `NAME` | `<provider>:<model>@<host>[:port][#prefixes]` | The embedder's name as the index records it. A prefix changes every vector, so a short hash of the prefixes is part of it; set your own when the model behind a name changes |

`min_similarity` belongs to the model: similarity scales differ, so measure it with [`passageway eval --sweep`](https://passageway.marceltov.de/guides/evaluate/) before relying on it.

## Behaviour

- **The dimension** is learned at start by embedding one word (`passageway`), unless `DIMENSIONS` is set. Without `DIMENSIONS`, a service that is down when passageway starts keeps passageway in its error state until passageway is restarted; with it, passageway starts and the first `recall` succeeds once the service is up.
- **Retries:** 429 and 5xx answers and connection errors are retried with backoff (honouring `Retry-After`, at most 30 s), up to five attempts within `TIMEOUT`. A request that timed out while being answered is not repeated, because a paid service may already have charged for it. Any other HTTP error, and giving up, is an error reply to the core for that request; the process stays up.
- **The key** is never printed: it is masked in every error, also when a gateway quotes the header back.
- **Tested against a fake** of the API in this repository, not against any live service; Voyage is written from its public API documentation. Recent Ollama versions serve the OpenAI-compatible `/v1/embeddings`; older ones only `/api/embed`, which this embedder does not speak.
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
