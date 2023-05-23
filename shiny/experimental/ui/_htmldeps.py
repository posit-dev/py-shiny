from __future__ import annotations

from pathlib import PurePath

from htmltools import HTMLDependency

from ... import __version__ as shiny_version
from ..._versions import bslib as bslib_version
from ..._versions import htmltools as htmltools_version

_x_www = PurePath(__file__).parent.parent / "www"
_x_www_path = str(_x_www)
_x_components_path = str(_x_www / "bslib" / "components")
_x_fill_path = str(_x_www / "htmltools" / "fill")


def card_dependency() -> HTMLDependency:
    return HTMLDependency(
        name="bslib-card",
        version=bslib_version,
        source={
            "package": "shiny",
            "subdir": _x_components_path,
        },
        script={"src": "card.min.js"},
    )


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


def accordion_dependency() -> HTMLDependency:
    return HTMLDependency(
        "bslib-accordion",
        version=bslib_version,
        source={
            "package": "shiny",
            "subdir": _x_components_path,
        },
        script={"src": "accordion.min.js"},
    )


def autoresize_dependency():
    return HTMLDependency(
        "shiny-textarea-autoresize",
        shiny_version,
        source={"package": "shiny", "subdir": _x_www_path},
        script={"src": "textarea-autoresize.js"},
        stylesheet={"href": "textarea-autoresize.css"},
    )
