from __future__ import annotations

from htmltools import HTMLDependency

from .. import __version__

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
