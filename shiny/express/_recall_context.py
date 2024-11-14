from __future__ import annotations

import functools
import sys
from types import TracebackType
from typing import Any, Callable, Generic, Mapping, Optional, Type, TypeVar

from htmltools import (
    HTML,
    MetadataNode,
    ReprHtml,
    Tag,
    Tagifiable,
    TagList,
    wrap_displayhook_handler,
)

from .._typing_extensions import ParamSpec
from ..render.renderer import Renderer

P = ParamSpec("P")
R = TypeVar("R")
U = TypeVar("U")


def only_append_renderable(handler: Callable[[object], None]) -> Callable[[Any], None]:
    def f(x: Any):
        if isinstance(x, (list, tuple)):
            for item in x:  # pyright: ignore[reportUnknownVariableType]
                f(item)
            return
        elif isinstance(x, (str, float, int, bool)):
            handler(x)
            return
        elif isinstance(x, (HTML, Tag, TagList, Tagifiable, ReprHtml, Renderer)):
            handler(x)  # pyright: ignore[reportUnknownArgumentType]
            return

        trunc_to = 80
        x_trunc = f"{x!r}"
        if len(x_trunc) > trunc_to:
            x_trunc = x_trunc[:trunc_to] + "..."

        print(
            # TODO: Make this a more informative warning
            f"Express has suppressed the object `{x_trunc}` because it is of type {type(x)}. "
            "Coerce to HTML, a string, or an htmltools tag to display this object."
        )

    return f


class RecallContextManager(Generic[R]):
    def __init__(
        self,
        fn: Callable[..., R],
        *,
        args: tuple[object, ...] | None = None,
        kwargs: Mapping[str, object] | None = None,
    ):
        self.fn = fn
        if args is None:
            args = tuple()
        if kwargs is None:
            kwargs = {}
        self.args: list[object] = list(args)
        self.kwargs: dict[str, object] = dict(kwargs)
        # Let htmltools.wrap_displayhook_handler decide what to do with objects before
        # we append them.
        self.wrapped_append = only_append_renderable(
            wrap_displayhook_handler(self.args.append)
        )

    def __enter__(self) -> None:
        self._prev_displayhook = sys.displayhook
        sys.displayhook = self.displayhook

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

    def displayhook(self, x: object) -> None:
        if isinstance(x, RecallContextManager):
            # This displayhook first checks if x (the child) is a RecallContextManager,
            # in which case it uses `with x` to trigger x.__enter__() and x.__exit__().
            # When x.__exit__() is called, it will invoke x.fn() and then pass the
            # result to this object's (the parent) self.displayhook(), which is this
            # same function, but instead of passing in a RecallContextManager, it will
            # pass in the actual object.
            #
            # In short, this is a way of invoking a re-entrant call to the current
            # function, but instead of passing in a RecallContextManager, it passes in
            # the result from the RecallContextManager.
            with x:
                pass
        else:
            self.wrapped_append(x)

    def tagify(self) -> Tag | TagList | MetadataNode | str:
        res = self.fn(*self.args, **self.kwargs)

        if callable(getattr(res, "tagify", None)):
            return res.tagify()  # pyright: ignore
        if callable(getattr(res, "_repr_html_", None)):
            return res._repr_html_()  # pyright: ignore

        raise RuntimeError(
            "RecallContextManager was used without `with`. When used this way, the "
            "result must have a .tagify() or ._repr_html_() method, but it does not."
        )


def wrap_recall_context_manager(
    fn: Callable[P, R]
) -> Callable[P, RecallContextManager[R]]:
    @functools.wraps(fn)
    def wrapped_fn(*args: P.args, **kwargs: P.kwargs) -> RecallContextManager[R]:
        return RecallContextManager(fn, args=args, kwargs=kwargs)

    return wrapped_fn
