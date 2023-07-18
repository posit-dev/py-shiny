from __future__ import annotations

import copy
import os
import secrets
from typing import Any, Callable, Optional, cast

import starlette.applications
import starlette.exceptions
import starlette.middleware
import starlette.routing
import starlette.websockets
from htmltools import HTMLDependency, HTMLDocument, RenderedHTML, Tag, TagList
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, Response
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from ._autoreload import InjectAutoreloadMiddleware, autoreload_url
from ._connection import Connection, StarletteConnection
from ._error import ErrorMiddleware
from ._shinyenv import is_pyodide
from ._utils import is_async_callable
from .html_dependencies import jquery_deps, require_deps, shiny_deps
from .http_staticfiles import StaticFiles
from .session import Inputs, Outputs, Session, session_context

# Default values for App options.
LIB_PREFIX: str = "lib/"
SANITIZE_ERRORS: bool = False
SANITIZE_ERROR_MSG: str = "An error has occurred. Check your logs or contact the app author for clarification."


class App:
    """
    Create a Shiny app instance.

    Parameters
    ----------
    ui
        The UI definition for the app (e.g., a call to :func:`~shiny.ui.page_fluid` or
        :func:`~shiny.ui.page_fixed`, with layouts and controls nested inside). You can
        also pass a function that takes a :class:`~starlette.requests.Request` and
        returns a UI definition, if you need the UI definition to be created dynamically
        for each pageview.
    server
        A function which is called once for each session, ensuring that each app is
        independent.
    static_assets
        An absolute directory containing static files to be served by the app.
    debug
        Whether to enable debug mode.

    Example
    -------

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

    sanitize_error_msg: str = "An error has occurred. Check your logs or contact the app author for clarification."
    """
    The message to show when an error occurs and ``SANITIZE_ERRORS=True``.
    """

    ui: RenderedHTML | Callable[[Request], Tag | TagList]
    server: Callable[[Inputs, Outputs, Session], None]

    def __init__(
        self,
        ui: Tag | TagList | Callable[[Request], Tag | TagList],
        server: Optional[Callable[[Inputs, Outputs, Session], None]],
        *,
        static_assets: Optional["str" | "os.PathLike[str]"] = None,
        debug: bool = False,
    ) -> None:
        if server is None:

            def _server(inputs: Inputs, outputs: Outputs, session: Session):
                pass

            server = _server

        self.server = server

        self._debug: bool = debug

        # Settings that the user can change after creating the App object.
        self.lib_prefix: str = LIB_PREFIX
        self.sanitize_errors: bool = SANITIZE_ERRORS
        self.sanitize_error_msg: str = SANITIZE_ERROR_MSG

        if static_assets is not None:
            if not os.path.isdir(static_assets):
                raise ValueError(f"static_assets must be a directory: {static_assets}")
            if not os.path.isabs(static_assets):
                raise ValueError(
                    f"static_assets must be an absolute path: {static_assets}"
                )

        self._static_assets: str | os.PathLike[str] | None = static_assets

        self._sessions: dict[str, Session] = {}

        self._sessions_needing_flush: dict[int, Session] = {}

        self._registered_dependencies: dict[str, HTMLDependency] = {}
        self._dependency_handler = starlette.routing.Router()

        if self._static_assets is not None:
            self._dependency_handler.routes.append(
                starlette.routing.Mount(
                    "/",
                    StaticFiles(directory=self._static_assets),
                    name="shiny-app-static-assets-directory",
                )
            )

        starlette_app = self.init_starlette_app()

        self.starlette_app = starlette_app

        if is_uifunc(ui):
            if is_async_callable(cast(Callable[[Request], Any], ui)):
                raise TypeError("App UI cannot be a coroutine function")
            # Dynamic UI: just store the function for later
            self.ui = cast("Callable[[Request], Tag | TagList]", ui)
        else:
            # Static UI: render the UI now and save the results
            self.ui = self._render_page(
                cast("Tag | TagList", ui), lib_prefix=self.lib_prefix
            )

    def init_starlette_app(self):
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
        )

        return starlette_app

    def _create_session(self, conn: Connection) -> Session:
        id = secrets.token_hex(32)
        session = Session(self, id, conn, debug=self._debug)
        self._sessions[id] = session
        return session

    def _remove_session(self, session: Session | str) -> None:
        if isinstance(session, Session):
            session = session.id

        if self._debug:
            print(f"remove_session: {session}", flush=True)
        del self._sessions[session]

    def run(self, **kwargs: object) -> None:
        """
        Run the app.

        Parameters
        ----------
        kwargs
            Keyword arguments passed to :func:`~shiny.run_app`.
        """
        from ._main import run_app

        run_app(self, **kwargs)

    # ASGI entrypoint. Handles HTTP, WebSocket, and lifespan.
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await self.starlette_app(scope, receive, send)

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
        ~shiny.Session.close
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
        if callable(self.ui):
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
            session: Session = self._sessions[session_id]
            with session_context(session):
                return await session._handle_request(request, action, subpath)

        return JSONResponse({"detail": "Not Found"}, status_code=404)

    # ==========================================================================
    # Flush
    # ==========================================================================
    def _request_flush(self, session: Session) -> None:
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
        # Make sure requirejs, jQuery, and Shiny come before any other dependencies.
        # (see require_deps() for a comment about why we even include it)
        ui_res.insert(0, [require_deps(), jquery_deps(), shiny_deps()])
        rendered = HTMLDocument(ui_res).render(lib_prefix=lib_prefix)
        self._ensure_web_dependencies(rendered["dependencies"])
        return rendered


def is_uifunc(x: Tag | TagList | Callable[[Request], Tag | TagList]):
    if isinstance(x, Tag) or isinstance(x, TagList) or not callable(x):
        return False
    else:
        return True


def html_dep_name(dep: HTMLDependency) -> str:
    return dep.name + "-" + str(dep.version)
