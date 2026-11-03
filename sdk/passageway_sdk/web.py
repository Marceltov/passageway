"""A polite, read-only web client for connectors. Needs the extra: `pip install passageway-sdk[web]`."""

import ssl
import time
from collections.abc import Callable
from typing import NamedTuple

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


class TooLarge(SourceError):
    """The reply was larger than the limit."""


class Web:
    """GET with the operating system's trust store (never certifi's bundle), a pause between requests and a size cap.

    A failure to reach the server, or a 5xx or 429, raises SourceError, so a source that is down fails the whole call and
    never looks empty. Any other status is returned for the connector to judge; `required=True` raises on it too.
    """

    def __init__(self, user_agent: str, *, pause: float = 0.2, timeout: float = 30.0, max_bytes: int = 2_000_000,
                 transport: "httpx.BaseTransport | None" = None, sleep: Callable[[float], None] = time.sleep):
        self._http = httpx.Client(headers={"User-Agent": user_agent}, timeout=timeout, follow_redirects=True, transport=transport,
                                  verify=truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT))
        self._pause, self._max_bytes, self._sleep, self._last = pause, max_bytes, sleep, None

    def get(self, url: str, *, required: bool = False, max_bytes: int | None = None) -> Reply:
        limit = max_bytes or self._max_bytes
        if self._last is not None and (wait := self._pause - (time.monotonic() - self._last)) > 0:
            self._sleep(wait)
        try:
            with self._http.stream("GET", url) as response:
                body = bytearray()
                for chunk in response.iter_bytes():
                    body += chunk
                    if len(body) > limit:
                        raise TooLarge(f"{url}: larger than {limit} bytes")
                status, kind = response.status_code, response.headers.get("content-type", "")
        except httpx.HTTPError as e:
            raise SourceError(f"{url}: {e}") from e
        finally:
            self._last = time.monotonic()
        if status >= 500 or status == 429 or (required and status != 200):
            raise SourceError(f"{url}: HTTP {status}")
        return Reply(status, body.decode("utf-8", errors="replace"), kind)
