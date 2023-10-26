from __future__ import annotations

import functools
import sys
from types import TracebackType
from typing import Callable, Generic, Optional, ParamSpec, Type, TypeVar

from htmltools import HTML, Tag, Tagifiable, TagList, tags

P = ParamSpec("P")
R = TypeVar("R")
U = TypeVar("U")


class RecallContextManager(Generic[R]):
    def __init__(self, fn: Callable[..., R], *args: object, **kwargs: object):
        self._fn = fn
        self._args: list[object] = list(args)
        self._kwargs: dict[str, object] = kwargs

    def append_arg(self, value: object):
        if isinstance(value, (Tag, TagList, Tagifiable)):
            self._args.append(value)
        elif hasattr(value, "_repr_html_"):
            self._args.append(HTML(value._repr_html_()))  # pyright: ignore
        else:
            if value is not None:
                self._args.append(tags.pre(repr(value)))

    def __enter__(self) -> None:
        self._prev_displayhook = sys.displayhook
        # Collect each of the "printed" values in the args list.
        sys.displayhook = self.append_arg

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


def wrap_recall_context_manager(
    fn: Callable[P, R]
) -> Callable[P, RecallContextManager[R]]:
    @functools.wraps(fn)
    def wrapped_fn(*args: P.args, **kwargs: P.kwargs) -> RecallContextManager[R]:
        return RecallContextManager(fn, *args, **kwargs)

    return wrapped_fn
