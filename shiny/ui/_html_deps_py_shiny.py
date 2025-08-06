from __future__ import annotations

from htmltools import HTMLDependency

from .. import __version__
from . import busy_indicators

"""
HTML dependencies for internal dependencies such as dataframe.

For...
* External dependencies (e.g. jQuery, Bootstrap), see `shiny.ui._html_deps_external`
* Internal dependencies (e.g. dataframe), see `shiny.ui._html_deps_py_shiny`
* shinyverse dependencies (e.g. bslib, htmltools), see `shiny.ui._html_deps_shinyverse`
"""


def data_frame_deps() -> HTMLDependency:
    return HTMLDependency(
        name="shiny-data-frame-output",
        version=__version__,
        source={
            "package": "shiny",
            "subdir": "www/py-shiny/data-frame",
        },
        script={"src": "data-frame.js", "type": "module"},
    )


def page_output_dependency() -> HTMLDependency:
    return HTMLDependency(
        "shiny-page-output",
        __version__,
        source={"package": "shiny", "subdir": "www/py-shiny/page-output"},
        script={"src": "page-output.js", "type": "module"},
    )


def spin_dependency() -> HTMLDependency:
    return HTMLDependency(
        "shiny-spin",
        __version__,
        source={"package": "shiny", "subdir": "www/py-shiny/spin"},
        stylesheet={"href": "spin.css"},
    )


def busy_indicators_dep() -> HTMLDependency:
    return HTMLDependency(
        "shiny-busy-indicators",
        __version__,
        source={"package": "shiny", "subdir": "www/shared/busy-indicators"},
        stylesheet={"href": "busy-indicators.css"},
        head=busy_indicators.use(),  # Enable busy indicators by default.
        all_files=True,
    )
