import asyncio
from abc import ABC, abstractmethod
from typing import Optional

import starlette.websockets
from starlette.websockets import WebSocketState
from starlette.requests import HTTPConnection

from ._shinyenv import is_pyodide
from ._asyncutils import run_elsewhere
from . import _utils


class Connection(ABC):
    """Abstract class to serve a session and send/receive messages to the
    client."""

    @abstractmethod
    def send(self, message: str) -> None:
        ...

    @abstractmethod
    async def receive(self) -> str:
        ...

    @abstractmethod
    async def close(self, code: int, reason: Optional[str]) -> None:
        ...

    @abstractmethod
    def get_http_conn(self) -> HTTPConnection:
        ...


class MockConnection(Connection):
    def __init__(self):
        # This currently hard-codes some basic values for scope. In the future, we could
        # make those more configurable if we need to customize the HTTPConnection (like
        # "scheme", "path", and "query_string").
        self._http_conn = HTTPConnection(scope={"type": "websocket", "headers": {}})

    def send(self, message: str) -> None:
        pass

    # I should say I’m not 100% that the receive method can be a no-op for our testing
    # purposes. It might need to be asyncio.sleep(0), and/or it might need an external
    # way to yield until we tell the connection to continue, so that the run loop can
    # continue.
    async def receive(self) -> str:
        # Sleep forever
        await asyncio.Event().wait()
        raise RuntimeError("make the type checker happy")

    async def close(self, code: int, reason: Optional[str]) -> None:
        pass

    def get_http_conn(self) -> HTTPConnection:
        return self._http_conn


class ThreadedStarletteConnection(Connection):
    def __init__(self, conn: starlette.websockets.WebSocket):
        self.conn: starlette.websockets.WebSocket = conn
        self.event_loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()

    def send(self, message: str) -> None:
        if self._is_closed():
            return

        asyncio.run_coroutine_threadsafe(self.conn.send_text(message), self.event_loop)

    async def receive(self) -> str:
        if self._is_closed():
            raise ConnectionClosed()

        try:
            return await run_elsewhere(self.conn.receive_text(), self.event_loop)
        except starlette.websockets.WebSocketDisconnect:
            raise ConnectionClosed()

    async def close(self, code: int, reason: Optional[str]) -> None:
        if self._is_closed():
            return

        # TODO: Figure out how to await this
        await run_elsewhere(self.conn.close(code), self.event_loop)

    def _is_closed(self) -> bool:
        return (
            self.conn.application_state == WebSocketState.DISCONNECTED  # type: ignore
            or self.conn.client_state == WebSocketState.DISCONNECTED  # type: ignore
        )

    def get_http_conn(self) -> HTTPConnection:
        return self.conn


class PyodideStarletteConnection(Connection):
    def __init__(self, conn: starlette.websockets.WebSocket):
        self.conn: starlette.websockets.WebSocket = conn

    def send(self, message: str) -> None:
        if self._is_closed():
            return

        # The pyodide impl of send_text is guaranteed not to yield
        _utils.run_coro_sync(self.conn.send_text(message))

    async def receive(self) -> str:
        if self._is_closed():
            raise ConnectionClosed()

        try:
            return await self.conn.receive_text()
        except starlette.websockets.WebSocketDisconnect:
            raise ConnectionClosed()

    async def close(self, code: int, reason: Optional[str]) -> None:
        if self._is_closed():
            return

        # TODO: Figure out how to await this
        await self.conn.close(code)

    def _is_closed(self) -> bool:
        return (
            self.conn.application_state == WebSocketState.DISCONNECTED  # type: ignore
            or self.conn.client_state == WebSocketState.DISCONNECTED  # type: ignore
        )

    def get_http_conn(self) -> HTTPConnection:
        return self.conn


if is_pyodide:
    StarletteConnection = PyodideStarletteConnection
else:
    StarletteConnection = ThreadedStarletteConnection


class ConnectionClosed(Exception):
    """Raised when a Connection is closed from the other side."""

    pass
