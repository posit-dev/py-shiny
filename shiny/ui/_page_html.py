from __future__ import annotations

from pathlib import Path

from htmltools import HTMLDependency, HTMLTextDocument

from .._docstring import add_example
from ..html_dependencies import _page_deps
from ..types import ListOrTuple

__all__ = ("page_html",)

DEPS_PLACEHOLDER = '<meta name="shiny-dependency-placeholder" content="">'
"""
The default marker in the document that is replaced with the HTML dependencies.
"""


class PageHtmlDocument(HTMLTextDocument):
    """
    A complete HTML document to serve as an app's UI, with Shiny's dependencies.

    Create one with :func:`~shiny.ui.page_html`; see its documentation for details.
    """

    def __init__(
        self,
        html: str,
        *,
        extra_deps: ListOrTuple[HTMLDependency] | None = None,
        deps_replace_pattern: str = DEPS_PLACEHOLDER,
    ) -> None:
        super().__init__(
            html,
            # A complete document has no tag tree to inspect for the Bootstrap
            # dependency, so Shiny's CSS is always included.
            deps=[*_page_deps(include_css=True), *(extra_deps or [])],
            deps_replace_pattern=deps_replace_pattern,
        )


@add_example()
def page_html(
    html: str | Path,
    *,
    extra_deps: ListOrTuple[HTMLDependency] | None = None,
    deps_replace_pattern: str = DEPS_PLACEHOLDER,
) -> PageHtmlDocument:
    """
    Create a page from a complete HTML document that you own.

    Use this as ``App(ui=)`` when your app's UI is a complete HTML document -- the
    ``index.html`` a JS bundler emits, say -- rather than one Shiny builds for you
    from ``ui.page_*()`` components. The document is served as-is, with Shiny's own
    HTML dependencies (and any in ``extra_deps``) inserted at
    ``deps_replace_pattern``, and their files served by the app.

    Parameters
    ----------
    html
        A complete HTML document, including ``<html>``, as a string -- or a
        :class:`~pathlib.Path` to an HTML file, which is read (as UTF-8) each time
        this function is called. It must contain ``deps_replace_pattern`` to mark
        where the dependencies are inserted.
    extra_deps
        Additional HTML dependencies to include, alongside Shiny's own. These are
        inserted after Shiny's, and their files are served by the app.
    deps_replace_pattern
        The string in ``html`` to replace with Shiny's dependencies. Only the first
        instance is replaced. Defaults to
        ``'<meta name="shiny-dependency-placeholder" content="">'``.

    Returns
    -------
    :
        A document object to pass as ``App(ui=)``, or to return from a UI function
        (``App(ui=lambda request: ...)``, which is what bookmarking requires).
    """
    if isinstance(html, Path):
        html = html.read_text(encoding="utf-8")

    return PageHtmlDocument(
        html,
        extra_deps=extra_deps,
        deps_replace_pattern=deps_replace_pattern,
    )
