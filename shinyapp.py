from shinysession import ShinySession
import json
import react

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import uvicorn

class ShinyApp:
    def __init__(self, ui, server) -> None:
        self.ui = ui
        self.server = server
        self._app = create_fastapi_app(server)

    def run(self) -> None:
        uvicorn.run(self._app, host = "0.0.0.0", port = 8000)


# Create a FastAPI app, given the app's server function.
def create_fastapi_app(server: callable) -> FastAPI:

    app = FastAPI()

    html = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Chat</title>
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


    @app.get("/")
    async def get():
        return HTMLResponse(html)


    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        session = ShinySession(server)

        while True:
            line = await websocket.receive_text()
            if not line:
                break

            print("RECV: " + line)

            vals = json.loads(line)
            for (key, val) in vals.items():
                session.input[key] = val

            react.flush()

            for message in session.get_messages():
                message_str = json.dumps(message) + "\n"
                print("SEND: " + message_str, end = "")
                await websocket.send_text(message_str)

            session.clear_messages()

    return app
