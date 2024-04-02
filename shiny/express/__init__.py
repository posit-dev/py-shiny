from __future__ import annotations

# Import these with underscore names so they won't show in autocomplete from the Python
# console.
from ..session import (
    Inputs as _Inputs,
    Outputs as _Outputs,
    Session as _Session,
    get_current_session as _get_current_session,
)
from .. import render
from . import ui
from ._is_express import is_express_app
from ._output import (  # noqa: F401
    output_args,  # pyright: ignore[reportUnusedImport]
    suspend_display,  # pyright: ignore[reportUnusedImport] - Deprecated
)
from ._run import app_opts, wrap_express_app
from .expressify_decorator import expressify


__all__ = (
    "render",
    "input",
    "output",
    "session",
    "is_express_app",
    "app_opts",
    "wrap_express_app",
    "ui",
    "expressify",
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
    session = _get_current_session()

    if name == "input":
        if session is None:
            return _ExpressOnlyPlaceholder("input")
        else:
            return session.input  # pyright: ignore
    elif name == "output":
        if session is None:
            return _ExpressOnlyPlaceholder("output")
        else:
            return session.output  # pyright: ignore
    elif name == "session":
        if session is None:
            return _ExpressOnlyPlaceholder("session")
        else:
            return session

    raise AttributeError(f"Module 'shiny.express' has no attribute '{name}'")


class _ExpressOnlyPlaceholder:
    """Placeholder class for objects that can only be used in a Shiny Express app."""

    def __init__(self, name: str):
        self.name = name

    def __getattr__(self, name: str) -> None:
        raise RuntimeError(
            f"shiny.express.{self.name} can only be used inside of a Shiny Express app."
        )

    def __call__(self, *args: object, **kwargs: object) -> None:
        raise RuntimeError(
            f"shiny.express.{self.name} can only be used inside of a Shiny Express app."
        )
