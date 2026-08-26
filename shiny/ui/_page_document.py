from __future__ import annotations

from htmltools import HTMLDependency, HTMLTextDocument

from ..html_dependencies import _page_deps

__all__ = ("PageDocument",)


class PageDocument(HTMLTextDocument):
    """
    A complete HTML document to serve as an app's UI, with Shiny's dependencies.

    Use this as ``App(ui=)`` when your app's UI is a complete HTML document that you
    own -- the ``index.html`` a JS bundler emits, say -- rather than one Shiny builds
    for you from ``ui.page_*()`` components. The document is served as-is, with
    Shiny's own HTML dependencies (and any in ``extra_deps``) inserted at
    ``deps_replace_pattern``.

    This is an :class:`~htmltools.HTMLTextDocument`, so it can also be rendered
    directly with ``.render()``.

    Parameters
    ----------
    html
        A complete HTML document, including ``<html>``. It must contain
        ``deps_replace_pattern`` to mark where the dependencies are inserted.
    extra_deps
        Additional HTML dependencies to include, alongside Shiny's own. These are
        inserted after Shiny's, and their files are served by the app.
    deps_replace_pattern
        The string in ``html`` to replace with the dependencies. The first instance is
        replaced. Defaults to :attr:`DEPS_PLACEHOLDER`.

    Examples
    --------

    ```{python}
    #| eval: false
    from pathlib import Path

    from shiny import App, ui

    index_html = (Path(__file__).parent / "dist" / "index.html").read_text()

    app = App(ui.PageDocument(index_html, extra_deps=[my_bundle_dep]), server)
    ```
    """

    DEPS_PLACEHOLDER = '<meta name="shiny-dependency-placeholder" content="">'
    """
    The default marker in the document that is replaced with the HTML dependencies.
    """

    def __init__(
        self,
        html: str,
        *,
        extra_deps: list[HTMLDependency] | None = None,
        deps_replace_pattern: str = DEPS_PLACEHOLDER,
    ) -> None:
        super().__init__(
            html,
            # A complete document has no tag tree to inspect for the Bootstrap
            # dependency, so Shiny's CSS is always included.
            deps=[*_page_deps(include_css=True), *(extra_deps or [])],
            deps_replace_pattern=deps_replace_pattern,
        )
