"""A read-mostly web client for connectors and embedders. Needs the extra: `pip install passageway-sdk[web]`."""

import json as jsonlib
import ssl
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any, NamedTuple

from passageway_sdk import SourceError

try:
    import httpx
    import truststore
except ImportError as e:  # the SDK itself has no dependencies; this module is the one that has
    raise ImportError("passageway_sdk.web needs httpx and truststore: install passageway-sdk[web]") from e


class Reply(NamedTuple):
    status: int
    text: str  # decoded as UTF-8, undecodable bytes replaced
    content_type: str

    def json(self) -> Any:
        return jsonlib.loads(self.text)


class TooLarge(SourceError):
    """The reply was larger than the limit."""


class HttpError(SourceError):
    """The server answered with a status the call cannot go on with: a 5xx or 429 that retries did not clear, or any
    non-200 when the call was `required`."""

    def __init__(self, url: str, status: int):
        super().__init__(f"{url}: HTTP {status}")
        self.url, self.status = url, status


@dataclass(frozen=True)
class Retry:
    """Wait and try again when the server asks to come back later (seconds)."""

    statuses: tuple[int, ...] = (429, 502, 503, 504)
    budget: float = 900  # the most that is waited in total for one request before giving up
    max_backoff: float = 60  # the longest wait the client picks itself: 1, 2, 4, … up to this
    max_after: float = 300  # the longest wait a Retry-After header may ask for


class Web:
    """HTTP with the operating system's trust store (never certifi's bundle), a pause between requests and a size cap.

    A failure to reach the server, or a 5xx or 429 that a `retry` policy did not clear, raises SourceError (HttpError for a
    status), so a source that is down fails the whole call and never looks empty. Any other status is returned for the
    connector to judge; `required=True` raises on it too. Turning TLS checking off (`verify=False`) is an explicit switch.
    """

    def __init__(self, user_agent: str | None = None, *, base_url: str = "", headers: Mapping[str, str] | None = None,
                 verify: bool = True, follow_redirects: bool = True, pause: float = 0.2, timeout: float = 30.0,
                 max_bytes: int = 2_000_000, retry: Retry | None = None, transport: "httpx.BaseTransport | None" = None,
                 sleep: Callable[[float], None] = time.sleep):
        all_headers = {**({"User-Agent": user_agent} if user_agent else {}), **(headers or {})}
        self._http = httpx.Client(base_url=base_url, headers=all_headers, timeout=timeout, follow_redirects=follow_redirects,
                                  transport=transport, verify=truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT) if verify else False)
        self._pause, self._max_bytes, self._retry, self._sleep, self._last = pause, max_bytes, retry, sleep, None

    def get(self, url: str, *, params: Mapping[str, str] | None = None, required: bool = False, max_bytes: int | None = None) -> Reply:
        return self.request("GET", url, params=params, required=required, max_bytes=max_bytes)

    def request(self, method: str, url: str, *, params: Mapping[str, str] | None = None, json: Any = None, required: bool = False,
                max_bytes: int | None = None) -> Reply:
        limit, waited, attempt = max_bytes or self._max_bytes, 0.0, 0
        while True:
            reply, retry_after = self._once(method, url, params, json, limit)
            if self._retry and reply.status in self._retry.statuses:
                wait = self._wait(attempt, retry_after)
                if waited + wait <= self._retry.budget:
                    self._sleep(wait)
                    waited, attempt = waited + wait, attempt + 1
                    continue
            if reply.status >= 500 or reply.status == 429 or (required and reply.status != 200):
                raise HttpError(url, reply.status)
            return reply

    def _wait(self, attempt: int, retry_after: str | None) -> float:
        backoff = min(float(2 ** attempt), self._retry.max_backoff)
        try:
            return max(backoff, min(float(retry_after), self._retry.max_after)) if retry_after else backoff
        except ValueError:
            return backoff

    def _once(self, method: str, url: str, params, json, limit: int) -> tuple[Reply, str | None]:
        if self._last is not None and (wait := self._pause - (time.monotonic() - self._last)) > 0:
            self._sleep(wait)
        try:
            with self._http.stream(method, url, params=params, json=json) as response:
                body = bytearray()
                for chunk in response.iter_bytes():
                    body += chunk
                    if len(body) > limit:
                        raise TooLarge(f"{url}: larger than {limit} bytes")
                reply = Reply(response.status_code, body.decode("utf-8", errors="replace"), response.headers.get("content-type", ""))
                return reply, response.headers.get("retry-after")
        except httpx.HTTPError as e:
            raise SourceError(f"{url}: {e}") from e
        finally:
            self._last = time.monotonic()
