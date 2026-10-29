"""An in-test embeddings API: the JSON shapes of POST /v1/embeddings as OpenAI, Ollama and Voyage answer them."""

import hashlib
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def vector(text: str, dim: int) -> list[float]:
    """Deterministic, and different for different texts: hashed words into buckets (not normalised on purpose)."""
    out = [0.0] * dim
    for word in text.lower().split():
        out[int.from_bytes(hashlib.blake2b(word.encode(), digest_size=4).digest(), "big") % dim] += 1.0
    return out


class FakeApi:
    def __init__(self):
        self.dim = 16
        self.requests: list[dict] = []  # {"path", "headers", "body"} per request
        self.status_errors: list[int] = []  # answer the next requests with these statuses
        self.retry_after = "0"
        self.models = {"nomic-embed-text", "text-embedding-3-small", "voyage-3"}

    def respond(self, body: dict) -> tuple[int, dict]:
        if body.get("model") not in self.models:
            return 404, {"error": {"message": f"model '{body.get('model')}' not found", "type": "invalid_request_error"}}
        texts = body["input"] if isinstance(body["input"], list) else [body["input"]]
        dim = int(body.get("dimensions") or self.dim)
        data = [{"object": "embedding", "index": i, "embedding": vector(t, dim)} for i, t in enumerate(texts)]
        data.reverse()  # out of order, as the API may answer: the client must sort by index
        return 200, {"object": "list", "data": data, "model": body["model"], "usage": {"prompt_tokens": 1, "total_tokens": 1}}


def serve(api: FakeApi):
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            raw = self.rfile.read(int(self.headers.get("Content-Length", "0")))
            body = json.loads(raw) if raw else {}
            api.requests.append({"path": self.path, "headers": dict(self.headers), "body": body})
            if api.status_errors:
                self.send_response(api.status_errors.pop(0))
                self.send_header("Retry-After", api.retry_after)
                self.end_headers()
                return
            status, reply = api.respond(body)
            payload = json.dumps(reply).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True).start()
    return server
