from __future__ import annotations

from typing import Callable

from htmltools import Tag

from ... import ui
from ...types import MISSING, MISSING_TYPE
from .._recall_context import RecallContextManager
from .._run import get_top_level_recall_context_manager

__all__ = ("page_opts",)


def page_auto_cm() -> RecallContextManager[Tag]:
    return RecallContextManager(ui.page_auto)


def page_opts(
    *,
    title: str | MISSING_TYPE = MISSING,
    lang: str | MISSING_TYPE = MISSING,
    page_fn: Callable[..., Tag] | None | MISSING_TYPE = MISSING,
    fillable: bool | MISSING_TYPE = MISSING,
    full_width: bool | MISSING_TYPE = MISSING,
) -> None:
    cm = get_top_level_recall_context_manager()

    if not isinstance(title, MISSING_TYPE):
        cm.kwargs["title"] = title
    if not isinstance(lang, MISSING_TYPE):
        cm.kwargs["lang"] = lang
    if not isinstance(page_fn, MISSING_TYPE):
        cm.kwargs["_page_fn"] = page_fn
    if not isinstance(fillable, MISSING_TYPE):
        cm.kwargs["_fillable"] = fillable
    if not isinstance(full_width, MISSING_TYPE):
        cm.kwargs["_full_width"] = full_width
