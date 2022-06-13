import asyncio
from abc import ABC, abstractmethod
from typing import Callable, Optional, TYPE_CHECKING, cast

if TYPE_CHECKING:
    from shiny import Session, Inputs, Outputs

import starlette.websockets
from starlette.websockets import WebSocketState
from starlette.requests import HTTPConnection

from . import _utils


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
    def __init__(
        self, server: Optional[Callable[["Inputs", "Outputs", "Session"], None]] = None
    ) -> None:
        # This currently hard-codes some basic values for scope. In the future, we could
        # make those more configurable if we need to customize the HTTPConnection (like
        # "scheme", "path", and "query_string").
        self._http_conn = HTTPConnection(scope={"type": "websocket", "headers": {}})

        self._on_ended_callbacks = _utils.Callbacks()

        if server is not None:
            from .session import Inputs, Outputs, Session, session_context

            self = cast(Session, self)
            self.input = Inputs()
            self.output = Outputs(self)
            with session_context(self):
                server(self.input, self.output, self)

    def on_ended(self, fn: Callable[[], None]) -> Callable[[], None]:
        return self._on_ended_callbacks.register(fn)

    async def send(self, message: str) -> None:
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


class StarletteConnection(Connection):
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
