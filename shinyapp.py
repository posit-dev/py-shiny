from typing import Union
from shinysession import ShinySession
import json
import react

from fastapi import BackgroundTasks, FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import uvicorn



class ShinyApp:
    def __init__(self, ui, server: callable) -> None:
        self.ui = ui
        self.server: callable = server
        self._app: FastAPI = create_fastapi_app(self)
        self._sessions: dict[int, ShinySession] = {}
        self._last_session_id: int = 0    # Counter for generating session IDs

        self._sessions_needing_flush: dict[int, ShinySession] = {}

    def create_session(self) -> ShinySession:
        self._last_session_id += 1
        id = self._last_session_id
        session = ShinySession(self, id)
        self._sessions[id] = session
        return session

    def remove_session(self, session: Union[ShinySession, int]) -> None:
        if (isinstance(session, ShinySession)):
            session = session.id

        print(f"remove_session: {session}")
        del self._sessions[session]

    def run(self) -> None:
        uvicorn.run(self._app, host = "0.0.0.0", port = 8000)

    def request_flush(self, session) -> None:
        # TODO: Until we have reactive domains, because we can't yet keep track
        # of which sessions need a flush.
        pass
        # self._sessions_needing_flush[session.id] = session

    async def flush_pending_sessions(self) -> None:
        react.flush()

        # TODO: Until we have reactive domains, flush all sessions (because we
        # can't yet keep track of which ones need a flush)
        for id, session in self._sessions.items():
            await session.flush()
        # for id, session in self._sessions_needing_flush.items():
        #     await session.flush()
        #     del self._sessions_needing_flush[id]


# Create a FastAPI app, given the app's server function.
def create_fastapi_app(shinyapp: ShinyApp) -> FastAPI:

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
        session = shinyapp.create_session()

        await session.listen(websocket)

        # Unregister the session when done.
        shinyapp.remove_session(session)

    return app
