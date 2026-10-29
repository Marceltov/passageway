# Embedder protocol

An embedder turns texts into vectors. The built-in one runs the multilingual e5-small model; any other model is a program that speaks this protocol, configured as `kind = "command"`. The core starts it once and keeps it running, because loading a model takes seconds. This page is the protocol reference (v1); the messages are also described by a [JSON Schema](embedder-protocol.schema.json).

The core writes one JSON object per line to the program's stdin and reads one line from its stdout in answer, in order:

| Request | Reply |
|---|---|
| `{"op": "info"}` | `{"name": "bge-m3", "dim": 1024}`, optionally with `"protocol": "1"` |
| `{"op": "embed", "kind": "query", "texts": ["…"]}` (or `"kind": "passage"`) | `{"vectors": [[0.1, …], …]}`: one vector per text, in the same order, each with `dim` numbers |
| (any) | `{"error": "message"}` if the request failed; the process stays in use |

```json
{"op": "info"}
{"name": "toy-hash-64", "dim": 64}
{"op": "embed", "kind": "passage", "texts": ["Lighthouses guide ships."]}
{"vectors": [[0.0, 1.0, 0.0, 2.0]]}
```

## Rules

- **The name identifies the model.** The index stores the name and the dimension; a different name rebuilds the index, and the core refuses a program that, after a restart, answers with another name or dimension. Change the name when you change the model.
- **A query and a passage are told apart by `kind`.** Models that need a prefix for each (the e5 family wants `query: ` and `passage: `) add it themselves. Pooling and tokenisation are the program's business too.
- **The core normalises the vectors** to unit length, so a program may send them as they are. A vector of zero length is an error.
- **Batches:** the core sends at most `batch_size` texts per request (32 by default) and puts the answers together in order.
- **Time and failure:** a request that takes longer than `timeout` seconds (60 by default) kills the process and fails the call; the next call starts it again. A process that died is restarted once and the request repeated; if it dies again the call fails with the program's error output (secrets masked), and the index that exists keeps serving.
- **Isolation:** the program runs with an empty environment plus `PATH`, `HOME`, `PASSAGEWAY_PROTOCOL=1`, the `env` table and the named `secrets` from its configuration. It never sees the core's password, and a timeout kills its whole process group.
- **Nothing else on stdout.** Log to stderr.

## Configure it

```toml
[embedder]
kind = "command"
command = ["/path/to/python", "/path/to/my_embedder.py"]
env = { MODEL = "bge-m3" }
secrets = { API_KEY = "env:EMBED_KEY" }   # references to environment variables, never values
min_similarity = 0.80
batch_size = 32
timeout = 60
```

`min_similarity` is the relevance gate for this model. Similarity scales differ from model to model, so measure it with `passageway eval --sweep`: without it the default of the built-in model is used, which is probably wrong for yours.

## An example

A toy that hashes words into 64 buckets, to show the loop. Replace `embed` with your model.

```python
#!/usr/bin/env python3
"""A toy embedder: words hashed into 64 buckets. Replace embed() with your model."""
import hashlib
import json
import re
import sys

DIM = 64


def embed(texts, kind):
    vectors = []
    for text in texts:
        vector = [0.0] * DIM
        for word in re.findall(r"\w+", text.lower()):
            vector[int.from_bytes(hashlib.blake2b(word.encode(), digest_size=4).digest(), "big") % DIM] += 1.0
        vectors.append(vector)
    return vectors


for line in sys.stdin:
    request = json.loads(line)
    try:
        if request["op"] == "info":
            reply = {"name": "toy-hash-64", "dim": DIM}
        else:
            reply = {"vectors": embed(request["texts"], request["kind"])}
    except Exception as error:
        reply = {"error": str(error)}
    print(json.dumps(reply), flush=True)
```

## Test it

```python
import sys
from passageway.embed_command import CommandEmbedder
from passageway.testing.embedder_contract import check_embedder

def test_my_embedder():
    embedder = CommandEmbedder("mine", [sys.executable, "my_embedder.py"])
    try:
        check_embedder(embedder)
    finally:
        embedder.close()
```

`check_embedder` checks the dimension, finite numbers, unit length, determinism, the same vector alone and in a batch, and that the embedder tells a passage about lighthouses from one about bananas.
