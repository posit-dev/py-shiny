from abc import ABC, abstractmethod
from typing import Optional
import starlette.websockets
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


class ConnectionClosed(Exception):
    """Raised when a Connection is closed from the other side."""

    pass
