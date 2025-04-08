from __future__ import annotations

import warnings
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Awaitable, Callable, Literal, Optional

from .._docstring import add_example
from .._utils import AsyncCallbacks, CancelCallback, wrap_async
from ._button import BOOKMARK_ID
from ._restore_state import RestoreState
from ._save_state import BookmarkState
from ._types import BookmarkStore

if TYPE_CHECKING:
    from ..express._stub_session import ExpressStubSession
    from ..module import ResolvedId
    from ..session._session import AppSession, Session, SessionProxy
    from . import RestoreContext
else:
    from typing import Any

    RestoreContext = Any
    SessionProxy = Any
    Session = Any
    AppSession = Any
    ResolvedId = Any
    ExpressStubSession = Any


class Bookmark(ABC):

    _on_get_exclude: list[Callable[[], list[str]]]
    """Callbacks that BookmarkProxy classes utilize to help determine the list of inputs to exclude from bookmarking."""

    exclude: list[str]
    """A list of scoped Input names to exclude from bookmarking."""

    _on_bookmark_callbacks: AsyncCallbacks
    _on_bookmarked_callbacks: AsyncCallbacks
    _on_restore_callbacks: AsyncCallbacks
    _on_restored_callbacks: AsyncCallbacks

    @add_example("input_bookmark_button")
    async def __call__(self) -> None:
        await self.do_bookmark()

    def __init__(self):

        super().__init__()

        self._on_get_exclude = []
        self.exclude = []

        self._on_bookmark_callbacks = AsyncCallbacks()
        self._on_bookmarked_callbacks = AsyncCallbacks()
        self._on_restore_callbacks = AsyncCallbacks()
        self._on_restored_callbacks = AsyncCallbacks()

    # Making this a read only property as app authors will not be able to change how the
    # session is restored as the server function will run after the session has been
    # restored.
    @property
    @abstractmethod
    def store(self) -> BookmarkStore:
        """
        App's bookmark store value

        Possible values:
        * `"url"`: Save / reload the bookmark state in the URL.
        * `"server"`: Save / reload the bookmark state on the server.
        * `"disable"` (default): Bookmarking is diabled.
        """
        ...

    @property
    @abstractmethod
    def _restore_context(self) -> RestoreContext | None:
        """
        A read-only value of the session's RestoreContext object.
        """
        ...

    # # TODO: Barret - Implement this?!?
    # @abstractmethod
    # async def get_url(self) -> str:
    #     ...

    # # TODO: Barret - Implement this?!?
    # # `session.bookmark.on_bookmarked(session.bookmark.update_query_string)`
    # # `session.bookmark.on_bookmarked(session.bookmark.show_modal)`
    # await def show_modal(self, url: Optional[str] = None) -> None:
    #     if url is None:
    #         url:str = self._get_encoded_url()

    #     await session.insert_ui(modal_with_url(url))

    @add_example("bookmark_callbacks")
    def on_bookmark(
        self,
        callback: (
            Callable[[BookmarkState], None] | Callable[[BookmarkState], Awaitable[None]]
        ),
        /,
    ) -> CancelCallback:
        """
        Registers a function that will be called just before bookmarking state.

        This callback will be executed **before** the bookmark state is saved serverside or in the URL.

        Parameters
        ----------
        callback
            The callback function to call when the session is bookmarked.
            This method should accept a single argument, which is a
            :class:`~shiny.bookmark._bookmark.ShinySaveState` object.
        """
        return self._on_bookmark_callbacks.register(wrap_async(callback))

    @add_example("bookmark_callbacks")
    def on_bookmarked(
        self,
        callback: Callable[[str], None] | Callable[[str], Awaitable[None]],
        /,
    ) -> CancelCallback:
        """
        Registers a function that will be called just after bookmarking state.

        This callback will be executed **after** the bookmark state is saved serverside or in the URL.

        Parameters
        ----------
        callback
            The callback function to call when the session is bookmarked. This method
            should accept a single argument, the string representing the query parameter
            component of the URL.
        """

        return self._on_bookmarked_callbacks.register(wrap_async(callback))

    def on_restore(
        self,
        callback: (
            Callable[[RestoreState], None] | Callable[[RestoreState], Awaitable[None]]
        ),
    ) -> CancelCallback:
        """
        Registers a function that will be called just before restoring state.

        This callback will be executed **before** the bookmark state is restored.
        """
        return self._on_restore_callbacks.register(wrap_async(callback))

    def on_restored(
        self,
        callback: (
            Callable[[RestoreState], None] | Callable[[RestoreState], Awaitable[None]]
        ),
    ) -> CancelCallback:
        """
        Registers a function that will be called just after restoring state.

        This callback will be executed **after** the bookmark state is restored.
        """
        return self._on_restored_callbacks.register(wrap_async(callback))

    @abstractmethod
    async def update_query_string(
        self,
        query_string: Optional[str] = None,
        mode: Literal["replace", "push"] = "replace",
    ) -> None:
        """
        Update the query string of the current URL.

        Parameters
        ----------
        query_string
            The query string to set. If `None`, the current bookmark state URL will be used.
        mode
            Whether to replace the current URL or push a new one. Pushing a new value
            will add to the user's browser history.
        """
        ...

    @abstractmethod
    async def get_bookmark_url(self) -> str | None:
        """
        Get the URL of the current bookmark state

        This method should return the full URL, including the query string.

        As a side effect, all `on_bookmark` callbacks will be invoked to allow the
        bookmark state to be modified before it is serialized. This will cause the
        bookmark state to be serialized to disk when `session.bookmark.store ==
        "server"`.

        Returns
        -------
        :
            The full URL of the current bookmark state, including the query string.
            `None` if bookmarking is not enabled.
        """
        ...

    @abstractmethod
    async def do_bookmark(self) -> None:
        """
        Perform bookmarking.

        This method will also call the `on_bookmark` and `on_bookmarked` callbacks to
        alter the bookmark state. Then, the bookmark state will be either saved to the
        server or encoded in the URL, depending on the `.store` option.

        No actions will be performed if the `.store` option is set to `"disable"`.

        Note: this method is called when `session.bookmark()` is executed.
        """
        ...

    async def show_bookmark_url_modal(
        self,
        url: str | None = None,
    ) -> None:
        """
        Display a modal dialog for displaying the bookmark URL.

        This method should be called when the bookmark button is clicked, and it
        should display a modal dialog with the current bookmark URL.

        Parameters
        ----------
        url
            The URL to display in the modal dialog. If `None`, the current bookmark
            URL will be retrieved using `session.bookmark.get_bookmark_url()`.
        """
        import textwrap

        from htmltools import TagList, tags

        from ..ui import modal, modal_show

        title = "Bookmarked application link"
        subtitle: str | None = None
        if self.store == "url":
            subtitle = "This link stores the current state of this application."
        elif self.store == "server":
            subtitle = (
                "The current state of this application has been stored on the server."
            )

        if url is None:
            url = await self.get_bookmark_url()

        subtitle_tag = TagList(
            tags.br(),
            (
                tags.span(subtitle + " ", class_="text-muted")
                if isinstance(subtitle, str)
                else subtitle
            ),
            tags.span(id="shiny-bookmark-copy-text", class_="text-muted"),
        )
        # Need separate show and shown listeners. The show listener sizes the
        # textarea just as the modal starts to fade in. The 200ms delay is needed
        # because if we try to resize earlier, it can't calculate the text height
        # (scrollHeight will be reported as zero). The shown listener selects the
        # text; it's needed because because selection has to be done after the fade-
        # in is completed.
        modal_js = tags.script(
            textwrap.dedent(
                """
            $('#shiny-modal').
                one('show.bs.modal', function() {
                setTimeout(function() {
                    var $textarea = $('#shiny-modal textarea');
                    $textarea.innerHeight($textarea[0].scrollHeight);
                }, 200);
            });
            $('#shiny-modal')
                .one('shown.bs.modal', function() {
                $('#shiny-modal textarea').select().focus();
            });
            $('#shiny-bookmark-copy-text')
                .text(function() {
                if (/Mac/i.test(navigator.userAgent)) {
                    return 'Press \u2318-C to copy.';
                } else {
                    return 'Press Ctrl-C to copy.';
                }
            });
            """
            )
        )

        url_modal = modal(
            tags.textarea(
                url,
                class_="form-control",
                rows="1",
                style="resize: none;",
                readonly="readonly",
            ),
            subtitle_tag,
            modal_js,
            title=title,
            easy_close=True,
        )

        modal_show(url_modal)
        return


class BookmarkApp(Bookmark):
    _root_session: AppSession
    """
    The root session object.
    """

    _restore_context_value: RestoreContext
    """
    Placeholder value that should only be manually set within the session's `init` websocket message.
    """

    def __init__(self, root_session: AppSession):
        from ..session._session import AppSession

        assert isinstance(root_session, AppSession)
        super().__init__()

        self._root_session = root_session

        # # Do not set it to avoid supporting a `None` type.
        # # Instead, only use it after it's been set.
        # self._restore_context_value = None

    # Making this a read only property as app authors will not be able to change how the
    # session is restored as the server function will run after the session has been
    # restored.
    @property
    def store(self) -> BookmarkStore:

        return self._root_session.app.bookmark_store

    @property
    def _restore_context(self) -> RestoreContext | None:
        return self._restore_context_value

    def _set_restore_context(self, restore_context: RestoreContext):
        """
        Set the session's RestoreContext object.

        This should only be done within the `init` websocket message.
        """
        self._restore_context_value = restore_context

    def _create_effects(self) -> None:
        """
        Create the bookmarking `@reactive.effect`s for the session.

        Effects:
        * Call `session.bookmark()` on the bookmark button click.
        * Show an error message if the restore context has an error.
        * Invoke the `@session.bookmark.on_restore` callbacks at the beginning of the flush cycle.
        * Invoke the `@session.bookmark.on_restored` callbacks after the flush cycle completes.
        """
        # Get bookmarking config
        if self.store == "disable":
            return

        root_session = self._root_session

        from .. import reactive
        from ..session import session_context
        from ..ui._notification import notification_show

        with session_context(root_session):

            # Fires when the bookmark button is clicked.
            @reactive.effect
            @reactive.event(root_session.input[BOOKMARK_ID])
            async def _():
                await root_session.bookmark()

            # If there was an error initializing the current restore context, show
            # notification in the client.
            @reactive.effect
            def init_error_message():
                if self._restore_context and self._restore_context._init_error_msg:
                    notification_show(
                        f"Error in RestoreContext initialization: {self._restore_context._init_error_msg}",
                        duration=None,
                        type="error",
                        session=root_session,
                    )

            # Run the on_restore function at the beginning of the flush cycle, but after
            # the server function has been executed.
            @reactive.effect(priority=1000000)
            async def invoke_on_restore_callbacks():
                if self._on_restore_callbacks.count() == 0:
                    return

                with session_context(root_session):

                    try:
                        # ?withLogErrors
                        with reactive.isolate():
                            if self._restore_context and self._restore_context.active:
                                restore_state = self._restore_context.as_state()
                                await self._on_restore_callbacks.invoke(restore_state)
                    except Exception as e:
                        warnings.warn(
                            f"Error calling on_restore callback: {e}",
                            stacklevel=2,
                        )
                        notification_show(
                            f"Error calling on_restore callback: {e}",
                            duration=None,
                            type="error",
                        )

            # Run the on_restored function after the flush cycle completes and
            # information is sent to the client.
            @root_session.on_flushed
            async def invoke_on_restored_callbacks():
                if self._on_restored_callbacks.count() == 0:
                    return

                with session_context(root_session):
                    try:
                        with reactive.isolate():
                            if self._restore_context and self._restore_context.active:
                                restore_state = self._restore_context.as_state()
                                await self._on_restored_callbacks.invoke(restore_state)
                    except Exception as e:
                        warnings.warn(
                            f"Error calling on_restored callback: {e}",
                            stacklevel=2,
                        )
                        notification_show(
                            f"Error calling on_restored callback: {e}",
                            duration=None,
                            type="error",
                        )

        return

    async def update_query_string(
        self,
        query_string: Optional[str] = None,
        mode: Literal["replace", "push"] = "replace",
    ) -> None:
        if query_string is None:
            query_string = await self.get_bookmark_url()

        if mode not in {"replace", "push"}:
            raise ValueError(f"Invalid mode: {mode}")
        await self._root_session._send_message(
            {
                "updateQueryString": {
                    "queryString": query_string,
                    "mode": mode,
                }
            }
        )

    def _get_bookmark_exclude(self) -> list[str]:
        """
        Get the list of inputs excluded from being bookmarked.
        """

        scoped_excludes: list[str] = []
        for proxy_exclude_fn in self._on_get_exclude:
            scoped_excludes.extend(proxy_exclude_fn())
        # Remove duplicates
        return [str(name) for name in set([*self.exclude, *scoped_excludes])]

    async def get_bookmark_url(self) -> str | None:
        if self.store == "disable":
            return None

        # ?withLogErrors
        from ..bookmark._bookmark import BookmarkState
        from ..session import session_context

        async def root_state_on_save(state: BookmarkState) -> None:
            with session_context(self._root_session):
                await self._on_bookmark_callbacks.invoke(state)

        root_state = BookmarkState(
            input=self._root_session.input,
            exclude=self._get_bookmark_exclude(),
            on_save=root_state_on_save,
        )

        if self.store == "server":
            query_string = await root_state._save_state(app=self._root_session.app)
        elif self.store == "url":
            query_string = await root_state._encode_state()
        # # Can we have browser storage?
        # elif self.store == "browser":
        #     get_json object
        #     get consistent storage value (not session id)
        #     send object to browser storage
        #     return server-like-id url value
        else:
            raise ValueError("Unknown bookmark store: " + self.store)

        clientdata = self._root_session.clientdata

        port = str(clientdata.url_port())
        full_url = "".join(
            [
                clientdata.url_protocol(),
                "//",
                clientdata.url_hostname(),
                ":" if port else "",
                port,
                clientdata.url_pathname(),
                "?",
                query_string,
            ]
        )

        return full_url

    async def do_bookmark(self) -> None:

        from ..session import session_context

        try:
            full_url = await self.get_bookmark_url()

            if full_url is None:
                # If you have a bookmark button or request a bookmark to be saved,
                # then it should be saved. (Present a warning telling author how to fix it)
                warnings.warn(
                    "Saving the bookmark state has been requested. "
                    'However, bookmarking is current set to `"disable"`. '
                    "Please enable bookmarking by setting "
                    "`shiny.App(bookmark_store=)` or "
                    "`shiny.express.app_opts(bookmark_store=)`",
                    stacklevel=2,
                )
                return

            # If on_bookmarked callback was provided, invoke it; if not call
            # the default.
            if self._on_bookmarked_callbacks.count() > 0:
                with session_context(self._root_session):
                    await self._on_bookmarked_callbacks.invoke(full_url)
            else:
                # Barret:
                # This action feels weird. I don't believe it should occur
                # Instead, I believe it should update the query string and set the user's clipboard with a UI notification in the corner.
                with session_context(self._root_session):
                    await self.show_bookmark_url_modal(full_url)

        except Exception as e:
            msg = f"Error bookmarking state: {e}"
            from ..ui._notification import notification_show

            notification_show(msg, duration=None, type="error")


class BookmarkProxy(Bookmark):

    _ns: ResolvedId
    _proxy_session: SessionProxy
    _root_session: Session

    @property
    def _root_bookmark(self) -> Bookmark:
        return self._root_session.bookmark

    def __init__(self, session_proxy: SessionProxy):
        from ..session._session import SessionProxy

        assert isinstance(session_proxy, SessionProxy)
        super().__init__()

        self._ns = session_proxy.ns
        self._proxy_session = session_proxy
        self._root_session = session_proxy._root_session

        # Be sure root bookmark has access to proxy's excluded values
        self._root_bookmark._on_get_exclude.append(
            lambda: [str(self._ns(name)) for name in self.exclude]
        )

        # Note: This proxy bookmark class will not register a handler (`on_bookmark`,
        # `on_bookmarked`, `on_restore`, `on_restored`) until one is requested either by
        # the app author or a sub-proxy bookmark class
        # These function are utilized

    @property
    def _ns_prefix(self) -> str:
        return str(self._ns + self._ns._sep)

    # The goal of this method is to save the scope's values. All namespaced inputs
    # will already exist within the `root_state`.
    async def _scoped_on_bookmark(self, root_state: BookmarkState) -> None:
        from ..bookmark._bookmark import BookmarkState

        scoped_state = BookmarkState(
            input=self._proxy_session.input,
            exclude=self.exclude,
            on_save=None,
        )

        # Make subdir for scope
        #
        # Folder only used by author callbacks. File uploads are handled by root session
        if root_state.dir is not None:
            scope_subpath = self._ns
            scoped_state.dir = Path(root_state.dir) / scope_subpath
            # Barret - 2025-03-17:
            # Having Shiny make this directory feels like the wrong thing to do here.
            # Feels like we should be using the App's bookmark_save_dir function to
            # determine where to save the bookmark state.
            # However, R-Shiny currently creates the directory:
            # https://github.com/rstudio/shiny/blob/f55c26af4a0493b082d2967aca6d36b90795adf1/R/shiny.R#L940
            scoped_state.dir.mkdir(parents=True, exist_ok=True)

            if not scoped_state.dir.exists():
                raise FileNotFoundError(
                    f"Scope directory could not be created for {scope_subpath}"
                )

        from ..session import session_context

        with session_context(self._proxy_session):
            await self._on_bookmark_callbacks.invoke(scoped_state)

        # Copy `values` from scoped_state to root_state (adding namespace)
        if scoped_state.values:
            for key, value in scoped_state.values.items():
                if key.strip() == "":
                    raise ValueError("All scope values must be named.")
                root_state.values[str(self._ns(key))] = value

    def on_bookmark(
        self,
        callback: (
            Callable[[BookmarkState], None] | Callable[[BookmarkState], Awaitable[None]]
        ),
    ) -> CancelCallback:
        if self._on_bookmark_callbacks.count() == 0:
            # Register a proxy callback on the parent session
            self._root_bookmark.on_bookmark(self._scoped_on_bookmark)
        return super().on_bookmark(callback)

    def on_bookmarked(
        self,
        callback: Callable[[str], None] | Callable[[str], Awaitable[None]],
    ) -> CancelCallback:
        if self._on_bookmarked_callbacks.count() == 0:
            from ..session import session_context

            # Register a proxy callback on the parent session
            @self._root_bookmark.on_bookmarked
            async def scoped_on_bookmarked(url: str) -> None:
                if self._on_bookmarked_callbacks.count() == 0:
                    return
                with session_context(self._proxy_session):
                    await self._on_bookmarked_callbacks.invoke(url)

        return super().on_bookmarked(callback)

    def on_restore(
        self,
        callback: (
            Callable[[RestoreState], None] | Callable[[RestoreState], Awaitable[None]]
        ),
    ) -> CancelCallback:

        if self._on_restore_callbacks.count() == 0:
            from ..session import session_context

            # Register a proxy callback on the parent session
            @self._root_bookmark.on_restore
            async def scoped_on_restore(restore_state: RestoreState) -> None:
                if self._on_restore_callbacks.count() == 0:
                    return

                scoped_restore_state = restore_state._state_within_namespace(
                    self._ns_prefix
                )

                with session_context(self._proxy_session):
                    await self._on_restore_callbacks.invoke(scoped_restore_state)

        return super().on_restore(callback)

    def on_restored(
        self,
        callback: (
            Callable[[RestoreState], None] | Callable[[RestoreState], Awaitable[None]]
        ),
    ) -> CancelCallback:

        if self._on_restored_callbacks.count() == 0:
            from ..session import session_context

            # Register a proxy callback on the parent session
            @self._root_bookmark.on_restored
            async def scoped_on_restored(restore_state: RestoreState) -> None:
                if self._on_restored_callbacks.count() == 0:
                    return

                scoped_restore_state = restore_state._state_within_namespace(
                    self._ns_prefix
                )

                with session_context(self._proxy_session):
                    await self._on_restored_callbacks.invoke(scoped_restore_state)

        return super().on_restored(callback)

    @property
    def store(self) -> BookmarkStore:
        return self._root_bookmark.store

    @property
    def _restore_context(self) -> RestoreContext | None:
        return self._root_bookmark._restore_context

    async def update_query_string(
        self,
        query_string: Optional[str] = None,
        mode: Literal["replace", "push"] = "replace",
    ) -> None:
        await self._root_bookmark.update_query_string(query_string, mode)

    async def get_bookmark_url(self) -> str | None:
        return await self._root_bookmark.get_bookmark_url()

    async def do_bookmark(self) -> None:
        await self._root_bookmark.do_bookmark()


class BookmarkExpressStub(Bookmark):

    def __init__(self, session: ExpressStubSession) -> None:
        super().__init__()

        from ..express._stub_session import ExpressStubSession

        assert isinstance(session, ExpressStubSession)

    @property
    def store(self) -> BookmarkStore:
        return "disable"

    @property
    def _restore_context(self) -> RestoreContext | None:
        # no-op within ExpressStub
        return None

    def on_bookmark(
        self,
        callback: (
            Callable[[BookmarkState], None] | Callable[[BookmarkState], Awaitable[None]]
        ),
    ) -> CancelCallback:
        # Provide a no-op function within ExpressStub
        return lambda: None

    def on_bookmarked(
        self,
        callback: Callable[[str], None] | Callable[[str], Awaitable[None]],
    ) -> CancelCallback:
        # Provide a no-op function within ExpressStub
        return lambda: None

    async def update_query_string(
        self,
        query_string: Optional[str] = None,
        mode: Literal["replace", "push"] = "replace",
    ) -> None:
        # no-op within ExpressStub
        return None

    async def get_bookmark_url(self) -> str | None:
        return None

    async def do_bookmark(self) -> None:
        # no-op within ExpressStub
        return None

    def on_restore(
        self,
        callback: (
            Callable[[RestoreState], None] | Callable[[RestoreState], Awaitable[None]]
        ),
    ) -> CancelCallback:
        # Provide a no-op function within ExpressStub
        return lambda: None

    def on_restored(
        self,
        callback: (
            Callable[[RestoreState], None] | Callable[[RestoreState], Awaitable[None]]
        ),
    ) -> CancelCallback:
        # Provide a no-op function within ExpressStub
        return lambda: None


# #' Display a modal dialog for bookmarking
# #'
# #' This is a wrapper function for [urlModal()] that is automatically
# #' called if an application is bookmarked but no other [onBookmark()]
# #' callback was set. It displays a modal dialog with the bookmark URL, along
# #' with a subtitle that is appropriate for the type of bookmarking used ("url"
# #' or "server").
# #'
# #' @param url A URL to show in the modal dialog.
# #' @export
# showBookmarkUrlModal <- function(url) {
#   store <- getShinyOption("bookmarkStore", default = "")
#   if (store == "url") {
#     subtitle <- "This link stores the current state of this application."
#   } else if (store == "server") {
#     subtitle <- "The current state of this application has been stored on the server."
#   } else {
#     subtitle <- NULL
#   }

#   showModal(urlModal(url, subtitle = subtitle))
# }
