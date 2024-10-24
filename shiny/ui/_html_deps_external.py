from __future__ import annotations

from pathlib import Path
from typing import List, Union

from htmltools import HTML, HTMLDependency, Tagifiable, TagList, head_content
from htmltools.tags import link

from .._versions import bootstrap as bootstrap_version
from ..html_dependencies import jquery_deps, shiny_deps
from ._html_deps_shinyverse import (
    components_dependencies as bslib_component_dependencies,
)
from ._include_helpers import check_path, include_css
from ._theme import Theme

"""
HTML dependencies for external dependencies Bootstrap, ionrangeslider, datepicker, selectize, and jQuery UI.

For...
* External dependencies (e.g. jQuery, Bootstrap), see `shiny.ui._html_deps_external`
* Internal dependencies (e.g. dataframe, autoresize), see `shiny.ui._html_deps_py_shiny`
* shinyverse dependencies (e.g. bslib, htmltools), see `shiny.ui._html_deps_shinyverse`
"""

ThemeProvider = Union[Tagifiable, HTMLDependency, List[HTMLDependency]]


def shiny_page_theme_deps(theme: str | Path | Theme | ThemeProvider | None) -> TagList:
    deps_bootstrap = bootstrap_deps(include_css=theme is None)

    if theme is None:
        deps_theme = None
    elif isinstance(theme, Theme):
        deps_theme = theme._html_dependencies()
    elif isinstance(theme, str) and theme.startswith(("http", "//")):
        deps_theme = head_content(link(rel="stylesheet", href=theme, type="text/css"))
    elif isinstance(theme, (str, Path)):
        check_path(theme)
        deps_theme = head_content(include_css(theme))
    elif isinstance(theme, Tagifiable) or isinstance(theme, HTMLDependency):
        deps_theme = theme
    elif isinstance(theme, list) and all(
        [isinstance(dep, HTMLDependency) for dep in theme]
    ):
        deps_theme = theme
    else:
        raise ValueError(
            "Invalid `theme`. "
            + "Expected a URL or path to a full Bootstrap CSS file, "
            + "or a theme provider, "
            + f"but received `theme` with type {type(theme)}."
        )

    return TagList(
        deps_bootstrap,
        deps_theme,
        # These next dependencies have their CSS bundled in the main Bootstrap CSS
        # but are also included at the component level. This page-level dependency will
        # win in Shiny apps, but the component-level dependencies will win in other
        # contexts where we don't have a page function.
        #
        # Note: this approach is only intended for legacy bundled components. If you're
        # contemplating following this approach for a new component, please reconsider
        # and explore styling the component with CSS variables instead.
        shiny_deps(include_css=False),
        bslib_component_dependencies(include_css=False),
        ionrangeslider_deps(include_css=False),
        datepicker_deps(include_css=False),
        selectize_deps(include_css=False),
    )


def bootstrap_deps(include_css: bool = True) -> list[HTMLDependency]:
    dep = HTMLDependency(
        name="bootstrap",
        version=bootstrap_version,
        source={"package": "shiny", "subdir": "www/shared/bootstrap/"},
        script={"src": "bootstrap.bundle.min.js"},
        stylesheet={"href": "bootstrap.min.css"} if include_css else None,
        meta={"name": "viewport", "content": "width=device-width, initial-scale=1"},
        all_files=True,
    )
    deps = [jquery_deps(), dep]
    return deps


def ionrangeslider_deps(include_css: bool = True) -> list[HTMLDependency]:
    return [
        HTMLDependency(
            name="ionrangeslider",
            version="2.3.1",
            source={"package": "shiny", "subdir": "www/shared/ionrangeslider/"},
            script={"src": "js/ion.rangeSlider.min.js"},
            # This CSS is rendered against default Bootstrap
            stylesheet={"href": "css/ion.rangeSlider.css"} if include_css else None,
        ),
        HTMLDependency(
            name="strftime",
            version="0.9.2",
            source={"package": "shiny", "subdir": "www/shared/strftime/"},
            script={"src": "strftime-min.js"},
        ),
    ]


def datepicker_deps(include_css: bool = True) -> HTMLDependency:
    return HTMLDependency(
        name="bootstrap-datepicker",
        version="1.9.0",
        source={"package": "shiny", "subdir": "www/shared/datepicker/"},
        # This CSS is rendered against default Bootstrap
        stylesheet=(
            {"href": "css/bootstrap-datepicker3.min.css"} if include_css else None
        ),
        script={"src": "js/bootstrap-datepicker.min.js"},
        # Need to enable noConflict mode. See #1346.
        head=HTML(
            "<script>(function() { var datepicker = $.fn.datepicker.noConflict(); $.fn.bsDatepicker = datepicker; })();</script>"
        ),
    )


def selectize_deps(include_css: bool = True) -> HTMLDependency:
    return HTMLDependency(
        name="selectize",
        version="0.12.6",
        source={"package": "shiny", "subdir": "www/shared/selectize/"},
        script=[
            {"src": "js/selectize.min.js"},
            {"src": "accessibility/js/selectize-plugin-a11y.min.js"},
        ],
        # This CSS is rendered against default Bootstrap
        stylesheet={"href": "css/selectize.min.css"} if include_css else None,
    )


def jqui_deps() -> HTMLDependency:
    return HTMLDependency(
        name="jquery-ui",
        version="1.12.1",
        source={"package": "shiny", "subdir": "www/shared/jqueryui/"},
        script={"src": "jquery-ui.min.js"},
        stylesheet={"href": "jquery-ui.min.css"},
    )
