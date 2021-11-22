__all__ = ("ShinyApp",)

from typing import List, Optional, Union, Dict, Callable, Literal
import re
import os

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from htmltools import Tag, TagList, HTMLDocument, HTMLDependency, RenderedHTML

from .shinysession import ShinySession, session_context
from . import reactcore
from .connmanager import (
    ConnectionManager,
    Connection,
    FastAPIConnectionManager,
    TCPConnectionManager,
)
from .html_dependencies import shiny_deps


class ShinyApp:
    HREF_LIB_PREFIX = "lib/"

    def __init__(
        self, ui: Union[Tag, TagList], server: Callable[[ShinySession], None]
    ) -> None:
        self.ui: RenderedHTML = _render_ui(ui, lib_prefix=self.HREF_LIB_PREFIX)
        self.server: Callable[[ShinySession], None] = server

        self._debug: bool = False

        self._conn_manager: ConnectionManager
        self._sessions: Dict[str, ShinySession] = {}
        self._last_session_id: int = 0  # Counter for generating session IDs

        self._sessions_needing_flush: Dict[int, ShinySession] = {}

        self._registered_dependencies: Dict[str, HTMLDependency] = {}

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

    def run(
        self, conn_type: Literal["websocket", "tcp"] = "websocket", debug: bool = False
    ) -> None:
        self._debug = debug

        if conn_type == "websocket":
            self._conn_manager: ConnectionManager = FastAPIConnectionManager(
                self._on_root_request_cb,
                self._on_connect_cb,
                self._on_session_request_cb,
            )
        elif conn_type == "tcp":
            self._conn_manager: ConnectionManager = TCPConnectionManager(
                self._on_connect_cb
            )
        else:
            raise ValueError(f"Unknown conn_type {conn_type}")

        self._conn_manager.run()

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

    async def _on_connect_cb(self, conn: Connection) -> None:
        """
        Callback passed to the ConnectionManager which is invoked when a new
        connection is established.
        """
        session = self.create_session(conn)

        await session.run()

    async def _on_session_request_cb(self, request: Request) -> Response:
        """
        Callback passed to the ConnectionManager which is invoked when a HTTP
        request for /session/* occurs.
        """
        matches = re.search("^/session/([0-9a-f]+)(/.*)$", request.url.path)
        if matches is None:
            # Exact same response as a "normal" 404 from FastAPI.
            return JSONResponse({"detail": "Not Found"}, status_code=404)

        session_id = matches.group(1)
        subpath = matches.group(2)

        if session_id in self._sessions:
            session: ShinySession = self._sessions[session_id]
            with session_context(session):
                return await session.handle_request(request, subpath)
        else:
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

        prefix = dep.name + "-" + str(dep.version)
        prefix = os.path.join(ShinyApp.HREF_LIB_PREFIX, prefix)
        if isinstance(self._conn_manager, FastAPIConnectionManager):
            self._conn_manager._fastapi_app.mount(
                "/" + prefix, StaticFiles(directory=dep.get_source_dir()), name=prefix
            )
        self._registered_dependencies[dep.name] = dep


def _render_ui(ui: Union[Tag, TagList], lib_prefix: Optional[str]) -> RenderedHTML:
    ui.append(shiny_deps())
    doc = HTMLDocument(ui)
    res = doc.render(lib_prefix=lib_prefix)
    return res
