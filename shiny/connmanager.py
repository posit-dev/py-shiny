from abc import ABC, abstractmethod
from typing import Optional
import starlette.websockets


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
        await self.conn.send_text(message)

    async def receive(self) -> str:
        return await self.conn.receive_text()

    async def close(self, code: int, reason: Optional[str]) -> None:
        await self.conn.close(code)


class ConnectionClosed(Exception):
    """Raised when a Connection is closed from the other side."""

    pass
