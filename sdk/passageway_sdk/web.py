"""A read-mostly web client for connectors and embedders. Needs the extra: `pip install passageway-sdk[web]`."""

import json as jsonlib
import ssl
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from types import MappingProxyType
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
    headers: Mapping[str, str] = MappingProxyType({})  # names in lower case

    def json(self) -> Any:
        return jsonlib.loads(self.text)


class TooLarge(SourceError):
    """The reply was larger than the limit."""


class HttpError(SourceError):
    """The server answered with a status the call cannot go on with: a 5xx or 429 that retries did not clear, or any
    non-200 when the call was `required`."""

    def __init__(self, url: str, status: int, message: str | None = None, attempts: int = 1):
        super().__init__(message or f"{url}: HTTP {status}")
        self.url, self.status, self.attempts = url, status, attempts  # attempts > 1: a retry policy gave up


class NetworkError(SourceError):
    """The server could not be reached or went silent (a connection or timeout error)."""


@dataclass(frozen=True)
class Retry:
    """Wait and try again when the server asks to come back later (seconds)."""

    statuses: tuple[int, ...] = (429, 502, 503, 504)
    network: bool = False  # also retry when the server cannot be reached or times out
    budget: float = 900  # the most that is waited in total for one request before giving up
    max_backoff: float = 60  # the longest wait the client picks itself: 1, 2, 4, … up to this
    max_after: float = 300  # the longest wait a Retry-After header may ask for
    say_from: float = 10  # a wait this long is reported to `log`, shorter ones stay quiet


class Web:
    """HTTP with the operating system's trust store (never certifi's bundle), a pause between requests and a size cap.

    A failure to reach the server, or a 5xx or 429 that a `retry` policy did not clear, raises SourceError (HttpError for a
    status), so a source that is down fails the whole call and never looks empty. Any other status is returned for the
    connector to judge; `required=True` raises on it too. Turning TLS checking off (`verify=False`) is an explicit switch.
    """

    def __init__(self, user_agent: str | None = None, *, base_url: str = "", headers: Mapping[str, str] | None = None,
                 verify: bool = True, follow_redirects: bool = True, pause: float = 0.2, timeout: float = 30.0,
                 max_bytes: int = 2_000_000, retry: Retry | None = None, log: Callable[[str], None] | None = None, transport: "httpx.BaseTransport | None" = None,
                 sleep: Callable[[float], None] = time.sleep):
        all_headers = {**({"User-Agent": user_agent} if user_agent else {}), **(headers or {})}
        self._http = httpx.Client(base_url=base_url, headers=all_headers, timeout=timeout, follow_redirects=follow_redirects,
                                  transport=transport, verify=truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT) if verify else False)
        self._pause, self._max_bytes, self._retry, self._log, self._sleep, self._last = pause, max_bytes, retry, log, sleep, None

    def get(self, url: str, *, params: Mapping[str, str] | None = None, required: bool = False, max_bytes: int | None = None,
            retry_if: Callable[[Reply], str | None] | None = None) -> Reply:
        return self.request("GET", url, params=params, required=required, max_bytes=max_bytes, retry_if=retry_if)

    def request(self, method: str, url: str, *, params: Mapping[str, str] | None = None, json: Any = None, required: bool = False,
                max_bytes: int | None = None, retry_if: Callable[[Reply], str | None] | None = None) -> Reply:
        """`retry_if(reply)` may name a reason to try again although the status is fine (an API that answers 200 with
        "I am lagging"); it counts against the same budget as a busy status."""
        limit, waited, attempt = max_bytes or self._max_bytes, 0.0, 0
        retry = self._retry
        if retry_if and not retry:
            raise ValueError("retry_if needs a retry policy: pass retry=Retry(...) to Web")
        while True:
            attempt += 1
            retry_after = None
            try:
                reply, retry_after = self._once(method, url, params, json, limit)
                reason = f"HTTP {reply.status}"
                if again := retry_if(reply) if retry_if else None:
                    reason = again
                elif not (retry and reply.status in retry.statuses):
                    if reply.status >= 500 or reply.status == 429 or (required and reply.status != 200):
                        raise HttpError(url, reply.status)
                    return reply
            except NetworkError as e:
                if not (retry and retry.network):
                    raise
                reply, reason = None, str(e)
            if waited >= retry.budget:
                message = f"{url}: giving up after {attempt} attempts and {waited:.0f} s of waiting: {reason}"
                raise HttpError(url, reply.status, message, attempt) if reply else NetworkError(message)
            wait = min(self._wait(attempt, retry_after), retry.budget - waited)
            if wait >= retry.say_from and self._log:
                self._log(f"{reason} on {method} {url}: waiting {wait:.0f} s ({waited:.0f} s of {retry.budget:.0f} s waited)")
            self._sleep(wait)
            waited += wait

    def _wait(self, attempt: int, retry_after: str | None) -> float:
        backoff = min(float(2 ** (attempt - 1)), self._retry.max_backoff)
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
                headers = {k.lower(): v for k, v in response.headers.items()}
                reply = Reply(response.status_code, body.decode("utf-8", errors="replace"), headers.get("content-type", ""), headers)
                return reply, headers.get("retry-after")
        except httpx.TransportError as e:
            raise NetworkError(f"{url}: {type(e).__name__}: {e}") from e
        except httpx.HTTPError as e:
            raise SourceError(f"{url}: {e}") from e
        finally:
            self._last = time.monotonic()
