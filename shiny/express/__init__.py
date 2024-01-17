from __future__ import annotations

# Import these with underscore names so they won't show in autocomplete from the Python
# console.
from ..session import Inputs as _Inputs, Outputs as _Outputs, Session as _Session
from ..session import _utils as _session_utils
from .. import render
from . import ui
from ._is_express import is_express_app
from ._output import (  # noqa: F401
    suspend_display,
    output_args,  # pyright: ignore[reportUnusedImport]
)
from ._run import wrap_express_app
from .display_decorator import display_body


__all__ = (
    "render",
    "input",
    "output",
    "session",
    "is_express_app",
    "suspend_display",
    "wrap_express_app",
    "ui",
    "display_body",
)

# Add types to help type checkers
input: _Inputs
output: _Outputs
session: _Session


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

        self.input = _Inputs({})
        self.output = _Outputs(cast(_Session, self), Root, {}, {})

    # This is needed so that Outputs don't throw an error.
    def _is_hidden(self, name: str) -> bool:
        return False


_current_mock_session: _MockSession | None = None


def _get_current_session_or_mock() -> _Session:
    from typing import cast

    session = _session_utils.get_current_session()
    if session is None:
        global _current_mock_session
        if _current_mock_session is None:
            _current_mock_session = _MockSession()
        return cast(_Session, _current_mock_session)

    else:
        return session
