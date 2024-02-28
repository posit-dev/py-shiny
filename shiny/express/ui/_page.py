from __future__ import annotations

from typing import Callable

from htmltools import Tag

from ... import ui
from ..._docstring import no_example
from ...types import MISSING, MISSING_TYPE
from .._recall_context import RecallContextManager
from .._run import get_top_level_recall_context_manager

__all__ = ("page_opts",)


def page_auto_cm() -> RecallContextManager[Tag]:
    return RecallContextManager(ui.page_auto)


@no_example()
def page_opts(
    *,
    title: str | MISSING_TYPE = MISSING,
    window_title: str | MISSING_TYPE = MISSING,
    lang: str | MISSING_TYPE = MISSING,
    page_fn: Callable[..., Tag] | None | MISSING_TYPE = MISSING,
    fillable: bool | MISSING_TYPE = MISSING,
    full_width: bool | MISSING_TYPE = MISSING,
) -> None:
    """
    Set page-level options for the current app.

    The arguments to this function get passed to :func:`~shiny.ui.page_auto`.

    Parameters
    ----------
    title
        A title shown on the page.
    window_title
        The browser window title. If no value is provided, this will use the value of
        ``title``.
    lang
        ISO 639-1 language code for the HTML page, such as ``"en"`` or ``"ko"``. This
        will be used as the lang in the ``<html>`` tag, as in ``<html lang="en">``. The
        default, `None`, results in an empty string.
    fillable
        If there is a top-level sidebar or nav, then the value is passed through to the
        :func:`~shiny.ui.page_sidebar` or :func:`~shiny.ui.page_navbar` function.
        Otherwise, if ``True``, use :func:`~shiny.ui.page_fillable`, where the content
        fills the window; if ``False`` (the default), the value of ``full_width`` will
        determine which page function is used.
    full_width
        This has an effect only if there are no sidebars or top-level navs, and
        ``fillable`` is ``False``. If this is ``False`` (the default), use use
        :func:`~shiny.ui.page_fixed`; if ``True``, use :func:`~shiny.ui.page_fillable`.
    page_fn
        The page function to use. If ``None`` (the default), will automatically choose
        one based on the arguments provided. If not ``None``, this will override all
        heuristics for choosing page functions.
    """
    cm = get_top_level_recall_context_manager()

    if not isinstance(title, MISSING_TYPE):
        cm.kwargs["title"] = title
    if not isinstance(window_title, MISSING_TYPE):
        cm.kwargs["window_title"] = window_title
    if not isinstance(lang, MISSING_TYPE):
        cm.kwargs["lang"] = lang
    if not isinstance(page_fn, MISSING_TYPE):
        cm.kwargs["page_fn"] = page_fn
    if not isinstance(fillable, MISSING_TYPE):
        cm.kwargs["fillable"] = fillable
    if not isinstance(full_width, MISSING_TYPE):
        cm.kwargs["full_width"] = full_width
