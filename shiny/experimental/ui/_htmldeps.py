from __future__ import annotations

from pathlib import PurePath

from htmltools import HTMLDependency

from ... import __version__ as shiny_version
from ..._versions import bslib as bslib_version
from ..._versions import htmltools as htmltools_version

_x_www = PurePath(__file__).parent.parent / "www"
_x_www_path = str(_x_www)
_x_htmltools_path = _x_www / "htmltools"
_x_components_path = _x_www / "bslib" / "components"


def _htmltools_dep(
    name: str,
    script: bool = False,
    stylesheet: bool = False,
    all_files: bool = True,
) -> HTMLDependency:
    return HTMLDependency(
        name=f"htmltools-{name}",
        version=htmltools_version,
        source={
            "package": "shiny",
            "subdir": str(_x_htmltools_path / "fill"),
        },
        script={"src": f"{name}.min.js"} if script else None,
        stylesheet={"href": f"{name}.css"} if stylesheet else None,
        all_files=all_files,
    )


def _bslib_component_dep(
    name: str,
    script: bool = False,
    stylesheet: bool = False,
    all_files: bool = True,
) -> HTMLDependency:
    return HTMLDependency(
        name=f"bslib-{name}",
        version=bslib_version,
        source={
            "package": "shiny",
            "subdir": str(_x_components_path / name),
        },
        script={"src": f"{name}.min.js"} if script else None,
        stylesheet={"href": f"{name}.css"} if stylesheet else None,
        all_files=all_files,
    )


# -- htmltools ---------------------


def fill_dependency() -> HTMLDependency:
    return _htmltools_dep("fill", stylesheet=True)


# -- bslib -------------------------


def accordion_dependency() -> HTMLDependency:
    return _bslib_component_dep("accordion", script=True, stylesheet=True)


def card_dependency() -> HTMLDependency:
    return _bslib_component_dep("card", script=True, stylesheet=True)


def grid_dependency() -> HTMLDependency:
    return _bslib_component_dep("grid", stylesheet=True)


# Coped to `ui._x._htmldeps.py`
# def nav_spacer_dependency() -> HTMLDependency:
#     return _bslib_component_dep("nav_spacer", stylesheet=True)


def page_fillable_dependency() -> HTMLDependency:
    return _bslib_component_dep("page_fillable", stylesheet=True)


# TODO-barret; Confirm with carson;
# # Not used!
# def page_navbar_dependency() -> HTMLDependency:
#     return _bslib_component_dep("page_navbar", stylesheet=True)


def page_sidebar_dependency() -> HTMLDependency:
    return _bslib_component_dep("page_sidebar", stylesheet=True)


def sidebar_dependency() -> HTMLDependency:
    return _bslib_component_dep("sidebar", script=True, stylesheet=True)


def value_box_dependency() -> HTMLDependency:
    return _bslib_component_dep("value_box", stylesheet=True)


# -- Experimental ------------------


def autoresize_dependency():
    return HTMLDependency(
        "shiny-textarea-autoresize",
        shiny_version,
        source={"package": "shiny", "subdir": _x_www_path},
        script={"src": "textarea-autoresize.js"},
        stylesheet={"href": "textarea-autoresize.css"},
    )
