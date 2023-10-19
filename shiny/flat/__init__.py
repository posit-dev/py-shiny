# This file should only be imported by the user, not by any modules in Shiny, because it
# has side effects.

from __future__ import annotations

import sys

from ..session import Inputs, Outputs, Session
from ..session import _utils as session_utils

from ._flat import output_args, suspend_display, is_flat_app, wrap_flat_app
from . import app

# Add types to help type checkers
input: Inputs
output: Outputs
session: Session


class ThisMod(sys.modules[__name__].__class__):
    def __getattr__(self, name: str):
        # TODO: cache the value so that it is the same on subsequent calls?
        if name == "input":
            return session_utils.get_current_session().input
        elif name == "session":
            return session_utils.get_current_session()
        elif name == "output":
            # warn?
            return session_utils.get_current_session().output
        raise AttributeError(name=name)


sys.modules[__name__].__class__ = ThisMod


__all__ = (
    "input",
    "output",
    "session",
    "is_flat_app",
    "output_args",
    "suspend_display",
    "wrap_flat_app",
    "app",
)
