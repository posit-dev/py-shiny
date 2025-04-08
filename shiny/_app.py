from __future__ import annotations

import copy
import os
import secrets
from contextlib import AsyncExitStack, asynccontextmanager
from inspect import signature
from pathlib import Path
from typing import Any, Callable, Literal, Mapping, Optional, TypeVar, cast

import starlette.applications
import starlette.middleware
import starlette.routing
import starlette.websockets
from htmltools import (
    HTMLDependency,
    HTMLDocument,
    HTMLTextDocument,
    RenderedHTML,
    Tag,
    TagList,
)
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, Response
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from ._autoreload import InjectAutoreloadMiddleware, autoreload_url
from ._connection import Connection, StarletteConnection
from ._error import ErrorMiddleware
from ._shinyenv import is_pyodide
from ._utils import guess_mime_type, is_async_callable, sort_keys_length
from .bookmark._global import as_bookmark_dir_fn
from .bookmark._restore_state import RestoreContext, restore_context
from .bookmark._types import (
    BookmarkDirFn,
    BookmarkRestoreDirFn,
    BookmarkSaveDirFn,
    BookmarkStore,
)
from .html_dependencies import jquery_deps, require_deps, shiny_deps
from .http_staticfiles import FileResponse, StaticFiles
from .session._session import AppSession, Inputs, Outputs, Session, session_context
from .types import MISSING, MISSING_TYPE

T = TypeVar("T")

# Default values for App options.
LIB_PREFIX: str = "lib/"
SANITIZE_ERRORS: bool = False
SANITIZE_ERROR_MSG: str = (
    "An error has occurred. Check your logs or contact the app author for clarification."
)


class App:
    """
    Create a Shiny app instance.

    Parameters
    ----------
    ui
        The UI definition for the app (e.g., a call to :func:`~shiny.ui.page_fluid` or
        similar, with layouts and controls nested inside). You can
        also pass a function that takes a :class:`~starlette.requests.Request` and
        returns a UI definition, if you need the UI definition to be created dynamically
        for each pageview.
    server
        A function which is called once for each session, ensuring that each session is
        independent.
    static_assets
        Static files to be served by the app. If this is a string or Path object, it
        must be a directory, and it will be mounted at `/`. If this is a dictionary,
        each key is a mount point and each value is a file or directory to be served at
        that mount point.
    debug
        Whether to enable debug mode.

    Examples
    --------

    ```{python}
    #| eval: false
    from shiny import  App, Inputs, Outputs, Session, ui

    app_ui = ui.page_fluid("Hello Shiny!")

    def server(input: Inputs, output: Outputs, session: Session):
        pass

    app = App(app_ui, server)
    ```
    """

    lib_prefix: str = "lib/"
    """
    A path prefix to place before all HTML dependencies processed by
    ``register_web_dependency()``.
    """

    sanitize_errors: bool = False
    """
    Whether or not to show a generic message (``SANITIZE_ERRORS=True``) or the actual
    message (``SANITIZE_ERRORS=False``) in the app UI when an error occurs. This flag
    may default to ``True`` in some production environments (e.g., Posit Connect).
    """

    sanitize_error_msg: str = (
        "An error has occurred. Check your logs or contact the app author for clarification."
    )
    """
    The message to show when an error occurs and ``SANITIZE_ERRORS=True``.
    """

    ui: RenderedHTML | Callable[[Request], Tag | TagList]
    server: Callable[[Inputs, Outputs, Session], None]

    _bookmark_save_dir_fn: BookmarkSaveDirFn | None | MISSING_TYPE
    _bookmark_restore_dir_fn: BookmarkRestoreDirFn | None | MISSING_TYPE
    _bookmark_store: BookmarkStore

    def __init__(
        self,
        ui: Tag | TagList | Callable[[Request], Tag | TagList] | Path,
        server: (
            Callable[[Inputs], None] | Callable[[Inputs, Outputs, Session], None] | None
        ),
        *,
        static_assets: Optional[str | Path | Mapping[str, str | Path]] = None,
        # Document type as Literal to have clearer type hints to App author
        bookmark_store: Literal["url", "server", "disable"] = "disable",
        debug: bool = False,
    ) -> None:
        # Used to store callbacks to be called when the app is shutting down (according
        # to the ASGI lifespan protocol)
        self._exit_stack = AsyncExitStack()

        if server is None:
            self.server = noop_server_fn
        elif len(signature(server).parameters) == 1:
            self.server = wrap_server_fn_with_output_session(
                cast(Callable[[Inputs], None], server)
            )
        elif len(signature(server).parameters) == 3:
            self.server = cast(Callable[[Inputs, Outputs, Session], None], server)
        else:
            raise ValueError(
                "`server` must have 1 (Inputs) or 3 parameters (Inputs, Outputs, Session)"
            )

        self._init_bookmarking(bookmark_store=bookmark_store, ui=ui)

        self._debug: bool = debug

        # Settings that the user can change after creating the App object.
        self.lib_prefix: str = LIB_PREFIX
        self.sanitize_errors: bool = SANITIZE_ERRORS
        self.sanitize_error_msg: str = SANITIZE_ERROR_MSG

        if static_assets is None:
            static_assets = {}

        if isinstance(static_assets, Mapping):
            static_assets_map = {k: Path(v) for k, v in static_assets.items()}
        else:
            static_assets_map = {"/": Path(static_assets)}

        for _, static_asset_path in static_assets_map.items():
            if not static_asset_path.is_absolute():
                raise ValueError(
                    f'static_assets must be an absolute path: "{static_asset_path}".'
                    " Consider using one of the following instead:\n"
                    f'  os.path.join(os.path.dirname(__file__), "{static_asset_path}")  OR'
                    f'  pathlib.Path(__file__).parent/"{static_asset_path}"'
                )

        # Sort the static assets keys by descending length, to ensure that the most
        # specific paths are mounted first. Suppose there are mounts "/foo" and "/". If
        # "/" is first in the dict, then requests to "/foo/file.html" will never reach
        # the second mount. We need to put "/foo" first and "/" second so that it will
        # actually look in the "/foo" mount.
        static_assets_map = sort_keys_length(static_assets_map, descending=True)
        self._static_assets: dict[str, Path] = static_assets_map

        self._sessions: dict[str, AppSession] = {}

        # self._sessions_needing_flush: dict[int, AppSession] = {}

        self._registered_dependencies: dict[str, HTMLDependency] = {}
        self._dependency_handler = starlette.routing.Router()

        for mount_point, static_asset_path in self._static_assets.items():
            self._dependency_handler.routes.append(
                create_static_asset_route(mount_point, static_asset_path)
            )

        starlette_app = self.init_starlette_app()

        self.starlette_app = starlette_app

        if is_uifunc(ui):
            if is_async_callable(cast(Callable[[Request], Any], ui)):
                raise TypeError("App UI cannot be a coroutine function")
            # Dynamic UI: just store the function for later
            self.ui = cast("Callable[[Request], Tag | TagList]", ui)
        elif isinstance(ui, Path):
            if not ui.is_absolute():
                raise ValueError("Path to UI must be absolute")

            self.ui = self._render_page_from_file(ui, lib_prefix=self.lib_prefix)

        else:
            # Static UI: render the UI now and save the results
            self.ui = self._render_page(
                cast("Tag | TagList", ui), lib_prefix=self.lib_prefix
            )

    def init_starlette_app(self) -> starlette.applications.Starlette:
        routes: list[starlette.routing.BaseRoute] = [
            starlette.routing.WebSocketRoute("/websocket/", self._on_connect_cb),
            starlette.routing.Route("/", self._on_root_request_cb, methods=["GET"]),
            starlette.routing.Route(
                "/session/{session_id}/{action}/{subpath:path}",
                self._on_session_request_cb,
                methods=["GET", "POST"],
            ),
            starlette.routing.Mount("/", app=self._dependency_handler),
        ]
        middleware: list[starlette.middleware.Middleware] = []
        if autoreload_url():
            shared_dir = os.path.join(os.path.dirname(__file__), "www", "shared")
            routes.insert(
                0,
                starlette.routing.Mount(
                    "/__shared",
                    app=StaticFiles(directory=shared_dir),
                ),
            )
            middleware.append(
                starlette.middleware.Middleware(InjectAutoreloadMiddleware)
            )
        # In Pyodide mode, an HTTPException(404) being thrown resulted in
        # some default error handler (that happened not to be async) being
        # run in a threadpool, which Pyodide could not handle. So in Pyodide
        # mode, install our own async error handler at the outermost layer
        # that we can.
        if is_pyodide:
            middleware.append(starlette.middleware.Middleware(ErrorMiddleware))

        starlette_app = starlette.applications.Starlette(
            routes=routes,
            middleware=middleware,
            lifespan=self._lifespan,
        )

        return starlette_app

    @asynccontextmanager
    async def _lifespan(self, app: starlette.applications.Starlette):
        async with self._exit_stack:
            yield

    def _create_session(self, conn: Connection) -> AppSession:
        id = secrets.token_hex(32)
        session = AppSession(self, id, conn, debug=self._debug)
        self._sessions[id] = session
        return session

    def _remove_session(self, session: AppSession | str) -> None:
        if isinstance(session, AppSession):
            session = session.id

        if self._debug:
            print(f"remove_session: {session}", flush=True)
        del self._sessions[session]

    def run(self, **kwargs: object) -> None:
        """
        Run the app.

        Parameters
        ----------
        **kwargs
            Keyword arguments passed to :func:`~shiny.run_app`.
        """
        from ._main import run_app

        run_app(self, **kwargs)  # pyright: ignore[reportArgumentType]

    # ASGI entrypoint. Handles HTTP, WebSocket, and lifespan.
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await self.starlette_app(scope, receive, send)

    def on_shutdown(self, callback: Callable[[], None]) -> Callable[[], None]:
        """
        Register a callback to be called when the app is shutting down. This can be
        useful for cleaning up app-wide resources, like connection pools, temporary
        directories, worker threads/processes, etc.

        Parameters
        ----------
        callback
            The callback to call. It should take no arguments, and any return value will
            be ignored. Try not to raise an exception in the callback, as exceptions
            during cleanup can hide the original exception that caused the app to shut
            down.

        Returns
        -------
        :
            The callback, to allow this method to be used as a decorator.
        """
        return self._exit_stack.callback(callback)

    async def call_pyodide(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Communicate with pyodide.

        Warning
        -------
        This method is not intended for public usage. It's exported for use by
        shinylive.
        """

        # TODO: Pretty sure there are objects that need to be destroy()'d here?
        scope = cast(Any, scope).to_py()

        # ASGI requires some values to be byte strings, not character strings. Those are
        # not that easy to create in JavaScript, so we let the JS side pass us strings
        # and we convert them to bytes here.
        if "headers" in scope:
            # JS doesn't have `bytes` so we pass as strings and convert here
            scope["headers"] = [
                [value.encode("latin-1") for value in header]
                for header in scope["headers"]
            ]
        if "query_string" in scope and scope["query_string"]:
            scope["query_string"] = scope["query_string"].encode("latin-1")
        if "raw_path" in scope and scope["raw_path"]:
            scope["raw_path"] = scope["raw_path"].encode("latin-1")

        async def rcv() -> Message:
            event = await receive()
            return cast(Message, cast(Any, event).to_py())

        async def snd(event: Message):
            await send(event)

        await self(scope, rcv, snd)

    async def stop(self) -> None:
        """
        Stop the app (i.e., close all sessions).

        See Also
        --------
        * :func:`~shiny.Session.close`
        """
        # convert to list to avoid modifying the dict while iterating over it, which
        # throws an error
        for session in list(self._sessions.values()):
            await session.close()

    # ==========================================================================
    # Connection callbacks
    # ==========================================================================
    async def _on_root_request_cb(self, request: Request) -> Response:
        """
        Callback passed to the ConnectionManager which is invoked when a HTTP
        request for / occurs.
        """
        ui: RenderedHTML
        if self.bookmark_store == "disable":
            restore_ctx = RestoreContext()
        else:
            restore_ctx = await RestoreContext.from_query_string(
                request.url.query, app=self
            )

        if callable(self.ui):
            # At this point, if `app.bookmark_store != "disable"`, then we've already
            # checked that `ui` is a function (in `App._init_bookmarking()`). No need to throw warning if `ui` is _not_ a function.
            with restore_context(restore_ctx):
                ui = self._render_page(self.ui(request), self.lib_prefix)
        else:
            ui = self.ui
        return HTMLResponse(content=ui["html"])

    async def _on_connect_cb(self, ws: starlette.websockets.WebSocket) -> None:
        """
        Callback which is invoked when a new WebSocket connection is established.
        """
        await ws.accept()
        conn = StarletteConnection(ws)
        session = self._create_session(conn)

        await session._run()

    async def _on_session_request_cb(self, request: Request) -> ASGIApp:
        """
        Callback passed to the ConnectionManager which is invoked when a HTTP
        request for /session/* occurs.
        """
        session_id: str = request.path_params["session_id"]  # type: ignore
        action: str = request.path_params["action"]  # type: ignore
        subpath: str = request.path_params["subpath"]  # type: ignore

        if session_id in self._sessions:
            session: AppSession = self._sessions[session_id]
            with session_context(session):
                return await session._handle_request(request, action, subpath)

        return JSONResponse({"detail": "Not Found"}, status_code=404)

    # ==========================================================================
    # Flush
    # ==========================================================================
    def _request_flush(self, session: AppSession) -> None:
        # TODO: Until we have reactive domains, because we can't yet keep track
        # of which sessions need a flush.
        pass
        # self._sessions_needing_flush[session.id] = session

    # ==========================================================================
    # HTML Dependency stuff
    # ==========================================================================
    def _ensure_web_dependencies(self, deps: list[HTMLDependency]) -> None:
        for dep in deps:
            self._register_web_dependency(dep)

    def _register_web_dependency(self, dep: HTMLDependency) -> None:
        # If the dependency has been seen before, quit early.

        # Even if the htmldependency version is higher or lower, the HTML being sent to
        # the user is requesting THIS dependency. Therefore, it should be available to
        # the user independent of any previous versions of the dependency being served.

        # Note: htmltools does de-duplicate dependencies and finds the highest version
        # to return. However, dynamic UI and callable UI do not run through the same
        # filter over time. When using callable UI functions, UI dependencies are reset
        # on refresh. So if a dependency makes it here, it is not necessarily the
        # highest version served over time but is the highest version for this
        # particular UI. Therefore, serve it must be served.
        dep_name = html_dep_name(dep)
        if dep_name in self._registered_dependencies:
            return

        # For HTMLDependencies that have sources on disk, mount the source dir.
        # (Some HTMLDependencies only carry head content, and have no source on disk.)
        if dep.source:
            paths = dep.source_path_map(lib_prefix=self.lib_prefix)
            if paths["source"] != "":
                self._dependency_handler.routes.insert(
                    0,
                    starlette.routing.Mount(
                        "/" + paths["href"],
                        StaticFiles(directory=paths["source"]),
                        name=dep_name,
                    ),
                )

        self._registered_dependencies[dep_name] = dep

    def _render_page(self, ui: Tag | TagList, lib_prefix: str) -> RenderedHTML:
        ui_res = copy.copy(ui)
        # Use presence of the Bootstrap dependency as a signal that the UI uses a
        # shiny.ui.page_*() function, in which case the Shiny CSS is already included.
        has_bootstrap = any(
            [dep.name == "bootstrap" for dep in ui_res.get_dependencies()]
        )
        # Make sure requirejs, jQuery, and Shiny come before any other dependencies.
        # (see require_deps() for a comment about why we even include it)
        ui_res.insert(
            0,
            [require_deps(), jquery_deps(), *shiny_deps(include_css=not has_bootstrap)],
        )
        rendered = HTMLDocument(ui_res).render(lib_prefix=lib_prefix)
        self._ensure_web_dependencies(rendered["dependencies"])
        return rendered

    def _render_page_from_file(self, file: Path, lib_prefix: str) -> RenderedHTML:
        with open(file, "r") as f:
            page_html = f.read()

        doc = HTMLTextDocument(
            page_html,
            deps=[require_deps(), jquery_deps(), *shiny_deps(include_css=True)],
            deps_replace_pattern='<meta name="shiny-dependency-placeholder" content="">',
        )

        rendered = doc.render(lib_prefix=lib_prefix)
        self._ensure_web_dependencies(rendered["dependencies"])

        return rendered

    # ==========================================================================
    # Bookmarking
    # ==========================================================================

    def _init_bookmarking(self, *, bookmark_store: BookmarkStore, ui: Any) -> None:
        self._bookmark_save_dir_fn = MISSING
        self._bookmark_restore_dir_fn = MISSING
        self._bookmark_store = bookmark_store

        if bookmark_store != "disable" and not callable(ui):
            raise TypeError(
                "App(ui=) must be a function that accepts a request object to allow the UI to be properly reconstructed from a bookmarked state."
            )

    @property
    def bookmark_store(self) -> BookmarkStore:
        return self._bookmark_store

    def set_bookmark_save_dir_fn(self, bookmark_save_dir_fn: BookmarkDirFn):
        self._bookmark_save_dir_fn = as_bookmark_dir_fn(bookmark_save_dir_fn)

    def set_bookmark_restore_dir_fn(self, bookmark_restore_dir_fn: BookmarkDirFn):
        self._bookmark_restore_dir_fn = as_bookmark_dir_fn(bookmark_restore_dir_fn)


def is_uifunc(x: Path | Tag | TagList | Callable[[Request], Tag | TagList]) -> bool:
    if (
        isinstance(x, Path)
        or isinstance(x, Tag)
        or isinstance(x, TagList)
        or not callable(x)
    ):
        return False
    else:
        return True


def html_dep_name(dep: HTMLDependency) -> str:
    return dep.name + "-" + str(dep.version)


def create_static_asset_route(
    mount_point: str, static_asset_path: Path
) -> starlette.routing.BaseRoute:
    """
    Create a Starlette route for serving static assets.

    Parameters
    ----------
    mount_point
        The mount point where the static assets will be served.
    static_asset_path
        The path on disk to the static assets.
    """
    if static_asset_path.is_dir():
        return starlette.routing.Mount(
            mount_point,
            StaticFiles(directory=static_asset_path),
            name="shiny-app-static-assets-" + mount_point,
        )
    else:
        mime_type = guess_mime_type(static_asset_path, strict=False)

        def file_response_handler(req: Request) -> FileResponse:
            return FileResponse(static_asset_path, media_type=mime_type)

        return starlette.routing.Route(
            mount_point,
            file_response_handler,
            name="shiny-app-static-assets-" + mount_point,
        )


def noop_server_fn(input: Inputs, output: Outputs, session: Session) -> None:
    pass


def wrap_server_fn_with_output_session(
    server: Callable[[Inputs], None],
) -> Callable[[Inputs, Outputs, Session], None]:
    def _server(input: Inputs, output: Outputs, session: Session):
        # Only has 1 parameter, ignore output, session
        server(input)

    return _server
