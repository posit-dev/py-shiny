# Needed for types imported only during TYPE_CHECKING with Python 3.7 - 3.9
# See https://www.python.org/dev/peps/pep-0655/#usage-in-python-3-11
from __future__ import annotations

__all__ = ("Session", "Inputs", "Outputs")

import contextlib
import dataclasses
import enum
import functools
import json
import os
import re
import traceback
import typing
import urllib.parse
import warnings
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncIterable,
    Awaitable,
    Callable,
    Iterable,
    Optional,
    TypeVar,
    cast,
    overload,
)

from htmltools import TagChild, TagList
from starlette.requests import HTTPConnection, Request
from starlette.responses import HTMLResponse, PlainTextResponse, StreamingResponse
from starlette.types import ASGIApp

if TYPE_CHECKING:
    from .._app import App

from .. import _utils, render
from .._connection import Connection, ConnectionClosed
from .._docstring import add_example
from .._fileupload import FileInfo, FileUploadManager
from .._namespaces import Id, ResolvedId, Root
from .._typing_extensions import TypedDict
from ..http_staticfiles import FileResponse
from ..input_handler import input_handlers
from ..reactive import Effect, Effect_, Value, flush, isolate
from ..reactive._core import lock, on_flushed
from ..render import RenderFunction
from ..types import SafeException, SilentCancelOutputException, SilentException
from ._utils import RenderedDeps, read_thunk_opt, session_context

IT = TypeVar("IT")
OT = TypeVar("OT")


class ConnectionState(enum.Enum):
    Start = 0
    Running = 1
    Closed = 2


class ProtocolError(Exception):
    message: str

    def __init__(self, message: str = ""):
        super(ProtocolError, self).__init__(message)
        self.message = message


class SessionWarning(RuntimeWarning):
    pass


# By default warnings are shown once; we want to always show them.
warnings.simplefilter("always", SessionWarning)


# This cast is necessary because if the type checker thinks that if
# "tag" isn't in `message`, then it's not a ClientMessage object.
# This will be fixable when TypedDict items can be marked as
# potentially missing, in Python 3.10, with PEP 655.
class ClientMessage(TypedDict):
    method: str


class ClientMessageInit(ClientMessage):
    data: dict[str, object]


class ClientMessageUpdate(ClientMessage):
    data: dict[str, object]


# For messages where "method" is something other than "init" or "update".
class ClientMessageOther(ClientMessage):
    args: list[object]
    tag: int


# This is the type for the function provided by the user to provide the contents of a
# download. It must be a function that takes no arguments, and returns one of:
# 1. A string, which will be interpreted as a path
# 2. A regular Iterable of bytes or strings (i.e. a generator function)
# 3. An AsyncIterable of bytes or strings (i.e. an async generator function)
#
# (Not currently supported is Awaitable[str], could be added easily enough if needed.)
DownloadHandler = Callable[
    [], "str | Iterable[bytes | str] | AsyncIterable[bytes | str]"
]

DynamicRouteHandler = Callable[[Request], ASGIApp]


@dataclasses.dataclass
class DownloadInfo:
    filename: Callable[[], str] | str | None
    content_type: Optional[Callable[[], str] | str]
    handler: DownloadHandler
    encoding: str


class OutBoundMessageQueues(TypedDict):
    values: list[dict[str, Any]]
    input_messages: list[dict[str, Any]]
    errors: list[dict[str, Any]]


def empty_outbound_message_queues() -> OutBoundMessageQueues:
    return {"values": [], "input_messages": [], "errors": []}


# Makes isinstance(x, Session) also return True when x is a SessionProxy (i.e., a module
# session)
class SessionMeta(type):
    def __instancecheck__(self, __instance: Any) -> bool:
        return isinstance(__instance, SessionProxy)


class Session(object, metaclass=SessionMeta):
    """
    A class representing a user session.
    """

    ns: ResolvedId = Root

    # These declarations are here only for pyright and stubgen to generate stub files.
    app: App
    id: str
    http_conn: HTTPConnection
    input: Inputs
    output: Outputs
    user: str | None
    groups: list[str] | None

    # ==========================================================================
    # Initialization
    # ==========================================================================
    def __init__(
        self, app: App, id: str, conn: Connection, debug: bool = False
    ) -> None:
        self.app: App = app
        self.id: str = id
        self._conn: Connection = conn
        self._debug: bool = debug

        # The HTTPConnection representing the WebSocket. This is used so that we can
        # query information about the request, like headers, cookies, etc.
        self.http_conn: HTTPConnection = conn.get_http_conn()

        self.input: Inputs = Inputs(dict())
        self.output: Outputs = Outputs(self, self.ns, dict(), dict())

        self.user: str | None = None
        self.groups: list[str] | None = None
        credentials_json: str = ""
        if "shiny-server-credentials" in self.http_conn.headers:
            credentials_json = self.http_conn.headers["shiny-server-credentials"]
        elif "rstudio-connect-credentials" in self.http_conn.headers:
            # Fall back to "rstudio-connect-credentials" if "shiny-server-credentials"
            # isn't available. Note: This is only needed temporarily, because Connect
            # treates PyShiny apps as FastAPI apps. When there's proper Shiny support,
            # this can be removed.
            credentials_json = self.http_conn.headers["rstudio-connect-credentials"]
        if credentials_json:
            try:
                creds = json.loads(credentials_json)
                self.user = creds["user"]
                self.groups = creds["groups"]
            except Exception as e:
                print("Error parsing credentials header: " + str(e))

        self._outbound_message_queues = empty_outbound_message_queues()

        self._message_handlers: dict[
            str, Callable[..., Awaitable[object]]
        ] = self._create_message_handlers()
        self._file_upload_manager: FileUploadManager = FileUploadManager()
        self._on_ended_callbacks = _utils.Callbacks()
        self._has_run_session_end_tasks: bool = False
        self._downloads: dict[str, DownloadInfo] = {}
        self._dynamic_routes: dict[str, DynamicRouteHandler] = {}

        self._register_session_end_callbacks()

        self._flush_callbacks = _utils.Callbacks()
        self._flushed_callbacks = _utils.Callbacks()

    def _register_session_end_callbacks(self) -> None:
        # This is to be called from the initialization. It registers functions
        # that are called when a session ends.

        # Clear file upload directories, if present
        self.on_ended(self._file_upload_manager.rm_upload_dir)

    def _run_session_end_tasks(self) -> None:
        if self._has_run_session_end_tasks:
            return
        self._has_run_session_end_tasks = True

        try:
            self._on_ended_callbacks.invoke()
        finally:
            self.app._remove_session(self)

    async def close(self, code: int = 1001) -> None:
        """
        Close the session.
        """
        await self._conn.close(code, None)
        self._run_session_end_tasks()

    async def _run(self) -> None:
        conn_state: ConnectionState = ConnectionState.Start

        def verify_state(expected_state: ConnectionState) -> None:
            if conn_state != expected_state:
                raise ProtocolError("Invalid method for the current session state")

        with contextlib.ExitStack() as stack:
            try:
                await self._send_message(
                    {
                        "config": {
                            "workerId": "",
                            "sessionId": self.id,
                            "user": None,
                        }
                    }
                )

                while True:
                    message: str = await self._conn.receive()
                    if self._debug:
                        print("RECV: " + message, flush=True)

                    try:
                        message_obj = json.loads(
                            message, object_hook=_utils.lists_to_tuples
                        )
                    except json.JSONDecodeError:
                        warnings.warn(
                            "ERROR: Invalid JSON message", SessionWarning, stacklevel=2
                        )
                        return

                    if "method" not in message_obj:
                        self._send_error_response("Message does not contain 'method'.")
                        return

                    async with lock():
                        if message_obj["method"] == "init":
                            verify_state(ConnectionState.Start)

                            # When a reactive flush occurs, flush the session's outputs,
                            # errors, etc. to the client. Note that this is
                            # `reactive._core.on_flushed`, not `self.on_flushed`.
                            unreg = on_flushed(self._flush)
                            # When the session ends, stop flushing outputs on reactive
                            # flush.
                            stack.callback(unreg)

                            conn_state = ConnectionState.Running
                            message_obj = typing.cast(ClientMessageInit, message_obj)
                            self._manage_inputs(message_obj["data"])

                            with session_context(self):
                                self.app.server(self.input, self.output, self)

                        elif message_obj["method"] == "update":
                            verify_state(ConnectionState.Running)

                            message_obj = typing.cast(ClientMessageUpdate, message_obj)
                            self._manage_inputs(message_obj["data"])

                        elif "tag" in message_obj and "args" in message_obj:
                            verify_state(ConnectionState.Running)

                            message_obj = typing.cast(ClientMessageOther, message_obj)
                            await self._dispatch(message_obj)

                        else:
                            raise ProtocolError(
                                f"Unrecognized method {message_obj['method']}"
                            )

                        self._request_flush()

                        await flush()

            except ConnectionClosed:
                ...
            except Exception as e:
                try:
                    self._send_error_response(str(e))
                except Exception:
                    pass
                finally:
                    await self.close()
            finally:
                self._run_session_end_tasks()

    def _manage_inputs(self, data: dict[str, object]) -> None:
        for key, val in data.items():
            keys = key.split(":")
            if len(keys) > 2:
                raise ValueError(
                    "Input name+type is not allowed to contain more than one ':' -- "
                    + key
                )
            if len(keys) == 2:
                val = input_handlers._process_value(keys[1], val, keys[0], self)

            # The keys[0] value is already a fully namespaced id; make that explicit by
            # wrapping it in ResolvedId, otherwise self.input will throw an id
            # validation error.
            self.input[ResolvedId(keys[0])]._set(val)

        self.output._manage_hidden()

    def _is_hidden(self, name: str) -> bool:
        with isolate():
            # The .clientdata_output_{name}_hidden string is already a fully namespaced
            # id; make that explicit by wrapping it in ResolvedId, otherwise self.input
            # will throw an id validation error.
            hidden_value_obj = cast(
                Value[bool], self.input[ResolvedId(f".clientdata_output_{name}_hidden")]
            )
            if not hidden_value_obj.is_set():
                return True

            return hidden_value_obj()

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
        await self._send_message({"response": {"tag": message["tag"], "value": value}})

    # This is called during __init__.
    def _create_message_handlers(self) -> dict[str, Callable[..., Awaitable[object]]]:
        async def uploadInit(file_infos: list[FileInfo]) -> dict[str, object]:
            with session_context(self):
                if self._debug:
                    print("Upload init: " + str(file_infos), flush=True)

                # TODO: Don't alter message in place?
                for fi in file_infos:
                    if fi["type"] == "":
                        fi["type"] = _utils.guess_mime_type(fi["name"])

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
                    "Received uploadEnd message for non-existent upload operation.",
                    SessionWarning,
                    stacklevel=2,
                )
                return None
            file_data = upload_op.finish()
            # The input_id string is already a fully namespaced id; make that explicit
            # by wrapping it in ResolvedId, otherwise self.input will throw an id
            # validation error.
            self.input[ResolvedId(input_id)]._set(file_data)
            # Explicitly return None to signal that the message was handled.
            return None

        return {
            "uploadInit": uploadInit,
            "uploadEnd": uploadEnd,
        }

    # ==========================================================================
    # Handling /session/{session_id}/{action}/{subpath} requests
    # ==========================================================================
    async def _handle_request(
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
            download_id = subpath
            if download_id in self._downloads:
                with session_context(self):
                    with isolate():
                        download = self._downloads[download_id]
                        filename = read_thunk_opt(download.filename)
                        content_type = read_thunk_opt(download.content_type)
                        contents = download.handler()

                        if filename is None:
                            if isinstance(contents, str):
                                filename = os.path.basename(contents)
                            else:
                                warnings.warn(
                                    "Unable to infer a filename for the "
                                    f"'{download_id}' download handler; please use "
                                    "@session.download(filename=) to specify one "
                                    "manually",
                                    SessionWarning,
                                    stacklevel=2,
                                )
                                filename = download_id

                        if content_type is None:
                            content_type = _utils.guess_mime_type(filename)
                        content_disposition_filename = urllib.parse.quote(filename)
                        if content_disposition_filename != filename:
                            content_disposition = f"attachment; filename*=utf-8''{content_disposition_filename}"
                        else:
                            content_disposition = f'attachment; filename="{filename}"'
                        headers = {
                            "Content-Disposition": content_disposition,
                            "Cache-Control": "no-store",
                        }

                        if isinstance(contents, str):
                            # contents is the path to a file
                            return FileResponse(
                                Path(contents),
                                headers=headers,
                                media_type=content_type,
                            )

                        wrapped_contents: AsyncIterable[bytes]

                        if isinstance(contents, AsyncIterable):
                            # Need to wrap the app-author-provided iterator in a
                            # callback that installs the appropriate context mgrs.
                            # We already use this context mgrs further up in the
                            # implementation of handle_request(), but the iterators
                            # aren't invoked until after handle_request() returns.
                            async def wrap_content_async() -> AsyncIterable[bytes]:
                                with session_context(self):
                                    with isolate():
                                        async for chunk in contents:
                                            if isinstance(chunk, str):
                                                yield chunk.encode(download.encoding)
                                            else:
                                                yield chunk

                            wrapped_contents = wrap_content_async()

                        else:  # isinstance(contents, Iterable):

                            async def wrap_content_sync() -> AsyncIterable[bytes]:
                                with session_context(self):
                                    with isolate():
                                        for chunk in contents:
                                            if isinstance(chunk, str):
                                                yield chunk.encode(download.encoding)
                                            else:
                                                yield chunk

                            wrapped_contents = wrap_content_sync()

                        # In streaming downloads, we send a 200 response, but if an
                        # error occurs in the middle of it, the client needs to know.
                        # With chunked encoding, the client will know if an error occurs
                        # if it does not receive a terminating (empty) chunk.
                        headers["Transfer-Encoding"] = "chunked"

                        return StreamingResponse(
                            wrapped_contents,
                            200,
                            headers=headers,
                            media_type=content_type,  # type: ignore
                        )

        elif action == "dynamic_route" and request.method == "GET" and subpath:
            name = subpath
            handler = self._dynamic_routes.get(name, None)
            if handler is None:
                return HTMLResponse("<h1>Bad Request</h1>", 400)

            with session_context(self):
                with isolate():
                    if _utils.is_async_callable(handler):
                        return await handler(request)
                    else:
                        return handler(request)

        return HTMLResponse("<h1>Not Found</h1>", 404)

    def send_input_message(self, id: str, message: dict[str, object]) -> None:
        """
        Send an input message to the session.

        Sends a message to an input on the session's client web page; if the input is
        present and bound on the page at the time the message is received, then the
        input binding object's ``receiveMessage(el, message)`` method will be called.
        This method should generally not be called directly from Shiny apps, but through
        friendlier wrapper functions like ``ui.update_text()``.

        Parameters
        ----------
        id
            An id matching the id of an input to update.
        message
            The message to send.
        """
        msg: dict[str, object] = {"id": id, "message": message}
        self._outbound_message_queues["input_messages"].append(msg)
        self._request_flush()

    def _send_insert_ui(
        self, selector: str, multiple: bool, where: str, content: RenderedDeps
    ) -> None:
        msg = {
            "selector": selector,
            "multiple": multiple,
            "where": where,
            "content": content,
        }
        self._send_message_sync({"shiny-insert-ui": msg})

    def _send_remove_ui(self, selector: str, multiple: bool) -> None:
        msg = {"selector": selector, "multiple": multiple}
        self._send_message_sync({"shiny-remove-ui": msg})

    def _send_progress(self, type: str, message: object) -> None:
        msg: dict[str, object] = {"progress": {"type": type, "message": message}}
        self._send_message_sync(msg)

    @add_example()
    async def send_custom_message(self, type: str, message: dict[str, object]) -> None:
        """
        Send a message to the client.

        Parameters
        ----------
        type
            The type of message to send.
        message
            The message to send.

        Note
        ----
        Sends messages to the client which can be handled in JavaScript with
        ``Shiny.addCustomMessageHandler(type, function(message){...})``. Once the
        message handler is added, it will be invoked each time ``send_custom_message()``
        is called on the server.
        """
        await self._send_message({"custom": {type: message}})

    async def _send_message(self, message: dict[str, object]) -> None:
        message_str: str = json.dumps(message) + "\n"
        if self._debug:
            print(
                "SEND: "
                + re.sub("(?m)base64,[a-zA-Z0-9+/=]+", "[base64 data]", message_str),
                end="",
                flush=True,
            )
        await self._conn.send(json.dumps(message))

    def _send_message_sync(self, message: dict[str, object]) -> None:
        """
        Same as _send_message, except that if the message isn't too large and the socket
        isn't too backed up, then the message may be sent synchronously instead of
        having to wait until the current task yields (and potentially much longer than
        that, if there is a lot of contention for the main thread).
        """
        _utils.run_coro_hybrid(self._send_message(message))

    def _send_error_response(self, message_str: str) -> None:
        print("_send_error_response: " + message_str)
        pass

    # ==========================================================================
    # Flush
    # ==========================================================================
    @add_example()
    def on_flush(self, fn: Callable[[], None], once: bool = True) -> Callable[[], None]:
        """
        Register a function to call before the next reactive flush.

        Parameters
        ----------
        fn
            The function to call.
        once
            Whether to call the function only once or on every flush.

        Returns
        -------
        :
            A function that can be used to cancel the registration.
        """
        return self._flush_callbacks.register(fn, once)

    @add_example()
    def on_flushed(
        self, fn: Callable[[], None], once: bool = True
    ) -> Callable[[], None]:
        """
        Register a function to call after the next reactive flush.

        Parameters
        ----------
        fn
            The function to call.
        once
            Whether to call the function only once or on every flush.

        Returns
        -------
        :
            A function that can be used to cancel the registration.
        """
        return self._flushed_callbacks.register(fn, once)

    def _request_flush(self) -> None:
        self.app._request_flush(self)

    async def _flush(self) -> None:
        with session_context(self):
            self._flush_callbacks.invoke()

        try:
            omq = self._outbound_message_queues

            values: dict[str, object] = {}
            for v in omq["values"]:
                values.update(v)

            errors: dict[str, object] = {}
            for err in omq["errors"]:
                errors.update(err)

            message: dict[str, object] = {
                "values": values,
                "inputMessages": omq["input_messages"],
                "errors": errors,
            }

            try:
                await self._send_message(message)
            finally:
                self._outbound_message_queues = empty_outbound_message_queues()
        finally:
            with session_context(self):
                self._flushed_callbacks.invoke()

    # ==========================================================================
    # On session ended
    # ==========================================================================
    @add_example()
    def on_ended(self, fn: Callable[[], None]) -> Callable[[], None]:
        """
        Registers a function to be called after the client has disconnected.

        Parameters
        ----------
        fn
            The function to call.

        Returns
        -------
        :
            A function that can be used to cancel the registration.
        """
        return self._on_ended_callbacks.register(fn)

    # ==========================================================================
    # Misc
    # ==========================================================================
    async def _unhandled_error(self, e: Exception) -> None:
        print("Unhandled error: " + str(e))
        await self.close()

    @add_example()
    def download(
        self,
        id: Optional[str] = None,
        filename: Optional[str | Callable[[], str]] = None,
        media_type: None | str | Callable[[], str] = None,
        encoding: str = "utf-8",
    ) -> Callable[[DownloadHandler], None]:
        """
        Decorator to register a function to handle a download.

        Parameters
        ----------
        id
            The name of the download.
        filename
            The filename of the download.
        media_type
            The media type of the download.
        encoding
            The encoding of the download.

        Returns
        -------
        :
            The decorated function.
        """

        def wrapper(fn: DownloadHandler):
            effective_name = id or fn.__name__

            self._downloads[effective_name] = DownloadInfo(
                filename=filename,
                content_type=media_type,
                handler=fn,
                encoding=encoding,
            )

            @self.output(id=effective_name)
            @render.text
            @functools.wraps(fn)
            def _():
                # TODO: the `w=` parameter should eventually be a worker ID, if we add those
                return f"session/{urllib.parse.quote(self.id)}/download/{urllib.parse.quote(effective_name)}?w="

        return wrapper

    @add_example()
    def dynamic_route(self, name: str, handler: DynamicRouteHandler) -> str:
        """
        Register a function to call when a dynamically generated, session-specific,
        route is requested.

        Provides a convenient way to serve-up session-dependent values for other
        clients/applications to consume.

        Parameters
        ----------
        name
            A name for the route (used to determine part of the URL path).
        handler
            The function to call when a request is made to the route. This function
            should take a single argument (a :class:`starlette.requests.Request` object)
            and return a :class:`starlette.types.ASGIApp` object.


        Returns
        -------
        :
            The URL path for the route.
        """

        self._dynamic_routes.update({name: handler})
        nonce = _utils.rand_hex(8)
        return f"session/{urllib.parse.quote(self.id)}/dynamic_route/{urllib.parse.quote(name)}?nonce={urllib.parse.quote(nonce)}"

    def _process_ui(self, ui: TagChild) -> RenderedDeps:
        res = TagList(ui).render()
        deps: list[dict[str, Any]] = []
        for dep in res["dependencies"]:
            self.app._register_web_dependency(dep)
            dep_dict = dep.as_dict(lib_prefix=self.app.lib_prefix)
            deps.append(dep_dict)

        return {"deps": deps, "html": res["html"]}

    def make_scope(self, id: Id) -> Session:
        ns = self.ns(id)
        return SessionProxy(parent=self, ns=ns)  # type: ignore

    def root_scope(self) -> Session:
        return self


class SessionProxy:
    ns: ResolvedId
    input: Inputs
    output: Outputs

    def __init__(self, parent: Session, ns: ResolvedId) -> None:
        self._parent = parent
        self.ns = ns
        self.input = Inputs(values=parent.input._map, ns=ns)
        self.output = Outputs(
            session=cast(Session, self),
            effects=self.output._effects,
            suspend_when_hidden=self.output._suspend_when_hidden,
            ns=ns,
        )

    def __getattr__(self, attr: str) -> Any:
        return getattr(self._parent, attr)

    def make_scope(self, id: str) -> Session:
        return self._parent.make_scope(self.ns(id))

    def root_scope(self) -> Session:
        res = self
        while isinstance(res, SessionProxy):
            res = res._parent
        return res

    def send_input_message(self, id: str, message: dict[str, object]) -> None:
        return self._parent.send_input_message(self.ns(id), message)

    def dynamic_route(self, name: str, handler: DynamicRouteHandler) -> str:
        return self._parent.dynamic_route(self.ns(name), handler)

    def download(
        self, id: Optional[str] = None, **kwargs: object
    ) -> Callable[[DownloadHandler], None]:
        def wrapper(fn: DownloadHandler):
            id_ = self.ns(id or fn.__name__)
            return self._parent.download(id=id_, **kwargs)(fn)

        return wrapper


# ======================================================================================
# Inputs
# ======================================================================================


# TODO: provide a real input typing example when we have an answer for that
# https://github.com/rstudio/py-shiny/issues/70
class Inputs:
    """
    A class representing Shiny input values.

    This class provides access to a :class:`~shiny.session.Session`'s input values. The
    input values are reactive :class:`~shiny.reactive.Values`, and can be accessed with
    the ``[]`` operator, or with ``.``. For example, if there is an input named ``x``,
    it can be accessed via ``input["x"]()`` or ``input.x()``.
    """

    def __init__(
        self, values: dict[str, Value[Any]], ns: Callable[[str], str] = Root
    ) -> None:
        self._map = values
        self._ns = ns

    def __setitem__(self, key: str, value: Value[Any]) -> None:
        if not isinstance(value, Value):
            raise TypeError("`value` must be a reactive.Value object.")

        self._map[self._ns(key)] = value

    def __getitem__(self, key: str) -> Value[Any]:
        key = self._ns(key)
        # Auto-populate key if accessed but not yet set. Needed to take reactive
        # dependencies on input values that haven't been received from client
        # yet.
        if key not in self._map:
            self._map[key] = Value[Any](read_only=True)

        return self._map[key]

    def __delitem__(self, key: str) -> None:
        del self._map[self._ns(key)]

    # Allow access of values as attributes.
    def __setattr__(self, attr: str, value: Value[Any]) -> None:
        if attr in ("_map", "_ns"):
            super().__setattr__(attr, value)
            return

        self.__setitem__(attr, value)

    def __getattr__(self, attr: str) -> Value[Any]:
        if attr in ("_map", "_ns"):
            return object.__getattribute__(self, attr)
        return self.__getitem__(attr)

    def __delattr__(self, key: str) -> None:
        self.__delitem__(key)

    def __contains__(self, key: str) -> bool:
        # This looks simple, but does a number of things. By accessing `self[key]`, it
        # indirectly calls `__getitem__`, which applies a namespace to the key, and
        # it populates the key if it doesn't exist yet. It then calls `is_set()`, which
        # creates a reactive dependency, and returns whether the value is set.
        return self[key].is_set()


# ======================================================================================
# Outputs
# ======================================================================================
class Outputs:
    """
    A class representing Shiny output definitions.
    """

    def __init__(
        self,
        session: Session,
        ns: Callable[[str], str],
        effects: dict[str, Effect_],
        suspend_when_hidden: dict[str, bool],
    ) -> None:
        self._session = session
        self._ns = ns
        self._effects = effects
        self._suspend_when_hidden = suspend_when_hidden

    @overload
    def __call__(self, fn: RenderFunction[Any, Any]) -> None:
        ...

    @overload
    def __call__(
        self,
        *,
        id: Optional[str] = None,
        suspend_when_hidden: bool = True,
        priority: int = 0,
        name: Optional[str] = None,
    ) -> Callable[[RenderFunction[Any, Any]], None]:
        ...

    def __call__(
        self,
        fn: Optional[RenderFunction[IT, OT]] = None,
        *,
        id: Optional[str] = None,
        suspend_when_hidden: bool = True,
        priority: int = 0,
        name: Optional[str] = None,
    ) -> None | Callable[[RenderFunction[IT, OT]], None]:
        if name is not None:
            from .. import _deprecated

            _deprecated.warn_deprecated(
                "`@output(name=...)` is deprecated. Use `@output(id=...)` instead."
            )
            id = name

        def set_fn(fn: RenderFunction[IT, OT]) -> None:
            # Get the (possibly namespaced) output id
            output_name = self._ns(id or fn.__name__)

            if not isinstance(fn, RenderFunction):
                raise TypeError(
                    "`@output` must be applied to a `@render.xx` function.\n"
                    + "In other words, `@output` must be above `@render.xx`."
                )

            # fn is a RenderFunction object. Give it a bit of metadata.
            fn.set_metadata(self._session, output_name)

            if output_name in self._effects:
                self._effects[output_name].destroy()

            self._suspend_when_hidden[output_name] = suspend_when_hidden

            @Effect(
                suspended=suspend_when_hidden and self._session._is_hidden(output_name),
                priority=priority,
            )
            async def output_obs():
                await self._session._send_message(
                    {"recalculating": {"name": output_name, "status": "recalculating"}}
                )

                message: dict[str, Optional[OT]] = {}
                try:
                    if _utils.is_async_callable(fn):
                        message[output_name] = await fn()
                    else:
                        message[output_name] = fn()
                except SilentCancelOutputException:
                    return
                except SilentException:
                    message[output_name] = None
                except Exception as e:
                    # Print traceback to the console
                    traceback.print_exc()
                    # Possibly sanitize error for the user
                    if self._session.app.sanitize_errors and not isinstance(
                        e, SafeException
                    ):
                        err_msg = self._session.app.sanitize_error_msg
                    else:
                        err_msg = str(e)
                    # Register the outbound error message
                    err_message = {
                        output_name: {
                            "message": err_msg,
                            # TODO: is it possible to get the call?
                            "call": None,
                            # TODO: I don't think we actually use this for anything client-side
                            "type": None,
                        }
                    }
                    self._session._outbound_message_queues["errors"].append(err_message)

                self._session._outbound_message_queues["values"].append(message)

                await self._session._send_message(
                    {"recalculating": {"name": output_name, "status": "recalculated"}}
                )

            output_obs.on_invalidate(
                lambda: self._session._send_progress("binding", {"id": output_name})
            )

            self._effects[output_name] = output_obs

            return None

        if fn is None:
            return set_fn
        else:
            return set_fn(fn)

    def _manage_hidden(self) -> None:
        "Suspends execution of hidden outputs and resumes execution of visible outputs."
        output_names = list(self._suspend_when_hidden.keys())
        for name in output_names:
            if self._should_suspend(name):
                self._effects[name].suspend()
            else:
                self._effects[name].resume()

    def _should_suspend(self, name: str) -> bool:
        return self._suspend_when_hidden[name] and self._session._is_hidden(name)
