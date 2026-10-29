"""passageway embedder for OpenAI-compatible embedding services (Ollama, LM Studio, vLLM, OpenAI) and Voyage.

Speaks the embedder protocol (https://passageway.marceltov.de/reference/embedder-protocol/) on stdin/stdout; every setting
comes from the environment and is documented in README.md.
"""

import hashlib
import json
import math
import os
import sys
import time
from collections.abc import Mapping
from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from typing import TextIO
from urllib.parse import urlparse

import httpx

PROVIDERS = {"openai": "https://api.openai.com/v1", "voyage": "https://api.voyageai.com/v1"}
CLOUD_HOSTS = {"api.openai.com", "api.voyageai.com"}
PROBE = "passageway"  # the word embedded once at `info` to learn the dimension
MAX_ATTEMPTS = 5
RETRY_STATUS = (429, 500, 502, 503, 504)
RETRY_ERRORS = (httpx.ConnectError, httpx.ConnectTimeout, httpx.RemoteProtocolError, httpx.PoolTimeout)  # never a read timeout:
# a request that timed out while being answered may already have been charged for


class SettingsError(Exception):
    pass


@dataclass(frozen=True)
class Settings:
    provider: str
    base_url: str
    model: str
    api_key: str
    query_prefix: str
    passage_prefix: str
    dimensions: int | None
    timeout: float
    name: str


def parse_settings(env: Mapping[str, str]) -> Settings:
    provider = env.get("PROVIDER", "").strip() or "openai"
    if provider not in PROVIDERS:
        raise SettingsError(f"PROVIDER must be one of {', '.join(PROVIDERS)}, got {provider!r}")
    model = env.get("MODEL", "").strip()
    if not model:
        raise SettingsError("MODEL is required: the embedding model the service serves, e.g. nomic-embed-text")
    base_url = (env.get("BASE_URL", "").strip() or PROVIDERS[provider]).rstrip("/")
    if base_url.endswith("/embeddings"):
        base_url = base_url[: -len("/embeddings")]  # the endpoint is added here
    parsed = urlparse(base_url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise SettingsError(f"BASE_URL must be an http(s) URL such as http://localhost:11434/v1, got {base_url!r}")
    if parsed.username or parsed.password:
        raise SettingsError("BASE_URL must not carry credentials: put the key in API_KEY (as a secret reference)")
    api_key = env.get("API_KEY", "").strip()
    if parsed.hostname in CLOUD_HOSTS and not api_key:
        raise SettingsError(f"API_KEY is required for {parsed.hostname} (as a secret reference, never a value)")
    if not api_key.isascii():
        raise SettingsError("API_KEY holds a character that cannot go into an HTTP header; check for a pasted quote or space")
    raw = env.get("DIMENSIONS", "").strip()
    dimensions = None
    if raw:
        if not raw.isdecimal() or int(raw) < 1:
            raise SettingsError(f"DIMENSIONS must be a whole number from 1, got {raw!r}")
        dimensions = int(raw)
    try:
        timeout = float(env.get("TIMEOUT", "").strip() or 50)
    except ValueError:
        raise SettingsError(f"TIMEOUT must be a number of seconds, got {env.get('TIMEOUT')!r}") from None
    if not math.isfinite(timeout) or timeout <= 0:
        raise SettingsError("TIMEOUT must be a number of seconds greater than 0")
    query_prefix, passage_prefix = env.get("QUERY_PREFIX", ""), env.get("PASSAGE_PREFIX", "")
    name = env.get("NAME", "").strip()
    if not name:
        host = parsed.hostname + (f":{parsed.port}" if parsed.port else "")
        name = f"{provider}:{model}@{host}"
        if query_prefix or passage_prefix:  # a prefix changes every vector, so it is part of the identity
            name += "#" + hashlib.sha256(f"{query_prefix}\0{passage_prefix}".encode()).hexdigest()[:6]
    return Settings(provider, base_url, model, api_key, query_prefix, passage_prefix, dimensions, timeout, name)


class ApiError(Exception):
    pass


def _retry_after(header: str | None, default: float) -> float:
    if header:
        try:
            value = float(header)
        except ValueError:
            try:
                value = (parsedate_to_datetime(header) - parsedate_to_datetime(time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime()))).total_seconds()
            except (TypeError, ValueError):
                value = default
        if math.isfinite(value):
            return min(max(value, 0.0), 30.0)
    return min(max(default, 0.0), 30.0)


class Embedder:
    def __init__(self, settings: Settings, *, sleep=time.sleep):
        self.s = settings
        self._sleep = sleep
        headers = {"Authorization": f"Bearer {settings.api_key}"} if settings.api_key else {}
        self._http = httpx.Client(headers=headers, timeout=settings.timeout, follow_redirects=False)
        self._dim = settings.dimensions

    def _mask(self, text: str) -> str:
        return text.replace(self.s.api_key, "***") if self.s.api_key else text

    def _post(self, texts: list[str], kind: str) -> list[list[float]]:
        body: dict = {"model": self.s.model, "input": texts}
        if self.s.dimensions:
            body["output_dimension" if self.s.provider == "voyage" else "dimensions"] = self.s.dimensions
        if self.s.provider == "voyage":
            body["input_type"] = "query" if kind == "query" else "document"
        deadline = time.monotonic() + self.s.timeout  # the whole request, retries included, stays within TIMEOUT
        for attempt in range(MAX_ATTEMPTS):
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            wait = min(2 ** attempt, 30)
            try:
                response = self._http.post(f"{self.s.base_url}/embeddings", json=body, timeout=remaining)
            except RETRY_ERRORS as e:
                response, reason = None, f"{self.s.base_url}: {type(e).__name__}: {e}"
            except httpx.HTTPError as e:  # a read timeout or another error: not repeated
                raise ApiError(f"{self.s.base_url}: {type(e).__name__}: {e}") from None
            if response is not None:
                if response.status_code in RETRY_STATUS:
                    reason = f"HTTP {response.status_code} from {self.s.base_url}"
                    wait = _retry_after(response.headers.get("Retry-After"), wait)
                elif 300 <= response.status_code < 400:
                    raise ApiError(f"{self.s.base_url} answered with a redirect to {response.headers.get('Location', '?')}: "
                                   "set BASE_URL to the final address")
                elif response.status_code >= 400:
                    detail = ""
                    try:
                        detail = response.json().get("error", {}).get("message", "")
                    except (ValueError, AttributeError):
                        pass
                    raise ApiError(f"HTTP {response.status_code} from {self.s.base_url}: {detail or response.text[:200]}")
                else:
                    return self._vectors(response, len(texts))
            if attempt < MAX_ATTEMPTS - 1 and time.monotonic() + wait < deadline:
                self._sleep(wait)
            else:
                break
        raise ApiError(f"giving up after {attempt + 1} attempt(s) within {self.s.timeout:g} s: {reason}")

    def _vectors(self, response: httpx.Response, expected: int) -> list[list[float]]:
        try:
            data = response.json()["data"]
            rows = sorted(data, key=lambda d: d["index"])
            vectors = [row["embedding"] for row in rows]
        except (ValueError, KeyError, TypeError, RecursionError):
            raise ApiError(f"the service did not answer with {{data: [{{index, embedding}}]}}: {response.text[:200]}") from None
        if len(vectors) != expected:
            raise ApiError(f"the service returned {len(vectors)} vectors for {expected} texts")
        for v in vectors:
            if not (isinstance(v, list) and v and all(isinstance(x, (int, float)) and not isinstance(x, bool)
                                                       and math.isfinite(x) for x in v)):
                raise ApiError("the service returned an embedding that is not a non-empty list of finite numbers")
        if self._dim is not None and len(vectors[0]) != self._dim:
            raise ApiError(f"the service returned vectors with {len(vectors[0])} dimensions, but DIMENSIONS (or the probe) "
                           f"says {self._dim}: the model does not honour the setting")
        return vectors

    def embed(self, kind: str, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        prefix = self.s.query_prefix if kind == "query" else self.s.passage_prefix
        return self._post([prefix + t for t in texts], kind)

    def info(self) -> dict:
        if self._dim is None:
            self._dim = len(self._post([PROBE], "query")[0])
        return {"name": self.s.name, "dim": self._dim, "protocol": "1"}

    # -- the protocol loop -------------------------------------------------------------------

    @classmethod
    def run(cls, env: Mapping[str, str], stdin: TextIO, stdout: TextIO, stderr: TextIO, *, sleep=time.sleep) -> int:
        try:
            settings = parse_settings(env)
        except SettingsError as e:
            print(f"openai embedder: {e}", file=stderr)
            return 2
        embedder = cls(settings, sleep=sleep)
        for line in stdin:
            if not line.strip():
                continue
            try:
                request = json.loads(line)
                if not isinstance(request, dict):
                    raise ValueError("a request is a JSON object")
                if request.get("op") == "info":
                    reply = embedder.info()
                elif request.get("op") == "embed":
                    kind, texts = request.get("kind"), request.get("texts")
                    if kind not in ("query", "passage") or not isinstance(texts, list) or not all(isinstance(t, str) for t in texts):
                        raise ValueError("embed needs kind query|passage and texts as a list of strings")
                    reply = {"vectors": embedder.embed(kind, texts)}
                else:
                    reply = {"error": f"unknown op {request.get('op')!r}"}
            except (ApiError, httpx.HTTPError) as e:
                reply = {"error": embedder._mask(str(e))}
            except (ValueError, KeyError, TypeError, RecursionError) as e:
                reply = {"error": f"bad request: {e}"}
            print(json.dumps(reply), file=stdout, flush=True)
        return 0


def main() -> None:
    sys.exit(Embedder.run(os.environ, sys.stdin, sys.stdout, sys.stderr))
