from __future__ import annotations

from pathlib import Path
from typing import Callable

from htmltools import Tag

from ... import ui
from ..._docstring import add_example
from ...types import MISSING, MISSING_TYPE
from ...ui._html_deps_external import ThemeProvider
from .._recall_context import RecallContextManager
from .._run import get_top_level_recall_context_manager

__all__ = ("page_opts",)


def page_auto_cm() -> RecallContextManager[Tag]:
    return RecallContextManager(ui.page_auto)


@add_example()
def page_opts(
    *,
    title: str | MISSING_TYPE = MISSING,
    window_title: str | MISSING_TYPE = MISSING,
    lang: str | MISSING_TYPE = MISSING,
    theme: str | Path | ui.Theme | ThemeProvider | MISSING_TYPE = MISSING,
    page_fn: Callable[..., Tag] | None | MISSING_TYPE = MISSING,
    fillable: bool | MISSING_TYPE = MISSING,
    full_width: bool | MISSING_TYPE = MISSING,
    **kwargs: object,
) -> None:
    """
    Set page-level options for the current app.

    The arguments to this function get passed to :func:`~shiny.ui.page_auto`, which
    determines which page function should be used based on the page options and the
    top-level items in the app.

    If there is a top-level :func:`~shiny.ui.nav_panel`, :func:`~shiny.ui.page_auto`
    will use :func:`~shiny.ui.page_navbar`. Otherwise, if there is a top-level sidebar,
    :func:`~shiny.ui.page_sidebar` is used.

    If there are neither top-level nav panels nor sidebars, this will use the `fillable`
    and `full_width` arguments to determine which page function to use:

    1. If `fillable` is `True`, :func:`~shiny.ui.page_fillable` is used.
    2. Otherwise, if `full_width` is `True`, :func:`~shiny.ui.page_fluid` is used.
    3. If neither are `True`, :func:`~shiny.ui.page_fixed` is used.

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
    theme
        A custom Shiny theme created using the :class:`~shiny.ui.Theme` class, or a path
        to a local or online CSS file that will replace the Bootstrap CSS bundled by
        default with a Shiny app. This file should be a complete `bootstrap.css` or
        `bootstrap.min.css` file.

        For advanced uses, you can also pass a :class:`~htmltools.Tagifiable` object.
        In this case, Shiny will suppress the default Bootstrap CSS.

        To modify the theme of an app without replacing the Bootstrap CSS entirely, use
        :func:`~shiny.ui.include_css` to add custom CSS.
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
    **kwargs
        Additional arguments to pass to the page function. See the description above for
        further details on how the page function is selected.
    """
    try:
        cm = get_top_level_recall_context_manager()
    except RuntimeError:
        # We can get here if a Shiny Core app, or if we're in the UI rendering phase of
        # a Quarto-Shiny dashboard.
        raise RuntimeError(
            "express.ui.page_opts() can only be used inside of a standalone Shiny Express app."
        )

    if not isinstance(title, MISSING_TYPE):
        cm.kwargs["title"] = title
    if not isinstance(window_title, MISSING_TYPE):
        cm.kwargs["window_title"] = window_title
    if not isinstance(lang, MISSING_TYPE):
        cm.kwargs["lang"] = lang
    if not isinstance(theme, MISSING_TYPE):
        cm.kwargs["theme"] = theme
    if not isinstance(page_fn, MISSING_TYPE):
        cm.kwargs["page_fn"] = page_fn
    if not isinstance(fillable, MISSING_TYPE):
        cm.kwargs["fillable"] = fillable
    if not isinstance(full_width, MISSING_TYPE):
        cm.kwargs["full_width"] = full_width
    if len(kwargs) > 0:
        cm.kwargs.update(kwargs)
