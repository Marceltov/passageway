"""HTTP + MCP front of the recall engine, and the background sync loop.

Routes: GET /health (open), POST /recall (Claude Code hook), /mcp (MCP `recall` tool). The static
Bearer token is PASSAGEWAY_LOGIN_PASSWORD. With PASSAGEWAY_BASE_URL set, /mcp also takes OAuth tokens from a
login with that password (mcp-login-oauth) and the OAuth routes are open; /recall stays static-only.
"""

import asyncio
import contextlib
import hmac
import json
import logging
import os
import sys
import time

import anyio
from fastmcp import FastMCP
from fastmcp.server.auth import OAuthProvider
from mcp_login_oauth import LoginField, LoginOAuthProvider, LoginRejected, build_store
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

from passageway.config import DEFAULT_TOOL_DESCRIPTION, Config, ConfigError, load_config
from passageway.embed import Embedder, EmbedderError
from passageway.index import Index
from passageway.rank import Hit, RankParams, embed_query, rank
from passageway.protocol import Connector
from passageway.render import fit, render
from passageway.sessions import SessionMemory
from passageway.skip import should_skip
from passageway.sync import Syncer

log = logging.getLogger("recall")

VERSION = os.environ.get("APP_VERSION", "dev")
NOTHING = "Nothing relevant in the sources for this query."


class UnknownSource(ValueError):
    pass


class Engine:
    def __init__(self, config: Config, embedder: Embedder, connectors: dict[str, Connector] | None = None):
        self.config = config
        self.embedder = embedder
        self.params = RankParams(min_cos=config.min_similarity) if config.min_similarity is not None else RankParams()
        self.embedder_error: str | None = None
        self.sessions = SessionMemory()
        self.syncers: dict[str, Syncer] = {}
        self.ready: dict[str, bool] = {}
        for cc in config.connectors:
            connector = (connectors or {}).get(cc.name) or Connector(
                cc.name, list(cc.command), env=cc.env, secrets=cc.secrets, timeout=cc.timeout,
                max_line_bytes=cc.max_line_bytes, max_output_bytes=cc.max_output_bytes)
            index = Index(config.data_dir / f"{cc.name}.db", embedder.name, embedder.dim)
            self.syncers[cc.name] = Syncer(cc.name, connector, index, embedder,
                                           max_delete_fraction=cc.max_delete_fraction)
            self.ready[cc.name] = False

    # -- search ------------------------------------------------------------------------------

    def recall(self, query: str, cwd: str | None = None, limit: int = 3, source: str | None = None) -> list[Hit]:
        if source and source not in self.syncers:
            raise UnknownSource(f"Unknown source {source!r}. Configured: {', '.join(self.syncers)}.")
        names = [source] if source else list(self.syncers)
        try:
            qvec = embed_query(self.embedder, query)  # once, not once per source
        except Exception as e:  # the embedder, not a source: no answer is possible, and silence would hide it
            self.embedder_error = f"{type(e).__name__}: {e}"
            log.error("embedding the query failed: %s", self.embedder_error)
            raise e if isinstance(e, EmbedderError) else EmbedderError(f"embedding the query failed: {e}") from e
        self.embedder_error = None
        hits: list[Hit] = []
        for name in names:
            index = self.syncers[name].index
            if not self.ready[name] and index.needs_rebuild():
                continue  # built with another embedder and not rebuilt yet: its vectors cannot be compared
            try:
                hits += rank(name, index, self.embedder, query, cwd, self.params, limit, qvec)
            except Exception:  # one broken source must not take the answers of the others with it
                log.exception("recall failed for source %s", name)
        return sorted(hits, key=lambda h: -h.score)[:limit]

    # -- sync --------------------------------------------------------------------------------

    def _first_sync(self, name: str) -> None:
        syncer = self.syncers[name]
        index = syncer.index
        if index.needs_rebuild() or index.counts()[0] == 0:
            syncer.full_build()
        else:
            syncer.reconcile()
        if syncer.status.last_error is None:
            self.ready[name] = True

    def sync_all_once(self) -> None:
        for name in self.syncers:
            self._first_sync(name)

    def poll_once(self) -> None:
        for name, syncer in self.syncers.items():
            if not self.ready[name]:
                self._first_sync(name)
            else:
                syncer.poll()

    def reconcile_once(self) -> None:
        for name, syncer in self.syncers.items():
            if not self.ready[name]:
                self._first_sync(name)
            else:
                syncer.reconcile()

    async def run_sync_forever(self) -> None:
        last_reconcile = time.monotonic()
        try:
            await anyio.to_thread.run_sync(self.sync_all_once)
        except Exception:  # a source not marked ready is retried by poll_once below
            log.exception("first sync failed")
        while True:
            await asyncio.sleep(self.config.poll_seconds)
            try:
                if time.monotonic() - last_reconcile >= self.config.reconcile_seconds:
                    await anyio.to_thread.run_sync(self.reconcile_once)
                    last_reconcile = time.monotonic()
                else:
                    await anyio.to_thread.run_sync(self.poll_once)
            except Exception:  # never let the loop die; Syncer already records connector errors
                log.exception("sync loop iteration failed")

    def health(self) -> dict:
        sources = {}
        for name, syncer in self.syncers.items():
            items, sections = syncer.index.counts()
            st = syncer.status
            sources[name] = {"items": items, "sections": sections,
                               "last_ok": st.last_ok.isoformat() if st.last_ok else None,
                               "last_error": st.last_error}
        embedder = {"name": self.embedder.name, "dim": self.embedder.dim, "last_error": self.embedder_error}
        if any(v["last_error"] for v in sources.values()) or self.embedder_error:
            status = "degraded"
        elif not all(self.ready.values()):
            status = "starting"
        else:
            status = "ok"
        return {"status": status, "sources": sources, "embedder": embedder, "version": VERSION}


# -- auth ---------------------------------------------------------------------------------------

class BearerGate:
    """Pure ASGI (streamable HTTP must not be buffered). Without OAuth every path but /health needs the
    static token; with OAuth only /recall does, and FastMCP's auth guards /mcp."""

    def __init__(self, app, token: str, oauth: bool = False):
        self.app = app
        self.expected = f"Bearer {token}".encode()
        self.oauth = oauth

    def _gated(self, path: str) -> bool:
        return path == "/recall" if self.oauth else path != "/health"

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and self._gated(scope["path"]):
            given = dict(scope["headers"]).get(b"authorization", b"")
            if not hmac.compare_digest(given, self.expected):
                response = JSONResponse({"error": "unauthorized"}, status_code=401,
                                        headers={"WWW-Authenticate": "Bearer"})
                await response(scope, receive, send)
                return
        await self.app(scope, receive, send)


# -- app ----------------------------------------------------------------------------------------

def build_oauth_provider(config: Config, **overrides) -> LoginOAuthProvider:
    """OAuth login for /mcp whose password is PASSAGEWAY_LOGIN_PASSWORD; the same password also works as a
    static Bearer token. Logins carry no grant: recall has nothing per client to hand to its tools. The
    store's key is the password, so changing it logs every client out."""
    expected = config.password.encode()

    async def check_login(form) -> dict:
        if hmac.compare_digest(form["password"].encode(), expected):
            return {}
        raise LoginRejected("Wrong password.")

    async def verify_static(token: str) -> dict | None:
        return {} if hmac.compare_digest(token.encode(), expected) else None

    args = dict(base_url=config.base_url,
                store=build_store(config.data_dir / "oauth", secret=config.password, salt="passageway-oauth"),
                service_name="Passageway",
                fields=[LoginField("password", "Passageway password", type="password", required=True)],
                check_login=check_login, verify_static=verify_static, token_prefix="pw_")
    return LoginOAuthProvider(**{**args, **overrides})


def build_mcp(engine: Engine, auth: OAuthProvider | None = None) -> FastMCP:
    mcp = FastMCP("passageway", auth=auth, instructions=engine.config.instructions)

    @mcp.tool(description=engine.config.tool_description)
    async def recall(query: str, limit: int = 3, source: str | None = None) -> str:
        try:
            hits = await anyio.to_thread.run_sync(
                lambda: engine.recall(query, None, max(1, min(limit, 3)), source))
        except UnknownSource as e:
            return str(e)
        return render(hits) or NOTHING

    return mcp


def build_app(engine: Engine, background: bool = True, oauth_overrides: dict | None = None) -> BearerGate:
    """`oauth_overrides` passes provider arguments through, for tests (e.g. failed_login_delay=0)."""
    config = engine.config
    auth = build_oauth_provider(config, **(oauth_overrides or {})) if config.base_url else None
    mcp_app = build_mcp(engine, auth).http_app(path="/mcp", host_origin_protection=False)

    async def health(request: Request) -> JSONResponse:
        body = engine.health()
        given = request.headers.get("authorization", "").encode()
        if not hmac.compare_digest(given, f"Bearer {config.password}".encode()):
            # The open endpoint says that a source is failing, not why: connector output can hold hosts and paths.
            for part in (*body["sources"].values(), body["embedder"]):
                if part["last_error"]:
                    part["last_error"] = "failing (authenticate to see the error)"
        return JSONResponse(body)

    async def recall(request: Request) -> JSONResponse:
        try:
            body = json.loads(await request.body())
            prompt = body["prompt"]
            session_id, cwd = body.get("session_id"), body.get("cwd")
            if not isinstance(prompt, str) or not isinstance(session_id, str | None) or not isinstance(cwd, str | None):
                raise TypeError
        except (ValueError, KeyError, TypeError, AttributeError):
            return JSONResponse({"error": "body must be {prompt: str, session_id?: str, cwd?: str}"}, status_code=400)
        if reason := should_skip(prompt):
            return JSONResponse({"context": "", "skipped": reason})
        started = time.perf_counter()
        hits = await anyio.to_thread.run_sync(lambda: engine.recall(prompt, cwd))
        unseen = set(engine.sessions.peek(session_id, [h.item_id for h in hits]))
        # Remember only what the token budget let through; a dropped hit may come next time.
        text, shown = fit([h for h in hits if h.item_id in unseen])
        engine.sessions.record(session_id, [h.item_id for h in shown])
        ms = round((time.perf_counter() - started) * 1000, 1)
        log.info("recall hits=%d ms=%s", len(shown), ms)  # never log the prompt
        return JSONResponse({"context": text, "hits": [h.item_id for h in shown], "ms": ms})

    @contextlib.asynccontextmanager
    async def lifespan(app):
        async with mcp_app.lifespan(app):
            task = asyncio.create_task(engine.run_sync_forever()) if background else None
            try:
                yield
            finally:
                if task:
                    task.cancel()

    app = Starlette(routes=[Route("/health", health), Route("/recall", recall, methods=["POST"]),
                            Mount("/", app=mcp_app)], lifespan=lifespan)
    return BearerGate(app, config.password, oauth=auth is not None)


def build_error_app(message: str) -> Starlette:
    """Started with a broken configuration: say what is wrong instead of dying silently."""
    mcp = FastMCP("passageway")

    @mcp.tool(description=DEFAULT_TOOL_DESCRIPTION)
    def recall(query: str, limit: int = 3, source: str | None = None) -> str:
        return f"The passageway engine is not running: {message}"

    mcp_app = mcp.http_app(path="/mcp", host_origin_protection=False)

    async def health(_: Request) -> JSONResponse:
        return JSONResponse({"status": "error", "error": message}, status_code=503)

    async def unavailable(_: Request) -> JSONResponse:
        return JSONResponse({"error": message}, status_code=503)

    return Starlette(routes=[Route("/health", health), Route("/recall", unavailable, methods=["POST"]),
                            Mount("/", app=mcp_app)], lifespan=mcp_app.lifespan)


def public_message(error: Exception) -> str:
    """What the error page may say: a configuration mistake in full, an embedder's output only as 'see the log'."""
    return getattr(error, "public", str(error))


def main() -> None:
    if sys.argv[1:2] == ["eval"]:  # passageway eval cases.toml: measure retrieval quality instead of serving
        from passageway.eval.cli import main as eval_main

        sys.exit(eval_main(sys.argv[2:]))
    import uvicorn

    from passageway.embed import build_embedder

    logging.basicConfig(level=os.environ.get("PASSAGEWAY_LOG_LEVEL", "INFO"),
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)  # one line per request drowns the log
    try:
        config = load_config(os.environ)
        app = build_app(Engine(config, build_embedder(config.embedder, config.model_dir)))
        host, port = config.host, config.port
    except (ConfigError, OSError) as e:
        log.error("startup failed: %s", e)
        app = build_error_app(public_message(e))
        host, port = os.environ.get("PASSAGEWAY_HOST", "127.0.0.1"), int(os.environ.get("PASSAGEWAY_PORT", "8082") or 8082)
    uvicorn.run(app, host=host, port=port, log_level="warning")


if __name__ == "__main__":
    sys.exit(main())
