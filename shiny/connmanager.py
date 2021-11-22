from abc import ABC, abstractmethod
from asyncio.tasks import Task
from typing import Callable, Awaitable, Optional, Union
import typing
import sys

PYODIDE = "pyodide" in sys.modules


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
    async def close(self) -> None:
        ...


class ConnectionManager(ABC):
    """Base class for handling incoming connections."""

    @abstractmethod
    def __init__(self, on_connect_cb: Callable[[Connection], Awaitable[None]]) -> None:
        ...

    @abstractmethod
    def run(self) -> None:
        ...


class ConnectionClosed(Exception):
    """Raised when a Connection is closed from the other side."""

    pass


if not PYODIDE:

    # =============================================================================
    # FastAPIConnection / FastAPIConnectionManager
    # =============================================================================

    from fastapi import FastAPI, Request, Response, WebSocket, WebSocketDisconnect
    import uvicorn


    class FastAPIConnection(Connection):
        def __init__(self, websocket: WebSocket) -> None:
            self._websocket: WebSocket = websocket

        async def send(self, message: str) -> None:
            await self._websocket.send_text(message)

        async def receive(self) -> str:
            try:
                return await self._websocket.receive_text()
            except WebSocketDisconnect:
                raise ConnectionClosed

        async def close(self) -> None:
            await self._websocket.close()


    class FastAPIConnectionManager(ConnectionManager):
        """Implementation of ConnectionManager which listens on a HTTP port to serve a web
        page, and also listens for WebSocket connections."""

        def __init__(
            self,
            on_root_request_cb: Callable[[Request], Awaitable[Response]],
            on_connect_cb: Callable[[Connection], Awaitable[None]],
            on_session_request_cb: Callable[[Request], Awaitable[Response]],
        ) -> None:
            self._on_root_request_cb: Callable[
                [Request], Awaitable[Response]
            ] = on_root_request_cb
            self._on_connect_cb: Callable[[Connection], Awaitable[None]] = on_connect_cb
            self._on_session_request_cb: Callable[
                [Request], Awaitable[Response]
            ] = on_session_request_cb
            self._fastapi_app: FastAPI = FastAPI()

            @self._fastapi_app.get("/")
            async def get(request: Request) -> Response:
                return await self._on_root_request_cb(request)

            @self._fastapi_app.api_route(
                "/session/{rest_of_path:path}", methods=["GET", "POST"]
            )
            async def route_session_request(request: Request) -> Response:
                return await self._on_session_request_cb(request)

            @self._fastapi_app.websocket("/websocket/")
            async def websocket_endpoint(websocket: WebSocket):
                await websocket.accept()

                conn = FastAPIConnection(websocket)
                await self._on_connect_cb(conn)

            if typing.TYPE_CHECKING:
                # The only purpose of this block is to make the type checker not
                # warn about these functions not being accessed.
                (get, route_session_request, websocket_endpoint)

        def run(self) -> None:
            uvicorn.run(self._fastapi_app, host="0.0.0.0", port=8000)


# =============================================================================
# TCPConnection / TCPConnectionManager
# =============================================================================

import asyncio
from asyncio import StreamReader, StreamWriter


class TCPConnection(Connection):
    def __init__(self, reader: StreamReader, writer: StreamWriter) -> None:
        self._reader: StreamReader = reader
        self._writer: StreamWriter = writer

    async def send(self, message: str) -> None:
        self._writer.write(message.encode("utf-8"))

    async def receive(self) -> str:
        data: bytes = await self._reader.readline()
        if not data:
            raise ConnectionClosed

        message: str = data.decode("latin1").rstrip()
        return message

    async def close(self) -> None:
        self._writer.close()
        await self._writer.wait_closed()


class TCPConnectionManager(ConnectionManager):
    """Implementation of ConnectionManager which listens on a TCP port."""

    def __init__(self, on_connect_cb: Callable[[Connection], Awaitable[None]]) -> None:
        self._on_connect_cb: Callable[[Connection], Awaitable[None]] = on_connect_cb

    def run(self) -> None:
        asyncio.run(self._run())

    async def _run(self) -> None:
        server = await asyncio.start_server(
            self._handle_incoming_connection, "127.0.0.1", 8888
        )

        addr = server.sockets[0].getsockname()
        print(f"Serving on {addr}")

        # Run event loop to listen for events
        async with server:
            await server.serve_forever()

    async def _handle_incoming_connection(
        self, reader: StreamReader, writer: StreamWriter
    ) -> None:
        # When incoming connection arrives, spawn a session
        conn = TCPConnection(reader, writer)
        await self._on_connect_cb(conn)


# =============================================================================
# FunctionCallConnection / FunctionCallConnectionManager
# =============================================================================
class FunctionCallConnection(Connection):
    def __init__(
        self,
        send_message: Callable[[str], Awaitable[None]],
        notify_close: Callable[[], Awaitable[None]],
    ) -> None:
        self._in_queue: asyncio.Queue[Union[str, None]]
        self._send_message: Optional[Callable[[str], Awaitable[None]]] = send_message
        self._notify_close: Callable[[], Awaitable[None]] = notify_close

    # This init() method exists because __init__() is called outside of an asyncio.Task,
    # but the asyncio.Queue() must be created within the Task where it is used. After the
    # task is launched, this init() method is called to set up the queue..
    def init(self):
        self._in_queue = asyncio.Queue()

    async def send(self, message: str) -> None:
        if not self._send_message:
            raise Exception("No send callback set")
        await self._send_message(message)

    async def receive(self) -> str:
        data = await self._in_queue.get()
        if data is None:
            raise ConnectionClosed

        return data

    async def close(self) -> None:
        self._send_message = None
        # The None tells the receive() loop to exit.
        await self._in_queue.put(None)

        await self._notify_close()


class FunctionCallExternalInterface:
    def __init__(self, connection: FunctionCallConnection) -> None:
        self._conn: FunctionCallConnection = connection

    async def post_message(self, message: str) -> None:
        """
        This is for the external system to post a message to the shiny session.
        """
        await self._conn._in_queue.put(message)

    async def notify_close(self) -> None:
        """
        This is for the external system to notify that the connection has been closed.
        """
        await self._conn._in_queue.put(None)


class FunctionCallConnectionManager(ConnectionManager):
    """
    Implementation of ConnectionManager which listens to function calls pushing messages
    on a queue.
    """

    def __init__(
        self,
        on_connect_cb: Callable[[Connection], Awaitable[None]],
        send_message: Callable[[str], Awaitable[None]],
        notify_close: Callable[[], Awaitable[None]],
    ) -> None:
        """
        - on_connect_cb: A callback to execute when the connection is established.
        - send_message: A callback to execute when a message is sent. This should send
            messages to the external system.
        - send_close: A callback to execute when the connection is closed from the
            server side. This callback should notify the external system that the
            connection is closed.
        """
        self._on_connect_cb: Callable[[Connection], Awaitable[None]] = on_connect_cb
        self._send_message: Callable[[str], Awaitable[None]] = send_message
        self._notify_close: Callable[[], Awaitable[None]] = notify_close
        self._conn: FunctionCallConnection
        self._task = Optional[Task[None]]

    def run(self) -> None:
        raise NotImplementedError

    def run_bg_task(self) -> FunctionCallExternalInterface:
        """
        Run non-blocking, by creating a new task. It must run non-blocking, because
        the only way to push messages on the queue is by calling a function.
        """
        self._task = asyncio.create_task(self._run())
        self._conn = FunctionCallConnection(self._send_message, self._notify_close)

        return FunctionCallExternalInterface(self._conn)

    async def _run(self) -> None:
        self._conn.init()
        await self._on_connect_cb(self._conn)
