from __future__ import annotations

from pathlib import PurePath

from htmltools import HTMLDependency

from ..._versions import bslib as bslib_version
from ..._versions import htmltools as htmltools_version

_x_www = PurePath(__file__).parent.parent.parent / "www" / "shared" / "_x"
_x_components_path = str(_x_www / "bslib" / "components")
_x_fill_path = str(_x_www / "htmltools" / "fill")


def fill_dependency() -> HTMLDependency:
    return HTMLDependency(
        "htmltools-fill",
        htmltools_version,
        source={
            "package": "shiny",
            "subdir": _x_fill_path,
        },
        stylesheet={"href": "fill.css"},
    )


def sidebar_dependency() -> HTMLDependency:
    return HTMLDependency(
        "bslib-sidebar",
        bslib_version,
        source={
            "package": "shiny",
            "subdir": _x_components_path,
        },
        script={"src": "sidebar.min.js"},
    )
