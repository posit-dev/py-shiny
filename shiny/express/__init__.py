from __future__ import annotations

from ..session import Inputs, Outputs, Session
from ..session import _utils as session_utils

from ._output import output_args, suspend_display
from ._run import is_express_app, wrap_express_app
from . import app
from . import layout

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
)

# Add types to help type checkers
input: Inputs
output: Outputs
session: Session


def __getattr__(name: str):
    # TODO: cache the value so that it is the same on subsequent calls?
    if name == "input":
        return session_utils.get_current_session().input
    elif name == "session":
        return session_utils.get_current_session()
    elif name == "output":
        # warn?
        return session_utils.get_current_session().output
    raise AttributeError(name=name)
