from __future__ import annotations

from pathlib import PurePath

from htmltools import HTMLDependency

from ... import __version__ as shiny_version
from ..._versions import bslib as bslib_version
from ..._versions import htmltools as htmltools_version

_x_www = PurePath(__file__).parent.parent / "www"
_x_www_path = str(_x_www)
_x_fill_path = str(_x_www / "htmltools" / "fill")

_x_components_path = _x_www / "bslib" / "components"
_x_accordion_path = str(_x_components_path / "accordion")
_x_card_path = str(_x_components_path / "card")
_x_sidebar_path = str(_x_components_path / "sidebar")


def card_dependency() -> HTMLDependency:
    return HTMLDependency(
        name="bslib-card",
        version=bslib_version,
        source={
            "package": "shiny",
            "subdir": _x_card_path,
        },
        script={"src": "card.min.js"},
        stylesheet={"href": "card.css"},
        all_files=True,
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
            "subdir": _x_sidebar_path,
        },
        script={"src": "sidebar.min.js"},
        stylesheet={"href": "sidebar.css"},
        all_files=True,
    )


def accordion_dependency() -> HTMLDependency:
    return HTMLDependency(
        "bslib-accordion",
        version=bslib_version,
        source={
            "package": "shiny",
            "subdir": _x_accordion_path,
        },
        script={"src": "accordion.min.js"},
        stylesheet={"href": "accordion.css"},
        all_files=True,
    )


def autoresize_dependency():
    return HTMLDependency(
        "shiny-textarea-autoresize",
        shiny_version,
        source={"package": "shiny", "subdir": _x_www_path},
        script={"src": "textarea-autoresize.js"},
        stylesheet={"href": "textarea-autoresize.css"},
    )


# # TODO: styles for...
# grid - layout_column_wrap
# nav_spacer
# page_fillable
# page_navbar
# page_sidebar
# value_box
