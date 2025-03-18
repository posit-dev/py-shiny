from __future__ import annotations

from typing import TYPE_CHECKING, Awaitable, Callable, Literal, Optional

from htmltools import TagChild

from .._namespaces import Id, Root
from ..bookmark import BookmarkExpressStub
from ..module import ResolvedId
from ..session import Inputs, Outputs, Session
from ..session._session import SessionProxy

if TYPE_CHECKING:
    from ..session._session import DownloadHandler, DynamicRouteHandler, RenderedDeps
    from ..types import Jsonifiable
    from ._run import AppOpts

all = ("ExpressStubSession",)


class ExpressStubSession(Session):
    """
    A very bare-bones stub session class that is used only in shiny.express's UI
    rendering phase.

    Note that this class is also used to hold application-level options that are set via
    the `app_opts()` function.
    """

    def __init__(self, ns: ResolvedId = Root):
        self.ns = ns
        # Setting self.app to None works for our uses, though in the future it may be
        # necessary to also create a ExpressStubApp class to be a placeholder.
        self.app = None  # pyright: ignore
        self.id = "express_stub_session"
        self.input = Inputs({})
        self.output = Outputs(self, self.ns, outputs={})

        # Set these values to None just to satisfy the abstract base class to make this
        # code run -- these things should not be used at run time, so None will work as
        # a placeholder. But we also need to tell pyright to ignore that the Nones don't
        # match the type declared in the Session abstract base class.
        self._outbound_message_queues = None  # pyright: ignore
        self._downloads = None  # pyright: ignore

        # Application-level (not session-level) options that may be set via app_opts().
        self.app_opts: AppOpts = {}

        self.bookmark = BookmarkExpressStub(self)

    def is_stub_session(self) -> Literal[True]:
        return True

    async def close(self, code: int = 1001) -> None:
        return

    # This is needed so that Outputs don't throw an error.
    def _is_hidden(self, name: str) -> bool:
        return False

    def on_ended(
        self,
        fn: Callable[[], None] | Callable[[], Awaitable[None]],
    ) -> Callable[[], None]:
        return lambda: None

    def make_scope(self, id: Id) -> Session:
        ns = self.ns(id)
        return SessionProxy(root_session=self, ns=ns)

    def root_scope(self) -> ExpressStubSession:
        return self

    def _process_ui(self, ui: TagChild) -> RenderedDeps:
        return {"deps": [], "html": ""}

    def send_input_message(self, id: str, message: dict[str, object]) -> None:
        return

    def _send_insert_ui(
        self, selector: str, multiple: bool, where: str, content: RenderedDeps
    ) -> None:
        return

    def _send_remove_ui(self, selector: str, multiple: bool) -> None:
        return

    def _send_progress(self, type: str, message: object) -> None:
        return

    async def send_custom_message(self, type: str, message: dict[str, object]) -> None:
        return

    def set_message_handler(
        self,
        name: str,
        handler: (
            Callable[..., Jsonifiable] | Callable[..., Awaitable[Jsonifiable]] | None
        ),
        *,
        _handler_session: Optional[Session] = None,
    ) -> str:
        return ""

    async def _send_message(self, message: dict[str, object]) -> None:
        return

    def _send_message_sync(self, message: dict[str, object]) -> None:
        return

    def _increment_busy_count(self) -> None:
        return

    def _decrement_busy_count(self) -> None:
        return

    def on_flush(
        self,
        fn: Callable[[], None] | Callable[[], Awaitable[None]],
        once: bool = True,
    ) -> Callable[[], None]:
        return lambda: None

    def on_flushed(
        self,
        fn: Callable[[], None] | Callable[[], Awaitable[None]],
        once: bool = True,
    ) -> Callable[[], None]:
        return lambda: None

    def dynamic_route(self, name: str, handler: DynamicRouteHandler) -> str:
        return ""

    async def _unhandled_error(self, e: Exception) -> None:
        return

    def download(
        self,
        id: Optional[str] = None,
        filename: Optional[str | Callable[[], str]] = None,
        media_type: None | str | Callable[[], str] = None,
        encoding: str = "utf-8",
    ) -> Callable[[DownloadHandler], None]:
        return lambda x: None
