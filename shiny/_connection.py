from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import Optional

import starlette.websockets
from starlette.requests import HTTPConnection
from starlette.websockets import WebSocketState


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
        self._closed = False

    async def accept(self, subprotocol: Optional[str] = None):
        await self.conn.accept(subprotocol)  # type: ignore

    async def send(self, message: str) -> None:
        if self._is_closed():
            return

        try:
            await self.conn.send_text(message)
            return
        # For the record, websockets.exceptions.ConnectionClosed is one exception I see
        # when hammering on the browser reload button
        except Exception:
            # The contract of WebSocket.send() is to never throw (unless the websocket
            # is not yet connected; sending a message after the ws has closed is OK.)
            # However, it's also not very safe to keep using this websocket if we can't
            # be sure they've received this message. So close it, and then continue as
            # if nothing is wrong.
            if not self._is_closed():
                await self.close(1008, "Send failure")
            return

    async def receive(self) -> str:
        if self._is_closed():
            raise ConnectionClosed()

        try:
            return await self.conn.receive_text()
        except starlette.websockets.WebSocketDisconnect:
            raise ConnectionClosed()
        except Exception:
            # From RFC6455:
            # 1008 indicates that an endpoint is terminating the connection because it
            # has received a message that violates its policy.  This is a generic status
            # code that can be returned when there is no other more suitable status code
            # (e.g., 1003 or 1009) or if there is a need to hide specific details about
            # the policy.
            try:
                await self.close(1008, "Receive operation failed")
            except Exception:
                pass
            raise

    async def close(self, code: int, reason: Optional[str]) -> None:
        if self._is_closed():
            return

        # Even if self.conn.close() fails, treat this as closed.
        self._closed = True

        try:
            await self.conn.close(code)
        except Exception:
            # WebSocket failed to close (usually because it already terminated in some
            # unusual fashion); ignoring because the contract of WebSocket.close() is to
            # never throw. (Not in Python, but in the browser, and it's pretty hard to
            # reason about otherwise.)
            pass

    def _is_closed(self) -> bool:
        return (
            self.conn.application_state == WebSocketState.DISCONNECTED  # type: ignore
            or self.conn.client_state == WebSocketState.DISCONNECTED  # type: ignore
            or self._closed
        )

    def get_http_conn(self) -> HTTPConnection:
        return self.conn


class ConnectionClosed(Exception):
    """Raised when a Connection is closed from the other side."""

    pass
