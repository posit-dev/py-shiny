from __future__ import annotations

import contextlib
import sys
from contextlib import AbstractContextManager
from typing import Callable, TypeVar, overload

from .. import ui
from .._typing_extensions import ParamSpec
from ..render.transformer import OutputRenderer
from ..render.transformer._renderer import RendererBase
from ..render.transformer._transformer import OT

__all__ = (
    "ui_kwargs",
    "suspend_display",
)

P = ParamSpec("P")
R = TypeVar("R")
CallableT = TypeVar("CallableT", bound=Callable[..., object])


def ui_kwargs(
    **kwargs: object,
) -> Callable[[RendererBase], RendererBase]:
    """
    Sets default UI arguments for a Shiny rendering function.

    Each Shiny render function (like :func:`~shiny.render.plot`) can display itself when
    declared within a Shiny inline-style application. In the case of
    :func:`~shiny.render.plot`, the :func:`~shiny.ui.output_plot` function is called
    implicitly to display the plot. Use the `@ui_kwargs` decorator to specify
    arguments to be passed to `output_plot` (or whatever the corresponding UI function
    is) when the render function displays itself.

    Parameters
    ----------
    **kwargs
        Keyword arguments to be passed to the UI function.

    Returns
    -------
    :
        A decorator that sets the default UI arguments for a Shiny rendering function.
    """

    def wrapper(renderer: RendererBase) -> RendererBase:
        # renderer._default_ui_args = args
        renderer._default_ui_kwargs = kwargs
        return renderer

    return wrapper


def output_args(
    *args: object,
    **kwargs: object,
) -> Callable[[OutputRenderer[OT]], OutputRenderer[OT]]:
    """
    Sets default UI arguments for a Shiny rendering function.

    Each Shiny render function (like :func:`~shiny.render.plot`) can display itself when
    declared within a Shiny inline-style application. In the case of
    :func:`~shiny.render.plot`, the :func:`~shiny.ui.output_plot` function is called
    implicitly to display the plot. Use the `@output_args` decorator to specify
    arguments to be passed to `output_plot` (or whatever the corresponding UI function
    is) when the render function displays itself.


    Parameters
    ----------
    *args
        Positional arguments to be passed to the UI function.
    **kwargs
        Keyword arguments to be passed to the UI function.

    Returns
    -------
    :
        A decorator that sets the default UI arguments for a Shiny rendering function.
    """

    def wrapper(renderer: OutputRenderer[OT]) -> OutputRenderer[OT]:
        if not isinstance(renderer, OutputRenderer):
            raise TypeError(
                f"Expected an OutputRenderer, but got {type(renderer).__name__}."
                "\nIf you are trying to set default UI arguments for a `Renderer`, use"
                " `@ui_kwargs` instead."
            )
        renderer._default_ui_args = args
        renderer._default_ui_kwargs = kwargs

        return renderer

    return wrapper


@overload
def suspend_display(fn: CallableT) -> CallableT:
    ...


@overload
def suspend_display(fn: RendererBase) -> RendererBase:
    ...


@overload
def suspend_display() -> AbstractContextManager[None]:
    ...


def suspend_display(
    fn: Callable[P, R] | RendererBase | None = None
) -> Callable[P, R] | RendererBase | AbstractContextManager[None]:
    """Suppresses the display of UI elements in various ways.

    If used as a context manager (`with suspend_display():`), it suppresses the display
    of all UI elements within the context block. (This is useful when you want to
    temporarily suppress the display of a large number of UI elements, or when you want
    to suppress the display of UI elements that are not directly under your control.)

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
        The function to decorate. If `None`, returns a context manager that suppresses
        the display of UI elements within the context block.

    Returns
    -------
    :
        If `fn` is `None`, returns a context manager that suppresses the display of UI
        elements within the context block. Otherwise, returns a decorated version of
        `fn`.
    """

    if fn is None:
        return suspend_display_ctxmgr()

    # Special case for RendererBase; when we decorate those, we just mean "don't
    # display yourself"
    if isinstance(fn, RendererBase):
        # By setting the class value, the `self` arg will be auto added.
        fn.default_ui = null_ui
        return fn

    return suspend_display_ctxmgr()(fn)


@contextlib.contextmanager
def suspend_display_ctxmgr():
    oldhook = sys.displayhook
    sys.displayhook = null_displayhook
    try:
        yield
    finally:
        sys.displayhook = oldhook


def null_ui(
    id: str,
    *args: object,
    **kwargs: object,
) -> ui.TagList:
    return ui.TagList()


def null_displayhook(x: object) -> None:
    pass
