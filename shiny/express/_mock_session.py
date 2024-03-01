from __future__ import annotations

import textwrap
from typing import TYPE_CHECKING, Awaitable, Callable, cast

from .._namespaces import Root
from ..session import Inputs, Outputs, Session

if TYPE_CHECKING:
    from ._run import AppOpts

all = ("ExpressMockSession",)


class ExpressMockSession:
    """
    A very bare-bones mock session class that is used only in shiny.express's UI
    rendering phase.

    Note that this class is also used to hold application-level options that are set via
    the `app_opts()` function.
    """

    def __init__(self):
        self.ns = Root
        self.input = Inputs({})
        self.output = Outputs(cast(Session, self), self.ns, {}, {})

        # Application-level (not session-level) options that may be set via app_opts().
        self.app_opts: AppOpts = {}

    # This is needed so that Outputs don't throw an error.
    def _is_hidden(self, name: str) -> bool:
        return False

    def on_ended(
        self,
        fn: Callable[[], None] | Callable[[], Awaitable[None]],
    ) -> Callable[[], None]:
        return lambda: None

    def __getattr__(self, name: str):
        raise AttributeError(
            textwrap.dedent(
                f"""
            The session attribute `{name}` is not yet available for use. Since this code
            will run again when the session is initialized, you can use `if session:` to
            only run this code when the session is established.
        """
            )
        )
