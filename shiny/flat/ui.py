from __future__ import annotations

import functools
import sys
from types import TracebackType
from typing import Callable, Optional, ParamSpec, Type, TypeVar

from htmltools import TagAttrValue, TagChild

from .. import ui

__all__ = ("sidebar", "page_sidebar", "column", "row")

P = ParamSpec("P")
T = TypeVar("T")
U = TypeVar("U")


class RecallContextManager:
    def __init__(self, fn: Callable[P, object], *args: T, **kwargs: U):
        self._fn = fn
        self._args: list[T] = list(args)
        self._kwargs: dict[str, U] = kwargs

    def __enter__(self) -> None:
        self._prev_displayhook = sys.displayhook
        # Collect each of the "printed" values in the args list.
        sys.displayhook = self._args.append

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> bool:
        sys.displayhook = self._prev_displayhook
        if exc_type is None:
            res = self._fn(*self._args, **self._kwargs)
            sys.displayhook(res)
        return False


def as_recall_context_manager(fn: Callable[P, T]):
    @functools.wraps(fn)
    def wrapped_fn(*args: TagChild, **kwargs: TagAttrValue):
        return RecallContextManager(fn, *args, **kwargs)

    return wrapped_fn


sidebar = as_recall_context_manager(ui.sidebar)

page_sidebar = as_recall_context_manager(ui.page_sidebar)

column = as_recall_context_manager(ui.column)

row = as_recall_context_manager(ui.row)
