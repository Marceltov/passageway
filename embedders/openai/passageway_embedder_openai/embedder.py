"""passageway embedder for OpenAI-compatible embedding services (Ollama, LM Studio, vLLM, OpenAI) and Voyage.

Speaks the embedder protocol (https://passageway.marceltov.de/reference/embedder-protocol/) on stdin/stdout; every setting
comes from the environment and is documented in README.md.
"""

import json
import os
import re
import sys
import time
from collections.abc import Mapping
from dataclasses import dataclass
from typing import TextIO
from urllib.parse import urlparse

import httpx

PROVIDERS = {"openai": "https://api.openai.com/v1", "voyage": "https://api.voyageai.com/v1"}
CLOUD_HOSTS = {"api.openai.com", "api.voyageai.com"}
PROBE = "passageway"  # the word embedded once at `info` to learn the dimension
MAX_ATTEMPTS = 5
RETRY_STATUS = (429, 500, 502, 503, 504)


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
    parsed = urlparse(base_url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise SettingsError(f"BASE_URL must be an http(s) URL such as http://localhost:11434/v1, got {base_url!r}")
    api_key = env.get("API_KEY", "").strip()
    if parsed.hostname in CLOUD_HOSTS and not api_key:
        raise SettingsError(f"API_KEY is required for {parsed.hostname} (as a secret reference, never a value)")
    raw = env.get("DIMENSIONS", "").strip()
    dimensions = None
    if raw:
        if not raw.isdigit() or int(raw) < 1:
            raise SettingsError(f"DIMENSIONS must be a whole number from 1, got {raw!r}")
        dimensions = int(raw)
    try:
        timeout = float(env.get("TIMEOUT", "").strip() or 60)
    except ValueError:
        raise SettingsError(f"TIMEOUT must be a number of seconds, got {env.get('TIMEOUT')!r}") from None
    if timeout <= 0:
        raise SettingsError("TIMEOUT must be greater than 0")
    name = env.get("NAME", "").strip() or f"{provider}:{model}@{parsed.hostname}"
    return Settings(provider, base_url, model, api_key, env.get("QUERY_PREFIX", ""), env.get("PASSAGE_PREFIX", ""),
                    dimensions, timeout, name)


class ApiError(Exception):
    pass


class Embedder:
    def __init__(self, settings: Settings, *, sleep=time.sleep):
        self.s = settings
        self._sleep = sleep
        headers = {"Authorization": f"Bearer {settings.api_key}"} if settings.api_key else {}
        self._http = httpx.Client(headers=headers, timeout=settings.timeout)
        self._dim = settings.dimensions

    def _mask(self, text: str) -> str:
        return text.replace(self.s.api_key, "***") if self.s.api_key else text

    def _post(self, texts: list[str], kind: str) -> list[list[float]]:
        body: dict = {"model": self.s.model, "input": texts}
        if self.s.dimensions:
            body["dimensions"] = self.s.dimensions
        if self.s.provider == "voyage":
            body["input_type"] = "query" if kind == "query" else "document"
        for attempt in range(MAX_ATTEMPTS):
            wait = min(2 ** attempt, 30)
            try:
                response = self._http.post(f"{self.s.base_url}/embeddings", json=body)
            except httpx.HTTPError as e:  # refused, timed out, dropped: worth another try
                response, reason = None, f"{self.s.base_url}: {type(e).__name__}: {e}"
            if response is not None:
                if response.status_code in RETRY_STATUS:
                    reason = f"HTTP {response.status_code} from {self.s.base_url}"
                    try:
                        wait = min(float(response.headers.get("Retry-After", wait)), 30)
                    except ValueError:
                        pass
                elif response.status_code >= 400:
                    detail = ""
                    try:
                        detail = response.json().get("error", {}).get("message", "")
                    except (ValueError, AttributeError):
                        pass
                    raise ApiError(f"HTTP {response.status_code} from {self.s.base_url}: {detail or response.text[:200]}")
                else:
                    return self._vectors(response, len(texts))
            if attempt < MAX_ATTEMPTS - 1:
                self._sleep(wait)
        raise ApiError(f"giving up after {MAX_ATTEMPTS} attempts: {reason}")

    def _vectors(self, response: httpx.Response, expected: int) -> list[list[float]]:
        try:
            data = response.json()["data"]
            rows = sorted(data, key=lambda d: d["index"])
            vectors = [row["embedding"] for row in rows]
        except (ValueError, KeyError, TypeError):
            raise ApiError(f"the service did not answer with {{data: [{{index, embedding}}]}}: {response.text[:200]}") from None
        if len(vectors) != expected:
            raise ApiError(f"the service returned {len(vectors)} vectors for {expected} texts")
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
                if request["op"] == "info":
                    reply = embedder.info()
                elif request["op"] == "embed":
                    reply = {"vectors": embedder.embed(request["kind"], list(request["texts"]))}
                else:
                    reply = {"error": f"unknown op {request['op']!r}"}
            except (ApiError, httpx.HTTPError) as e:
                reply = {"error": embedder._mask(str(e))}
            except (ValueError, KeyError, TypeError) as e:
                reply = {"error": f"bad request: {e}"}
            print(json.dumps(reply), file=stdout, flush=True)
        return 0


def main() -> None:
    sys.exit(Embedder.run(os.environ, sys.stdin, sys.stdout, sys.stderr))
