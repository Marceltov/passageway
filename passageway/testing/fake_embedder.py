"""An embedder over the hash embedder, for tests and docs. Run: python -m passageway.testing.fake_embedder.

Settings (environment): FAKE_EMBED_NAME (default fake-hash), FAKE_EMBED_DIM (default 64), FAKE_EMBED_LOG (a file that gets
one JSON line per start and per request, with the process id). FAKE_EMBED_FAIL makes it misbehave, to test the core:
start (exits at once), no-read (answers info, then never reads again), info-error, protocol2, die-after:N (exits after N embed requests), always-die (exits on the first
embed request), hang (never answers an embed request), error (answers embed with an error), garbage, not-an-object,
count (one vector too few), dim (vectors one longer), nan, zero.
FAKE_EMBED_NAME_FILE: if that file exists, its text is the name (changes the identity across a restart).
"""

import json
import os
import sys
import time

import numpy as np

from passageway.embed import HashEmbedder


def main() -> int:
    fail = os.environ.get("FAKE_EMBED_FAIL", "")
    log_path = os.environ.get("FAKE_EMBED_LOG")
    name = os.environ.get("FAKE_EMBED_NAME", "fake-hash")
    name_file = os.environ.get("FAKE_EMBED_NAME_FILE")
    if name_file and os.path.exists(name_file):
        name = open(name_file).read().strip()
    dim = int(os.environ.get("FAKE_EMBED_DIM", "64"))
    model = HashEmbedder(dim)

    def log(record: dict) -> None:
        if log_path:
            with open(log_path, "a") as f:
                f.write(json.dumps({"pid": os.getpid(), **record}) + "\n")

    log({"start": True, "env": sorted(os.environ)})
    if fail == "start":
        print("fake start failure: secret=" + os.environ.get("FAKE_SECRET", ""), file=sys.stderr, flush=True)
        return 3
    served = 0
    for line in sys.stdin:
        if not line.strip():
            continue
        request = json.loads(line)
        log({"request": request})
        if request["op"] == "info":
            if fail == "info-error":
                print(json.dumps({"error": "no model loaded"}), flush=True)
            else:
                print(json.dumps({"name": name, "dim": dim, **({"protocol": "2"} if fail == "protocol2" else {})}), flush=True)
            if fail == "no-read":
                time.sleep(600)  # never reads another line: a request bigger than the pipe blocks its writer
            continue
        served += 1
        if fail == "always-die" or (fail.startswith("die-after:") and served > int(fail.split(":")[1])):
            print("fake died: secret=" + os.environ.get("FAKE_SECRET", ""), file=sys.stderr, flush=True)
            os._exit(1)
        if fail == "hang":
            time.sleep(600)
        if fail == "error":
            print(json.dumps({"error": "out of memory"}), flush=True)
            continue
        if fail == "garbage":
            print("this is not json", flush=True)
            continue
        if fail == "not-an-object":
            print("[1, 2]", flush=True)
            continue
        embed = model.embed_queries if request["kind"] == "query" else model.embed_passages
        vectors = embed(request["texts"]) * 3.0  # not unit length: normalising is the core's job
        if fail == "count":
            vectors = vectors[:-1]
        if fail == "dim":
            vectors = np.hstack([vectors, np.ones((len(vectors), 1), dtype=np.float32)])
        if fail == "nan":
            vectors[0, 0] = float("nan")
        if fail == "zero":
            vectors[0, :] = 0.0
        print(json.dumps({"vectors": vectors.tolist()}), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
