from __future__ import annotations

import functools
from typing import Callable, Generic, Protocol, TypeVar, cast

from .. import ui
from .._typing_extensions import ParamSpec
from .ui import RecallContextManager

__all__ = (
    "Openable",
    "make_openable",
    "page_sidebar",
    "sidebar",
    "column",
    "row",
    "Openable2",
    "make_openable2",
    "page_sidebar2",
    "sidebar2",
    "column2",
    "row2",
)


P = ParamSpec("P")
R = TypeVar("R")


# ==========================================================================
# Implementation 1:
# Wrap the function in a class named Openable. Return the Openable object.
# ==========================================================================
class Openable(Generic[P, R]):
    def __init__(self, fn: Callable[P, R]):
        self.fn = fn

    def __call__(self, *args: P.args, **kwargs: P.kwargs):
        return self.fn(*args, **kwargs)

    def open(self, **kwargs: P.kwargs) -> RecallContextManager:
        return RecallContextManager(self.fn, **kwargs)


def make_openable(fn: Callable[P, R]) -> Openable[P, R]:
    return functools.wraps(fn)(Openable(fn))


page_sidebar = make_openable(ui.page_sidebar)
sidebar = make_openable(ui.sidebar)
column = make_openable(ui.column)
row = make_openable(ui.row)


# ==========================================================================
# Implementation 2:
# Add .open() method directly to the function.
# ==========================================================================
Rc = TypeVar("Rc", covariant=True)


class Openable2(Protocol[P, Rc]):
    __name__: str

    def __call__(self, *args: P.args, **kwargs: P.kwargs):
        ...

    def open(self, **kwargs: P.kwargs) -> RecallContextManager:
        ...


def make_openable2(fn: Callable[P, Rc]) -> Openable2[P, Rc]:
    def open(**kwargs: P.kwargs) -> RecallContextManager:
        return RecallContextManager(fn, **kwargs)

    fn.open = open  # pyright: ignore[reportFunctionMemberAccess]
    return cast(Openable2[P, Rc], fn)


page_sidebar2 = make_openable2(ui.page_sidebar)
sidebar2 = make_openable2(ui.sidebar)
column2 = make_openable2(ui.column)
row2 = make_openable2(ui.row)
