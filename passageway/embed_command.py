"""An embedder that is a program of its own: one long-lived process speaking JSON Lines (docs/reference/embedder-protocol.md)."""

import atexit
import json
import logging
import os
import queue
import subprocess
import threading
import time
from collections import deque
from collections.abc import Mapping, Sequence

import numpy as np

from passageway.embed import EmbedderError
from passageway.protocol import PROTOCOL_VERSION, _kill

_STDERR_LINES = 5
_EOF = object()


class _Died(Exception):
    """The process ended while a request was open."""


class _Process:
    """One started process: its pipes, a thread that reads its output into a queue, and the tail of its error output."""

    def __init__(self, proc: subprocess.Popen, mask, limit: int, log: logging.Logger):
        self.proc = proc
        self.lines: queue.Queue = queue.Queue()
        self.tail: deque[str] = deque(maxlen=_STDERR_LINES)

        def read_stdout() -> None:
            for raw in iter(lambda: proc.stdout.readline(limit + 2), b""):
                self.lines.put(raw)
            self.lines.put(_EOF)

        def read_stderr() -> None:
            for raw in proc.stderr:
                line = mask(raw.decode(errors="replace").rstrip())
                self.tail.append(line)
                log.info("%s", line)

        self._stderr_thread = threading.Thread(target=read_stderr, daemon=True)
        threading.Thread(target=read_stdout, daemon=True).start()
        self._stderr_thread.start()

    def stderr_tail(self) -> str:
        self._stderr_thread.join(timeout=2)  # the process is gone or going: let its last words arrive
        return " | ".join(self.tail)

    def stop(self, grace: float = 0.0) -> None:
        proc = self.proc
        if grace:  # a polite end: close its input and give it a moment
            try:
                proc.stdin.close()
            except OSError:
                pass
            try:
                proc.wait(timeout=grace)
            except subprocess.TimeoutExpired:
                pass
        if proc.poll() is None:
            _kill(proc)  # first: a writer blocked on a full pipe holds the lock that closing stdin would wait for
        proc.wait()  # reap it: a killed child that nobody waits for stays a zombie
        try:
            proc.stdin.close()
        except (OSError, ValueError):
            pass


class CommandEmbedder:
    """name and dim come from the process (`info`); the vectors are normalised here, whatever the process sends."""

    def __init__(self, label: str, command: Sequence[str], *, env: Mapping[str, str] | None = None,
                 secrets: Mapping[str, str] | None = None, batch_size: int = 32, timeout: float = 60.0,
                 max_line_bytes: int = 64 * 1024 * 1024):
        self._label, self._command = label, list(command)
        self._env, self._secrets = dict(env or {}), dict(secrets or {})
        self._batch, self._timeout, self._max_line = batch_size, timeout, max_line_bytes
        self._log = logging.getLogger(f"embedder.{label}")
        self._lock = threading.RLock()
        self._state: _Process | None = None
        self._closed = False
        with self._lock:
            self._start(first=True)
        atexit.register(self.close)

    # -- the Embedder interface ------------------------------------------------------------------

    def embed_queries(self, texts: list[str]):
        return self._embed("query", texts)

    def embed_passages(self, texts: list[str]):
        return self._embed("passage", texts)

    def close(self) -> None:
        with self._lock:
            self._closed = True
            if self._state is not None:
                self._state.stop(grace=2.0)
                self._state = None
        atexit.unregister(self.close)

    # -- requests ------------------------------------------------------------------------------------

    def _fail(self, message: str) -> EmbedderError:
        return EmbedderError(f"embedder '{self._label}': {message}")

    def _mask(self, text: str) -> str:
        for value in self._secrets.values():
            if value:
                text = text.replace(value, "***")
        return text

    def _spawn(self) -> _Process:
        env = {k: os.environ[k] for k in ("PATH", "HOME") if k in os.environ}
        env.update(self._env)
        env.update(self._secrets)
        env["PASSAGEWAY_PROTOCOL"] = PROTOCOL_VERSION
        try:
            proc = subprocess.Popen(self._command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    env=env, start_new_session=True)
        except OSError as e:
            raise self._fail(f"cannot start {self._command[0]!r}: {e.strerror or e}") from None
        return _Process(proc, self._mask, self._max_line, self._log)

    def _drop(self) -> None:
        if self._state is not None:
            self._state.stop()
            self._state = None

    def _start(self, *, first: bool = False) -> None:
        """Start the process and ask it who it is; after a restart it must be the same embedder."""
        self._state = self._spawn()
        try:
            reply = self._ask({"op": "info"})
        except _Died:
            tail = self._state.stderr_tail()
            self._drop()
            raise self._fail(f"the process ended before it answered: {tail or 'no error output'}") from None
        except EmbedderError:
            self._drop()
            raise
        name, dim, protocol = reply.get("name"), reply.get("dim"), reply.get("protocol", PROTOCOL_VERSION)
        if protocol != PROTOCOL_VERSION:
            self._drop()
            raise self._fail(f"speaks protocol {protocol!r}, this core speaks {PROTOCOL_VERSION!r}")
        if not (isinstance(name, str) and name and isinstance(dim, int) and not isinstance(dim, bool) and dim >= 1):
            self._drop()
            raise self._fail("info must answer {\"name\": a non-empty string, \"dim\": a whole number from 1}")
        if first:
            self.name, self.dim = name, dim
        elif (name, dim) != (self.name, self.dim):
            self._drop()
            raise self._fail(f"after a restart the embedder identifies as {name!r} ({dim} dimensions), but the index was "
                             f"built with {self.name!r} ({self.dim}): its identity must not change while passageway runs")

    def _ask(self, request: dict) -> dict:
        state = self._state
        deadline = time.monotonic() + self._timeout
        failed: list[BaseException] = []

        def write() -> None:
            try:
                state.proc.stdin.write((json.dumps(request) + "\n").encode())
                state.proc.stdin.flush()
            except (BrokenPipeError, OSError, ValueError) as e:  # ValueError: the pipe was closed under us
                failed.append(e)

        # In a thread of its own: a process that does not read leaves a request bigger than the pipe blocked in write().
        writer = threading.Thread(target=write, daemon=True)
        writer.start()
        writer.join(timeout=self._timeout)
        if writer.is_alive():
            self._drop()  # killing the process closes the pipe and frees the writer
            raise self._fail(f"{request['op']} timed out after {self._timeout:g} s (the process does not read its input)")
        if failed:
            raise _Died
        try:
            raw = state.lines.get(timeout=max(deadline - time.monotonic(), 0.001))
        except queue.Empty:
            self._drop()  # a hung process is killed; the next call starts a fresh one
            raise self._fail(f"{request['op']} timed out after {self._timeout:g} s") from None
        if raw is _EOF:
            raise _Died
        if len(raw.rstrip(b"\r\n")) > self._max_line:
            self._drop()  # the rest of the line is still in the pipe: the stream cannot be trusted any more
            raise self._fail(f"a reply is longer than {self._max_line} bytes")
        try:
            reply = json.loads(raw)
            if not isinstance(reply, dict):
                raise ValueError("a reply must be a JSON object")
        except ValueError as e:
            # a line that is not a reply (a log line on stdout, say) means the real reply is still queued and would be
            # read as the answer to the next request: nothing from this process can be trusted any more
            self._drop()
            raise self._fail(f"a reply is not valid JSON: {e}; the process was stopped") from None
        if "error" in reply:
            raise self._fail(self._mask(str(reply["error"])))
        return reply

    def _request(self, request: dict) -> dict:
        with self._lock:
            if self._closed:
                raise self._fail("this embedder is closed")
            starts = 0  # a call may start the process once (it died, was killed or timed out) and ask again
            while True:
                if self._state is None or self._state.proc.poll() is not None:
                    self._drop()
                    self._start()
                    starts += 1
                try:
                    return self._ask(request)
                except _Died:
                    tail = self._state.stderr_tail()
                    self._drop()
                    if starts:
                        raise self._fail(f"the process died: {tail or 'no error output'}") from None

    def _embed(self, kind: str, texts: list[str]):
        if not texts:
            return np.zeros((0, self.dim), dtype=np.float32)
        parts = []
        for i in range(0, len(texts), self._batch):
            batch = texts[i:i + self._batch]
            reply = self._request({"op": "embed", "kind": kind, "texts": batch})
            try:
                parts.append(self._vectors(reply, len(batch)))
            except EmbedderError:
                with self._lock:
                    self._drop()  # an answer of the wrong shape: the stream may be out of step
                raise
        return np.vstack(parts)

    def _vectors(self, reply: dict, expected: int):
        vectors = reply.get("vectors")
        if not isinstance(vectors, list) or len(vectors) != expected:
            raise self._fail(f"expected {{\"vectors\": [...]}} with {expected} vectors, got "
                             f"{len(vectors) if isinstance(vectors, list) else type(vectors).__name__}")
        if not all(isinstance(v, list) and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in v)
                   for v in vectors):
            raise self._fail("every vector must be a list of numbers")
        array = np.array(vectors, dtype=np.float64)
        if array.shape != (expected, self.dim):
            raise self._fail(f"expected vectors with {self.dim} dimensions, got shape {array.shape}")
        if not np.isfinite(array).all():
            raise self._fail("a vector holds a value that is not a finite number")
        with np.errstate(over="raise"):
            try:
                norms = np.linalg.norm(array, axis=1, keepdims=True)
            except FloatingPointError:
                raise self._fail("a vector holds values too large to be normalised to finite numbers") from None
        if (norms == 0).any() or not np.isfinite(norms).all():
            raise self._fail("a vector has zero length or values too large to be normalised to finite numbers")
        return (array / norms).astype(np.float32)
