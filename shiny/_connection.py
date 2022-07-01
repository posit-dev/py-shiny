import asyncio
from abc import ABC, abstractmethod
from typing import Optional

import starlette.websockets
from starlette.websockets import WebSocketState
from starlette.requests import HTTPConnection


class Connection(ABC):
    """Abstract class to serve a session and send/receive messages to the
    client."""

    @abstractmethod
    async def send(self, message: str) -> None:
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
        self._queue: asyncio.Queue[str] = asyncio.Queue()

    async def send(self, message: str) -> None:
        pass

    async def receive(self) -> str:
        msg = await self._queue.get()
        if msg == "":
            raise ConnectionClosed()
        return msg

    async def close(self, code: int, reason: Optional[str]) -> None:
        pass

    def get_http_conn(self) -> HTTPConnection:
        return self._http_conn

    def cause_receive(self, message: str) -> None:
        """Call from tests to simulate the other side sending a message"""
        self._queue.put_nowait(message)

    def cause_disconnect(self) -> None:
        """Call from tests to simulate the other side disconnecting"""
        self.cause_receive("")


class StarletteConnection(Connection):
    conn: starlette.websockets.WebSocket

    def __init__(self, conn: starlette.websockets.WebSocket):
        self.conn: starlette.websockets.WebSocket = conn

    async def accept(self, subprotocol: Optional[str] = None):
        await self.conn.accept(subprotocol)  # type: ignore

    async def send(self, message: str) -> None:
        if self._is_closed():
            return

        await self.conn.send_text(message)

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

        await self.conn.close(code)

    def _is_closed(self) -> bool:
        return (
            self.conn.application_state == WebSocketState.DISCONNECTED  # type: ignore
            or self.conn.client_state == WebSocketState.DISCONNECTED  # type: ignore
        )

    def get_http_conn(self) -> HTTPConnection:
        return self.conn


class ConnectionClosed(Exception):
    """Raised when a Connection is closed from the other side."""

    pass
