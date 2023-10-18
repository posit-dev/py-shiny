from __future__ import annotations

from typing import Literal

from htmltools import HTMLDependency

from .._typing_extensions import NotRequired, TypedDict
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
            "subdir": f"{_htmltools_path}/{name}",
        },
        script={"src": f"{name}.min.js"} if script else None,
        stylesheet={"href": f"{name}.css"} if stylesheet else None,
        all_files=all_files,
    )


class _ScriptItemDict(TypedDict):
    src: str
    type: NotRequired[Literal["module"]]


def _bslib_component_dep(
    name: str,
    script: bool = False,
    stylesheet: bool = False,
    all_files: bool = True,
    script_is_module: bool = False,
) -> HTMLDependency:
    script_val: _ScriptItemDict | None = None
    if script:
        script_val = {"src": f"{name}.min.js"}
        if script_is_module:
            script_val["type"] = "module"

    return HTMLDependency(
        name=f"bslib-{name}",
        version=bslib_version,
        source={
            "package": "shiny",
            "subdir": f"{_components_path}/{name}",
        },
        script=script_val,  # type: ignore # https://github.com/posit-dev/py-htmltools/issues/59
        stylesheet={"href": f"{name}.css"} if stylesheet else None,
        all_files=all_files,
    )


# -- htmltools ---------------------


def fill_dependency() -> HTMLDependency:
    return _htmltools_dep("fill", stylesheet=True, all_files=False)


# -- bslib -------------------------


def accordion_dependency() -> HTMLDependency:
    return _bslib_component_dep("accordion", script=True, stylesheet=True)


def card_dependency() -> HTMLDependency:
    return _bslib_component_dep("card", script=True, stylesheet=True)


def grid_dependency() -> HTMLDependency:
    return _bslib_component_dep("grid", stylesheet=True)


def nav_spacer_dependency() -> HTMLDependency:
    return _bslib_component_dep("nav_spacer", stylesheet=True)


def page_fillable_dependency() -> HTMLDependency:
    return _bslib_component_dep("page_fillable", stylesheet=True)


# # Not used!
# def page_navbar_dependency() -> HTMLDependency:
#     return _bslib_component_dep("page_navbar", stylesheet=True)


def page_sidebar_dependency() -> HTMLDependency:
    return _bslib_component_dep("page_sidebar", stylesheet=True)


def sidebar_dependency() -> HTMLDependency:
    return _bslib_component_dep("sidebar", script=True, stylesheet=True)


def value_box_dependency() -> HTMLDependency:
    return _bslib_component_dep("value_box", stylesheet=True)


def web_component_dependency() -> HTMLDependency:
    return _bslib_component_dep("webComponents", script=True, script_is_module=True)


def bslibshiny_dependency() -> HTMLDependency:
    return _bslib_component_dep("bslibShiny", script=True)
