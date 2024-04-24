from __future__ import annotations

import textwrap
from typing import TYPE_CHECKING, Awaitable, Callable, Literal, Optional

from htmltools import TagChild

from .._namespaces import Id, ResolvedId, Root
from ..session import Inputs, Outputs, Session
from ..session._session import SessionProxy

if TYPE_CHECKING:
    from .._typing_extensions import Never
    from ..session._session import DynamicRouteHandler, RenderedDeps
    from ..types import Jsonifiable
    from ._run import AppOpts

all = ("ExpressMockSession",)


class ExpressMockSession(Session):
    """
    A very bare-bones mock session class that is used only in shiny.express's UI
    rendering phase.

    Note that this class is also used to hold application-level options that are set via
    the `app_opts()` function.
    """

    def __init__(self, ns: ResolvedId = Root):
        self.ns = ns
        self.input = Inputs({})
        self.output = Outputs(self, self.ns, outputs={})

        # Set some of these values to None just to satisfy the abstract base class to
        # make this code run -- these things should not be used at run time, so None
        # will work as a placeholder. But we also need to tell pyright to ignore that
        # the Nones don't match the type declared in the Session abstract base class.
        self.app = None  # pyright: ignore
        self.id = None  # pyright: ignore

        self._outbound_message_queues = None  # pyright: ignore
        self._downloads = None  # pyright: ignore

        # Application-level (not session-level) options that may be set via app_opts().
        self.app_opts: AppOpts = {}

    def is_real_session(self) -> Literal[False]:
        return False

    # This is needed so that Outputs don't throw an error.
    def _is_hidden(self, name: str) -> bool:
        return False

    def on_ended(
        self,
        fn: Callable[[], None] | Callable[[], Awaitable[None]],
    ) -> Callable[[], None]:
        return lambda: None

    def make_scope(self, id: Id) -> SessionProxy:
        ns = self.ns(id)
        return SessionProxy(parent=self, ns=ns)

    def root_scope(self):
        self._not_implemented("root_scope")

    def _process_ui(self, ui: TagChild):
        self._not_implemented("_process_ui")

    def send_input_message(self, id: str, message: dict[str, object]):
        self._not_implemented("send_input_message")

    def _send_insert_ui(
        self, selector: str, multiple: bool, where: str, content: RenderedDeps
    ):
        self._not_implemented("_send_insert_ui")

    def _send_remove_ui(self, selector: str, multiple: bool):
        self._not_implemented("_send_remove_ui")

    def _send_progress(self, type: str, message: object):
        self._not_implemented("_send_progress")

    async def send_custom_message(self, type: str, message: dict[str, object]):
        self._not_implemented("send_custom_message")

    def set_message_handler(
        self,
        name: str,
        handler: (
            Callable[..., Jsonifiable] | Callable[..., Awaitable[Jsonifiable]] | None
        ),
        *,
        _handler_session: Optional[Session] = None,
    ):
        self._not_implemented("set_message_handler")

    async def _send_message(self, message: dict[str, object]):
        self._not_implemented("_send_message")

    def _send_message_sync(self, message: dict[str, object]):
        self._not_implemented("_send_message_sync")

    def on_flush(
        self,
        fn: Callable[[], None] | Callable[[], Awaitable[None]],
        once: bool = True,
    ):
        self._not_implemented("on_flush")

    def on_flushed(
        self,
        fn: Callable[[], None] | Callable[[], Awaitable[None]],
        once: bool = True,
    ):
        self._not_implemented("on_flushed")

    def dynamic_route(self, name: str, handler: DynamicRouteHandler):
        self._not_implemented("dynamic_route")

    async def _unhandled_error(self, e: Exception):
        self._not_implemented("_unhandled_error")

    def download(
        self,
        id: Optional[str] = None,
        filename: Optional[str | Callable[[], str]] = None,
        media_type: None | str | Callable[[], str] = None,
        encoding: str = "utf-8",
    ):
        self._not_implemented("download")

    def _not_implemented(self, name: str) -> Never:
        raise NotImplementedError(
            textwrap.dedent(
                f"""
            The session attribute `{name}` is not yet available for use. Since this code
            will run again when the session is initialized, you can use `if session:` to
            only run this code when the session is established.
        """
            )
        )
