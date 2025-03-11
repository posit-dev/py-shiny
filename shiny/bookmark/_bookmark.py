from __future__ import annotations

import warnings
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Awaitable, Callable, Literal, NoReturn

from .._utils import AsyncCallbacks, CancelCallback, wrap_async
from ._button import BOOKMARK_ID
from ._restore_state import RestoreState
from ._save_state import BookmarkState
from ._types import BookmarkStore

# TODO: Barret - Bookmark state
# bookmark -> save/load interface
# * √ global hooks
# * √ default local functions
# save/load interface -> register functions
# * `shiny.bookmark.globals`
# register interface -> Make interface for Connect
# * TODO: implement in Connect PR
# bookmark -> save state
# save state -> {inputs, values, exclude}
# {inputs} -> custom serializer
# * √ Hook to `Inputs.set_serializer(id, fn)`
# * √ `Inputs._serialize()` to create a dict
# {values} -> dict (where as in R is an environment)
# * √ values is a dict!
# {exclude} -> Requires `session.setBookmarkExclude(names)`, `session.getBookmarkExclude()`
# * √ `session.bookmark_exclude: list[str]` value!
# * √ `session._get_bookmark_exclude()` & `session._bookmark_exclude_fn`
# Using a `.bookmark_exclude = []` and `._get_bookmark_exclude()` helper that accesses a `._bookmark_exclude_fns` list of functions which return scoped bookmark excluded values
# Enable bookmarking hooks:
# * √ `session.bookmark_store`: `url`, `server`, `disable`
# Session hooks -> `onBookmark()`, `onBookmarked()`, `onRestore(), `onRestored()`
# * √ `session.on_bookmark()` # Takes the save state
#     * Cancel callback
# * √ `session.on_bookmarked()` # Takes a url
#     * Cancel callback
# * `session.onRestore()`
# * `session.onRestored()`
# Session hooks -> Require list of callback functions for each
# * √ Session hooks -> Calling hooks in proper locations with info
# * √ Session hook -> Call bookmark "right now": `doBookmark()`
# * √ `session.do_bookmark()`
# Session updates -> Require updates for `SessionProxy` object
# * √ `doBookmark()` -> Update query string
# * √ Update query string

# bookmark -> restore state
# restore state -> {inputs, values}
# restore {inputs} -> Update all inputs given restored value

# Shinylive!
# Get query string from parent frame / tab
# * Ignore the code itself
# * May need to escape (all?) the parameters to avoid collisions with `h=` or `code=`.
# Set query string to parent frame / tab


if TYPE_CHECKING:
    from ..express._stub_session import ExpressStubSession
    from ..module import ResolvedId
    from ..session._session import AppSession, SessionProxy
    from . import RestoreContext
else:
    from typing import Any

    RestoreContext = Any
    SessionProxy = Any
    AppSession = Any
    ResolvedId = Any
    ExpressStubSession = Any


class Bookmark(ABC):

    _proxy_exclude_fns: list[Callable[[], list[str]]]
    """Callbacks that BookmarkProxy classes utilize to help determine the list of inputs to exclude from bookmarking."""
    exclude: list[str]
    """A list of scoped Input names to exclude from bookmarking."""

    _on_bookmark_callbacks: AsyncCallbacks
    _on_bookmarked_callbacks: AsyncCallbacks
    _on_restore_callbacks: AsyncCallbacks
    _on_restored_callbacks: AsyncCallbacks

    # Making this a read only property as app authors will not be able to change how the session is restored as the server function will run after the session has been restored.
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

    @abstractmethod
    def _set_restore_context(self, restore_context: RestoreContext):
        """
        Set the session's RestoreContext object.

        This should only be done within the `init` websocket message.
        """
        ...

    async def __call__(self) -> None:
        await self.do_bookmark()

    def __init__(self):

        super().__init__()

        self._proxy_exclude_fns = []
        self.exclude = []

        self._on_bookmark_callbacks = AsyncCallbacks()
        self._on_bookmarked_callbacks = AsyncCallbacks()
        self._on_restore_callbacks = AsyncCallbacks()
        self._on_restored_callbacks = AsyncCallbacks()

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

    @abstractmethod
    def _create_effects(self) -> None:
        """
        Create the effects for the bookmarking system.

        This method should be called when the session is created after the initial inputs have been set.
        """
        ...

    @abstractmethod
    def _get_bookmark_exclude(self) -> list[str]:
        """
        Retrieve the list of inputs excluded from being bookmarked.
        """
        ...

    @abstractmethod
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
        ...

    @abstractmethod
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
            The callback function to call when the session is bookmarked.
            This method should accept a single argument, the string representing the query parameter component of the URL.
        """
        ...

    @abstractmethod
    async def update_query_string(
        self,
        query_string: str,
        mode: Literal["replace", "push"] = "replace",
    ) -> None:
        """
        Update the query string of the current URL.

        Parameters
        ----------
        query_string
            The query string to set.
        mode
            Whether to replace the current URL or push a new one. Pushing a new value will add to the user's browser history.
        """
        ...

    @abstractmethod
    async def do_bookmark(self) -> None:
        """
        Perform bookmarking.

        This method will also call the `on_bookmark` and `on_bookmarked` callbacks to alter the bookmark state. Then, the bookmark state will be either saved to the server or encoded in the URL, depending on the `.store` option.

        No actions will be performed if the `.store` option is set to `"disable"`.

        Note: this method is called when `session.bookmark()` is executed.
        """
        ...

    @abstractmethod
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
        ...

    @abstractmethod
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
        ...


class BookmarkApp(Bookmark):
    _session: AppSession
    """
    The root session object (most likely a `AppSession` object).
    """
    _restore_context_value: RestoreContext
    """
    Placeholder value that should only be manually set within the session's `init` websocket message.
    """

    def __init__(self, session: AppSession):
        from ..session._session import AppSession

        assert isinstance(session, AppSession)
        super().__init__()

        self._session = session
        # self._restore_context_value = None

    # Making this a read only property as app authors will not be able to change how the session is restored as the server function will run after the session has been restored.
    @property
    def store(self) -> BookmarkStore:
        """
        App's bookmark store value

        Possible values:
        * `"url"`: Save / reload the bookmark state in the URL.
        * `"server"`: Save / reload the bookmark state on the server.
        * `"disable"` (default): Bookmarking is diabled.
        """

        return self._session.app.bookmark_store

    @property
    def _restore_context(self) -> RestoreContext | None:
        """
        A read-only value of the session's RestoreContext object.
        """
        return self._restore_context_value

    def _set_restore_context(self, restore_context: RestoreContext):
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

        session = self._session

        from .. import reactive
        from ..session import session_context
        from ..ui._notification import notification_show

        with session_context(session):

            # Fires when the bookmark button is clicked.
            @reactive.effect
            @reactive.event(session.input[BOOKMARK_ID])
            async def _():
                await session.bookmark()

            # If there was an error initializing the current restore context, show
            # notification in the client.
            @reactive.effect
            def init_error_message():
                if self._restore_context and self._restore_context._init_error_msg:
                    notification_show(
                        f"Error in RestoreContext initialization: {self._restore_context._init_error_msg}",
                        duration=None,
                        type="error",
                    )

            # Run the on_restore function at the beginning of the flush cycle, but after
            # the server function has been executed.
            @reactive.effect(priority=1000000)
            async def invoke_on_restore_callbacks():
                if self._on_restore_callbacks.count() == 0:
                    return

                with session_context(session):

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
            @session.on_flushed
            async def invoke_on_restored_callbacks():
                if self._on_restored_callbacks.count() == 0:
                    return

                with session_context(session):
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

    def _get_bookmark_exclude(self) -> list[str]:
        """
        Get the list of inputs excluded from being bookmarked.
        """

        scoped_excludes: list[str] = []
        for proxy_exclude_fn in self._proxy_exclude_fns:
            scoped_excludes.extend(proxy_exclude_fn())
        # Remove duplicates
        return list(set([*self.exclude, *scoped_excludes]))

    def on_bookmark(
        self,
        callback: (
            Callable[[BookmarkState], None] | Callable[[BookmarkState], Awaitable[None]]
        ),
        /,
    ) -> CancelCallback:
        return self._on_bookmark_callbacks.register(wrap_async(callback))

    def on_bookmarked(
        self,
        callback: Callable[[str], None] | Callable[[str], Awaitable[None]],
        /,
    ) -> CancelCallback:
        return self._on_bookmarked_callbacks.register(wrap_async(callback))

    def on_restore(
        self,
        callback: (
            Callable[[RestoreState], None] | Callable[[RestoreState], Awaitable[None]]
        ),
    ) -> CancelCallback:
        return self._on_restore_callbacks.register(wrap_async(callback))

    def on_restored(
        self,
        callback: (
            Callable[[RestoreState], None] | Callable[[RestoreState], Awaitable[None]]
        ),
    ) -> CancelCallback:
        return self._on_restored_callbacks.register(wrap_async(callback))

    async def update_query_string(
        self,
        query_string: str,
        mode: Literal["replace", "push"] = "replace",
    ) -> None:
        if mode not in {"replace", "push"}:
            raise ValueError(f"Invalid mode: {mode}")
        await self._session._send_message(
            {
                "updateQueryString": {
                    "queryString": query_string,
                    "mode": mode,
                }
            }
        )

    async def do_bookmark(self) -> None:

        if self.store == "disable":
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

        try:
            # ?withLogErrors
            from ..bookmark._bookmark import BookmarkState
            from ..session import session_context

            async def root_state_on_save(state: BookmarkState) -> None:
                with session_context(self._session):
                    await self._on_bookmark_callbacks.invoke(state)

            root_state = BookmarkState(
                input=self._session.input,
                exclude=self._get_bookmark_exclude(),
                on_save=root_state_on_save,
            )

            if self.store == "server":
                query_string = await root_state._save_state(app=self._session.app)
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

            clientdata = self._session.clientdata

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

            # If onBookmarked callback was provided, invoke it; if not call
            # the default.
            if self._on_bookmarked_callbacks.count() > 0:
                with session_context(self._session):
                    await self._on_bookmarked_callbacks.invoke(full_url)
            else:
                # `session.bookmark.show_modal(url)`

                # showBookmarkUrlModal(url)
                # This action feels weird. I don't believe it should occur
                # Instead, I believe it should update the query string automatically.
                # `session.bookmark.update_query_string(url)`
                raise NotImplementedError("Show bookmark modal not implemented")
        except Exception as e:
            msg = f"Error bookmarking state: {e}"
            from ..ui._notification import notification_show

            notification_show(msg, duration=None, type="error")


class BookmarkProxy(Bookmark):

    _ns: ResolvedId
    _session: SessionProxy

    def __init__(self, session_proxy: SessionProxy):
        from ..session._session import SessionProxy

        assert isinstance(session_proxy, SessionProxy)
        super().__init__()

        self._ns = session_proxy.ns
        self._session = session_proxy

        # TODO: Barret - This isn't getting to the root
        # Maybe `._get_bookmark_exclude()` should be used instead of`proxy_exclude_fns`?
        self._session._parent.bookmark._proxy_exclude_fns.append(
            lambda: [str(self._ns(name)) for name in self.exclude]
        )

        # When scope is created, register these bookmarking callbacks on the main
        # session object. They will invoke the scope's own callbacks, if any are
        # present.

        # The goal of this method is to save the scope's values. All namespaced inputs
        # will already exist within the `root_state`.
        @self._session._parent.bookmark.on_bookmark
        async def scoped_on_bookmark(root_state: BookmarkState) -> None:
            return await self._scoped_on_bookmark(root_state)

        from ..session import session_context

        @self._session._parent.bookmark.on_bookmarked
        async def scoped_on_bookmarked(url: str) -> None:
            if self._on_bookmarked_callbacks.count() == 0:
                return

            with session_context(self._session):
                await self._on_bookmarked_callbacks.invoke(url)

        ns_prefix = str(self._ns + self._ns._sep)

        @self._session._parent.bookmark.on_restore
        async def scoped_on_restore(restore_state: RestoreState) -> None:
            if self._on_restore_callbacks.count() == 0:
                return

            scoped_restore_state = restore_state._state_within_namespace(ns_prefix)

            with session_context(self._session):
                await self._on_restore_callbacks.invoke(scoped_restore_state)

        @self._session._parent.bookmark.on_restored
        async def scoped_on_restored(restore_state: RestoreState) -> None:
            if self._on_restored_callbacks.count() == 0:
                return

            scoped_restore_state = restore_state._state_within_namespace(ns_prefix)
            with session_context(self._session):
                await self._on_restored_callbacks.invoke(scoped_restore_state)

    async def _scoped_on_bookmark(self, root_state: BookmarkState) -> None:
        # Exit if no user-defined callbacks.
        if self._on_bookmark_callbacks.count() == 0:
            return

        from ..bookmark._bookmark import BookmarkState

        scoped_state = BookmarkState(
            input=self._session.input,
            exclude=self.exclude,
            on_save=None,
        )

        # Make subdir for scope
        # TODO: Barret; Is this for uploaded files?!?
        if root_state.dir is not None:
            scope_subpath = self._ns
            scoped_state.dir = Path(root_state.dir) / scope_subpath
            scoped_state.dir.mkdir(parents=True, exist_ok=True)

            if not scoped_state.dir.exists():
                raise FileNotFoundError(
                    f"Scope directory could not be created for {scope_subpath}"
                )

        # Invoke the callback on the scopeState object
        from ..session import session_context

        with session_context(self._session):
            await self._on_bookmark_callbacks.invoke(scoped_state)

        # Copy `values` from scoped_state to root_state (adding namespace)
        if scoped_state.values:
            for key, value in scoped_state.values.items():
                if key.strip() == "":
                    raise ValueError("All scope values must be named.")
                root_state.values[str(self._ns(key))] = value

    @property
    def store(self) -> BookmarkStore:
        return self._session._parent.bookmark.store

    @property
    def _restore_context(self) -> RestoreContext | None:
        return self._session._parent.bookmark._restore_context

    def _set_restore_context(self, restore_context: RestoreContext) -> NoReturn:
        raise NotImplementedError(
            "The `RestoreContext` should only be set on the root session object."
        )

    def _create_effects(self) -> NoReturn:
        raise NotImplementedError(
            "Please call `._create_effects()` from the root session only."
        )

    def on_bookmark(
        self,
        callback: (
            Callable[[BookmarkState], None] | Callable[[BookmarkState], Awaitable[None]]
        ),
        /,
    ) -> CancelCallback:
        return self._on_bookmark_callbacks.register(wrap_async(callback))

    def on_bookmarked(
        self,
        callback: Callable[[str], None] | Callable[[str], Awaitable[None]],
        /,
    ) -> CancelCallback:
        return self._on_bookmarked_callbacks.register(wrap_async(callback))

    def _get_bookmark_exclude(self) -> NoReturn:

        raise NotImplementedError(
            "Please call `._get_bookmark_exclude()` from the root session only."
        )

    async def update_query_string(
        self, query_string: str, mode: Literal["replace", "push"] = "replace"
    ) -> None:
        await self._session._parent.bookmark.update_query_string(query_string, mode)

    async def do_bookmark(self) -> None:
        await self._session._parent.bookmark.do_bookmark()

    def on_restore(
        self,
        callback: (
            Callable[[RestoreState], None] | Callable[[RestoreState], Awaitable[None]]
        ),
    ) -> CancelCallback:
        return self._on_restore_callbacks.register(wrap_async(callback))

    def on_restored(
        self,
        callback: (
            Callable[[RestoreState], None] | Callable[[RestoreState], Awaitable[None]]
        ),
    ) -> CancelCallback:
        return self._on_restored_callbacks.register(wrap_async(callback))


class BookmarkExpressStub(Bookmark):

    def __init__(self, session: ExpressStubSession) -> None:
        super().__init__()

        from ..express._stub_session import ExpressStubSession

        assert isinstance(session, ExpressStubSession)
        self._session = session

    @property
    def store(self) -> BookmarkStore:
        return "disable"

    @property
    def _restore_context(self) -> RestoreContext | None:
        return None

    def _set_restore_context(self, restore_context: RestoreContext) -> None:
        return None

    def _create_effects(self) -> NoReturn:
        raise NotImplementedError(
            "Please call `._create_effects()` only from a real session object"
        )

    def _get_bookmark_exclude(self) -> NoReturn:
        raise NotImplementedError(
            "Please call `._get_bookmark_exclude()` only from a real session object"
        )

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
        self, query_string: str, mode: Literal["replace", "push"] = "replace"
    ) -> None:
        return None

    async def do_bookmark(self) -> None:
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


# #' Generate a modal dialog that displays a URL
# #'
# #' The modal dialog generated by `urlModal` will display the URL in a
# #' textarea input, and the URL text will be selected so that it can be easily
# #' copied. The result from `urlModal` should be passed to the
# #' [showModal()] function to display it in the browser.
# #'
# #' @param url A URL to display in the dialog box.
# #' @param title A title for the dialog box.
# #' @param subtitle Text to display underneath URL.
# #' @export
# urlModal <- function(url, title = "Bookmarked application link", subtitle = NULL) {

#   subtitleTag <- tagList(
#     br(),
#     span(class = "text-muted", subtitle),
#     span(id = "shiny-bookmark-copy-text", class = "text-muted")
#   )

#   modalDialog(
#     title = title,
#     easyClose = TRUE,
#     tags$textarea(class = "form-control", rows = "1", style = "resize: none;",
#       readonly = "readonly",
#       url
#     ),
#     subtitleTag,
#     # Need separate show and shown listeners. The show listener sizes the
#     # textarea just as the modal starts to fade in. The 200ms delay is needed
#     # because if we try to resize earlier, it can't calculate the text height
#     # (scrollHeight will be reported as zero). The shown listener selects the
#     # text; it's needed because because selection has to be done after the fade-
#     # in is completed.
#     tags$script(
#       "$('#shiny-modal').
#         one('show.bs.modal', function() {
#           setTimeout(function() {
#             var $textarea = $('#shiny-modal textarea');
#             $textarea.innerHeight($textarea[0].scrollHeight);
#           }, 200);
#         });
#       $('#shiny-modal')
#         .one('shown.bs.modal', function() {
#           $('#shiny-modal textarea').select().focus();
#         });
#       $('#shiny-bookmark-copy-text')
#         .text(function() {
#           if (/Mac/i.test(navigator.userAgent)) {
#             return 'Press \u2318-C to copy.';
#           } else {
#             return 'Press Ctrl-C to copy.';
#           }
#         });
#       "
#     )
#   )
# }


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

# #' Enable bookmarking for a Shiny application
# #'
# #' @description
# #'
# #' There are two types of bookmarking: saving an application's state to disk on
# #' the server, and encoding the application's state in a URL. For state that has
# #' been saved to disk, the state can be restored with the corresponding state
# #' ID. For URL-encoded state, the state of the application is encoded in the
# #' URL, and no server-side storage is needed.
# #'
# #' URL-encoded bookmarking is appropriate for applications where there not many
# #' input values that need to be recorded. Some browsers have a length limit for
# #' URLs of about 2000 characters, and if there are many inputs, the length of
# #' the URL can exceed that limit.
# #'
# #' Saved-on-server bookmarking is appropriate when there are many inputs, or
# #' when the bookmarked state requires storing files.
# #'
# #' @details
# #'
# #' For restoring state to work properly, the UI must be a function that takes
# #' one argument, `request`. In most Shiny applications, the UI is not a
# #' function; it might have the form `fluidPage(....)`. Converting it to a
# #' function is as simple as wrapping it in a function, as in
# #' \code{function(request) \{ fluidPage(....) \}}.
# #'
# #' By default, all input values will be bookmarked, except for the values of
# #' passwordInputs. fileInputs will be saved if the state is saved on a server,
# #' but not if the state is encoded in a URL.
# #'
# #' When bookmarking state, arbitrary values can be stored, by passing a function
# #' as the `onBookmark` argument. That function will be passed a
# #' `ShinySaveState` object. The `values` field of the object is a list
# #' which can be manipulated to save extra information. Additionally, if the
# #' state is being saved on the server, and the `dir` field of that object
# #' can be used to save extra information to files in that directory.
# #'
# #' For saved-to-server state, this is how the state directory is chosen:
# #' \itemize{
# #'   \item If running in a hosting environment such as Shiny Server or
# #'     Connect, the hosting environment will choose the directory.
# #'   \item If running an app in a directory with [runApp()], the
# #'     saved states will be saved in a subdirectory of the app called
# #'    shiny_bookmarks.
# #'   \item If running a Shiny app object that is generated from code (not run
# #'     from a directory), the saved states will be saved in a subdirectory of
# #'     the current working directory called shiny_bookmarks.
# #' }
# #'
# #' When used with [shinyApp()], this function must be called before
# #' `shinyApp()`, or in the `shinyApp()`'s `onStart` function. An
# #' alternative to calling the `enableBookmarking()` function is to use the
# #' `enableBookmarking` *argument* for `shinyApp()`. See examples
# #' below.
# #'
# #' @param store Either `"url"`, which encodes all of the relevant values in
# #'   a URL, `"server"`, which saves to disk on the server, or
# #'   `"disable"`, which disables any previously-enabled bookmarking.
# #'
# #' @seealso [onBookmark()], [onBookmarked()],
# #'   [onRestore()], and [onRestored()] for registering
# #'   callback functions that are invoked when the state is bookmarked or
# #'   restored.
# #'
# #'   Also see [updateQueryString()].
# #'
# #' @export
# #' @examples
# #' ## Only run these examples in interactive R sessions
# #' if (interactive()) {
# #'
# #' # Basic example with state encoded in URL
# #' ui <- function(request) {
# #'   fluidPage(
# #'     textInput("txt", "Text"),
# #'     checkboxInput("chk", "Checkbox"),
# #'     bookmarkButton()
# #'   )
# #' }
# #' server <- function(input, output, session) { }
# #' enableBookmarking("url")
# #' shinyApp(ui, server)
# #'
# #'
# #' # An alternative to calling enableBookmarking(): use shinyApp's
# #' # enableBookmarking argument
# #' shinyApp(ui, server, enableBookmarking = "url")
# #'
# #'
# #' # Same basic example with state saved to disk
# #' enableBookmarking("server")
# #' shinyApp(ui, server)
# #'
# #'
# #' # Save/restore arbitrary values
# #' ui <- function(req) {
# #'   fluidPage(
# #'     textInput("txt", "Text"),
# #'     checkboxInput("chk", "Checkbox"),
# #'     bookmarkButton(),
# #'     br(),
# #'     textOutput("lastSaved")
# #'   )
# #' }
# #' server <- function(input, output, session) {
# #'   vals <- reactiveValues(savedTime = NULL)
# #'   output$lastSaved <- renderText({
# #'     if (!is.null(vals$savedTime))
# #'       paste("Last saved at", vals$savedTime)
# #'     else
# #'       ""
# #'   })
# #'
# #'   onBookmark(function(state) {
# #'     vals$savedTime <- Sys.time()
# #'     # state is a mutable reference object, and we can add arbitrary values
# #'     # to it.
# #'     state$values$time <- vals$savedTime
# #'   })
# #'   onRestore(function(state) {
# #'     vals$savedTime <- state$values$time
# #'   })
# #' }
# #' enableBookmarking(store = "url")
# #' shinyApp(ui, server)
# #'
# #'
# #' # Usable with dynamic UI (set the slider, then change the text input,
# #' # click the bookmark button)
# #' ui <- function(request) {
# #'   fluidPage(
# #'     sliderInput("slider", "Slider", 1, 100, 50),
# #'     uiOutput("ui"),
# #'     bookmarkButton()
# #'   )
# #' }
# #' server <- function(input, output, session) {
# #'   output$ui <- renderUI({
# #'     textInput("txt", "Text", input$slider)
# #'   })
# #' }
# #' enableBookmarking("url")
# #' shinyApp(ui, server)
# #'
# #'
# #' # Exclude specific inputs (The only input that will be saved in this
# #' # example is chk)
# #' ui <- function(request) {
# #'   fluidPage(
# #'     passwordInput("pw", "Password"), # Passwords are never saved
# #'     sliderInput("slider", "Slider", 1, 100, 50), # Manually excluded below
# #'     checkboxInput("chk", "Checkbox"),
# #'     bookmarkButton()
# #'   )
# #' }
# #' server <- function(input, output, session) {
# #'   setBookmarkExclude("slider")
# #' }
# #' enableBookmarking("url")
# #' shinyApp(ui, server)
# #'
# #'
# #' # Update the browser's location bar every time an input changes. This should
# #' # not be used with enableBookmarking("server"), because that would create a
# #' # new saved state on disk every time the user changes an input.
# #' ui <- function(req) {
# #'   fluidPage(
# #'     textInput("txt", "Text"),
# #'     checkboxInput("chk", "Checkbox")
# #'   )
# #' }
# #' server <- function(input, output, session) {
# #'   observe({
# #'     # Trigger this observer every time an input changes
# #'     reactiveValuesToList(input)
# #'     session$doBookmark()
# #'   })
# #'   onBookmarked(function(url) {
# #'     updateQueryString(url)
# #'   })
# #' }
# #' enableBookmarking("url")
# #' shinyApp(ui, server)
# #'
# #'
# #' # Save/restore uploaded files
# #' ui <- function(request) {
# #'   fluidPage(
# #'     sidebarLayout(
# #'       sidebarPanel(
# #'         fileInput("file1", "Choose CSV File", multiple = TRUE,
# #'           accept = c(
# #'             "text/csv",
# #'             "text/comma-separated-values,text/plain",
# #'             ".csv"
# #'           )
# #'         ),
# #'         tags$hr(),
# #'         checkboxInput("header", "Header", TRUE),
# #'         bookmarkButton()
# #'       ),
# #'       mainPanel(
# #'         tableOutput("contents")
# #'       )
# #'     )
# #'   )
# #' }
# #' server <- function(input, output) {
# #'   output$contents <- renderTable({
# #'     inFile <- input$file1
# #'     if (is.null(inFile))
# #'       return(NULL)
# #'
# #'     if (nrow(inFile) == 1) {
# #'       read.csv(inFile$datapath, header = input$header)
# #'     } else {
# #'       data.frame(x = "multiple files")
# #'     }
# #'   })
# #' }
# #' enableBookmarking("server")
# #' shinyApp(ui, server)
# #'
# #' }
# enableBookmarking <- function(store = c("url", "server", "disable")) {
#   store <- match.arg(store)
#   shinyOptions(bookmarkStore = store)
# }
