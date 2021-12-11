__all__ = ("ShinyApp",)

from typing import Any, List, Optional, Union, Dict, Callable, cast
import re
import os
from asgiref.typing import (
    ASGI3Application,
    ASGIReceiveCallable,
    ASGIReceiveEvent,
    ASGISendCallable,
    ASGISendEvent,
    Scope,
    HTTPScope,
)

from htmltools import Tag, TagList, HTMLDocument, HTMLDependency, RenderedHTML
import starlette.routing

from shiny.responses import HTMLResponse, JSONResponse, TextResponse

from .http_staticfiles import StaticFiles
from .shinysession import ShinySession, session_context
from . import reactcore
from .connmanager import (
    ASGIConnection,
    Connection,
)
from .html_dependencies import jquery_deps, shiny_deps


class ShinyApp:
    HREF_LIB_PREFIX = "lib/"

    def __init__(
        self,
        ui: Union[Tag, TagList],
        server: Callable[[ShinySession], None],
        *,
        debug: bool = False,
    ) -> None:
        self.ui: RenderedHTML = _render_ui(ui, lib_prefix=self.HREF_LIB_PREFIX)
        self.server: Callable[[ShinySession], None] = server

        self._debug: bool = debug

        self._sessions: Dict[str, ShinySession] = {}
        self._last_session_id: int = 0  # Counter for generating session IDs

        self._sessions_needing_flush: Dict[int, ShinySession] = {}

        self._registered_dependencies: Dict[str, HTMLDependency] = {}
        self._dependency_handler: Any = starlette.routing.Router()

    def create_session(self, conn: Connection) -> ShinySession:
        self._last_session_id += 1
        id = str(self._last_session_id)
        session = ShinySession(self, id, conn, debug=self._debug)
        self._sessions[id] = session
        return session

    def remove_session(self, session: Union[ShinySession, str]) -> None:
        if isinstance(session, ShinySession):
            session = session.id

        if self._debug:
            print(f"remove_session: {session}")
        del self._sessions[session]

    def run(self, debug: Optional[bool] = None) -> None:
        import uvicorn

        if debug is not None:
            self._debug = debug
        uvicorn.run(self, host="0.0.0.0", port=8000)

    # ASGI entrypoint. Handles HTTP, WebSocket, and lifespan.
    async def __call__(
        self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable
    ) -> None:
        if scope["type"] == "http":
            if scope["method"] == "GET":
                if scope["path"] == "/":
                    return await self._on_root_request_cb(scope, receive, send)
            if re.search("^/session/", scope["path"]):
                return await self._on_session_request_cb(scope, receive, send)

            return await cast(ASGI3Application, self._dependency_handler)(
                scope, receive, send
            )

            return await TextResponse("Not found", status_code=404)(
                scope, receive, send
            )
        elif scope["type"] == "websocket":
            conn = ASGIConnection(scope, receive, send)
            await conn.accept()
            await self._on_connect_cb(conn)
        elif scope["type"] == "lifespan":
            while True:
                message = await receive()
                if message["type"] == "lifespan.startup":
                    await send({"type": "lifespan.startup.complete"})
                elif message["type"] == "lifespan.shutdown":
                    await self.stop()
                    await send({"type": "lifespan.shutdown.complete"})
                    return
        else:
            raise Exception(f"Unexpected scope type: {scope['type']}")

    async def call_pyodide(
        self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable
    ) -> None:
        # TODO: Pretty sure there are objects that need to be destroy()'d here?
        scope = cast(Any, scope).to_py()

        async def rcv() -> ASGIReceiveEvent:
            event = await receive()
            return cast(ASGIReceiveEvent, cast(Any, event).to_py())

        async def snd(event: ASGISendEvent):
            await send(event)

        await self(scope, rcv, snd)

    async def stop(self) -> None:
        # Close all sessions (convert to list to avoid modifying the dict while
        # iterating over it, which throws an error).
        for session in list(self._sessions.values()):
            await session.close()

    # ==========================================================================
    # Connection callbacks
    # ==========================================================================
    async def _on_root_request_cb(
        self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable
    ) -> None:
        """
        Callback passed to the ConnectionManager which is invoked when a HTTP
        request for / occurs.
        """
        self._ensure_web_dependencies(self.ui["dependencies"])
        resp = HTMLResponse(content=self.ui["html"])
        await resp(scope, receive, send)

    async def _on_connect_cb(self, conn: Connection) -> None:
        """
        Callback passed to the ConnectionManager which is invoked when a new
        connection is established.
        """
        session = self.create_session(conn)

        await session.run()

    async def _on_session_request_cb(
        self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable
    ) -> None:
        """
        Callback passed to the ConnectionManager which is invoked when a HTTP
        request for /session/* occurs.
        """

        http_scope: HTTPScope = cast(HTTPScope, scope)
        matches = re.search("^/session/([0-9a-f]+)(/.*)$", http_scope["path"])
        if matches is None:
            # Exact same response as a "normal" 404 from FastAPI.
            resp = JSONResponse({"detail": "Not Found"}, status_code=404)
            return await resp(scope, receive, send)

        session_id = matches.group(1)
        subpath = matches.group(2)

        if session_id in self._sessions:
            session: ShinySession = self._sessions[session_id]
            with session_context(session):
                return await session.handle_request(scope, receive, send, subpath)

        resp = JSONResponse({"detail": "Not Found"}, status_code=404)
        await resp(scope, receive, send)

    # ==========================================================================
    # Flush
    # ==========================================================================
    def request_flush(self, session: ShinySession) -> None:
        # TODO: Until we have reactive domains, because we can't yet keep track
        # of which sessions need a flush.
        pass
        # self._sessions_needing_flush[session.id] = session

    async def flush_pending_sessions(self) -> None:
        await reactcore.flush()

        # TODO: Until we have reactive domains, flush all sessions (because we
        # can't yet keep track of which ones need a flush)
        for _, session in self._sessions.items():
            await session.flush()
        # for id, session in self._sessions_needing_flush.items():
        #     await session.flush()
        #     del self._sessions_needing_flush[id]

    # ==========================================================================
    # HTML Dependency stuff
    # ==========================================================================
    def _ensure_web_dependencies(self, deps: List[HTMLDependency]) -> None:
        for dep in deps:
            self.register_web_dependency(dep)

    def register_web_dependency(self, dep: HTMLDependency) -> None:
        if (
            dep.name in self._registered_dependencies
            and dep.version >= self._registered_dependencies[dep.name].version
        ):
            return

        prefix = dep.name + "-" + str(dep.version)
        prefix = os.path.join(ShinyApp.HREF_LIB_PREFIX, prefix)

        self._dependency_handler.mount(
            "/" + prefix, StaticFiles(directory=dep.get_source_dir()), name=prefix
        )
        self._registered_dependencies[dep.name] = dep


def _render_ui(ui: Union[Tag, TagList], lib_prefix: Optional[str]) -> RenderedHTML:
    doc = HTMLDocument(TagList(jquery_deps(), shiny_deps(), ui))
    res = doc.render(lib_prefix=lib_prefix)
    return res
