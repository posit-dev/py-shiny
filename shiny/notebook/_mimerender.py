# pyright: reportUnknownMemberType=false
from __future__ import annotations

"""
We don't use the normal IPython _repr_html_ rendering because we need to do two things
slightly differently: 1) include the htmltools JS/CSS dependencies, and 2) use the
<shiny-bind> custom element to wrap the HTML. This module implements a custom IPython
MIME type and formatter to do those things when our htmltools objects are being
formatted.
"""

import json
import os
from typing import Any, cast

from htmltools import HTML, HTMLDependency, Tag, TagList
from IPython.core.formatters import BaseFormatter
from IPython.core.interactiveshell import InteractiveShell

HTMLTOOLS_MIME_TYPE = "application/vnd.posit.htmltools+json"


def register_mimerenderer(
    ipython: InteractiveShell, mime: str, formatter: BaseFormatter
) -> BaseFormatter:
    if ipython.display_formatter is None:
        raise RuntimeError("ipython.display_formatter is None!?")
    ipython.display_formatter.active_types.append(  # pyright: ignore[reportGeneralTypeIssues]
        mime
    )
    ipython.display_formatter.formatters[  # pyright: ignore[reportGeneralTypeIssues]
        mime
    ] = formatter
    return cast(
        BaseFormatter,
        ipython.display_formatter.formatters[  # pyright: ignore[reportGeneralTypeIssues]
            mime
        ],
    )


def render_with_shinybind(tag_data: Any | None) -> str:
    if tag_data is None:
        return json.dumps(dict(deps=[], html=None))

    if isinstance(tag_data, Tag) or isinstance(tag_data, TagList):
        rendered = tag_data.render()
    else:
        # Necessary for strings, htmltools.HTML, and other stuff that can go in an HTML
        # graph but doesn't have its own .render method
        rendered = TagList(tag_data).render()

    deps = process_dependencies(rendered["dependencies"])

    return json.dumps(dict(deps=deps, html=rendered["html"]))


def render_repr_html(tag_data: Any | None):
    return dict(html=tag_data._repr_html_())  # type: ignore


def initialize(ipython: InteractiveShell):
    formatter = register_mimerenderer(
        ipython, HTMLTOOLS_MIME_TYPE, HtmlToolsFormatter()
    )
    formatter.for_type(Tag, render_with_shinybind)
    formatter.for_type(TagList, render_with_shinybind)
    formatter.for_type(HTML, render_with_shinybind)
    formatter.for_type(HTMLDependency, render_with_shinybind)
    formatter.for_type(str, render_with_shinybind)


class HtmlToolsFormatter(BaseFormatter):
    format_type = HTMLTOOLS_MIME_TYPE

    print_method = "_repr_htmltools_"


def process_dependencies(deps: list[HTMLDependency]) -> list[dict[str, Any]]:
    dest = os.environ.get("SHINY_JUPYTERLAB_SERVER_EXTENSION_ROOT", None)
    if dest is None or dest == "" or not os.path.isdir(dest):
        raise RuntimeError(
            "$SHINY_JUPYTERLAB_SERVER_EXTENSION_ROOT is not set. "
            "Perhaps the Shiny JupyterLab server extension is not installed/enabled?"
        )

    def process_dep(dep: HTMLDependency) -> dict[str, Any]:
        lib_prefix = "/shiny/dependencies/"

        dep.copy_to(dest, include_version=True)
        return dep.as_dict(lib_prefix=lib_prefix, include_version=True)

    return [process_dep(dep) for dep in deps if dep.name != "shiny"]
