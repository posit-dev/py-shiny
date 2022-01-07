__all__ = ("ShinyApp",)

from typing import Any, List, Optional, Union, Dict, Callable, cast

from htmltools import Tag, TagList, HTMLDocument, HTMLDependency, RenderedHTML

import starlette.routing
import starlette.websockets
from starlette.types import Message, Receive, Scope, Send
from starlette.requests import Request
from starlette.responses import Response, HTMLResponse, JSONResponse

from .http_staticfiles import StaticFiles
from .shinysession import ShinySession, session_context
from . import reactcore
from .connmanager import (
    Connection,
    StarletteConnection,
)
from .html_dependencies import jquery_deps, shiny_deps


class ShinyApp:
    LIB_PREFIX = "lib/"

    def __init__(
        self,
        ui: Union[Tag, TagList],
        server: Callable[[ShinySession], None],
        *,
        debug: bool = False,
    ) -> None:
        self.ui: RenderedHTML = _render_page(ui, lib_prefix=self.LIB_PREFIX)
        self.server: Callable[[ShinySession], None] = server

        self._debug: bool = debug

        self._sessions: Dict[str, ShinySession] = {}
        self._last_session_id: int = 0  # Counter for generating session IDs

        self._sessions_needing_flush: Dict[int, ShinySession] = {}

        self._registered_dependencies: Dict[str, HTMLDependency] = {}
        self._dependency_handler: Any = starlette.routing.Router()

        self.starlette_app = starlette.routing.Router(
            routes=[
                starlette.routing.WebSocketRoute("/websocket/", self._on_connect_cb),
                starlette.routing.Route("/", self._on_root_request_cb, methods=["GET"]),
                starlette.routing.Route(
                    "/session/{session_id}/{subpath:path}",
                    self._on_session_request_cb,
                    methods=["GET", "POST"],
                ),
                starlette.routing.Mount("/", app=self._dependency_handler),
            ]
        )

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
        import uvicorn  # type: ignore

        if debug is not None:
            self._debug = debug
        uvicorn.run(cast(Any, self), host="0.0.0.0", port=8000)

    # ASGI entrypoint. Handles HTTP, WebSocket, and lifespan.
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await self.starlette_app(scope, receive, send)

    async def call_pyodide(self, scope: Scope, receive: Receive, send: Send) -> None:
        # TODO: Pretty sure there are objects that need to be destroy()'d here?
        scope = cast(Any, scope).to_py()

        # ASGI requires some values to be byte strings, not character strings. Those are
        # not that easy to create in JavaScript, so we let the JS side pass us strings
        # and we convert them to bytes here.
        if "headers" in scope:
            # JS doesn't have `bytes` so we pass as strings and convert here
            scope["headers"] = [
                [value.encode("latin-1") for value in header]
                for header in scope["headers"]
            ]
        if "query_string" in scope and scope["query_string"]:
            scope["query_string"] = scope["query_string"].encode("latin-1")
        if "raw_path" in scope and scope["raw_path"]:
            scope["raw_path"] = scope["raw_path"].encode("latin-1")

        async def rcv() -> Message:
            event = await receive()
            return cast(Message, cast(Any, event).to_py())

        async def snd(event: Message):
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
    async def _on_root_request_cb(self, request: Request) -> Response:
        """
        Callback passed to the ConnectionManager which is invoked when a HTTP
        request for / occurs.
        """
        self._ensure_web_dependencies(self.ui["dependencies"])
        return HTMLResponse(content=self.ui["html"])

    async def _on_connect_cb(self, ws: starlette.websockets.WebSocket) -> None:
        """
        Callback which is invoked when a new WebSocket connection is established.
        """
        await ws.accept()
        conn = StarletteConnection(ws)
        session = self.create_session(conn)

        await session.run()

    async def _on_session_request_cb(self, request: Request) -> Response:
        """
        Callback passed to the ConnectionManager which is invoked when a HTTP
        request for /session/* occurs.
        """
        session_id: str = request.path_params["session_id"]  # type: ignore
        # subpath: str = request.path_params["subpath"]

        if session_id in self._sessions:
            session: ShinySession = self._sessions[session_id]
            with session_context(session):
                return await session.handle_request(request)

        return JSONResponse({"detail": "Not Found"}, status_code=404)

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

        paths = dep.source_path_map(lib_prefix=self.LIB_PREFIX)
        self._dependency_handler.mount(
            "/" + paths["href"],
            StaticFiles(directory=paths["source"]),
            name=dep.name + "-" + str(dep.version),
        )
        self._registered_dependencies[dep.name] = dep


def _render_page(ui: Union[Tag, TagList], lib_prefix: str) -> RenderedHTML:
    doc = HTMLDocument(TagList(jquery_deps(), shiny_deps(), ui))
    return doc.render(lib_prefix=lib_prefix)
