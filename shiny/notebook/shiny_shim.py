# pyright: reportUnknownMemberType=false
import asyncio
import json
from typing import Any, Awaitable, Callable, Optional, Tuple

import comm  # pyright: ignore[reportMissingTypeStubs]
from starlette.requests import HTTPConnection

from shiny import App, ui
from shiny._connection import Connection, ConnectionClosed
from shiny.session import Session

from .log import logger


def create_kernel_session(
    id: str,
) -> Tuple[Session, Callable[[Connection], Awaitable[None]]]:
    # app: App, id: str, conn: Connection, debug: bool = False
    app = App(ui.TagList(), None)
    iconn = IndirectConnection()
    return Session(app, id, iconn, debug=False), iconn.set_conn


class IndirectConnection(Connection):
    def __init__(self):
        self._conn: Optional[Connection] = None
        # Notifies when the connection is set
        self._conn_event = asyncio.Event()
        self._pending_messages: list[str] = []
        self._closed = False

    async def set_conn(self, conn: Connection) -> None:
        logger.debug("IndirectConnect.set_conn: Setting connection")
        self._conn = conn
        self._conn_event.set()
        while len(self._pending_messages) > 0:
            await self.send(self._pending_messages.pop(0))

    async def send(self, message: str) -> None:
        if self._closed:
            return

        if self._conn is None:
            self._pending_messages.append(message)
        else:
            await self._conn.send(message)

    async def receive(self) -> str:
        logger.debug("IndirectionConnection.receive: begin")
        while self._conn is None and not self._closed:
            logger.debug("IndirectionConnection.receive: waiting for connection")
            await self._conn_event.wait()

        logger.debug("IndirectionConnection.receive: Got connection OR closed")
        # If we get here, either self._conn is not None OR self._closed is true

        if self._closed:
            raise ConnectionClosed()
        if self._conn is not None:
            logger.debug("IndirectionConnection.receive: actually receiving")
            try:
                return await self._conn.receive()
            finally:
                logger.debug("IndirectionConnection.receive: finally")

        raise RuntimeError("This should be unreachable")

    async def close(self, code: int, reason: str | None) -> None:
        self._closed = True
        self._conn_event.set()
        if self._conn is not None:
            return await self._conn.close(code, reason)

    def get_http_conn(self) -> HTTPConnection:
        if not self._conn:
            # No idea what to do here
            return HTTPConnection(scope={"type": "websocket", "headers": {}})
        return self._conn.get_http_conn()


class JupyterKernelConnection(Connection):
    def __init__(self, comm: comm.BaseComm):
        self._comm = comm
        self._queue: asyncio.Queue[str | None] = asyncio.Queue()
        self._http_conn = HTTPConnection(scope={"type": "websocket", "headers": {}})

        comm.on_msg(self._on_msg)
        comm.on_close(self._on_close)

    def _on_msg(self, msg: Any) -> None:
        # TODO: Don't do this extra serialization/deserialization
        self._queue.put_nowait(json.dumps(msg["content"]["data"]))

    def _on_close(self, msg: Any) -> None:
        # TODO: Handle this by getting self.receive() to raise ConnectionClosed
        self._queue.put_nowait(None)

    async def send(self, message: str) -> None:
        # TODO: Don't do this extra serialization/deserialization
        self._comm.send(json.loads(message))

    async def receive(self) -> str:
        res = await self._queue.get()
        if res is None:
            raise ConnectionClosed()
        return res

    async def close(self, code: int, reason: Optional[str]) -> None:
        logger.debug("Shiny's Connection.close was called")
        self._comm.close({"code": code, "reason": reason})

    def get_http_conn(self) -> HTTPConnection:
        return self._http_conn
