from __future__ import annotations

__all__ = ("Session", "Inputs", "Outputs", "ClientData")
import asyncio
import contextlib
import dataclasses
import enum
import functools
import json
import os
import re
import sys
import traceback
import typing
import urllib.parse
import warnings
from abc import ABC, abstractmethod
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncIterable,
    Awaitable,
    Callable,
    Generator,
    Iterable,
    Literal,
    Optional,
    Union,
    cast,
    overload,
)

from htmltools import TagChild, TagList
from starlette.requests import HTTPConnection, Request
from starlette.responses import HTMLResponse, PlainTextResponse, StreamingResponse
from starlette.types import ASGIApp

from .. import _utils, reactive, render
from .._connection import Connection, ConnectionClosed
from .._deprecated import warn_deprecated
from .._docstring import add_example
from .._fileupload import FileInfo, FileUploadManager
from .._namespaces import Id, Root
from .._typing_extensions import NotRequired, TypedDict
from .._utils import wrap_async
from ..bookmark import BookmarkApp, BookmarkProxy
from ..bookmark._button import BOOKMARK_ID
from ..bookmark._restore_state import RestoreContext
from ..bookmark._serializers import serializer_file_input
from ..http_staticfiles import FileResponse
from ..input_handler import input_handlers
from ..module import ResolvedId
from ..reactive import Effect_, Value, effect
from ..reactive import flush as reactive_flush
from ..reactive import isolate
from ..reactive._core import lock
from ..reactive._core import on_flushed as reactive_on_flushed
from ..render.renderer import Renderer, RendererT
from ..types import (
    Jsonifiable,
    SafeException,
    SilentCancelOutputException,
    SilentException,
    SilentOperationInProgressException,
)
from ._utils import RenderedDeps, read_thunk_opt, session_context

if TYPE_CHECKING:
    from .._app import App
    from ..bookmark import Bookmark
    from ..bookmark._serializers import Unserializable


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
    [],
    Union[str, Iterable[Union[bytes, str]], AsyncIterable[Union[bytes, str]]],
]

DynamicRouteHandler = Callable[[Request], ASGIApp]


@dataclasses.dataclass
class DownloadInfo:
    filename: Callable[[], str] | str | None
    content_type: Optional[Callable[[], str] | str]
    handler: DownloadHandler
    encoding: str


class OutBoundMessageQueues:
    def __init__(self):
        self.values: dict[str, Any] = {}
        self.errors: dict[str, Any] = {}
        self.input_messages: list[dict[str, Any]] = []

    def reset(self) -> None:
        self.values.clear()
        self.errors.clear()
        self.input_messages.clear()

    def set_value(self, id: str, value: Any) -> None:
        self.values[id] = value
        # remove from self.errors
        if id in self.errors:
            del self.errors[id]

    def set_error(self, id: str, error: Any) -> None:
        self.errors[id] = error
        # remove from self.values
        if id in self.values:
            del self.values[id]

    def add_input_message(self, id: str, message: dict[str, Any]) -> None:
        self.input_messages.append({"id": id, "message": message})


# ======================================================================================
# Session abstract base class
# ======================================================================================
class Session(ABC):
    """
    Interface definition for Session-like classes, like :class:`AppSession`,
    :class:`SessionProxy`, and :class:`~shiny.express.ExpressStubSession`.
    """

    ns: ResolvedId
    app: App
    id: str
    input: Inputs
    output: Outputs
    clientdata: ClientData

    # Could be done with a weak ref dict from root to all children. Then we could just
    # iterate over all modules and check the `.bookmark_exclude` list of each proxy
    # session.
    bookmark: Bookmark
    user: str | None
    groups: list[str] | None

    # TODO: not sure these should be directly exposed
    _outbound_message_queues: OutBoundMessageQueues
    _downloads: dict[str, DownloadInfo]

    @abstractmethod
    def is_stub_session(self) -> bool:
        """
        Returns whether this is a stub session.

        In the UI-rendering phase of Shiny Express apps, the session context has a stub
        session. This stub session is not a real session; it is there only so that code
        which expects a session can run without raising errors.
        """

    @add_example("session_close")
    @abstractmethod
    async def close(self, code: int = 1001) -> None:
        """
        Close the session.
        """

    @abstractmethod
    def _is_hidden(self, name: str) -> bool: ...

    @add_example("session_on_ended")
    @abstractmethod
    def on_ended(
        self,
        fn: Callable[[], None] | Callable[[], Awaitable[None]],
    ) -> Callable[[], None]:
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

    @abstractmethod
    def make_scope(self, id: Id) -> Session: ...

    @abstractmethod
    def root_scope(self) -> Session: ...

    @abstractmethod
    def _process_ui(self, ui: TagChild) -> RenderedDeps: ...

    @abstractmethod
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

    @abstractmethod
    def _send_insert_ui(
        self, selector: str, multiple: bool, where: str, content: RenderedDeps
    ) -> None: ...

    @abstractmethod
    def _send_remove_ui(self, selector: str, multiple: bool) -> None: ...

    @overload
    @abstractmethod
    def _send_progress(
        self, type: Literal["binding"], message: BindingProgressMessage
    ) -> None:
        pass

    @overload
    @abstractmethod
    def _send_progress(
        self, type: Literal["open"], message: OpenProgressMessage
    ) -> None:
        pass

    @overload
    @abstractmethod
    def _send_progress(
        self, type: Literal["close"], message: CloseProgressMessage
    ) -> None:
        pass

    @overload
    @abstractmethod
    def _send_progress(
        self, type: Literal["update"], message: UpdateProgressMessage
    ) -> None:
        pass

    @abstractmethod
    def _send_progress(self, type: str, message: object) -> None: ...

    @add_example("session_send_custom_message")
    @abstractmethod
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

    @abstractmethod
    async def _send_message(self, message: dict[str, object]) -> None: ...

    @abstractmethod
    def _send_message_sync(self, message: dict[str, object]) -> None:
        """
        Same as _send_message, except that if the message isn't too large and the socket
        isn't too backed up, then the message may be sent synchronously instead of
        having to wait until the current task yields (and potentially much longer than
        that, if there is a lot of contention for the main thread).
        """

    @add_example("session_on_flush")
    @abstractmethod
    def on_flush(
        self,
        fn: Callable[[], None] | Callable[[], Awaitable[None]],
        once: bool = True,
    ) -> Callable[[], None]:
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

    @add_example("session_on_flushed")
    @abstractmethod
    def on_flushed(
        self,
        fn: Callable[[], None] | Callable[[], Awaitable[None]],
        once: bool = True,
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

    @abstractmethod
    async def _unhandled_error(self, e: Exception) -> None: ...

    @abstractmethod
    def download(
        self,
        id: Optional[str] = None,
        filename: Optional[str | Callable[[], str]] = None,
        media_type: None | str | Callable[[], str] = None,
        encoding: str = "utf-8",
    ) -> Callable[[DownloadHandler], None]:
        """
        Deprecated. Please use :class:`~shiny.render.download` instead.

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

    @add_example("session_dynamic_route")
    @abstractmethod
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

    @abstractmethod
    def set_message_handler(
        self,
        name: str,
        handler: (
            Callable[..., Jsonifiable] | Callable[..., Awaitable[Jsonifiable]] | None
        ),
        *,
        _handler_session: Optional[Session] = None,
    ) -> str:
        """
        Set a client message handler.

        Sets a method that can be called by the client via
        `Shiny.shinyapp.makeRequest()`. `Shiny.shinyapp.makeRequest()` makes a request
        to the server and waits for a response. By using `makeRequest()` (JS) and
        `set_message_handler()` (python), you can have a much richer communication
        interaction than just using Input values and re-rendering outputs.

        For example, `@render.data_frame` can have many cells edited. While it is
        possible to set many input values, if `makeRequest()` did not exist, the data
        frame would be updated on the first cell update. This would cause the data frame
        to be re-rendered, cancelling any pending cell updates. `makeRequest()` allows
        for individual cell updates to be sent to the server, processed, and handled by
        the existing data frame output.

        When the message handler is executed, it will be executed within an isolated
        reactive context and the session context that set the message handler.

        Parameters
        ----------
        name
            The name of the message handler.
        handler
            The handler function to be called when the client makes a message for the
            given name.  The handler function should take any number of arguments that
            are provided by the client and return a JSON-serializable object.

            If the value is `None`, then the handler at `name` will be removed.
        _handler_session
            For internal use. This is the session which will be used as the session
            context when calling the handler.

        Returns
        -------
        :
            The key under which the handler is stored (or removed). This value will be
            namespaced when used with a session proxy.
        """

    @abstractmethod
    def _increment_busy_count(self) -> None: ...

    @abstractmethod
    def _decrement_busy_count(self) -> None: ...


# ======================================================================================
# AppSession
# ======================================================================================


class AppSession(Session):
    """
    A class representing a user session.
    """

    # ==========================================================================
    # Initialization
    # ==========================================================================
    def __init__(
        self, app: App, id: str, conn: Connection, debug: bool = False
    ) -> None:
        self.ns: ResolvedId = Root
        self.app: App = app
        self.id: str = id
        self._conn: Connection = conn
        self._debug: bool = debug
        self._busy_count: int = 0
        self._message_handlers: dict[
            str,
            tuple[Callable[..., Awaitable[Jsonifiable]], Session],
        ] = {}
        """
        Dictionary of message handlers for the session.

        If a request is sent from the client to the server via
        `window.Shiny.make_request()`, the server will look up the method in this
        dictionary and call the corresponding function with the arguments provided in
        the request.
        """
        self._init_message_handlers()

        # The HTTPConnection representing the WebSocket. This is used so that we can
        # query information about the request, like headers, cookies, etc.
        self.http_conn: HTTPConnection = conn.get_http_conn()

        self.input: Inputs = Inputs(dict())
        self.output: Outputs = Outputs(self, self.ns, outputs=dict())
        self.clientdata: ClientData = ClientData(self)

        self.bookmark: Bookmark = BookmarkApp(self)

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
                print("Error parsing credentials header: " + str(e), file=sys.stderr)

        self._outbound_message_queues = OutBoundMessageQueues()

        self._file_upload_manager: FileUploadManager = FileUploadManager()
        self._on_ended_callbacks = _utils.AsyncCallbacks()
        self._has_run_session_ended_tasks: bool = False
        self._downloads: dict[str, DownloadInfo] = {}
        self._dynamic_routes: dict[str, DynamicRouteHandler] = {}

        self._register_session_ended_callbacks()

        self._flush_callbacks = _utils.AsyncCallbacks()
        self._flushed_callbacks = _utils.AsyncCallbacks()

    def _register_session_ended_callbacks(self) -> None:
        # This is to be called from the initialization. It registers functions
        # that are called when a session ends.

        # Clear file upload directories, if present
        self.on_ended(self._file_upload_manager.rm_upload_dir)

    async def _run_session_ended_tasks(self) -> None:
        if self._has_run_session_ended_tasks:
            return
        self._has_run_session_ended_tasks = True

        try:
            await self._on_ended_callbacks.invoke()
        finally:
            self.app._remove_session(self)

    def is_stub_session(self) -> Literal[False]:
        return False

    async def close(self, code: int = 1001) -> None:
        await self._conn.close(code, None)
        await self._run_session_ended_tasks()

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
                        self._print_error_message(
                            "Message does not contain 'method'.",
                        )
                        return

                    async with lock():
                        if message_obj["method"] == "init":
                            verify_state(ConnectionState.Start)

                            # BOOKMARKS!
                            if not isinstance(self.bookmark, BookmarkApp):
                                raise RuntimeError("`.bookmark` must be a BookmarkApp")

                            if ".clientdata_url_search" in message_obj["data"]:
                                self.bookmark._set_restore_context(
                                    await RestoreContext.from_query_string(
                                        message_obj["data"][".clientdata_url_search"],
                                        app=self.app,
                                    )
                                )
                            else:
                                self.bookmark._set_restore_context(RestoreContext())

                            # When a reactive flush occurs, flush the session's outputs,
                            # errors, etc. to the client. Note that this is
                            # `reactive._core.on_flushed`, not `self.on_flushed`.
                            unreg = reactive_on_flushed(self._flush)
                            # When the session ends, stop flushing outputs on reactive
                            # flush.
                            stack.callback(unreg)

                            # Set up bookmark callbacks here
                            self.bookmark._create_effects()

                            conn_state = ConnectionState.Running
                            message_obj = typing.cast(ClientMessageInit, message_obj)
                            self._manage_inputs(message_obj["data"])

                            with session_context(self):
                                self.app.server(self.input, self.output, self)

                            # TODO: Remove this call to reactive_flush() once https://github.com/posit-dev/py-shiny/issues/1889 is fixed
                            # Workaround: Any `on_flushed()` calls from bookmark's `on_restored()` will be flushed here
                            if self.bookmark.store != "disable":
                                await reactive_flush()

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

                        # Progress messages (of the "{binding: {id: xxx}}"" variety) may
                        # have queued up at this point; let them drain before we send
                        # the next message.
                        # https://github.com/posit-dev/py-shiny/issues/1381
                        await asyncio.sleep(0)

                        self._request_flush()

                        await reactive_flush()

            except ConnectionClosed:
                ...
            except Exception as e:
                try:
                    # Starting in Python 3.10 this could be traceback.print_exception(e)
                    traceback.print_exception(*sys.exc_info())
                    self._print_error_message(e)
                except Exception:
                    pass
                finally:
                    await self.close()
            finally:
                await self._run_session_ended_tasks()

    def _manage_inputs(self, data: dict[str, object]) -> None:
        for key, val in data.items():
            keys = key.split(":")
            if len(keys) > 2:
                raise ValueError(
                    "Input name+type is not allowed to contain more than one ':' -- "
                    + key
                )
            if len(keys) == 2:
                val = input_handlers._process_value(
                    keys[1], val, ResolvedId(keys[0]), self
                )

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
            async_func, handler_session = self._message_handlers[message["method"]]
        except KeyError:
            await self._send_error_response(
                message,
                "Unknown method: " + message["method"],
            )
            return
        except AttributeError:
            await self._send_error_response(
                message,
                "Unknown method: " + message["method"],
            )
            return

        try:
            # TODO: handle `blobs`

            # * Use the session context from when the message handler was set
            # * Using `isolate()` allows the handler to read reactive values in a
            #   non-reactive context
            with session_context(handler_session), isolate():
                value = await async_func(*message["args"])
        except Exception as e:
            # Safe error handling!
            if self.app.sanitize_errors and not isinstance(e, SafeException):
                await self._send_error_response(message, self.app.sanitize_error_msg)
            else:
                await self._send_error_response(message, str(e))
            return

        await self._send_response(message, value)

    async def _send_response(self, message: ClientMessageOther, value: object) -> None:
        await self._send_message({"response": {"tag": message["tag"], "value": value}})

    # This is called during __init__.
    def _init_message_handlers(self):
        # TODO-future; Make sure these methods work within MockSession

        async def uploadInit(file_infos: list[FileInfo]) -> dict[str, Jsonifiable]:
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

            # This also occurs during input handler: shiny.file
            self.input.set_serializer(input_id, serializer_file_input)

            # Explicitly return None to signal that the message was handled.
            return None

        self.set_message_handler("uploadInit", uploadInit)
        self.set_message_handler("uploadEnd", uploadEnd)

    # ==========================================================================
    # Handling /session/{session_id}/{action}/{subpath} requests
    # ==========================================================================
    async def _handle_request(
        self, request: Request, action: str, subpath: Optional[str]
    ) -> ASGIApp:
        self._increment_busy_count()
        try:
            return await self._handle_request_impl(request, action, subpath)
        finally:
            self._decrement_busy_count()

    async def _handle_request_impl(
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
                                    "@render.download(filename=) to specify one "
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
        self._outbound_message_queues.add_input_message(id, message)
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

    async def send_custom_message(self, type: str, message: dict[str, object]) -> None:
        await self._send_message({"custom": {type: message}})

    async def _send_message(self, message: dict[str, object]) -> None:
        message_str = json.dumps(message)
        if self._debug:
            print(
                "SEND: "
                + re.sub(
                    "(?m)base64,[a-zA-Z0-9+/=]+", "[base64 data]", message_str + "\n"
                ),
                end="",
                flush=True,
            )
        await self._conn.send(message_str)

    def _send_message_sync(self, message: dict[str, object]) -> None:
        _utils.run_coro_hybrid(self._send_message(message))

    def _print_error_message(self, message: str | Exception) -> None:
        print(str(message), file=sys.stderr)

    async def _send_error_response(
        self,
        message: ClientMessageOther,
        error: object,
    ) -> None:
        # { tag: number; value?: ResponseValue; error?: string }
        if "tag" not in message:
            raise RuntimeError("No `tag` key in message")
        tag = message["tag"]
        await self._send_message({"response": {"tag": tag, "error": error}})

    # ==========================================================================
    # Flush
    # ==========================================================================
    def on_flush(
        self,
        fn: Callable[[], None] | Callable[[], Awaitable[None]],
        once: bool = True,
    ) -> Callable[[], None]:
        return self._flush_callbacks.register(wrap_async(fn), once)

    def on_flushed(
        self,
        fn: Callable[[], None] | Callable[[], Awaitable[None]],
        once: bool = True,
    ) -> Callable[[], None]:
        return self._flushed_callbacks.register(wrap_async(fn), once)

    def _request_flush(self) -> None:
        self.app._request_flush(self)

    async def _flush(self) -> None:
        with session_context(self):
            # This is the only place in the session where the RestoreContext is flushed.
            if self.bookmark._restore_context:
                self.bookmark._restore_context.flush_pending()
            # Flush the callbacks
            await self._flush_callbacks.invoke()

        try:
            omq = self._outbound_message_queues

            message: dict[str, object] = {
                "values": omq.values,
                "inputMessages": omq.input_messages,
                "errors": omq.errors,
            }

            try:
                await self._send_message(message)
            finally:
                self._outbound_message_queues.reset()
        finally:
            with session_context(self):
                await self._flushed_callbacks.invoke()

    def _increment_busy_count(self) -> None:
        self._busy_count += 1
        if self._busy_count == 1:
            self._send_message_sync({"busy": "busy"})

    def _decrement_busy_count(self) -> None:
        self._busy_count -= 1
        if self._busy_count == 0:
            self._send_message_sync({"busy": "idle"})

    # ==========================================================================
    # On session ended
    # ==========================================================================
    def on_ended(
        self,
        fn: Callable[[], None] | Callable[[], Awaitable[None]],
    ) -> Callable[[], None]:
        return self._on_ended_callbacks.register(wrap_async(fn))

    # ==========================================================================
    # Misc
    # ==========================================================================
    async def _unhandled_error(self, e: Exception) -> None:
        print("Unhandled error: " + str(e), file=sys.stderr)
        await self.close()

    def download(
        self,
        id: Optional[str] = None,
        filename: Optional[str | Callable[[], str]] = None,
        media_type: None | str | Callable[[], str] = None,
        encoding: str = "utf-8",
    ) -> Callable[[DownloadHandler], None]:
        warn_deprecated(
            "session.download() is deprecated. Please use render.download() instead."
        )

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

    def dynamic_route(self, name: str, handler: DynamicRouteHandler) -> str:

        self._dynamic_routes.update({name: handler})
        nonce = _utils.rand_hex(8)
        return f"session/{urllib.parse.quote(self.id)}/dynamic_route/{urllib.parse.quote(name)}?nonce={urllib.parse.quote(nonce)}"

    def set_message_handler(
        self,
        name: str,
        handler: (
            Callable[..., Jsonifiable] | Callable[..., Awaitable[Jsonifiable]] | None
        ),
        *,
        _handler_session: Optional[Session] = None,
    ) -> str:
        # Verify that the name is a string
        assert isinstance(name, str)

        if _handler_session is None:
            _handler_session = self

        if handler is None:
            if name in self._message_handlers:
                del self._message_handlers[name]
        else:
            assert callable(handler)
            self._message_handlers[name] = (wrap_async(handler), _handler_session)
        return name

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
        return SessionProxy(root_session=self, ns=ns)

    def root_scope(self) -> AppSession:
        return self


class BindingProgressMessage(TypedDict):
    id: ResolvedId
    persistent: NotRequired[bool]


class OpenProgressMessage(TypedDict):
    id: ResolvedId
    style: str


class CloseProgressMessage(TypedDict):
    id: ResolvedId
    style: str


class UpdateProgressMessage(TypedDict):
    id: ResolvedId
    message: NotRequired[str | None]
    detail: NotRequired[str | None]
    value: NotRequired[float | int | None]
    style: str


# ======================================================================================
# SessionProxy
# ======================================================================================


class SessionProxy(Session):
    def __init__(self, root_session: Session, ns: ResolvedId) -> None:
        super().__init__()

        self._root_session = root_session
        self.app = root_session.app
        self.id = root_session.id
        self.ns = ns
        self.input = Inputs(values=root_session.input._map, ns=ns)
        self.output = Outputs(
            self,
            ns=ns,
            outputs=root_session.output._outputs,
        )
        self.clientdata = ClientData(self)
        self._outbound_message_queues = root_session._outbound_message_queues
        self._downloads = root_session._downloads

        self.bookmark = BookmarkProxy(self)

    def _is_hidden(self, name: str) -> bool:
        return self._root_session._is_hidden(name)

    def on_ended(
        self,
        fn: Callable[[], None] | Callable[[], Awaitable[None]],
    ) -> Callable[[], None]:
        return self._root_session.on_ended(fn)

    def is_stub_session(self) -> bool:
        return self._root_session.is_stub_session()

    async def close(self, code: int = 1001) -> None:
        await self._root_session.close(code)

    def make_scope(self, id: str) -> Session:
        return self._root_session.make_scope(self.ns(id))

    def root_scope(self) -> Session:
        return self._root_session

    def _process_ui(self, ui: TagChild) -> RenderedDeps:
        return self._root_session._process_ui(ui)

    def send_input_message(self, id: str, message: dict[str, object]) -> None:
        self._root_session.send_input_message(self.ns(id), message)

    def _send_insert_ui(
        self, selector: str, multiple: bool, where: str, content: RenderedDeps
    ) -> None:
        self._root_session._send_insert_ui(selector, multiple, where, content)

    def _send_remove_ui(self, selector: str, multiple: bool) -> None:
        self._root_session._send_remove_ui(selector, multiple)

    def _send_progress(self, type: str, message: object) -> None:
        self._root_session._send_progress(type, message)  # pyright: ignore

    async def send_custom_message(self, type: str, message: dict[str, object]) -> None:
        await self._root_session.send_custom_message(type, message)

    def _increment_busy_count(self) -> None:
        self._root_session._increment_busy_count()

    def _decrement_busy_count(self) -> None:
        self._root_session._decrement_busy_count()

    def set_message_handler(
        self,
        name: str,
        handler: (
            Callable[..., Jsonifiable] | Callable[..., Awaitable[Jsonifiable]] | None
        ),
        *,
        _handler_session: Optional[Session] = None,
    ) -> str:
        # Verify that the name is a string
        assert isinstance(name, str)

        if _handler_session is None:
            _handler_session = self

        return self._root_session.set_message_handler(
            self.ns(name),
            handler,
            _handler_session=_handler_session,
        )

    def on_flush(
        self,
        fn: Callable[[], None] | Callable[[], Awaitable[None]],
        once: bool = True,
    ) -> Callable[[], None]:
        return self._root_session.on_flush(fn, once)

    async def _send_message(self, message: dict[str, object]) -> None:
        await self._root_session._send_message(message)

    def _send_message_sync(self, message: dict[str, object]) -> None:
        self._root_session._send_message_sync(message)

    def on_flushed(
        self,
        fn: Callable[[], None] | Callable[[], Awaitable[None]],
        once: bool = True,
    ) -> Callable[[], None]:
        return self._root_session.on_flushed(fn, once)

    def dynamic_route(self, name: str, handler: DynamicRouteHandler) -> str:
        return self._root_session.dynamic_route(self.ns(name), handler)

    async def _unhandled_error(self, e: Exception) -> None:
        await self._root_session._unhandled_error(e)

    def download(
        self,
        id: Optional[str] = None,
        filename: Optional[str | Callable[[], str]] = None,
        media_type: None | str | Callable[[], str] = None,
        encoding: str = "utf-8",
    ) -> Callable[[DownloadHandler], None]:
        def wrapper(fn: DownloadHandler):
            id_ = self.ns(id or fn.__name__)
            return self._root_session.download(
                id=id_,
                filename=filename,
                media_type=media_type,
                encoding=encoding,
            )(fn)

        return wrapper


# ======================================================================================
# Inputs
# ======================================================================================


# TODO: provide a real input typing example when we have an answer for that
# https://github.com/posit-dev/py-shiny/issues/70
class Inputs:
    """
    A class representing Shiny input values.

    This class provides access to a :class:`~shiny.Session`'s input values. The
    input values are reactive :class:`~shiny.reactive.Value`s, and can be accessed with
    the ``[]`` operator, or with ``.``. For example, if there is an input named ``x``,
    it can be accessed via `input["x"]()` or ``input.x()``.
    """

    _serializers: dict[
        str,
        Callable[
            [Any, Path | None],
            Awaitable[Any | Unserializable],
        ],
    ]
    """
    A dictionary of serializers for input values.

    Set this value via `Inputs.set_serializer(id, fn)`.
    """

    def __init__(
        self, values: dict[str, Value[Any]], ns: Callable[[str], str] = Root
    ) -> None:
        self._map = values
        self._ns = ns
        self._serializers = {}

    def __setitem__(self, key: str, value: Value[Any]) -> None:
        if not isinstance(value, reactive.Value):
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
        if attr in ("_map", "_ns", "_serializers"):
            super().__setattr__(attr, value)
            return

        self.__setitem__(attr, value)

    def __getattr__(self, attr: str) -> Value[Any]:
        if attr in ("_map", "_ns", "_serializers"):
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

    def __dir__(self):
        return list(self._map.keys())

    # This method can not be on the `Value` class as the _value_ may not exist when the
    # "creating" method is executed.
    # Ex: File inputs do not _make_ the input reactive value. The browser does when the
    # client sets the value.
    def set_serializer(
        self,
        id: str,
        fn: (
            Callable[
                [Any, Path | None],
                Awaitable[Any | Unserializable],
            ]
            | Callable[
                [Any, Path | None],
                Any | Unserializable,
            ]
        ),
    ) -> None:
        """
        Add a function for serializing an input before bookmarking application state

        Parameters
        ----------
        id
            The ID of the input value.
        fn
            A function that takes the input value and returns a modified value. The
            returned value will be used for test snapshots and bookmarking.
        """
        self._serializers[id] = wrap_async(fn)

    async def _serialize(
        self,
        /,
        *,
        exclude: list[str],
        state_dir: Path | None,
    ) -> dict[str, Any]:
        from ..bookmark._serializers import Unserializable, serializer_default

        exclude_set = set(exclude)
        serialized_values: dict[str, Any] = {}

        with reactive.isolate():

            for key, value in self._map.items():
                # TODO: Barret - Q: Should this be ignoring any Input key that starts with a "."?
                if key.startswith(".clientdata_"):
                    continue
                # Ignore all bookmark inputs
                if key == BOOKMARK_ID or key.endswith(
                    f"{ResolvedId._sep}{BOOKMARK_ID}"
                ):
                    continue
                if key in exclude_set:
                    continue
                val = value()

                # Possibly apply custom serialization given the input id
                serializer = self._serializers.get(key, serializer_default)
                serialized_value = await serializer(val, state_dir)

                # Filter out any values that were marked as unserializable.
                if isinstance(serialized_value, Unserializable):
                    continue
                serialized_values[str(key)] = serialized_value

        return serialized_values


@add_example()
class ClientData:
    """
    Access (client-side) information from the browser.

    Provides access to client-side information, such as the URL components, the
    pixel ratio of the device, and the properties of outputs.

    Each method in this class reads a reactive input value, which means that the
    method will error if called outside of a reactive context.

    Raises
    ------
    RuntimeError
        If a method is called outside of a reactive context.
    """

    def __init__(self, session: Session) -> None:
        self._session: Session = session
        self._current_output_name: ResolvedId | None = None

    def url_hash(self) -> str:
        """
        Reactively read the hash part of the URL.
        """
        return self._read_input("url_hash")

    def url_hash_initial(self) -> str:
        """
        Reactively read the initial hash part of the URL.
        """
        return self._read_input("url_hash_initial")

    def url_hostname(self) -> str:
        """
        Reactively read the hostname part of the URL.
        """
        return self._read_input("url_hostname")

    def url_pathname(self) -> str:
        """
        The pathname part of the URL.
        """
        return self._read_input("url_pathname")

    def url_port(self) -> int:
        """
        Reactively read the port part of the URL.
        """
        return cast(int, self._read_input("url_port"))

    def url_protocol(self) -> str:
        """
        Reactively read the protocol part of the URL.
        """
        return self._read_input("url_protocol")

    def url_search(self) -> str:
        """
        Reactively read the search part of the URL.
        """
        return self._read_input("url_search")

    def pixelratio(self) -> float:
        """
        Reactively read the pixel ratio of the device.
        """
        return cast(int, self._read_input("pixelratio"))

    def output_height(self, id: Optional[Id] = None) -> float | None:
        """
        Reactively read the height of an output.

        Parameters
        ----------
        id
            The id of the output.

        Returns
        -------
        float | None
            The height of the output, or None if the output does not exist (or does not
            report its height).
        """
        return cast(float, self._read_output(id, "height"))

    def output_width(self, id: Optional[Id] = None) -> float | None:
        """
        Reactively read the width of an output.

        Parameters
        ----------
        id
            The id of the output.

        Returns
        -------
        float | None
            The width of the output, or None if the output does not exist (or does not
            report its width).
        """
        return cast(float, self._read_output(id, "width"))

    def output_hidden(self, id: Optional[Id] = None) -> bool | None:
        """
        Reactively read whether an output is hidden.

        Parameters
        ----------
        id
            The id of the output.

        Returns
        -------
        bool | None
            Whether the output is hidden, or None if the output does not exist.
        """
        return cast(bool, self._read_output(id, "hidden"))

    def output_bg_color(self, id: Optional[Id] = None) -> str | None:
        """
        Reactively read the background color of an output.

        Parameters
        ----------
        id
            The id of the output.

        Returns
        -------
        str | None
            The background color of the output, or None if the output does not exist (or
            does not report its bg color).
        """
        return cast(str, self._read_output(id, "bg"))

    def output_fg_color(self, id: Optional[Id] = None) -> str | None:
        """
        Reactively read the foreground color of an output.

        Parameters
        ----------
        id
            The id of the output.

        Returns
        -------
        str | None
            The foreground color of the output, or None if the output does not exist (or
            does not report its fg color).
        """
        return cast(str, self._read_output(id, "fg"))

    def output_accent_color(self, id: Optional[Id] = None) -> str | None:
        """
        Reactively read the accent color of an output.

        Parameters
        ----------
        id
            The id of the output.

        Returns
        -------
        str | None
            The accent color of the output, or None if the output does not exist (or
            does not report its accent color).
        """
        return cast(str, self._read_output(id, "accent"))

    def output_font(self, id: Optional[Id] = None) -> str | None:
        """
        Reactively read the font(s) of an output.

        Parameters
        ----------
        id
            The id of the output.

        Returns
        -------
        str | None
            The font family of the output, or None if the output does not exist (or
            does not report its font styles).
        """
        return cast(str, self._read_output(id, "font"))

    def _read_input(self, key: str) -> str:
        self._check_current_context(key)

        id = ResolvedId(f".clientdata_{key}")
        if id not in self._session.root_scope().input:
            raise ValueError(
                f"ClientData value '{key}' not found. Please report this issue."
            )

        return self._session.root_scope().input[id]()

    def _read_output(self, id: Id | None, key: str) -> str | None:
        self._check_current_context(f"output_{key}")

        # No `id` provided support
        if id is None and self._current_output_name is not None:
            id = self._current_output_name

        if id is None:
            raise ValueError(
                "session.clientdata.output_*() requires an id when not called within "
                "an output renderer."
            )

        # Module support
        if not isinstance(id, ResolvedId):
            id = self._session.ns(id)

        input_id = ResolvedId(f".clientdata_output_{id}_{key}")
        if input_id in self._session.root_scope().input:
            return self._session.root_scope().input[input_id]()
        else:
            return None

    @contextlib.contextmanager
    def _output_name_ctx(self, output_name: ResolvedId) -> Generator[None, None, None]:
        """
        Context manager to temporarily set the output name.

        This is used to allow `session.clientdata.output_*()` methods to access the
        current output name without needing to pass it explicitly.
        """
        old_output_name = self._current_output_name
        try:
            self._current_output_name = output_name
            yield
        finally:
            self._current_output_name = old_output_name

    @staticmethod
    def _check_current_context(key: str) -> None:
        try:
            reactive.get_current_context()
        except RuntimeError:
            raise RuntimeError(
                f"session.clientdata.{key}() must be called from within a reactive context."
            )


# ======================================================================================
# Outputs
# ======================================================================================


@dataclasses.dataclass
class OutputInfo:
    renderer: Renderer[Any]
    effect: Effect_
    suspend_when_hidden: bool


class Outputs:
    """
    A class representing Shiny output definitions.
    """

    def __init__(
        self,
        session: Session,
        ns: Callable[[str], ResolvedId],
        *,
        outputs: dict[str, OutputInfo],
    ) -> None:
        self._session = session
        self._ns = ns
        self._outputs = outputs

    @overload
    def __call__(self, renderer: RendererT) -> RendererT:
        pass

    @overload
    def __call__(
        self,
        *,
        id: Optional[str] = None,
        suspend_when_hidden: bool = True,
        priority: int = 0,
    ) -> Callable[[RendererT], RendererT]:
        pass

    def __call__(
        self,
        renderer: Optional[RendererT] = None,
        *,
        id: Optional[str] = None,
        suspend_when_hidden: bool = True,
        priority: int = 0,
    ) -> RendererT | Callable[[RendererT], RendererT]:

        def require_real_session() -> Session:
            if self._session.is_stub_session():
                raise RuntimeError(
                    "`output` must be used with a real session (as opposed to a stub session)."
                )

            return self._session

        def set_renderer(renderer: RendererT) -> RendererT:
            if not isinstance(renderer, Renderer):
                raise TypeError(
                    "`@output` must be applied to a `@render.xx` function.\n"
                    + "In other words, `@output` must be above `@render.xx`."
                )

            # Get the (possibly namespaced) output id
            output_id = id or renderer.__name__
            output_name = self._ns(output_id)

            # renderer is a Renderer object. Give it a bit of metadata.
            renderer._set_output_metadata(output_id=output_id)

            renderer._on_register()

            self.remove(output_name)

            @effect(
                suspended=suspend_when_hidden and self._session._is_hidden(output_name),
                priority=priority,
            )
            async def output_obs():
                if self._session.is_stub_session():
                    raise RuntimeError(
                        "`output` must be used with a real session (as opposed to a stub session)."
                    )

                session = require_real_session()

                await session._send_message(
                    {"recalculating": {"name": output_name, "status": "recalculating"}}
                )

                try:
                    with session.clientdata._output_name_ctx(output_name):
                        # Call the app's renderer function
                        value = await renderer.render()

                    session._outbound_message_queues.set_value(output_name, value)

                except SilentOperationInProgressException:
                    session._send_progress(
                        "binding", {"id": output_name, "persistent": True}
                    )
                    # It's important to exit early here _without_ a recalculated message
                    return
                except SilentCancelOutputException:
                    pass
                except SilentException:
                    session._outbound_message_queues.set_value(output_name, None)
                except Exception as e:
                    # Print traceback to the console
                    traceback.print_exc()
                    # Possibly sanitize error for the user
                    if session.app.sanitize_errors and not isinstance(e, SafeException):
                        err_msg = session.app.sanitize_error_msg
                    else:
                        err_msg = str(e)
                    # Register the outbound error message
                    err_message = {
                        "message": err_msg,
                        # TODO: is it possible to get the call?
                        "call": None,
                        # TODO: I don't think we actually use this for anything client-side
                        "type": None,
                    }
                    session._outbound_message_queues.set_error(output_name, err_message)

                await session._send_message(
                    {
                        "recalculating": {
                            "name": output_name,
                            "status": "recalculated",
                        }
                    }
                )

            output_obs.on_invalidate(
                lambda: require_real_session()._send_progress(
                    "binding", {"id": output_name}
                )
            )

            # Store the renderer and effect info
            self._outputs[output_name] = OutputInfo(
                renderer=renderer,
                effect=output_obs,
                suspend_when_hidden=suspend_when_hidden,
            )

            return renderer

        if renderer is None:
            return set_renderer
        else:
            return set_renderer(renderer)

    def remove(self, id: Id) -> None:
        output_name = self._ns(id)
        if output_name in self._outputs:
            self._outputs[output_name].effect.destroy()
            del self._outputs[output_name]

    def _manage_hidden(self) -> None:
        "Suspends execution of hidden outputs and resumes execution of visible outputs."
        for name, output in self._outputs.items():
            if self._should_suspend(name):
                output.effect.suspend()
            else:
                output.effect.resume()

    def _should_suspend(self, name: str) -> bool:
        return self._outputs[name].suspend_when_hidden and self._session._is_hidden(
            name
        )
