from __future__ import annotations

from typing import Optional

from htmltools import Tag, TagAttrValue, TagList

from .. import ui
from .._recall_context import RecallContextManager, wrap_recall_context_manager
from ..types import MISSING, MISSING_TYPE

__all__ = (
    "sidebar",
    "page_sidebar",
    "column",
    "row",
)


sidebar = wrap_recall_context_manager(ui.sidebar)


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


def column(
    width: int, *, offset: int = 0, **kwargs: TagAttrValue
) -> RecallContextManager:
    return RecallContextManager(
        ui.column,
        width=width,
        offset=offset,
        **kwargs,
    )


row = wrap_recall_context_manager(ui.row)
