from typing import Union, Callable, Any
import re

from fastapi import Request, Response
from fastapi.responses import JSONResponse

from .shinysession import ShinySession, Outputs, session_context
from .reactives import ReactiveValues
from . import reactcore
from .connmanager import ConnectionManager, Connection, FastAPIConnectionManager, TCPConnectionManager


class ShinyApp:
    def __init__(self, ui: Any, server: Callable[[ReactiveValues, Outputs], None]) -> None:
        self.ui: Any = ui
        self.server: Callable[[ReactiveValues, Outputs], None] = server
        self._sessions: dict[str, ShinySession] = {}
        self._last_session_id: int = 0    # Counter for generating session IDs

        self._sessions_needing_flush: dict[int, ShinySession] = {}

    def create_session(self, conn: Connection) -> ShinySession:
        self._last_session_id += 1
        id = str(self._last_session_id)
        session = ShinySession(self, id, conn)
        self._sessions[id] = session
        return session

    def remove_session(self, session: Union[ShinySession, str]) -> None:
        if (isinstance(session, ShinySession)):
            session = session.id

        print(f"remove_session: {session}")
        del self._sessions[session]

    def run(self, conn_type: str = "websocket") -> None:
        if (conn_type == "websocket"):
            self._conn_manager: ConnectionManager = \
                FastAPIConnectionManager(self._on_connect_cb, self._on_session_request_cb)
        elif (conn_type == "tcp"):
            self._conn_manager: ConnectionManager = TCPConnectionManager(self._on_connect_cb)
        else:
            raise ValueError(f"Unknown conn_type {conn_type}")

        if type(self.ui) is str:
            self._conn_manager.set_ui_path(self.ui)

        self._conn_manager.run()

    async def _on_connect_cb(self, conn: Connection) -> None:
        """Callback passed to the ConnectionManager, which is invoked when a new
        connection is established."""
        session = self.create_session(conn)

        await session.run()

    async def _on_session_request_cb(self, request: Request) -> Response:
        matches = re.search("^/session/([0-9a-f]+)(/.*)$", request.url.path)
        if matches is None:
            # Exact same response as a "normal" 404 from FastAPI.
            return JSONResponse({"detail":"Not Found"}, status_code=404)

        session_id = matches.group(1)
        subpath = matches.group(2)

        if session_id in self._sessions:
            session: ShinySession = self._sessions[session_id]
            with session_context(session):
                return await session.handle_request(request, subpath)
        else:
            return JSONResponse({"detail":"Not Found"}, status_code=404)

    def request_flush(self, session: ShinySession) -> None:
        # TODO: Until we have reactive domains, because we can't yet keep track
        # of which sessions need a flush.
        pass
        # self._sessions_needing_flush[session.id] = session

    async def flush_pending_sessions(self) -> None:
        await reactcore.flush()

        # TODO: Until we have reactive domains, flush all sessions (because we
        # can't yet keep track of which ones need a flush)
        for id, session in self._sessions.items():
            await session.flush()
        # for id, session in self._sessions_needing_flush.items():
        #     await session.flush()
        #     del self._sessions_needing_flush[id]
