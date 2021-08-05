class IOHandle:
    """Abstract class for a session to send messages."""
    async def send(self, message: str) -> None:
        pass

class IOManager:
    """Abstract class for handling I/O and spawning ShinySessions."""
    def __init__(self, app: 'ShinyApp') -> None:
        pass

    def run(self) -> None:
        pass


from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn

class FastAPIIOHandle(IOHandle):
    def __init__(self, websocket: WebSocket) -> None:
        self._websocket: WebSocket = websocket

    async def send(self, message: str) -> None:
        await self._websocket.send_text(message)


class FastAPIIOManager(IOManager):
    """Implementation of I/O manager which listens on a HTTP port to serve a web
    page, and then listens for WebSocket connections to spawn ShinySessions."""
    def __init__(self, shinyapp: 'ShinyApp') -> None:
        self._shinyapp = shinyapp
        self._app = FastAPI()

        @self._app.get("/")
        async def get():
            return HTMLResponse(self.html)

        @self._app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            iohandle = FastAPIIOHandle(websocket)
            session = self._shinyapp.create_session(iohandle)

            try:
                while True:
                    message = await websocket.receive_text()
                    if not message:
                        break

                    await session.handle_incoming_message(message)

            except WebSocketDisconnect:
                pass

            # Unregister the session when done.
            self._shinyapp.remove_session(session)


    def run(self) -> None:
        uvicorn.run(self._app, host = "0.0.0.0", port = 8000)

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

class TCPIOHandle(IOHandle):
    def __init__(self, writer: StreamWriter) -> None:
        self._writer: StreamWriter = writer

    async def send(self, message: str) -> None:
        self._writer.write(message.encode('utf-8'))


class TCPIOManager(IOManager):
    """Implementation of I/O manager which listens on a TCP port to spawn
    ShinySessions."""
    def __init__(self, shinyapp: 'ShinyApp') -> None:
        self._shinyapp = shinyapp

    def run(self) -> None:
        asyncio.run(self._run())

    async def _run(self) -> None:
        server = await asyncio.start_server(self._handle_incoming, '127.0.0.1', 8888)

        addr = server.sockets[0].getsockname()
        print(f'Serving on {addr}')

        # Run event loop to listen for events
        async with server:
            await server.serve_forever()

    async def _handle_incoming(self, reader: StreamReader, writer: StreamWriter) -> None:
        # When incoming connection arrives, spawn a session
        iohandle = TCPIOHandle(writer)
        session = self._shinyapp.create_session(iohandle)

        while True:
            line = await reader.readline()
            if not line:
                break

            line = line.decode('latin1').rstrip()

            await session.handle_incoming_message(line)

        writer.close()

        # Unregister the session when done.
        self._shinyapp.remove_session(session)
