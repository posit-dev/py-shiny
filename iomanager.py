from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from shinyapp import ShinyApp
    from shinysession import ShinySession

class IOHandler:
    """Abstract class to serve a session and send/receive messages to the
    client."""
    async def send(self, message: str) -> None:
        raise NotImplementedError

    async def receive(self) -> str:
        raise NotImplementedError


class IOManager:
    """Abstract class for handling incoming connections and spawning
    ShinySessions."""
    def __init__(self, app: 'ShinyApp') -> None:
        raise NotImplementedError

    def run(self) -> None:
        raise NotImplementedError


from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn

class IOHandlerDisconnect(Exception):
    """Raised when the IOHandler is disconnected."""
    pass

class FastAPIIOHandler(IOHandler):
    def __init__(self, websocket: WebSocket) -> None:
        self._websocket: WebSocket = websocket

    async def send(self, message: str) -> None:
        await self._websocket.send_text(message)

    async def receive(self) -> str:
        try:
            return await self._websocket.receive_text()
        except WebSocketDisconnect:
            raise IOHandlerDisconnect

class FastAPIIOManager(IOManager):
    """Implementation of I/O manager which listens on a HTTP port to serve a web
    page, and then listens for WebSocket connections to spawn ShinySessions."""
    def __init__(self, shinyapp: 'ShinyApp') -> None:
        self._shinyapp: ShinyApp = shinyapp
        self._fastapi_app: FastAPI = FastAPI()

        @self._fastapi_app.get("/")
        async def get():
            return HTMLResponse(self.html)

        @self._fastapi_app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()

            iohandler = FastAPIIOHandler(websocket)
            session = shinyapp.create_session(iohandler)
            await session.serve()


    def run(self) -> None:
        uvicorn.run(self._fastapi_app, host = "0.0.0.0", port = 8000)

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
                var ws = new WebSocket("ws://localhost:8000/ws");
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




import asyncio
from asyncio import StreamReader, StreamWriter

class TCPIOHandler(IOHandler):
    def __init__(self, reader: StreamReader, writer: StreamWriter) -> None:
        self._reader: StreamReader = reader
        self._writer: StreamWriter = writer

    async def send(self, message: str) -> None:
        self._writer.write(message.encode('utf-8'))

    async def receive(self) -> str:
        data: bytes = await self._reader.readline()
        if not data:
            raise IOHandlerDisconnect

        message: str = data.decode('latin1').rstrip()
        return message



class TCPIOManager(IOManager):
    """Implementation of I/O manager which listens on a TCP port to spawn
    ShinySessions."""
    def __init__(self, shinyapp: 'ShinyApp') -> None:
        self._shinyapp = shinyapp

    def run(self) -> None:
        asyncio.run(self._run())

    async def _run(self) -> None:
        server = await asyncio.start_server(self._handle_incoming_connection, '127.0.0.1', 8888)

        addr = server.sockets[0].getsockname()
        print(f'Serving on {addr}')

        # Run event loop to listen for events
        async with server:
            await server.serve_forever()

    async def _handle_incoming_connection(self, reader: StreamReader, writer: StreamWriter) -> None:
        # When incoming connection arrives, spawn a session
        iohandler = TCPIOHandler(reader, writer)
        session = self._shinyapp.create_session(iohandler)
        await session.serve()
