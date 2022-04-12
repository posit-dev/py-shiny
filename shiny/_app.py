import contextlib
import os
from typing import Any, List, Union, Dict, Callable, cast

from htmltools import Tag, TagList, HTMLDocument, HTMLDependency, RenderedHTML

import starlette.routing
import starlette.applications
import starlette.websockets
from starlette.types import ASGIApp, Message, Receive, Scope, Send
from starlette.requests import Request
from starlette.responses import Response, HTMLResponse, JSONResponse

from ._connmanager import Connection, StarletteConnection
from .html_dependencies import jquery_deps, shiny_deps
from .http_staticfiles import StaticFiles
from .reactive import on_flushed
from .session import Inputs, Outputs, Session, session_context


class App:
    """
    Create a Shiny app instance.

    Parameters
    ----------
    ui
        The UI definition for the app (e.g., a call to :func:`~shiny.ui.page_fluid`
        with nested controls).
    server
        A function which is called once for each session, ensuring that each app is
        independent.
    debug
        Whether to enable debug mode.

    Example
    -------

    .. code-block:: python

        from shiny import *

        app_ui = ui.page_fluid("Hello Shiny!")

        def server(input: Inputs, output: Outputs, session: Session):
            pass

        app = App(app_ui, server)
    """

    LIB_PREFIX: str = "lib/"
    """
    A path prefix to place before all HTML dependencies processed by
    ``register_web_dependency()``.
    """

    SANITIZE_ERRORS: bool = False
    """
    Whether or not to show a generic message (``SANITIZE_ERRORS=True``) or the actual
    message (``SANITIZE_ERRORS=False``) in the app UI when an error occurs. This flag
    may default to ``True`` in some production environments (e.g., RStudio Connect).
    """

    SANITIZE_ERROR_MSG: str = "An error has occurred. Check your logs or contact the app author for clarification."
    """
    The message to show when an error occurs and ``SANITIZE_ERRORS=True``.
    """

    STATIC_ASSETS_DIR: str = "www"
    """
    A directory, relative to the app's directory, which contains static files to be
    served by the app.
    """

    def __init__(
        self,
        ui: Union[Tag, TagList],
        server: Callable[[Inputs, Outputs, Session], None],
        *,
        debug: bool = False,
    ) -> None:
        self.ui: RenderedHTML = _render_page(ui, lib_prefix=self.LIB_PREFIX)
        self.server: Callable[[Inputs, Outputs, Session], None] = server

        self._debug: bool = debug

        self._sessions: Dict[str, Session] = {}
        self._last_session_id: int = 0  # Counter for generating session IDs

        self._sessions_needing_flush: Dict[int, Session] = {}

        self._registered_dependencies: Dict[str, HTMLDependency] = {}
        self._dependency_handler = starlette.routing.Router()

        self.starlette_app = starlette.applications.Starlette(
            routes=[
                starlette.routing.WebSocketRoute("/websocket/", self._on_connect_cb),
                starlette.routing.Route("/", self._on_root_request_cb, methods=["GET"]),
                starlette.routing.Route(
                    "/session/{session_id}/{action}/{subpath:path}",
                    self._on_session_request_cb,
                    methods=["GET", "POST"],
                ),
                starlette.routing.Mount("/", app=self._dependency_handler),
            ],
            lifespan=self._lifespan,
        )

    @contextlib.asynccontextmanager
    async def _lifespan(self, app: starlette.applications.Starlette):
        unreg = on_flushed(self._on_reactive_flushed, once=False)
        try:
            yield
        finally:
            unreg()

    async def _on_reactive_flushed(self):
        await self._flush_pending_sessions()

    def _create_session(self, conn: Connection) -> Session:
        self._last_session_id += 1
        id = str(self._last_session_id)
        session = Session(self, id, conn, debug=self._debug)
        self._sessions[id] = session
        return session

    def _remove_session(self, session: Union[Session, str]) -> None:
        if isinstance(session, Session):
            session = session.id

        if self._debug:
            print(f"remove_session: {session}")
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
        prism-experiments.
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

        # Mount static assets (i.e., the www subdir) if the app directory has been set
        # (by run_app())
        app_dir = os.getenv("SHINY_APP_DIRECTORY")
        if app_dir:
            www_dir = os.path.join(app_dir, self.STATIC_ASSETS_DIR)
            if os.path.isdir(www_dir):
                self._dependency_handler.mount(
                    "/",
                    StaticFiles(directory=www_dir),
                    name="shiny-app-static-assets-directory",
                )

        self._ensure_web_dependencies(self.ui["dependencies"])
        return HTMLResponse(content=self.ui["html"])

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

    async def _flush_pending_sessions(self) -> None:
        # TODO: Until we have reactive domains, flush all sessions (because we
        # can't yet keep track of which ones need a flush)
        for _, session in self._sessions.items():
            await session._flush()
        # for id, session in self._sessions_needing_flush.items():
        #     await session.flush()
        #     del self._sessions_needing_flush[id]

    # ==========================================================================
    # HTML Dependency stuff
    # ==========================================================================
    def _ensure_web_dependencies(self, deps: List[HTMLDependency]) -> None:
        for dep in deps:
            self._register_web_dependency(dep)

    def _register_web_dependency(self, dep: HTMLDependency) -> None:
        if (
            dep.name in self._registered_dependencies
            and dep.version >= self._registered_dependencies[dep.name].version
        ):
            return

        # For HTMLDependencies that have sources on disk, mount the source dir.
        # (Some HTMLDependencies only carry head content, and have no source on disk.)
        if dep.source:
            paths = dep.source_path_map(lib_prefix=self.LIB_PREFIX)
            self._dependency_handler.mount(
                "/" + paths["href"],
                StaticFiles(directory=paths["source"]),
                name=dep.name + "-" + str(dep.version),
            )

        self._registered_dependencies[dep.name] = dep


def _render_page(ui: Union[Tag, TagList], lib_prefix: str) -> RenderedHTML:
    doc = HTMLDocument(TagList(jquery_deps(), shiny_deps(), ui))
    return doc.render(lib_prefix=lib_prefix)
