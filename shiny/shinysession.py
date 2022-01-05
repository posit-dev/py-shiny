__all__ = (
    "ShinySession",
    "Outputs",
    "get_current_session",
    "session_context",
)

import functools
import os
from pathlib import Path
import sys
import json
import re
import asyncio
import warnings
import typing
import mimetypes
import dataclasses
import urllib.parse
from contextvars import ContextVar, Token
from contextlib import contextmanager
from typing import (
    TYPE_CHECKING,
    AsyncIterable,
    Callable,
    Iterable,
    Optional,
    TypeVar,
    Union,
    Awaitable,
    Dict,
    List,
    Any,
)
from starlette.requests import Request

from starlette.responses import (
    HTMLResponse,
    PlainTextResponse,
    StreamingResponse,
    guess_type,
)
from starlette.types import ASGIApp


if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

if TYPE_CHECKING:
    from .shinyapp import ShinyApp

from htmltools import TagChildArg, TagList, HTMLDependency

from .reactives import ReactiveValues, Observer, ObserverAsync, isolate
from .http_staticfiles import FileResponse
from .connmanager import Connection, ConnectionClosed
from . import render
from . import utils
from .fileupload import FileInfo, FileUploadManager
from .input_handlers import input_handlers

# This cast is necessary because if the type checker thinks that if
# "tag" isn't in `message`, then it's not a ClientMessage object.
# This will be fixable when TypedDict items can be marked as
# potentially missing, in Python 3.10, with PEP 655.
class ClientMessage(TypedDict):
    method: str


class ClientMessageInit(ClientMessage):
    data: Dict[str, object]


class ClientMessageUpdate(ClientMessage):
    data: Dict[str, object]


# For messages where "method" is something other than "init" or "update".
class ClientMessageOther(ClientMessage):
    args: List[object]
    tag: int


@dataclasses.dataclass
class DownloadHandler:
    filename: Optional[Union[Callable[[], str], str]]
    content_type: Optional[Union[Callable[[], str], str]]
    handler: Callable[[], Union[str, AsyncIterable[bytes], Iterable[bytes]]]


class ShinySession:
    # ==========================================================================
    # Initialization
    # ==========================================================================
    def __init__(
        self, app: "ShinyApp", id: str, conn: Connection, debug: bool = False
    ) -> None:
        self.app: ShinyApp = app
        self.id: str = id
        self._conn: Connection = conn
        self._debug: bool = debug

        self.input: ReactiveValues = ReactiveValues()
        self.output: Outputs = Outputs(self)

        self._message_queue_in: asyncio.Queue[Optional[ClientMessage]] = asyncio.Queue()
        self._message_queue_out: List[Dict[str, object]] = []

        self._message_handlers: Dict[
            str, Callable[..., Awaitable[object]]
        ] = self._create_message_handlers()
        self._file_upload_manager: FileUploadManager = FileUploadManager()
        self._on_ended_callbacks: List[Callable[[], None]] = []
        self._has_run_session_end_tasks: bool = False
        self._downloads: Dict[str, DownloadHandler] = {}

        self._register_session_end_callbacks()

        with session_context(self):
            self.app.server(self)

    def _register_session_end_callbacks(self) -> None:
        # This is to be called from the initialization. It registers functions
        # that are called when a session ends.

        # Clear file upload directories, if present
        self._on_ended_callbacks.append(self._file_upload_manager.rm_upload_dir)

    def _run_session_end_tasks(self) -> None:
        if self._has_run_session_end_tasks:
            return
        self._has_run_session_end_tasks = True

        for cb in self._on_ended_callbacks:
            try:
                cb()
            except Exception as e:
                print("Error in session on_ended callback: " + str(e))

        self.app.remove_session(self)

    async def close(self, code: int = 1001) -> None:
        await self._conn.close(code, None)
        self._run_session_end_tasks()

    async def run(self) -> None:
        await self.send_message(
            {"config": {"workerId": "", "sessionId": str(self.id), "user": None}}
        )

        try:
            while True:
                message: str = await self._conn.receive()
                if self._debug:
                    print("RECV: " + message)

                try:
                    message_obj = json.loads(message)
                except json.JSONDecodeError:
                    print("ERROR: Invalid JSON message")
                    continue

                if "method" not in message_obj:
                    self._send_error_response("Message does not contain 'method'.")
                    return

                if message_obj["method"] == "init":
                    message_obj = typing.cast(ClientMessageInit, message_obj)
                    self._manage_inputs(message_obj["data"])

                elif message_obj["method"] == "update":
                    message_obj = typing.cast(ClientMessageUpdate, message_obj)
                    self._manage_inputs(message_obj["data"])

                else:
                    if "tag" not in message_obj:
                        warnings.warn(
                            "Cannot dispatch message with missing 'tag'; method: "
                            + message_obj["method"]
                        )
                        return
                    if "args" not in message_obj:
                        warnings.warn(
                            "Cannot dispatch message with missing 'args'; method: "
                            + message_obj["method"]
                        )
                        return

                    message_obj = typing.cast(ClientMessageOther, message_obj)
                    await self._dispatch(message_obj)

                self.request_flush()

                await self.app.flush_pending_sessions()

        except ConnectionClosed:
            self._run_session_end_tasks()

    def _manage_inputs(self, data: Dict[str, object]) -> None:
        for (key, val) in data.items():
            keys = key.split(":")
            if len(keys) > 2:
                raise ValueError(
                    "Input name+type is not allowed to contain more than one ':' -- "
                    + key
                )
            if len(keys) == 2:
                val = input_handlers.process_value(keys[1], val, keys[0], self)

            self.input[keys[0]] = val

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
        await self.send_message({"response": {"tag": message["tag"], "value": value}})

    # This is called during __init__.
    def _create_message_handlers(self) -> Dict[str, Callable[..., Awaitable[object]]]:
        async def uploadInit(file_infos: List[FileInfo]) -> Dict[str, object]:
            with session_context(self):
                if self._debug:
                    print("Upload init: " + str(file_infos))

                # TODO: Don't alter message in place?
                for fi in file_infos:
                    if fi["type"] == "":
                        type = mimetypes.guess_type(fi["name"])[0]
                        fi["type"] = type if type else "application/octet-stream"

                job_id = self._file_upload_manager.create_upload_operation(file_infos)
                worker_id = ""
                return {
                    "jobId": job_id,
                    "uploadUrl": f"session/{self.id}/upload/{job_id}?w={worker_id}",
                }

        async def uploadEnd(job_id: str, input_id: str) -> None:
            upload_op = self._file_upload_manager.get_upload_operation(job_id)
            if upload_op is None:
                warnings.warn(
                    "Received uploadEnd message for non-existent upload operation."
                )
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
    # Handling /session/{session_id}/{action}/{subpath} requests
    # ==========================================================================
    async def handle_request(
        self, request: Request, action: str, subpath: Optional[str]
    ) -> ASGIApp:
        if action == "upload" and request.method == "POST":
            if subpath is None or subpath == "":
                return HTMLResponse("<h1>Bad Request</h1>", 400)

            job_id = subpath
            upload_op = self._file_upload_manager.get_upload_operation(job_id)
            if not upload_op:
                return HTMLResponse("<h1>Bad Request</h1>", 400)

            # The FileUploadOperation can have multiple files; each one will
            # have a separate POST request. Each call to  `with upload_op` will
            # open up each file (in sequence) for writing.
            with upload_op:
                async for chunk in request.stream():
                    upload_op.write_chunk(chunk)

            return PlainTextResponse("OK", 200)

        elif action == "download" and request.method == "GET" and subpath:
            matches = re.compile("^([^/?]+)$").match(subpath)
            if not matches:
                print("Not a match")
            if matches:
                download_id = matches[1]
                if download_id in self._downloads:
                    # TODO: This really needs to be `async with session_context`
                    with session_context(self):
                        async with isolate():
                            download = self._downloads[download_id]
                            filename = read_thunk(download.filename)
                            content_type = read_thunk(download.content_type)
                            contents = download.handler()

                            if filename is None:
                                if isinstance(contents, str):
                                    filename = os.path.basename(contents)
                                else:
                                    filename = "download"

                            if content_type is None:
                                (content_type, _) = guess_type(filename)
                            content_disposition_filename = urllib.parse.quote(filename)
                            if content_disposition_filename != filename:
                                content_disposition = f"attachment; filename*=utf-8''{content_disposition_filename}"
                            else:
                                content_disposition = (
                                    f'attachment; filename="{filename}"'
                                )

                            if isinstance(contents, str):
                                # contents is the path to a file
                                return FileResponse(
                                    Path(contents),
                                    headers={
                                        "Content-Disposition": content_disposition,
                                        "Cache-Control": "no-store",
                                    },
                                    media_type=content_type,
                                )
                            elif isinstance(contents, AsyncIterable):

                                async def wrap_content():
                                    # TODO: This really needs to be `async with session_context`
                                    with session_context(self):
                                        async with isolate():
                                            async for chunk in contents:
                                                yield chunk

                                wrapped_contents: AsyncIterable[bytes] = wrap_content()

                                # TODO: This won't work with pyodide, use something else
                                return StreamingResponse(
                                    wrapped_contents,
                                    200,
                                    headers={
                                        "Content-Disposition": content_disposition,
                                        "Cache-Control": "no-store",
                                    },
                                    media_type=content_type,  # type: ignore
                                )
                            else:  # isinstance(contents, Iterable):

                                async def wrap_content():
                                    # TODO: This really needs to be `async with session_context`
                                    with session_context(self):
                                        async with isolate():
                                            for chunk in contents:
                                                yield chunk

                                wrapped_contents: AsyncIterable[bytes] = wrap_content()
                                return StreamingResponse(
                                    wrapped_contents,
                                    200,
                                    headers={
                                        "Content-Disposition": content_disposition,
                                        "Cache-Control": "no-store",
                                    },
                                    media_type=content_type,  # type: ignore
                                )

        return HTMLResponse("<h1>Not Found</h1>", 404)

    # ==========================================================================
    # Outbound message handling
    # ==========================================================================
    def add_message_out(self, message: Dict[str, object]) -> None:
        self._message_queue_out.append(message)

    def get_messages_out(self) -> List[Dict[str, object]]:
        return self._message_queue_out

    def clear_messages_out(self) -> None:
        self._message_queue_out.clear()

    async def send_message(self, message: Dict[str, object]) -> None:
        message_str: str = json.dumps(message) + "\n"
        if self._debug:
            print(
                "SEND: "
                + re.sub("(?m)base64,[a-zA-Z0-9+/=]+", "[base64 data]", message_str),
                end="",
            )
        await self._conn.send(json.dumps(message))

    def _send_error_response(self, message_str: str) -> None:
        print("_send_error_response: " + message_str)
        pass

    # ==========================================================================
    # Flush
    # ==========================================================================
    def request_flush(self) -> None:
        self.app.request_flush(self)

    async def flush(self) -> None:
        values: Dict[str, object] = {}

        for value in self.get_messages_out():
            values.update(value)

        message: Dict[str, object] = {
            "errors": {},
            "values": values,
            "inputMessages": [],
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

    # ==========================================================================
    # Misc
    # ==========================================================================
    async def unhandled_error(self, e: Exception) -> None:
        print("Unhandled error: " + str(e))
        await self.close()

    # TODO: probably name should be id
    def download(
        self,
        name: Optional[str] = None,
        filename: Optional[Union[str, Callable[[], str]]] = None,
        media_type: Union[None, str, Callable[[], str]] = None,
    ):
        def wrapper(
            fn: Callable[[], Union[str, AsyncIterable[bytes], Iterable[bytes]]]
        ):
            if name is None:
                effective_name = fn.__name__
            else:
                effective_name = name

            self._downloads[effective_name] = DownloadHandler(
                filename=filename,
                content_type=media_type,
                handler=fn,
            )

            @self.output(effective_name)
            @functools.wraps(fn)
            def _():
                # TODO: the `w=` parameter should eventually be a worker ID, if we add those
                return f"session/{urllib.parse.quote(self.id)}/download/{urllib.parse.quote(effective_name)}?w="

        return wrapper


class Outputs:
    def __init__(self, session: ShinySession) -> None:
        self._output_obervers: Dict[str, Observer] = {}
        self._session: ShinySession = session

    def __call__(
        self, name: str
    ) -> Callable[[Union[Callable[[], object], render.RenderFunction]], None]:
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
                await self._session.send_message(
                    {"recalculating": {"name": name, "status": "recalculating"}}
                )

                message: Dict[str, object] = {}
                if utils.is_async_callable(fn):
                    fn2 = typing.cast(Callable[[], Awaitable[object]], fn)
                    val = await fn2()
                else:
                    val = fn()
                message[name] = val
                self._session.add_message_out(message)

                await self._session.send_message(
                    {"recalculating": {"name": name, "status": "recalculated"}}
                )

            self._output_obervers[name] = output_obs

            return None

        return set_fn


# ==============================================================================
# Context manager for current session (AKA current reactive domain)
# ==============================================================================
_current_session: ContextVar[Optional[ShinySession]] = ContextVar(
    "current_session", default=None
)


def get_current_session() -> Optional[ShinySession]:
    return _current_session.get()


# TODO: I don't think this works for async (i.e. `async with session_context():`), see
#       how isolate() works for an example
@contextmanager
def session_context(session: Optional[ShinySession]):
    token: Token[Union[ShinySession, None]] = _current_session.set(session)
    try:
        yield
    finally:
        _current_session.reset(token)


def _require_active_session(session: Optional[ShinySession]) -> ShinySession:
    if session is None:
        session = get_current_session()
    if session is None:
        import inspect

        call_stack = inspect.stack()
        if len(call_stack) > 1:
            caller = call_stack[1]
        else:
            # Uncommon case: this function is called from the top-level, so the caller
            # is just _require_active_session.
            caller = call_stack[0]

        calling_fn_name = caller.function
        if calling_fn_name == "__init__":
            # If the caller is __init__, then we're most likely in the initialization of
            # an object. This will get the class name.
            calling_fn_name = caller.frame.f_locals["self"].__class__.__name__

        raise RuntimeError(
            f"{calling_fn_name}() must be called from within an active Shiny session."
        )
    return session


# ==============================================================================
# Miscellaneous functions
# ==============================================================================


class _RenderedDeps(TypedDict):
    deps: List[Dict[str, Any]]
    html: str


def _process_deps(
    ui: TagChildArg, session: Optional[ShinySession] = None
) -> _RenderedDeps:

    session = _require_active_session(session)

    res = TagList(ui).render()
    deps: List[Dict[str, Any]] = []
    for dep in res["dependencies"]:
        session.app.register_web_dependency(dep)
        dep_dict = dep.as_dict(lib_prefix=session.app.LIB_PREFIX)
        deps.append(dep_dict)

    return {"deps": deps, "html": res["html"]}


T = TypeVar("T")


def read_thunk(thunk: Union[Callable[[], T], T]) -> T:
    if callable(thunk):
        return thunk()
    else:
        return thunk
