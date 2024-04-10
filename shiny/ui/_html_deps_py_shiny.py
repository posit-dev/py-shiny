from __future__ import annotations

from htmltools import HTMLDependency, TagList, tags

from .. import __version__
from . import busy_indicators

"""
HTML dependencies for internal dependencies such as dataframe or text area's autoresize.

For...
* External dependencies (e.g. jQuery, Bootstrap), see `shiny.ui._html_deps_external`
* Internal dependencies (e.g. dataframe, autoresize), see `shiny.ui._html_deps_py_shiny`
* shinyverse dependencies (e.g. bslib, htmltools), see `shiny.ui._html_deps_shinyverse`
"""


def data_frame_deps() -> HTMLDependency:
    return HTMLDependency(
        name="shiny-data-frame-output",
        version=__version__,
        source={
            "package": "shiny",
            "subdir": "www/shared/py-shiny/dataframe",
        },
        script={"src": "dataframe.js", "type": "module"},
    )


def autoresize_dependency() -> HTMLDependency:
    return HTMLDependency(
        "shiny-textarea-autoresize",
        __version__,
        source={"package": "shiny", "subdir": "www/shared/py-shiny/text-area"},
        script={"src": "textarea-autoresize.js", "type": "module"},
        stylesheet={"href": "textarea-autoresize.css"},
    )


def page_output_dependency() -> HTMLDependency:
    return HTMLDependency(
        "shiny-page-output",
        __version__,
        source={"package": "shiny", "subdir": "www/shared/py-shiny/page-output"},
        script={"src": "page-output.js", "type": "module"},
    )


def spin_dependency() -> HTMLDependency:
    return HTMLDependency(
        "shiny-spin",
        __version__,
        source={"package": "shiny", "subdir": "www/shared/py-shiny/spin"},
        stylesheet={"href": "spin.css"},
    )


def busy_indicators_dependency() -> HTMLDependency:
    return HTMLDependency(
        "shiny-busy-indicators",
        __version__,
        source={"package": "shiny", "subdir": "www/shared/py-shiny/busy-indicators"},
        stylesheet={"href": "busy-indicators.css"},
        head=TagList(
            # Enable busy indicators by default.
            busy_indicators.use(),
            # Show a page-level spinner up until the next idle.
            # Note: this is only sensible when this dependency comes bundled with the
            # main shiny dependency, which is currently the case (i.e., it should never
            # come in through dynamic UI).
            tags.script(
                "document.documentElement.classList.add('shiny-not-yet-idle');"
                + "$(document).on('shiny:idle', function() { document.documentElement.classList.remove('shiny-not-yet-idle'); });"
            ),
        ),
    )
