import json
import re
import asyncio
import inspect
import warnings
import typing
from contextvars import ContextVar, Token
from contextlib import contextmanager
from typing import TYPE_CHECKING, Callable, Optional, Union, Awaitable, TypedDict

from fastapi import Request, Response
from fastapi.responses import JSONResponse, HTMLResponse

if TYPE_CHECKING:
    from .shinyapp import ShinyApp

from .reactives import ReactiveValues, Observer, ObserverAsync
from .connmanager import Connection, ConnectionClosed
from . import render
from .fileupload import FileInfo, FileUploadManager

# This cast is necessary because if the type checker thinks that if
# "tag" isn't in `message`, then it's not a ClientMessage object.
# This will be fixable when TypedDict items can be marked as
# potentially missing, in Python 3.10, with PEP 655.
class ClientMessageBase(TypedDict):
    method: str

class ClientMessageInit(ClientMessageBase):
    data: dict[str, object]

class ClientMessageUpdate(ClientMessageBase):
    data: dict[str, object]

class ClientMessageOther(ClientMessageBase):
    args: list[object]
    tag: int


class ShinySession:
    def __init__(self, app: 'ShinyApp', id: str, conn: Connection) -> None:
        self._app: ShinyApp = app
        self.id: str = id
        self._conn: Connection = conn

        self.input: ReactiveValues = ReactiveValues()
        self.output: Outputs = Outputs(self)

        self._message_queue_in: asyncio.Queue[Optional[ClientMessageBase]] = asyncio.Queue()
        self._message_queue_out: list[dict[str, object]] = []

        self._message_handlers: dict[str, Callable[..., Awaitable[object]]] = self._create_message_handlers()
        self._file_upload_manager: FileUploadManager = FileUploadManager()
        self._on_ended_callbacks: list[Callable[[], None]] = []

        with session_context(self):
            self._app.server(self.input, self.output)

    async def run(self) -> None:
        await self.send_message({"config": {"workerId": "", "sessionId": str(self.id), "user": None}})

        # Start the producer and consumer coroutines.
        await asyncio.gather(
            self._message_queue_in_producer(),
            self._message_queue_in_consumer()
        )

        # When we get here, session has closed. Do cleanup stuff.
        for cb in self._on_ended_callbacks:
            try:
                cb()
            except Exception as e:
                print("Error in session on_ended callback: " + str(e))
        self._app.remove_session(self)


    async def _message_queue_in_producer(self) -> None:
        try:
            while True:
                message: str = await self._conn.receive()
                print("RECV: " + message)

                try:
                    message_obj = json.loads(message)
                except json.JSONDecodeError:
                    print("ERROR: Invalid JSON message")
                    continue

                self._message_queue_in.put_nowait(message_obj)

        except ConnectionClosed:
            # None is a sentinal value signalling that the connection was
            # closed. This is needed so that the consumer knows to stop.
            self._message_queue_in.put_nowait(None)

    # ==========================================================================
    # Inbound message handling
    # ==========================================================================
    async def _message_queue_in_consumer(self) -> None:
        while True:
            message = await self._message_queue_in.get()

            # None is a signal that the connection is closed.
            if message is None:
                return

            if "method" not in message:
                self._send_error_response("Message does not contain 'method'.")
                return

            if message["method"] == "init":
                message = typing.cast(ClientMessageInit, message)
                self._manage_inputs(message["data"])

            elif message["method"] == "update":
                message = typing.cast(ClientMessageUpdate, message)
                self._manage_inputs(message["data"])

            else:
                if "tag" not in message:
                    warnings.warn("Cannot dispatch message with missing 'tag'; method: " +
                                message["method"])
                    return
                if "args" not in message:
                    warnings.warn("Cannot dispatch message with missing 'args'; method: " +
                                message["method"])
                    return

                message = typing.cast(ClientMessageOther, message)
                await self._dispatch(message)

            self.request_flush()

            await self._app.flush_pending_sessions()


    def _manage_inputs(self, data: dict[str, object]) -> None:
        for (key, val) in data.items():
            if ":" in key:
                key = key.split(":")[0]

            self.input[key] = val

    # ==========================================================================
    # Message handlers
    # ==========================================================================

    async def _dispatch(self, message: ClientMessageOther) -> None:
        try:
            func = self._message_handlers[message["method"]]
        except AttributeError:
            self._send_error_response("Unknown method: " + message["method"])
            return

        try:
            # TODO: handle `blobs`
            value: object = await func(*message["args"])
        except Exception as e:
            self._send_error_response("Error: " + str(e))
            return

        await self._send_response(message, value)

    async def _send_response(self, message: ClientMessageOther, value: object) -> None:
        await self.send_message({
            "response": {
                "tag": message["tag"],
                "value": value
            }
        })

    # This is called during __init__.
    def _create_message_handlers(self) -> dict[str, Callable[..., Awaitable[object]]]:
        async def uploadInit(file_infos: list[FileInfo]) -> dict[str, object]:
            with session_context(self):
                print("uploadInit")
                print(file_infos)

                # TODO: Don't alter message in place?
                for fi in file_infos:
                    if "type" not in fi:
                        # TODO: Infer file type
                        fi["type"] = "application/octet-stream"

                job_id = self._file_upload_manager.create_upload_operation(file_infos)
                worker_id = ""
                return {
                    "jobId": job_id,
                    "uploadUrl": f"session/{self.id}/upload/{job_id}?w={worker_id}"
                }

        async def uploadEnd(job_id: str, input_id: str) -> None:
            upload_op = self._file_upload_manager.get_upload_operation(job_id)
            if upload_op is None:
                warnings.warn("Received uploadEnd message for non-existent upload operation.")
                return None
            file_data = upload_op.finish()
            self.input[input_id] = file_data
            # Explicitly return None to signal that the message was handled.
            return None

        return {
            "uploadInit": uploadInit,
            "uploadEnd": uploadEnd,
        }

    # ==========================================================================
    # Handling /session/{id}/{subpath} requests
    # ==========================================================================
    async def handle_request(self, request: Request, subpath: str) -> Response:
        matches = re.search("^/([a-z]+)/(.*)$", subpath)

        if not matches:
            return HTMLResponse("<h1>Bad Request</h1>", 400)

        if matches[1] == "upload" and request.method == "POST":
            # check that upload operation exists
            job_id = matches[2]
            upload_op = self._file_upload_manager.get_upload_operation(job_id)
            if not upload_op:
                return HTMLResponse("<h1>Bad Request</h1>", 400)

            # The FileUploadOperation can have multiple files; each one will
            # have a separate POST request. Each call to  `with upload_op` will
            # open up each file (in sequence) for writing.
            with upload_op:
                async for chunk in request.stream():
                    upload_op.write_chunk(chunk)

        return JSONResponse({"session_id":self.id, "subpath":subpath}, status_code=200)


    # ==========================================================================
    # Outbound message handling
    # ==========================================================================
    def add_message_out(self, message: dict[str, object]) -> None:
        self._message_queue_out.append(message)

    def get_messages_out(self) -> list[dict[str, object]]:
        return self._message_queue_out

    def clear_messages_out(self) -> None:
        self._message_queue_out.clear()


    async def send_message(self, message: dict[str, object]) -> None:
        message_str: str = json.dumps(message) + "\n"
        print(
            "SEND: " + re.sub('(?m)base64,[a-zA-Z0-9+/=]+', '[base64 data]', message_str),
            end = ""
        )
        await self._conn.send(json.dumps(message))

    def _send_error_response(self, message_str: str) -> None:
        print("_send_error_response: " + message_str)
        pass

    # ==========================================================================
    # Flush
    # ==========================================================================
    def request_flush(self) -> None:
        self._app.request_flush(self)

    async def flush(self) -> None:
        values: dict[str, object] = {}

        for value in self.get_messages_out():
            values.update(value)

        message: dict[str, object] = {
            "errors": {},
            "values": values,
            "inputMessages": []
        }

        try:
            await self.send_message(message)
        finally:
            self.clear_messages_out()

    # ==========================================================================
    # On session ended
    # ==========================================================================
    def on_ended(self, cb: Callable[[], None]) -> None:
        self._on_ended_callbacks.append(cb)


class Outputs:
    def __init__(self, session: ShinySession) -> None:
        self._output_obervers: dict[str, Observer] = {}
        self._session: ShinySession = session

    def set(self, name: str) -> Callable[[Union[Callable[[], object], render.RenderFunction]], None]:
        def set_fn(fn: Union[Callable[[], object], render.RenderFunction]) -> None:

            # fn is either a regular function or a RenderFunction object. If
            # it's the latter, we can give it a bit of metadata, which can be
            # used by the
            if isinstance(fn, render.RenderFunction):
                fn.set_metadata(self._session, name)

            if name in self._output_obervers:
                self._output_obervers[name].destroy()

            @ObserverAsync
            async def output_obs():
                await self._session.send_message({
                    "recalculating": {
                        "name": name,
                        "status": "recalculating"
                    }
                })

                message: dict[str, object] = {}
                if inspect.iscoroutinefunction(fn):
                    fn2 = typing.cast(Callable[[], Awaitable[object]], fn)
                    val = await fn2()
                else:
                    val = fn()
                message[name] = val
                self._session.add_message_out(message)

                await self._session.send_message({
                    "recalculating": {
                        "name": name,
                        "status": "recalculated"
                    }
                })

            self._output_obervers[name] = output_obs

            return None

        return set_fn


# ==============================================================================
# Context manager for current session (AKA current reactive domain)
# ==============================================================================
_current_session: ContextVar[Optional[ShinySession]] = \
    ContextVar("current_session", default = None)

def get_current_session() -> Optional[ShinySession]:
    return _current_session.get()

@contextmanager
def session_context(session: Optional[ShinySession]):
    token: Token[Union[ShinySession, None]] = _current_session.set(session)
    try:
        yield
    finally:
        _current_session.reset(token)
