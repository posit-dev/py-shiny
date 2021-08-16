from typing import Callable, Awaitable, Optional
import os

class Connection:
    """Abstract class to serve a session and send/receive messages to the
    client."""
    async def send(self, message: str) -> None:
        raise NotImplementedError

    async def receive(self) -> str:
        raise NotImplementedError


class ConnectionManager:
    """Base class for handling incoming connections."""
    def __init__(self, on_connect_cb: Callable[[Connection], Awaitable[None]]) -> None:
        raise NotImplementedError

    def run(self) -> None:
        raise NotImplementedError

    def set_ui_path(self, path: str) -> None:
        raise NotImplementedError

class ConnectionClosed(Exception):
    """Raised when a Connection is closed from the other side."""
    pass


# =============================================================================
# FastAPIConnection / FastAPIConnectionManager
# =============================================================================

from fastapi import FastAPI, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
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

class FastAPIConnectionManager(ConnectionManager):
    """Implementation of ConnectionManager which listens on a HTTP port to serve a web
    page, and also listens for WebSocket connections."""
    def __init__(
        self,
        on_connect_cb: Callable[[Connection], Awaitable[None]],
        on_session_request_cb: Callable[[Request], Awaitable[Response]]
    ) -> None:
        self._ui_path: Optional[str] = None
        self._on_connect_cb: Callable[[Connection], Awaitable[None]] = on_connect_cb
        self._on_session_request_cb: Callable[[Request], Awaitable[Response]] = on_session_request_cb
        self._fastapi_app: FastAPI = FastAPI()

        @self._fastapi_app.get("/")
        async def get() -> Response:
            if self._ui_path is None:
                return HTMLResponse(self.html)
            else:
                return FileResponse(os.path.join(self._ui_path, "index.html"))

        self._fastapi_app.mount(
            "/shared",
            StaticFiles(directory = os.path.join(os.path.dirname(__file__), "www/shared")),
            name = "shared"
        )

        @self._fastapi_app.api_route("/session/{path:path}", methods=["GET", "POST"])
        async def route_session_request(request: Request, path: str) -> Response:
            return await self._on_session_request_cb(request)

        @self._fastapi_app.websocket("/websocket/")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()

            conn = FastAPIConnection(websocket)
            await self._on_connect_cb(conn)


    def run(self) -> None:
        uvicorn.run(self._fastapi_app, host = "0.0.0.0", port = 8000)


    def set_ui_path(self, path: str) -> None:
        self._ui_path = path



    html = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>WebSocket App</title>
        </head>
        <body>
            <h1>WebSocket App</h1>
            <form action="" onsubmit="sendMessage(event)">
                <input type="text" id="messageText" autocomplete="off"/>
                <button>Send</button>
            </form>
            <ul id='messages'>
            </ul>
            <script>
                var ws = new WebSocket("ws://localhost:8000/websocket");
                ws.onmessage = function(event) {
                    var messages = document.getElementById('messages')
                    var message = document.createElement('li')
                    var content = document.createTextNode(event.data)
                    message.appendChild(content)
                    messages.appendChild(message)
                };
                function sendMessage(event) {
                    var input = document.getElementById("messageText")
                    ws.send(input.value)
                    input.value = ''
                    event.preventDefault()
                }
            </script>
        </body>
    </html>
    """


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
        self._writer.write(message.encode('utf-8'))

    async def receive(self) -> str:
        data: bytes = await self._reader.readline()
        if not data:
            raise ConnectionClosed

        message: str = data.decode('latin1').rstrip()
        return message


class TCPConnectionManager(ConnectionManager):
    """Implementation of ConnectionManager which listens on a TCP port."""

    def __init__(self, on_connect_cb: Callable[[Connection], Awaitable[None]]) -> None:
        self._on_connect_cb: Callable[[Connection], Awaitable[None]] = on_connect_cb

    def run(self) -> None:
        asyncio.run(self._run())

    def set_ui_path(self, path: str) -> None:
        """TCPConnectionManager doesn't serve files; it only listens for
        communication with the session."""
        pass

    async def _run(self) -> None:
        server = await asyncio.start_server(self._handle_incoming_connection, '127.0.0.1', 8888)

        addr = server.sockets[0].getsockname()
        print(f'Serving on {addr}')

        # Run event loop to listen for events
        async with server:
            await server.serve_forever()

    async def _handle_incoming_connection(self, reader: StreamReader, writer: StreamWriter) -> None:
        # When incoming connection arrives, spawn a session
        conn = TCPConnection(reader, writer)
        await self._on_connect_cb(conn)
