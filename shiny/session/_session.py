__all__ = ("Session", "Inputs", "Outputs")

import functools
import os
from pathlib import Path
import sys
import json
import re
import traceback
import warnings
import typing
import dataclasses
import urllib.parse
from typing import (
    TYPE_CHECKING,
    AsyncIterable,
    Callable,
    Iterable,
    Optional,
    Union,
    Awaitable,
    Dict,
    List,
    Any,
    cast,
)
from starlette.requests import Request, HTTPConnection

from starlette.responses import (
    HTMLResponse,
    PlainTextResponse,
    StreamingResponse,
)
from starlette.types import ASGIApp

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from htmltools import TagChildArg, TagList

if TYPE_CHECKING:
    from .._app import App

from .._connection import Connection, ConnectionClosed
from .._docstring import add_example
from .._fileupload import FileInfo, FileUploadManager
from ..http_staticfiles import FileResponse
from ..input_handler import input_handlers
from ..reactive import Value, Effect, Effect_, isolate, flush
from ..reactive._core import lock
from ..types import SafeException, SilentCancelOutputException, SilentException
from ._utils import RenderedDeps, read_thunk_opt, session_context

from .. import render
from .. import _utils

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


# This is the type for the function provided by the user to provide the contents of a
# download. It must be a function that takes no arguments, and returns one of:
# 1. A string, which will be interpreted as a path
# 2. A regular Iterable of bytes or strings (i.e. a generator function)
# 3. An AsyncIterable of bytes or strings (i.e. an async generator function)
#
# (Not currently supported is Awaitable[str], could be added easily enough if needed.)
DownloadHandler = Callable[
    [], Union[str, Iterable[Union[bytes, str]], AsyncIterable[Union[bytes, str]]]
]

DynamicRouteHandler = Callable[[Request], ASGIApp]


@dataclasses.dataclass
class DownloadInfo:
    filename: Union[Callable[[], str], str, None]
    content_type: Optional[Union[Callable[[], str], str]]
    handler: DownloadHandler
    encoding: str


class OutBoundMessageQueues(TypedDict):
    values: List[Dict[str, object]]
    input_messages: List[Dict[str, object]]
    errors: List[Dict[str, object]]


def empty_outbound_message_queues() -> OutBoundMessageQueues:
    return {"values": [], "input_messages": [], "errors": []}


class Session:
    """
    A class representing a user session.

    Warning
    -------
    An instance of this class is created for each request and passed as an argument to
    the :class:`shiny.App`'s ``server`` function. For this reason, you shouldn't
    need to create instances of this class yourself (it's only part of the public API
    for type checking reasons).
    """

    # ==========================================================================
    # Initialization
    # ==========================================================================
    def __init__(
        self, app: "App", id: str, conn: Connection, debug: bool = False
    ) -> None:
        self.app: App = app
        self.id: str = id
        self._conn: Connection = conn
        self._debug: bool = debug

        # The HTTPConnection representing the WebSocket. This is used so that we can
        # query information about the request, like headers, cookies, etc.
        self.http_conn: HTTPConnection = conn.get_http_conn()

        self.input: Inputs = Inputs()
        self.output: Outputs = Outputs(self)

        self.user: Union[str, None] = None
        self.groups: Union[List[str], None] = None
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

        self._message_handlers: Dict[
            str, Callable[..., Awaitable[object]]
        ] = self._create_message_handlers()
        self._file_upload_manager: FileUploadManager = FileUploadManager()
        self._on_ended_callbacks = _utils.Callbacks()
        self._has_run_session_end_tasks: bool = False
        self._downloads: Dict[str, DownloadInfo] = {}
        self._dynamic_routes: Dict[str, DynamicRouteHandler] = {}

        self._register_session_end_callbacks()

        self._flush_callbacks = _utils.Callbacks()
        self._flushed_callbacks = _utils.Callbacks()

        with session_context(self):
            self.app.server(self.input, self.output, self)

    def _register_session_end_callbacks(self) -> None:
        # This is to be called from the initialization. It registers functions
        # that are called when a session ends.

        # Clear file upload directories, if present
        self.on_ended(self._file_upload_manager.rm_upload_dir)

    def _run_session_end_tasks(self) -> None:
        if self._has_run_session_end_tasks:
            return
        self._has_run_session_end_tasks = True

        self._on_ended_callbacks.invoke()

        self.app._remove_session(self)

    async def close(self, code: int = 1001) -> None:
        """
        Close the session.
        """
        await self._conn.close(code, None)
        self._run_session_end_tasks()

    async def _run(self) -> None:
        await self._send_message(
            {"config": {"workerId": "", "sessionId": str(self.id), "user": None}}
        )

        try:
            while True:
                message: str = await self._conn.receive()
                if self._debug:
                    print("RECV: " + message, flush=True)

                try:
                    message_obj = json.loads(
                        message, object_hook=_utils.lists_to_tuples
                    )
                except json.JSONDecodeError:
                    print("ERROR: Invalid JSON message")
                    continue

                if "method" not in message_obj:
                    self._send_error_response("Message does not contain 'method'.")
                    return

                async with lock():

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

                    self._request_flush()

                    await flush()

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
                val = input_handlers._process_value(keys[1], val, keys[0], self)

            self.input[keys[0]]._set(val)

            self.output._manage_hidden()

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
    def _create_message_handlers(self) -> Dict[str, Callable[..., Awaitable[object]]]:
        async def uploadInit(file_infos: List[FileInfo]) -> Dict[str, object]:
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
                    "Received uploadEnd message for non-existent upload operation."
                )
                return None
            file_data = upload_op.finish()
            self.input[input_id]._set(file_data)
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
                                    "manually"
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

    def send_input_message(self, id: str, message: Dict[str, object]) -> None:
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
        msg: Dict[str, object] = {"id": id, "message": message}
        self._outbound_message_queues["input_messages"].append(msg)
        self._request_flush()

    def _send_insert_ui(
        self, selector: str, multiple: bool, where: str, content: "RenderedDeps"
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
        msg: Dict[str, object] = {"progress": {"type": type, "message": message}}
        self._send_message_sync(msg)

    @add_example()
    async def send_custom_message(self, type: str, message: Dict[str, object]) -> None:
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

    async def _send_message(self, message: Dict[str, object]) -> None:
        message_str: str = json.dumps(message) + "\n"
        if self._debug:
            print(
                "SEND: "
                + re.sub("(?m)base64,[a-zA-Z0-9+/=]+", "[base64 data]", message_str),
                end="",
                flush=True,
            )
        await self._conn.send(json.dumps(message))

    def _send_message_sync(self, message: Dict[str, object]) -> None:
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

            values: Dict[str, object] = {}
            for v in omq["values"]:
                values.update(v)

            errors: Dict[str, object] = {}
            for err in omq["errors"]:
                errors.update(err)

            message: Dict[str, object] = {
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
        A function that can be used to cancel the registration.
        """
        return self._on_ended_callbacks.register(fn)

    # ==========================================================================
    # Misc
    # ==========================================================================
    async def _unhandled_error(self, e: Exception) -> None:
        print("Unhandled error: " + str(e))
        await self.close()

    # TODO: probably name should be id
    @add_example()
    def download(
        self,
        name: Optional[str] = None,
        filename: Optional[Union[str, Callable[[], str]]] = None,
        media_type: Union[None, str, Callable[[], str]] = None,
        encoding: str = "utf-8",
    ) -> Callable[[DownloadHandler], None]:
        """
        Decorator to register a function to handle a download.

        Parameters
        ----------
        name
            The name of the download.
        filename
            The filename of the download.
        media_type
            The media type of the download.
        encoding
            The encoding of the download.

        Returns
        -------
        The decorated function.
        """

        def wrapper(fn: DownloadHandler):
            if name is None:
                effective_name = fn.__name__
            else:
                effective_name = name

            self._downloads[effective_name] = DownloadInfo(
                filename=filename,
                content_type=media_type,
                handler=fn,
                encoding=encoding,
            )

            @self.output(name=effective_name)
            @render.text()
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
            The URL path for the route.
        """

        self._dynamic_routes.update({name: handler})
        nonce = _utils.rand_hex(8)
        return f"session/{urllib.parse.quote(self.id)}/dynamic_route/{urllib.parse.quote(name)}?nonce={urllib.parse.quote(nonce)}"

    def _process_ui(self, ui: TagChildArg) -> RenderedDeps:

        res = TagList(ui).render()
        deps: List[Dict[str, Any]] = []
        for dep in res["dependencies"]:
            self.app._register_web_dependency(dep)
            dep_dict = dep.as_dict(lib_prefix=self.app.LIB_PREFIX)
            deps.append(dep_dict)

        return {"deps": deps, "html": res["html"]}


# ======================================================================================
# Inputs
# ======================================================================================

# TODO: provide a real input typing example when we have an answer for that
# https://github.com/rstudio/py-shiny/issues/70
class Inputs:
    """
    A class representing Shiny input values.

    Warning
    -------
    An instance of this class is created for each request and passed as an argument to
    the :class:`shiny.App`'s ``server`` function. For this reason, you shouldn't
    need to create instances of this class yourself (it's only part of the public API
    for type checking reasons).
    """

    def __init__(self, **kwargs: object) -> None:
        self._map: dict[str, Value[Any]] = {}
        for key, value in kwargs.items():
            self._map[key] = Value(value, read_only=True)

    def __setitem__(self, key: str, value: Value[Any]) -> None:
        if not isinstance(value, Value):
            raise TypeError("`value` must be a reactive.Value object.")

        self._map[key] = value

    def __getitem__(self, key: str) -> Value[Any]:
        # Auto-populate key if accessed but not yet set. Needed to take reactive
        # dependencies on input values that haven't been received from client
        # yet.
        if key not in self._map:
            self._map[key] = Value(read_only=True)

        return self._map[key]

    def __delitem__(self, key: str) -> None:
        del self._map[key]

    # Allow access of values as attributes.
    def __setattr__(self, attr: str, value: Value[Any]) -> None:
        # Need special handling of "_map".
        if attr == "_map":
            super().__setattr__(attr, value)
            return

        self.__setitem__(attr, value)

    def __getattr__(self, attr: str) -> Value[Any]:
        if attr == "_map":
            return object.__getattribute__(self, attr)
        return self.__getitem__(attr)

    def __delattr__(self, key: str) -> None:
        self.__delitem__(key)


# ======================================================================================
# Outputs
# ======================================================================================
class Outputs:
    """
    A class representing Shiny output definitions.

    Warning
    -------
    An instance of this class is created for each request and passed as an argument to
    the :class:`shiny.App`'s ``server`` function. For this reason, you shouldn't
    need to create instances of this class yourself (it's only part of the public API
    for type checking reasons).
    """

    def __init__(self, session: Session) -> None:
        self._effects: Dict[str, Effect_] = {}
        self._suspend_when_hidden: Dict[str, bool] = {}
        self._session: Session = session

    def __call__(
        self,
        *,
        id: Optional[str] = None,
        suspend_when_hidden: bool = True,
        priority: int = 0,
        name: Optional[str] = None,
    ) -> Callable[[render.RenderFunction], None]:
        if name is not None:
            from .. import _deprecated

            _deprecated._warn_deprecated(
                "`@output(name=...)` is deprecated. Use `@output(id=...)` instead."
            )
            id = name

        def set_fn(fn: render.RenderFunction) -> None:
            output_name = id or fn.__name__
            # fn is either a regular function or a RenderFunction object. If
            # it's the latter, give it a bit of metadata.
            if isinstance(fn, render.RenderFunction):
                fn.set_metadata(self._session, output_name)

            if output_name in self._effects:
                self._effects[output_name].destroy()

            self._suspend_when_hidden[output_name] = suspend_when_hidden

            @Effect(
                suspended=suspend_when_hidden and self._is_hidden(output_name),
                priority=priority,
            )
            async def output_obs():
                await self._session._send_message(
                    {"recalculating": {"name": output_name, "status": "recalculating"}}
                )

                message: Dict[str, object] = {}
                try:
                    if _utils.is_async_callable(fn):
                        message[output_name] = await fn()
                    else:
                        message[output_name] = fn()
                except SilentCancelOutputException:
                    return
                except SilentException:
                    pass
                except Exception as e:
                    # Print traceback to the console
                    traceback.print_exc()
                    # Possibly sanitize error for the user
                    if self._session.app.SANITIZE_ERRORS and not isinstance(
                        e, SafeException
                    ):
                        err_msg = self._session.app.SANITIZE_ERROR_MSG
                    else:
                        err_msg = str(e)
                    # Register the outbound error message
                    msg: Dict[str, object] = {
                        output_name: {
                            "message": err_msg,
                            # TODO: is it possible to get the call?
                            "call": None,
                            # TODO: I don't think we actually use this for anything client-side
                            "type": None,
                        }
                    }
                    self._session._outbound_message_queues["errors"].append(msg)

                self._session._outbound_message_queues["values"].append(message)

                await self._session._send_message(
                    {"recalculating": {"name": output_name, "status": "recalculated"}}
                )

            output_obs.on_invalidate(
                lambda: self._session._send_progress("binding", {"id": output_name})
            )

            self._effects[output_name] = output_obs

            return None

        return set_fn

    def _manage_hidden(self) -> None:
        "Suspends execution of hidden outputs and resumes execution of visible outputs."
        output_names = list(self._suspend_when_hidden.keys())
        for name in output_names:
            if self._should_suspend(name):
                self._effects[name].suspend()
            else:
                self._effects[name].resume()

    def _should_suspend(self, name: str) -> bool:
        return self._suspend_when_hidden[name] and self._is_hidden(name)

    def _is_hidden(self, name: str) -> bool:
        with isolate():
            hidden_value_obj = cast(
                Value[bool], self._session.input[f".clientdata_output_{name}_hidden"]
            )
            if not hidden_value_obj.is_set():
                return True

            return hidden_value_obj()
