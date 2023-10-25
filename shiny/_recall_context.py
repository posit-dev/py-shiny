from __future__ import annotations

import functools
import sys
from types import TracebackType
from typing import Callable, Optional, ParamSpec, Type, TypeVar

P = ParamSpec("P")
R = TypeVar("R")
U = TypeVar("U")


class RecallContextManager:
    def __init__(self, fn: Callable[..., object], *args: object, **kwargs: object):
        self._fn = fn
        self._args: list[object] = list(args)
        self._kwargs: dict[str, object] = kwargs

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


def wrap_recall_context_manager(fn: Callable[P, object]):
    @functools.wraps(fn)
    def wrapped_fn(*args: P.args, **kwargs: P.kwargs) -> RecallContextManager:
        return RecallContextManager(fn, *args, **kwargs)

    return wrapped_fn
