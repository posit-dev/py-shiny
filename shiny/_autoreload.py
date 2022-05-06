import asyncio
import html
import logging
import os
import secrets
from typing import Optional
import threading

from asgiref.typing import (
    ASGI3Application,
    Scope,
    ASGIReceiveCallable,
    ASGISendCallable,
    ASGISendEvent,
)

# Warning: `import websockets` alone doesn't work because the websockets package uses
# a lazy loading technique which is opaque to mypy and pyright.
# https://github.com/aaugustin/websockets/issues/940#issuecomment-874012438
from websockets.client import connect
from websockets.server import serve, WebSocketServerProtocol
import websockets.exceptions


# CHILD PROCESS ------------------------------------------------------------


def autoreload_url() -> Optional[str]:
    port = os.getenv("SHINY_AUTORELOAD_PORT")
    if not port:
        return None
    else:
        return f"ws://localhost:{port}/autoreload"


# Instantiated by Uvicorn in worker process when reload is enabled
class HotReloadHandler(logging.Handler):
    """Uvicorn log reader, detects reload events."""

    def __init__(self):
        logging.Handler.__init__(self)

    def emit(self, record: logging.LogRecord) -> None:
        # https://github.com/encode/uvicorn/blob/266db48888f3f1ba56710a49ec82e12eecde3aa3/uvicorn/supervisors/statreload.py#L46
        # https://github.com/encode/uvicorn/blob/266db48888f3f1ba56710a49ec82e12eecde3aa3/uvicorn/supervisors/watchgodreload.py#L148
        if "Reloading..." in record.getMessage():
            reload_begin()
        # https://github.com/encode/uvicorn/blob/926a8f5dc2c9265d5fb5daaafce13878f477e264/uvicorn/lifespan/on.py#L59
        elif "Application startup complete." in record.getMessage():
            reload_end()


# Called from child process when old application instance is shut down
def reload_begin():
    pass


# Called from child process when new application instance starts up
def reload_end():
    # os.kill(os.getppid(), signal.SIGUSR1)

    port = os.getenv("SHINY_AUTORELOAD_PORT")
    if not port:
        return None

    url = f"ws://localhost:{port}/notify"

    async def _() -> None:
        options = {
            "extra_headers": {
                "Shiny-Autoreload-Secret": os.getenv("SHINY_AUTORELOAD_SECRET", ""),
            }
        }
        try:
            async with connect(url, **options) as websocket:
                await websocket.send("reload_end")
        except websockets.exceptions.ConnectionClosed:
            pass

    asyncio.create_task(_())


class InjectAutoreloadMiddleware:
    """Inserts shiny-autoreload.js into the head.

    It's necessary to do it using middleware instead of in a nice htmldependency,
    because we want autoreload to be effective even when displaying an error page.
    """

    def __init__(self, app: ASGI3Application):
        self.app = app
        ws_url = autoreload_url()
        self.script = (
            f"""  <script src="__shared/shiny-autoreload.js" data-ws-url="{html.escape(ws_url)}"></script>
</head>""".encode(
                "ascii"
            )
            if ws_url
            else bytes()
        )

    async def __call__(
        self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable
    ) -> None:
        if scope["type"] != "http" or scope["path"] != "/" or len(self.script) == 0:
            return await self.app(scope, receive, send)
        intercept = True
        body = b""

        async def rewrite_send(event: ASGISendEvent) -> None:
            nonlocal intercept
            nonlocal body

            if intercept:
                if event["type"] == "http.response.start":
                    # Must remove Content-Length, if present; if we insert our
                    # scripts, it won't be correct anymore
                    event["headers"] = [
                        (name, value)
                        for (name, value) in event["headers"]
                        if name.decode("ascii").lower() != "content-length"
                    ]
                elif event["type"] == "http.response.body":
                    body += event["body"]
                    if b"</head>" in body:
                        event["body"] = body.replace(b"</head>", self.script, 1)
                        body = b""  # Allow gc
                        intercept = False
                    elif event["more_body"]:
                        # DO NOT send the response; wait for more data
                        return
                    else:
                        # The entire response was seen, and we never encountered
                        # any </head>. Just send everything we have
                        event["body"] = body
                        body = b""  # Allow gc

            return await send(event)

        await self.app(scope, receive, rewrite_send)


# PARENT PROCESS ------------------------------------------------------------


def start_server(port: int):
    """Starts a websocket server that listens on its own port (separate from the main
    Shiny listener).

    Clients can connect on either the /autoreload or /notify path.

    Clients from the uvicorn worker process connect to the /notify path to notify us
    that a successful startup or reload has occured.

    Clients from browsers (on localhost only) connect to the /autoreload path to be
    notified when a successful startup or reload has occured.
    """

    # Store port and secret in environment variables so they are inherited by uvicorn
    # worker processes.
    secret = secrets.token_hex(32)
    os.environ["SHINY_AUTORELOAD_PORT"] = str(port)
    os.environ["SHINY_AUTORELOAD_SECRET"] = secret

    # Run on a background thread so our event loop doesn't interfere with uvicorn.
    # Set daemon=True because we don't want to keep the process alive with this thread.
    threading.Thread(None, _thread_main, args=[port, secret], daemon=True).start()


def _thread_main(port: int, secret: str):
    asyncio.run(_coro_main(port, secret))


async def _coro_main(port: int, secret: str) -> None:
    reload_now: asyncio.Event = asyncio.Event()

    def nudge():
        reload_now.set()
        reload_now.clear()

    async def reload_server(conn: WebSocketServerProtocol):
        try:
            if conn.path == "/autoreload":
                # The client wants to be notified when the app has reloaded. The client
                # in this case is the web browser, specifically shiny-autoreload.js.
                while True:
                    await reload_now.wait()
                    await conn.send("autoreload")
            elif conn.path == "/notify":
                # The client is notifying us that the app has reloaded. The client in
                # this case is the uvicorn worker process (see reload_end(), above).
                req_secret = conn.request_headers.get("Shiny-Autoreload-Secret", "")
                if req_secret != secret:
                    # The client coudn't prove that they were from a child process
                    return
                data = await conn.recv()
                if isinstance(data, str) and data == "reload_end":
                    nudge()
        except websockets.exceptions.ConnectionClosed:
            pass

    async with serve(reload_server, "localhost", port):
        await asyncio.Future()  # wait forever
