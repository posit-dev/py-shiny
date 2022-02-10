from abc import ABC, abstractmethod
import asyncio
from typing import Optional

import starlette.websockets
from starlette.websockets import WebSocketState

from ._shinyenv import is_pyodide


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


class StarletteConnection(Connection):
    def __init__(self, conn: starlette.websockets.WebSocket):
        self.conn: starlette.websockets.WebSocket = conn

    async def accept(self, subprotocol: Optional[str] = None):
        await self.conn.accept(subprotocol)  # type: ignore

    async def send(self, message: str) -> None:
        if self._is_closed():
            return

        # In general, we want to be able to call this send() method from synchronous
        # functions. That means this method must either (A) be synchronous, or (B) if it
        # is marked as async, it must never yield so that we can use run_coro_sync() to
        # call it from synchronous functions.
        if is_pyodide:
            # The create_task() here isn't strictly necessary for things to work in
            # pyodide. The emulated websocket's .send() method is a proxy object for a
            # JS function, and when it's invoked, it returns a Future which will execute
            # even if we don't await it or create a new task, since it's running outside
            # of Python (similar to if a Future is run in a separate process).
            #
            # We can't wrap the Future in run_coro_sync(), because with pyodide's
            # implementation of async wrapper functions, it does yield, and so
            # run_coro_sync() will throw an error.
            #
            # If we just call conn.send_text() without either awaiting it or creating a
            # Task, then Python will raise a warning about the Future not being awaited.
            # So even though the code would work without create_task(), it would raise a
            # warning. We call create_task() to avoid that warning.
            asyncio.create_task(self.conn.send_text(message))
        else:
            # The uvicorn websocket.send() method does not yield, so we can wrap it with
            # run_coro_sync().
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


class ConnectionClosed(Exception):
    """Raised when a Connection is closed from the other side."""

    pass
