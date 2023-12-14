from __future__ import annotations

import functools
import sys
from types import TracebackType
from typing import Callable, Generic, Mapping, Optional, Type, TypeVar

from htmltools import Tag, wrap_displayhook_handler

from .._typing_extensions import ParamSpec

P = ParamSpec("P")
R = TypeVar("R")
U = TypeVar("U")


class RecallContextManager(Generic[R]):
    def __init__(
        self,
        fn: Callable[..., R],
        *,
        default_page: RecallContextManager[Tag] | None = None,
        args: tuple[object, ...] | None = None,
        kwargs: Mapping[str, object] | None = None,
    ):
        self.fn = fn
        self.default_page = default_page
        if args is None:
            args = tuple()
        if kwargs is None:
            kwargs = {}
        self.args: list[object] = list(args)
        self.kwargs: dict[str, object] = dict(kwargs)

    def __enter__(self) -> None:
        if self.default_page is not None:
            from . import _run

            _run.replace_top_level_recall_context_manager(self.default_page)

        self._prev_displayhook = sys.displayhook
        # Collect each of the "printed" values in the args list.
        sys.displayhook = wrap_displayhook_handler(self.args.append)

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> bool:
        sys.displayhook = self._prev_displayhook
        if exc_type is None:
            res = self.fn(*self.args, **self.kwargs)
            sys.displayhook(res)
        return False


def wrap_recall_context_manager(
    fn: Callable[P, R]
) -> Callable[P, RecallContextManager[R]]:
    @functools.wraps(fn)
    def wrapped_fn(*args: P.args, **kwargs: P.kwargs) -> RecallContextManager[R]:
        return RecallContextManager(fn, args=args, kwargs=kwargs)

    return wrapped_fn
