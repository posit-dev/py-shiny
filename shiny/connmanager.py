from abc import ABC, abstractmethod
from typing import Optional
from asgiref.typing import (
    ASGIReceiveCallable,
    ASGISendCallable,
    Scope,
    WebSocketAcceptEvent,
    WebSocketCloseEvent,
    WebSocketSendEvent,
)


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


# Adapts ASGI call (scope, receive, send) to a Connection object
class ASGIConnection(Connection):
    def __init__(
        self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable
    ):
        self.scope: Scope = scope
        self._rcv: ASGIReceiveCallable = receive
        self._snd: ASGISendCallable = send

    async def accept(self) -> None:
        """
        Call once when the connection is first established, in order to complete the
        WebSocket protocol handshake.
        """
        event = await self._rcv()
        if event["type"] == "websocket.connect":
            await self._snd(
                WebSocketAcceptEvent(
                    type="websocket.accept", subprotocol=None, headers=[]
                )
            )
        else:
            await self._snd(
                {
                    "type": "websocket.close",
                    "code": 403,
                    "reason": "Unexpected event received before handshake",
                }
            )

    async def send(self, message: str) -> None:
        await self._snd(
            WebSocketSendEvent(type="websocket.send", bytes=None, text=message)
        )

    async def receive(self) -> str:
        event = await self._rcv()
        if event["type"] == "websocket.receive":
            if "text" in event and event["text"] != None:
                return event["text"]
            else:
                # TODO: Log this?
                await self._snd(
                    WebSocketCloseEvent(
                        type="websocket.close",
                        code=1003,
                        reason="Can't understand non-text messages at this time",
                    )
                )
                raise ConnectionClosed()
        elif event["type"] == "websocket.disconnect":
            raise ConnectionClosed()
        else:
            # TODO: Log the event["type"] we didn't recognize
            await self._snd(
                WebSocketCloseEvent(
                    type="websocket.close",
                    code=1002,
                    reason="Unknown event type received",
                )
            )
            raise ConnectionClosed()

    async def close(self, code: int, reason: Optional[str]) -> None:
        await self._snd(
            WebSocketCloseEvent(type="websocket.close", code=code, reason=reason)
        )


class ConnectionClosed(Exception):
    """Raised when a Connection is closed from the other side."""

    pass
