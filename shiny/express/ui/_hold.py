from __future__ import annotations

import sys
from contextlib import ContextDecorator
from types import TracebackType
from typing import Callable, Optional, Type, TypeVar, overload

from ... import ui
from ..._typing_extensions import ParamSpec
from ...render.renderer import RendererBase, RendererBaseT

__all__ = ("hold",)

P = ParamSpec("P")
R = TypeVar("R")
CallableT = TypeVar("CallableT", bound=Callable[..., object])


@overload
def hold(fn: CallableT) -> CallableT:
    ...


@overload
def hold(fn: RendererBaseT) -> RendererBaseT:
    ...


@overload
def hold() -> HideContextManager:
    ...


def hold(
    fn: Callable[P, R] | RendererBaseT | None = None
) -> Callable[P, R] | RendererBaseT | HideContextManager:
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

    if fn is None:
        return HideContextManager()

    # Special case for RendererBase; when we decorate those, we just mean "don't
    # display yourself"
    if isinstance(fn, RendererBase):
        # By setting the class value, the `self` arg will be auto added.
        fn.auto_output_ui = null_ui
        return fn

    return HideContextManager()(fn)


class HideContextManager(ContextDecorator):
    def __init__(self):
        self.content = ui.TagList()

    def __enter__(self) -> ui.TagList:
        from htmltools import wrap_displayhook_handler

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
        if exc_type:
            print(f"An exception occurred: {exc_value}")
        return False


def null_ui(
    **kwargs: object,
) -> ui.TagList:
    return ui.TagList()


def null_displayhook(x: object) -> None:
    pass
