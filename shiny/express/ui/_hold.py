from __future__ import annotations

import sys
from types import TracebackType
from typing import Callable, Optional, Type, TypeVar

from htmltools import wrap_displayhook_handler

from ... import ui
from ..._typing_extensions import ParamSpec

__all__ = ("hold",)

P = ParamSpec("P")
R = TypeVar("R")
CallableT = TypeVar("CallableT", bound=Callable[..., object])


def hold() -> HoldContextManager:
    """Prevent the display of UI elements in various ways.

    If used as a context manager (`with hide():`), it prevents the display of all UI
    elements within the context block. (This is useful when you want to temporarily
    prevent the display of a large number of UI elements, or when you want to prevent
    the display of UI elements that are not directly under your control.)

    If used as a decorator (without parentheses) on a Shiny rendering function, it
    prevents that function from automatically outputting itself at the point of its
    declaration. (This is useful when you want to define the rendering logic for an
    output, but want to explicitly call a UI output function to indicate where and how
    it should be displayed.)

    If used as a decorator (without parentheses) on any other function, it turns
    Python's `sys.displayhook` into a no-op for the duration of the function call.

    Parameters
    ----------
    fn
        The function to decorate. If `None`, returns a context manager that prevents the
        display of UI elements within the context block.

    Returns
    -------
    :
        If `fn` is `None`, returns a context manager that prevents the display of UI
        elements within the context block. Otherwise, returns a decorated version of
        `fn`.
    """

    return HoldContextManager()


class HoldContextManager:
    def __init__(self):
        self.content = ui.TagList()

    def __enter__(self) -> ui.TagList:
        self.prev_displayhook = sys.displayhook
        sys.displayhook = wrap_displayhook_handler(
            self.content.append  # pyright: ignore[reportGeneralTypeIssues]
        )
        return self.content

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> bool:
        sys.displayhook = self.prev_displayhook
        return False
