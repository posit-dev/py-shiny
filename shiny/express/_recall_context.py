from __future__ import annotations

import functools
import sys
from types import TracebackType
from typing import Callable, Generic, Mapping, Optional, Type, TypeVar, cast

from htmltools import HTML, Tag, Tagifiable, TagList, tags

from .. import ui
from .._typing_extensions import ParamSpec
from ..ui._navs import Nav, NavMenu

P = ParamSpec("P")
R = TypeVar("R")
U = TypeVar("U")


class RecallContextManager(Generic[R]):
    def __init__(
        self,
        fn: Callable[..., R],
        *,
        args: tuple[object, ...] | None = None,
        kwargs: Mapping[str, object] | None = None,
    ):
        self._fn = fn
        if args is None:
            args = tuple()
        if kwargs is None:
            kwargs = {}
        self.args: list[object] = list(args)
        self.kwargs: dict[str, object] = dict(kwargs)

    def append_arg(self, value: object):
        if isinstance(value, (Tag, TagList, Tagifiable)):
            self.args.append(value)
        elif hasattr(value, "_repr_html_"):
            self.args.append(HTML(value._repr_html_()))  # pyright: ignore
        else:
            # We should NOT end up here for objects that were `def`ed, because they
            # would already have been filtered out by _display_decorator_function_def().
            # This is only for other kinds of expressions, the kind which would normally
            # be printed at the console.
            if value is not None:
                self.args.append(tags.pre(repr(value)))

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
            res = self.fn(*self.args, **self.kwargs)
            sys.displayhook(res)
        return False

    @property
    def fn(self) -> Callable[..., R]:
        return self._fn


class TopLevelRecallContextManager(RecallContextManager[Tag]):
    def __init__(
        self,
        *,
        args: tuple[object, ...] | None = None,
        kwargs: Mapping[str, object] | None = None,
    ):
        super().__init__(lambda x: x, args=args, kwargs=kwargs)

    @property
    def fn(self) -> Callable[..., Tag]:
        # Presence of a top-level nav items and/or sidebar determines the page function
        navs = [x for x in self.args if isinstance(x, (Nav, NavMenu))]
        sidebars = [x for x in self.args if isinstance(x, ui.Sidebar)]

        nNavs = len(navs)
        nSidebars = len(sidebars)

        # TODO: How should this work with .set_page_*()/.set_title()?
        if nNavs == 0:
            if nSidebars == 0:
                return _DEFAULT_PAGE_FUNCTION

            if nSidebars == 1:
                # page_sidebar() needs sidebar to be the first arg
                self.args = sidebars + [x for x in self.args if x not in sidebars]
                return ui.page_sidebar

            # If multiple sidebars(), wrap them in layout_sidebar()
            # TODO:
            # 1. Maybe this logic be should handled by non-top-level ctx managers?
            #    That is, if we're not in a top-level ctx manager, automatically wrap
            #    Sidebar() into layout_sidebar()?
            # 2. Provide a way to exit the layout.sidebar() context? Maybe '---'?
            if nSidebars > 1:
                new_args: object = []
                sidebar_idx = [
                    i for i, x in enumerate(self.args) if isinstance(x, ui.Sidebar)
                ]
                new_args.append(*self.args[0 : sidebar_idx[0]])
                for i, x in enumerate(sidebar_idx):
                    j = (
                        sidebar_idx[i + 1]
                        if i < len(sidebar_idx) - 1
                        else len(self.args)
                    )
                    s = ui.layout_sidebar(
                        cast(ui.Sidebar, self.args[x]),
                        *self.args[x + 1 : j],  # type: ignore
                    )
                    new_args.append(s)

                self.args = new_args
                return _DEFAULT_PAGE_FUNCTION

        # At least one nav
        else:
            if nSidebars == 0:
                # TODO: what do we do when nArgs != nNavs? Just let page_navbar handle it (i.e. error)?
                return ui.page_navbar

            if nSidebars == 1:
                self.kwargs["sidebar"] = self.kwargs.get("sidebar", sidebars[0])
                return ui.page_navbar

            if nSidebars > 1:
                raise NotImplementedError(
                    "Multiple top-level sidebars not allowed in combination with top-level navs"
                )

        return _DEFAULT_PAGE_FUNCTION


_DEFAULT_PAGE_FUNCTION = ui.page_fixed


def wrap_recall_context_manager(
    fn: Callable[P, R]
) -> Callable[P, RecallContextManager[R]]:
    @functools.wraps(fn)
    def wrapped_fn(*args: P.args, **kwargs: P.kwargs) -> RecallContextManager[R]:
        return RecallContextManager(fn, args=args, kwargs=kwargs)

    return wrapped_fn
