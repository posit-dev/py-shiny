# TODO: bookmark button

# TODO:
# bookmark -> save/load interface
# * √ base class
# * √ local
# save/load interface -> register interface
# * implement; Q on approach!
# register interface -> Make interface for Connect
# * implement in Connect PR
# bookmark -> save state
# save state -> {inputs, values, exclude}
# {inputs} -> custom serializer
# √ Hook to `Inputs.set_serializer(id, fn)`
# √ `Inputs._serialize()` to create a dict
# {values} -> dict (where as in R is an environment)
# √ values is a dict!
# {exclude} -> Requires `session.setBookmarkExclude(names)`, `session.getBookmarkExclude()`
# √ `session.bookmark_exclude: list[str]` value!
# √ `session._get_bookmark_exclude()` & `session._bookmark_exclude_fn`
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

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Awaitable, Callable, Literal, NoReturn

from .._utils import AsyncCallbacks, CancelCallback, wrap_async
from ._restore_state import RestoreContextState
from ._save_state import ShinySaveState

if TYPE_CHECKING:
    from .._namespaces import ResolvedId
    from ..express._stub_session import ExpressStubSession
    from ..session import Session
    from ..session._session import SessionProxy
    from ._restore_state import RestoreContext
else:
    from typing import Any

    RestoreContext = Any
    Session = Any
    SessionProxy = Any
    ResolvedId = Any
    ExpressStubSession = Any


BookmarkStore = Literal["url", "server", "disable"]


# TODO: future - Local storage Bookmark class!
# * Needs a consistent id for storage.
# * Needs ways to clean up other storage
# * Needs ways to see available IDs


class Bookmark(ABC):

    # TODO: Barret - This feels like it needs to be a weakref
    _session_root: Session

    store: BookmarkStore

    _proxy_exclude_fns: list[Callable[[], list[str]]]
    exclude: list[str]

    _on_bookmark_callbacks: AsyncCallbacks
    _on_bookmarked_callbacks: AsyncCallbacks
    _on_restore_callbacks: AsyncCallbacks
    _on_restored_callbacks: AsyncCallbacks

    _restore_context: RestoreContext | None

    async def __call__(self) -> None:
        await self._root_bookmark.do_bookmark()

    @property
    def _root_bookmark(self) -> "Bookmark":
        return self._session_root.bookmark

    def __init__(self, session_root: Session):
        # from ._restore_state import RestoreContext

        super().__init__()
        self._session_root = session_root
        self._restore_context = None

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
            Callable[[ShinySaveState], None]
            | Callable[[ShinySaveState], Awaitable[None]]
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
    # TODO: Barret - Q: Rename to `update()`? `session.bookmark.update()`?
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
            Callable[[RestoreContextState], None]
            | Callable[[RestoreContextState], Awaitable[None]]
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
            Callable[[RestoreContextState], None]
            | Callable[[RestoreContextState], Awaitable[None]]
        ),
    ) -> CancelCallback:
        """
        Registers a function that will be called just after restoring state.

        This callback will be executed **after** the bookmark state is restored.
        """
        ...


class BookmarkApp(Bookmark):
    def __init__(self, session_root: Session):

        super().__init__(session_root)

        self.store = "disable"
        self.store = "url"
        self.exclude = []
        self._proxy_exclude_fns = []
        self._on_bookmark_callbacks = AsyncCallbacks()
        self._on_bookmarked_callbacks = AsyncCallbacks()
        self._on_restore_callbacks = AsyncCallbacks()
        self._on_restored_callbacks = AsyncCallbacks()

    def _create_effects(self) -> None:
        # Get bookmarking config
        if self.store == "disable":
            return

        print("Creating effects")

        session = self._session_root

        from .. import reactive
        from ..session import session_context
        from ..ui._notification import notification_show

        with session_context(session):

            # Fires when the bookmark button is clicked.
            @reactive.effect
            @reactive.event(session.input["._bookmark_"])
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
                print("Trying on restore")
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
                        raise e
                        print(f"Error calling on_restore callback: {e}")
                        notification_show(
                            f"Error calling on_restore callback: {e}",
                            duration=None,
                            type="error",
                        )

            # Run the on_restored function after the flush cycle completes and
            # information is sent to the client.
            @session.on_flushed
            async def invoke_on_restored_callbacks():
                print("Trying on restored")
                if self._on_restored_callbacks.count() == 0:
                    return

                with session_context(session):
                    try:
                        with reactive.isolate():
                            if self._restore_context and self._restore_context.active:
                                restore_state = self._restore_context.as_state()
                                await self._on_restored_callbacks.invoke(restore_state)
                    except Exception as e:
                        print(f"Error calling on_restored callback: {e}")
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
            Callable[[ShinySaveState], None]
            | Callable[[ShinySaveState], Awaitable[None]]
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
            Callable[[RestoreContextState], None]
            | Callable[[RestoreContextState], Awaitable[None]]
        ),
    ) -> CancelCallback:
        return self._on_restore_callbacks.register(wrap_async(callback))

    def on_restored(
        self,
        callback: (
            Callable[[RestoreContextState], None]
            | Callable[[RestoreContextState], Awaitable[None]]
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
        await self._session_root._send_message(
            {
                "updateQueryString": {
                    "queryString": query_string,
                    "mode": mode,
                }
            }
        )

    async def do_bookmark(self) -> None:

        if self.store == "disable":
            return

        try:
            # ?withLogErrors
            from ..bookmark._bookmark import ShinySaveState
            from ..session import session_context

            async def root_state_on_save(state: ShinySaveState) -> None:
                with session_context(self._session_root):
                    await self._on_bookmark_callbacks.invoke(state)

            root_state = ShinySaveState(
                input=self._session_root.input,
                exclude=self._get_bookmark_exclude(),
                on_save=root_state_on_save,
            )

            if self.store == "server":
                query_string = await root_state._save_state()
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

            clientdata = self._session_root.clientdata

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
                with session_context(self._session_root):
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
            # TODO: Barret - Remove this!
            raise RuntimeError("Error bookmarking state") from e


class BookmarkProxy(Bookmark):

    _ns: ResolvedId

    def __init__(self, session_proxy: SessionProxy):
        super().__init__(session_proxy.root_scope())

        self._ns = session_proxy.ns
        # TODO: Barret - This feels like it needs to be a weakref
        self._session_proxy = session_proxy

        self.exclude = []
        self._proxy_exclude_fns = []
        self._on_bookmark_callbacks = AsyncCallbacks()
        self._on_bookmarked_callbacks = AsyncCallbacks()
        self._on_restore_callbacks = AsyncCallbacks()
        self._on_restored_callbacks = AsyncCallbacks()

        # TODO: Barret - Double check that this works with nested modules!
        self._session_root.bookmark._proxy_exclude_fns.append(
            lambda: [str(self._ns(name)) for name in self.exclude]
        )

        # When scope is created, register these bookmarking callbacks on the main
        # session object. They will invoke the scope's own callbacks, if any are
        # present.

        # The goal of this method is to save the scope's values. All namespaced inputs
        # will already exist within the `root_state`.
        @self._root_bookmark.on_bookmark
        async def scoped_on_bookmark(root_state: ShinySaveState) -> None:
            return await self._scoped_on_bookmark(root_state)

        from ..session import session_context

        ns_prefix = str(self._ns + self._ns._sep)

        @self._root_bookmark.on_restore
        async def scoped_on_restore(restore_state: RestoreContextState) -> None:
            if self._on_restore_callbacks.count() == 0:
                return

            scoped_restore_state = restore_state._state_within_namespace(ns_prefix)

            with session_context(self._session_proxy):
                await self._on_restore_callbacks.invoke(scoped_restore_state)

        @self._root_bookmark.on_restored
        async def scoped_on_restored(restore_state: RestoreContextState) -> None:
            if self._on_restored_callbacks.count() == 0:
                return

            scoped_restore_state = restore_state._state_within_namespace(ns_prefix)
            with session_context(self._session_proxy):
                await self._on_restored_callbacks.invoke(scoped_restore_state)

    async def _scoped_on_bookmark(self, root_state: ShinySaveState) -> None:
        # Exit if no user-defined callbacks.
        if self._on_bookmark_callbacks.count() == 0:
            return

        from ..bookmark._bookmark import ShinySaveState

        scoped_state = ShinySaveState(
            input=self._session_root.input,
            exclude=self._root_bookmark.exclude,
            on_save=None,
        )

        # Make subdir for scope
        if root_state.dir is not None:
            scope_subpath = self._ns
            scoped_state.dir = Path(root_state.dir) / scope_subpath
            if not scoped_state.dir.exists():
                raise FileNotFoundError(
                    f"Scope directory could not be created for {scope_subpath}"
                )

        # Invoke the callback on the scopeState object
        from ..session import session_context

        with session_context(self._session_proxy):
            await self._on_bookmark_callbacks.invoke(scoped_state)

        # Copy `values` from scoped_state to root_state (adding namespace)
        if scoped_state.values:
            for key, value in scoped_state.values.items():
                if key.strip() == "":
                    raise ValueError("All scope values must be named.")
                root_state.values[str(self._ns(key))] = value

    def _create_effects(self) -> NoReturn:
        raise NotImplementedError(
            "Please call `._create_effects()` from the root session only."
        )

    def on_bookmark(
        self,
        callback: (
            Callable[[ShinySaveState], None]
            | Callable[[ShinySaveState], Awaitable[None]]
        ),
        /,
    ) -> CancelCallback:
        return self._on_bookmark_callbacks.register(wrap_async(callback))

    def on_bookmarked(
        self,
        callback: Callable[[str], None] | Callable[[str], Awaitable[None]],
        /,
    ) -> NoReturn:
        # TODO: Barret - Q: Shouldn't we implement this? `self._root_bookmark.on_bookmark()`
        raise NotImplementedError(
            "Please call `.on_bookmarked()` from the root session only, e.g. `session.root_scope().bookmark.on_bookmark()`."
        )

    def _get_bookmark_exclude(self) -> NoReturn:
        raise NotImplementedError(
            "Please call `._get_bookmark_exclude()` from the root session only."
        )

    async def update_query_string(
        self, query_string: str, mode: Literal["replace", "push"] = "replace"
    ) -> None:
        await self._root_bookmark.update_query_string(query_string, mode)

    async def do_bookmark(self) -> None:
        await self._root_bookmark.do_bookmark()

    @property
    def store(self) -> BookmarkStore:
        return self._root_bookmark.store

    @store.setter
    def store(  # pyright: ignore[reportIncompatibleVariableOverride]
        self,
        value: BookmarkStore,
    ) -> None:
        self._root_bookmark.store = value

    def on_restore(
        self,
        callback: (
            Callable[[RestoreContextState], None]
            | Callable[[RestoreContextState], Awaitable[None]]
        ),
    ) -> CancelCallback:
        return self._on_restore_callbacks.register(wrap_async(callback))

    def on_restored(
        self,
        callback: (
            Callable[[RestoreContextState], None]
            | Callable[[RestoreContextState], Awaitable[None]]
        ),
    ) -> CancelCallback:
        return self._on_restored_callbacks.register(wrap_async(callback))


class BookmarkExpressStub(Bookmark):

    def __init__(self, session_root: ExpressStubSession) -> None:
        super().__init__(session_root)
        self._proxy_exclude_fns = []
        self._on_bookmark_callbacks = AsyncCallbacks()
        self._on_bookmarked_callbacks = AsyncCallbacks()
        self._on_restore_callbacks = AsyncCallbacks()
        self._on_restored_callbacks = AsyncCallbacks()

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
            Callable[[ShinySaveState], None]
            | Callable[[ShinySaveState], Awaitable[None]]
        ),
    ) -> NoReturn:
        raise NotImplementedError(
            "Please call `.on_bookmark()` only from a real session object"
        )

    def on_bookmarked(
        self,
        callback: Callable[[str], None] | Callable[[str], Awaitable[None]],
    ) -> NoReturn:
        raise NotImplementedError(
            "Please call `.on_bookmarked()` only from a real session object"
        )

    async def update_query_string(
        self, query_string: str, mode: Literal["replace", "push"] = "replace"
    ) -> NoReturn:
        raise NotImplementedError(
            "Please call `.update_query_string()` only from a real session object"
        )

    async def do_bookmark(self) -> NoReturn:
        raise NotImplementedError(
            "Please call `.do_bookmark()` only from a real session object"
        )

    def on_restore(
        self,
        callback: (
            Callable[[RestoreContextState], None]
            | Callable[[RestoreContextState], Awaitable[None]]
        ),
    ) -> NoReturn:
        raise NotImplementedError(
            "Please call `.on_restore()` only from a real session object"
        )

    def on_restored(
        self,
        callback: (
            Callable[[RestoreContextState], None]
            | Callable[[RestoreContextState], Awaitable[None]]
        ),
    ) -> NoReturn:
        raise NotImplementedError(
            "Please call `.on_restored()` only from a real session object"
        )


# #' Update URL in browser's location bar
# #'
# #' This function updates the client browser's query string in the location bar.
# #' It typically is called from an observer. Note that this will not work in
# #' Internet Explorer 9 and below.
# #'
# #' For `mode = "push"`, only three updates are currently allowed:
# #' \enumerate{
# #'   \item the query string (format: `?param1=val1&param2=val2`)
# #'   \item the hash (format: `#hash`)
# #'   \item both the query string and the hash
# #'     (format: `?param1=val1&param2=val2#hash`)
# #' }
# #'
# #' In other words, if `mode = "push"`, the `queryString` must start
# #' with either `?` or with `#`.
# #'
# #' A technical curiosity: under the hood, this function is calling the HTML5
# #' history API (which is where the names for the `mode` argument come from).
# #' When `mode = "replace"`, the function called is
# #' `window.history.replaceState(null, null, queryString)`.
# #' When `mode = "push"`, the function called is
# #' `window.history.pushState(null, null, queryString)`.
# #'
# #' @param queryString The new query string to show in the location bar.
# #' @param mode When the query string is updated, should the current history
# #'   entry be replaced (default), or should a new history entry be pushed onto
# #'   the history stack? The former should only be used in a live bookmarking
# #'   context. The latter is useful if you want to navigate between states using
# #'   the browser's back and forward buttons. See Examples.
# #' @param session A Shiny session object.
# #' @seealso [enableBookmarking()], [getQueryString()]
# #' @examples
# #' ## Only run these examples in interactive sessions
# #' if (interactive()) {
# #'
# #'   ## App 1: Doing "live" bookmarking
# #'   ## Update the browser's location bar every time an input changes.
# #'   ## This should not be used with enableBookmarking("server"),
# #'   ## because that would create a new saved state on disk every time
# #'   ## the user changes an input.
# #'   enableBookmarking("url")
# #'   shinyApp(
# #'     ui = function(req) {
# #'       fluidPage(
# #'         textInput("txt", "Text"),
# #'         checkboxInput("chk", "Checkbox")
# #'       )
# #'     },
# #'     server = function(input, output, session) {
# #'       observe({
# #'         # Trigger this observer every time an input changes
# #'         reactiveValuesToList(input)
# #'         session$doBookmark()
# #'       })
# #'       onBookmarked(function(url) {
# #'         updateQueryString(url)
# #'       })
# #'     }
# #'   )
# #'
# #'   ## App 2: Printing the value of the query string
# #'   ## (Use the back and forward buttons to see how the browser
# #'   ## keeps a record of each state)
# #'   shinyApp(
# #'     ui = fluidPage(
# #'       textInput("txt", "Enter new query string"),
# #'       helpText("Format: ?param1=val1&param2=val2"),
# #'       actionButton("go", "Update"),
# #'       hr(),
# #'       verbatimTextOutput("query")
# #'     ),
# #'     server = function(input, output, session) {
# #'       observeEvent(input$go, {
# #'         updateQueryString(input$txt, mode = "push")
# #'       })
# #'       output$query <- renderText({
# #'         query <- getQueryString()
# #'         queryText <- paste(names(query), query,
# #'                        sep = "=", collapse=", ")
# #'         paste("Your query string is:\n", queryText)
# #'       })
# #'     }
# #'   )
# #' }
# #' @export
# updateQueryString <- function(queryString, mode = c("replace", "push"),
#                               session = getDefaultReactiveDomain()) {
#   mode <- match.arg(mode)
#   session$updateQueryString(queryString, mode)
# }

# #' Create a button for bookmarking/sharing
# #'
# #' A `bookmarkButton` is a [actionButton()] with a default label
# #' that consists of a link icon and the text "Bookmark...". It is meant to be
# #' used for bookmarking state.
# #'
# #' @inheritParams actionButton
# #' @param title A tooltip that is shown when the mouse cursor hovers over the
# #'   button.
# #' @param id An ID for the bookmark button. The only time it is necessary to set
# #'   the ID unless you have more than one bookmark button in your application.
# #'   If you specify an input ID, it should be excluded from bookmarking with
# #'   [setBookmarkExclude()], and you must create an observer that
# #'   does the bookmarking when the button is pressed. See the examples below.
# #'
# #' @seealso [enableBookmarking()] for more examples.
# #'
# #' @examples
# #' ## Only run these examples in interactive sessions
# #' if (interactive()) {
# #'
# #' # This example shows how to use multiple bookmark buttons. If you only need
# #' # a single bookmark button, see examples in ?enableBookmarking.
# #' ui <- function(request) {
# #'   fluidPage(
# #'     tabsetPanel(id = "tabs",
# #'       tabPanel("One",
# #'         checkboxInput("chk1", "Checkbox 1"),
# #'         bookmarkButton(id = "bookmark1")
# #'       ),
# #'       tabPanel("Two",
# #'         checkboxInput("chk2", "Checkbox 2"),
# #'         bookmarkButton(id = "bookmark2")
# #'       )
# #'     )
# #'   )
# #' }
# #' server <- function(input, output, session) {
# #'   # Need to exclude the buttons from themselves being bookmarked
# #'   setBookmarkExclude(c("bookmark1", "bookmark2"))
# #'
# #'   # Trigger bookmarking with either button
# #'   observeEvent(input$bookmark1, {
# #'     session$doBookmark()
# #'   })
# #'   observeEvent(input$bookmark2, {
# #'     session$doBookmark()
# #'   })
# #' }
# #' enableBookmarking(store = "url")
# #' shinyApp(ui, server)
# #' }
# #' @export
# bookmarkButton <- function(label = "Bookmark...",
#   icon = shiny::icon("link", lib = "glyphicon"),
#   title = "Bookmark this application's state and get a URL for sharing.",
#   ...,
#   id = "._bookmark_")
# {
#   actionButton(id, label, icon, title = title, ...)
# }


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


# #' Exclude inputs from bookmarking
# #'
# #' This function tells Shiny which inputs should be excluded from bookmarking.
# #' It should be called from inside the application's server function.
# #'
# #' This function can also be called from a module's server function, in which
# #' case it will exclude inputs with the specified names, from that module. It
# #' will not affect inputs from other modules or from the top level of the Shiny
# #' application.
# #'
# #' @param names A character vector containing names of inputs to exclude from
# #'   bookmarking.
# #' @param session A shiny session object.
# #' @seealso [enableBookmarking()] for examples.
# #' @export
# setBookmarkExclude <- function(names = character(0), session = getDefaultReactiveDomain()) {
#   session$setBookmarkExclude(names)
# }


# #' Add callbacks for Shiny session bookmarking events
# #'
# #' @description
# #'
# #' These functions are for registering callbacks on Shiny session events. They
# #' should be called within an application's server function.
# #'
# #' \itemize{
# #'   \item `onBookmark` registers a function that will be called just
# #'     before Shiny bookmarks state.
# #'   \item `onBookmarked` registers a function that will be called just
# #'     after Shiny bookmarks state.
# #'   \item `onRestore` registers a function that will be called when a
# #'     session is restored, after the server function executes, but before all
# #'     other reactives, observers and render functions are run.
# #'   \item `onRestored` registers a function that will be called after a
# #'     session is restored. This is similar to `onRestore`, but it will be
# #'     called after all reactives, observers, and render functions run, and
# #'     after results are sent to the client browser. `onRestored`
# #'     callbacks can be useful for sending update messages to the client
# #'     browser.
# #' }
# #'
# #' @details
# #'
# #' All of these functions return a function which can be called with no
# #' arguments to cancel the registration.
# #'
# #' The callback function that is passed to these functions should take one
# #' argument, typically named "state" (for `onBookmark`, `onRestore`,
# #' and `onRestored`) or "url" (for `onBookmarked`).
# #'
# #' For `onBookmark`, the state object has three relevant fields. The
# #' `values` field is an environment which can be used to save arbitrary
# #' values (see examples). If the state is being saved to disk (as opposed to
# #' being encoded in a URL), the `dir` field contains the name of a
# #' directory which can be used to store extra files. Finally, the state object
# #' has an `input` field, which is simply the application's `input`
# #' object. It can be read, but not modified.
# #'
# #' For `onRestore` and `onRestored`, the state object is a list. This
# #' list contains `input`, which is a named list of input values to restore,
# #' `values`, which is an environment containing arbitrary values that were
# #' saved in `onBookmark`, and `dir`, the name of the directory that
# #' the state is being restored from, and which could have been used to save
# #' extra files.
# #'
# #' For `onBookmarked`, the callback function receives a string with the
# #' bookmark URL. This callback function should be used to display UI in the
# #' client browser with the bookmark URL. If no callback function is registered,
# #' then Shiny will by default display a modal dialog with the bookmark URL.
# #'
# #' @section Modules:
# #'
# #'   These callbacks may also be used in Shiny modules. When used this way, the
# #'   inputs and values will automatically be namespaced for the module, and the
# #'   callback functions registered for the module will only be able to see the
# #'   module's inputs and values.
# #'
# #' @param fun A callback function which takes one argument.
# #' @param session A shiny session object.
# #' @seealso enableBookmarking for general information on bookmarking.
# #'
# #' @examples
# #' ## Only run these examples in interactive sessions
# #' if (interactive()) {
# #'
# #' # Basic use of onBookmark and onRestore: This app saves the time in its
# #' # arbitrary values, and restores that time when the app is restored.
# #' ui <- function(req) {
# #'   fluidPage(
# #'     textInput("txt", "Input text"),
# #'     bookmarkButton()
# #'   )
# #' }
# #' server <- function(input, output) {
# #'   onBookmark(function(state) {
# #'     savedTime <- as.character(Sys.time())
# #'     cat("Last saved at", savedTime, "\n")
# #'     # state is a mutable reference object, and we can add arbitrary values to
# #'     # it.
# #'     state$values$time <- savedTime
# #'   })
# #'
# #'   onRestore(function(state) {
# #'     cat("Restoring from state bookmarked at", state$values$time, "\n")
# #'   })
# #' }
# #' enableBookmarking("url")
# #' shinyApp(ui, server)
# #'
# #'
# #'
# # This app illustrates two things: saving values in a file using state$dir, and
# # using an onRestored callback to call an input updater function. (In real use
# # cases, it probably makes sense to save content to a file only if it's much
# # larger.)
# #' ui <- function(req) {
# #'   fluidPage(
# #'     textInput("txt", "Input text"),
# #'     bookmarkButton()
# #'   )
# #' }
# #' server <- function(input, output, session) {
# #'   lastUpdateTime <- NULL
# #'
# #'   observeEvent(input$txt, {
# #'     updateTextInput(session, "txt",
# #'       label = paste0("Input text (Changed ", as.character(Sys.time()), ")")
# #'     )
# #'   })
# #'
# #'   onBookmark(function(state) {
# #'     # Save content to a file
# #'     messageFile <- file.path(state$dir, "message.txt")
# #'     cat(as.character(Sys.time()), file = messageFile)
# #'   })
# #'
# #'   onRestored(function(state) {
# #'     # Read the file
# #'     messageFile <- file.path(state$dir, "message.txt")
# #'     timeText <- readChar(messageFile, 1000)
# #'
# #'     # updateTextInput must be called in onRestored, as opposed to onRestore,
# #'     # because onRestored happens after the client browser is ready.
# #'     updateTextInput(session, "txt",
# #'       label = paste0("Input text (Changed ", timeText, ")")
# #'     )
# #'   })
# #' }
# #' # "server" bookmarking is needed for writing to disk.
# #' enableBookmarking("server")
# #' shinyApp(ui, server)
# #'
# #'
# #' # This app has a module, and both the module and the main app code have
# #' # onBookmark and onRestore functions which write and read state$values$hash. The
# #' # module's version of state$values$hash does not conflict with the app's version
# #' # of state$values$hash.
# #' #
# #' # A basic module that captializes text.
# #' capitalizerUI <- function(id) {
# #'   ns <- NS(id)
# #'   wellPanel(
# #'     h4("Text captializer module"),
# #'     textInput(ns("text"), "Enter text:"),
# #'     verbatimTextOutput(ns("out"))
# #'   )
# #' }
# #' capitalizerServer <- function(input, output, session) {
# #'   output$out <- renderText({
# #'     toupper(input$text)
# #'   })
# #'   onBookmark(function(state) {
# #'     state$values$hash <- rlang::hash(input$text)
# #'   })
# #'   onRestore(function(state) {
# #'     if (identical(rlang::hash(input$text), state$values$hash)) {
# #'       message("Module's input text matches hash ", state$values$hash)
# #'     } else {
# #'       message("Module's input text does not match hash ", state$values$hash)
# #'     }
# #'   })
# #' }
# #' # Main app code
# #' ui <- function(request) {
# #'   fluidPage(
# #'     sidebarLayout(
# #'       sidebarPanel(
# #'         capitalizerUI("tc"),
# #'         textInput("text", "Enter text (not in module):"),
# #'         bookmarkButton()
# #'       ),
# #'       mainPanel()
# #'     )
# #'   )
# #' }
# #' server <- function(input, output, session) {
# #'   callModule(capitalizerServer, "tc")
# #'   onBookmark(function(state) {
# #'     state$values$hash <- rlang::hash(input$text)
# #'   })
# #'   onRestore(function(state) {
# #'     if (identical(rlang::hash(input$text), state$values$hash)) {
# #'       message("App's input text matches hash ", state$values$hash)
# #'     } else {
# #'       message("App's input text does not match hash ", state$values$hash)
# #'     }
# #'   })
# #' }
# #' enableBookmarking(store = "url")
# #' shinyApp(ui, server)
# #' }
# #' @export
# onBookmark <- function(fun, session = getDefaultReactiveDomain()) {
#   session$onBookmark(fun)
# }

# #' @rdname onBookmark
# #' @export
# onBookmarked <- function(fun, session = getDefaultReactiveDomain()) {
#   session$onBookmarked(fun)
# }

# #' @rdname onBookmark
# #' @export
# onRestore <- function(fun, session = getDefaultReactiveDomain()) {
#   session$onRestore(fun)
# }

# #' @rdname onBookmark
# #' @export
# onRestored <- function(fun, session = getDefaultReactiveDomain()) {
#   session$onRestored(fun)
# }
# }
