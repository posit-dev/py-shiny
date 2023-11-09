from __future__ import annotations

from ..session import Inputs, Outputs, Session
from ..session import _utils as _session_utils
from . import app, layout
from ._is_express import is_express_app
from ._output import output_args, suspend_display
from ._run import wrap_express_app
from .display_decorator import display_body

__all__ = (
    "input",
    "output",
    "session",
    "is_express_app",
    "output_args",
    "suspend_display",
    "wrap_express_app",
    "app",
    "layout",
    "display_body",
)

# Add types to help type checkers
input: Inputs
output: Outputs
session: Session


# Note that users should use `from shiny.express import input` instead of `from shiny
# import express` and acces via `express.input`. The former provides a static value for
# `input`, but the latter is dynamic -- every time `express.input` is accessed, it
# returns the input for the current session. This will work in the vast majority of
# cases, but when it fails, it will be very confusing.
def __getattr__(name: str) -> object:
    if name == "input":
        return _get_current_session_or_mock().input
    elif name == "output":
        return _get_current_session_or_mock().output
    elif name == "session":
        return _get_current_session_or_mock()

    raise AttributeError(f"Module 'shiny.express' has no attribute '{name}'")


# A very bare-bones mock session class that is used only in shiny.express.
class _MockSession:
    def __init__(self):
        from typing import cast

        from .._namespaces import Root

        self.input = Inputs({})
        self.output = Outputs(cast(Session, self), Root, {}, {})

    # This is needed so that Outputs don't throw an error.
    def _is_hidden(self, name: str) -> bool:
        return False


_current_mock_session: _MockSession | None = None


def _get_current_session_or_mock() -> Session:
    from typing import cast

    session = _session_utils.get_current_session()
    if session is None:
        global _current_mock_session
        if _current_mock_session is None:
            _current_mock_session = _MockSession()
        return cast(Session, _current_mock_session)

    else:
        return session
