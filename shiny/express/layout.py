from __future__ import annotations

from typing import Literal, Optional

import htmltools
from htmltools import Tag, TagAttrValue, TagChild, TagList

from .. import ui
from ..types import MISSING, MISSING_TYPE
from ..ui.css import CssUnit
from . import _run
from ._recall_context import RecallContextManager, wrap_recall_context_manager

__all__ = (
    "set_page",
    "sidebar",
    "page_sidebar",
    "column",
    "row",
)


# ======================================================================================
# Page functions
# ======================================================================================


def set_page(page_fn: RecallContextManager[Tag]):
    """Set the page function for the current Shiny express app."""
    _run.replace_top_level_recall_context_manager(page_fn)


# ======================================================================================
# htmltools Tag functions
# ======================================================================================

p = wrap_recall_context_manager(htmltools.p)
div = wrap_recall_context_manager(htmltools.div)
span = wrap_recall_context_manager(htmltools.span)
pre = wrap_recall_context_manager(htmltools.pre)


# ======================================================================================
# Shiny layout components
# ======================================================================================


def page_fluid(
    *,
    title: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: str,
) -> RecallContextManager[Tag]:
    return RecallContextManager(
        ui.page_fluid,
        title=title,
        lang=lang,
        **kwargs,
    )


def sidebar(
    *,
    width: CssUnit = 250,
    position: Literal["left", "right"] = "left",
    open: Literal["desktop", "open", "closed", "always"] = "desktop",
    id: Optional[str] = None,
    title: TagChild | str = None,
    bg: Optional[str] = None,
    fg: Optional[str] = None,
    class_: Optional[str] = None,  # TODO-future; Consider using `**kwargs` instead
    max_height_mobile: Optional[str | float] = None,
    gap: Optional[CssUnit] = None,
    padding: Optional[CssUnit | list[CssUnit]] = None,
) -> RecallContextManager[ui.Sidebar]:
    return RecallContextManager(
        ui.sidebar,
        width=width,
        position=position,
        open=open,
        id=id,
        title=title,
        bg=bg,
        fg=fg,
        class_=class_,
        max_height_mobile=max_height_mobile,
        gap=gap,
        padding=padding,
    )


def page_sidebar(
    *,
    title: Optional[str | Tag | TagList] = None,
    fillable: bool = True,
    fillable_mobile: bool = False,
    window_title: str | MISSING_TYPE = MISSING,
    lang: Optional[str] = None,
    **kwargs: TagAttrValue,
):
    return RecallContextManager(
        ui.page_sidebar,
        title=title,
        fillable=fillable,
        fillable_mobile=fillable_mobile,
        window_title=window_title,
        lang=lang,
        **kwargs,
    )


def column(width: int, *, offset: int = 0, **kwargs: TagAttrValue):
    return RecallContextManager(
        ui.column,
        width,
        offset=offset,
        **kwargs,
    )


def row(**kwargs: TagAttrValue):
    return RecallContextManager(ui.row, **kwargs)


def card(
    *,
    full_screen: bool = False,
    height: Optional[CssUnit] = None,
    max_height: Optional[CssUnit] = None,
    min_height: Optional[CssUnit] = None,
    fill: bool = True,
    class_: Optional[str] = None,
    **kwargs: TagAttrValue,
):
    return RecallContextManager(
        ui.card,
        full_screen=full_screen,
        height=height,
        max_height=max_height,
        min_height=min_height,
        fill=fill,
        class_=class_,
        **kwargs,
    )
