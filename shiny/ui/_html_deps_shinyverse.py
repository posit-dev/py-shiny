from __future__ import annotations

from htmltools import HTMLDependency

from .._versions import bslib as bslib_version
from .._versions import htmltools as htmltools_version

"""
HTML dependencies for shinyverse dependencies from R packages such as bslib or htmltools.

For...
* External dependencies (e.g. jQuery, Bootstrap), see `shiny.ui._html_deps_external`
* Internal dependencies (e.g. dataframe, autoresize), see `shiny.ui._html_deps_py_shiny`
* shinyverse dependencies (e.g. bslib, htmltools), see `shiny.ui._html_deps_shinyverse`
"""


_rel_www_shared = "www/shared"
_htmltools_path = f"{_rel_www_shared}/htmltools"
_components_path = f"{_rel_www_shared}/bslib/components"


# -- htmltools ---------------------


def fill_dependency() -> HTMLDependency:
    return HTMLDependency(
        name="htmltools-fill",
        version=htmltools_version,
        source={
            "package": "shiny",
            "subdir": f"{_htmltools_path}/fill",
        },
        stylesheet={"href": "fill.css"},
    )


# -- bslib -------------------------


def components_dependencies() -> HTMLDependency:
    return HTMLDependency(
        name="bslib-components",
        version=bslib_version,
        source={
            "package": "shiny",
            "subdir": f"{_components_path}",
        },
        script=[
            {"src": "components.min.js"},
            {"src": "web-components.min.js", "type": "module"},
        ],
        stylesheet={"href": "components.css"},
    )
