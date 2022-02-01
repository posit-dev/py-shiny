__all__ = (
    "page_navbar",
    "page_fluid",
    "page_fixed",
    "page_bootstrap",
)

import sys
from typing import Optional, Any, List, Union
from warnings import warn

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

from htmltools import (
    HTMLDependency,
    tags,
    Tag,
    TagList,
    div,
    TagChildArg,
    head_content,
)

from .._docstring import doc
from ._html_dependencies import bootstrap_deps
from ._navs import navs_bar, navs_bar_params
from ..types import MISSING, MISSING_TYPE

_params = {
    "args": "UI elements.",
    "title": """
    The browser window title (defaults to the host URL of the page). Can also be set as
    a side effect via :func:`~shiny.ui.panel_title`.
    """,
    "lang": """
    ISO 639-1 language code for the HTML page, such as ``"en"`` or ``"ko"``. This will
    be used as the lang in the ``<html>`` tag, as in ``<html lang="en">``. The default,
    `None`, results in an empty string.
    """,
    "kwargs": "Attributes on the page level container.",
}


@doc(
    "Create a navbar with a navs bar and a title.",
    parameters={
        **navs_bar_params,
        **_params,
        "window_title": """
        The browser's window title (defaults to the host URL of the page). Can also be set as
        """,
    },
    returns="A UI element.",
    note="""
    See :func:`~shiny.ui.nav` for an example.
    """,
    see_also=[
        ":func:`~shiny.ui.nav`",
        ":func:`~shiny.ui.nav_menu`",
        ":func:`~shiny.ui.navs_bar`",
        ":func:`~shiny.ui.page_fluid`",
    ],
)
def page_navbar(
    *args: TagChildArg,  # Create a type for nav()?
    title: Optional[Union[str, Tag, TagList]] = None,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    position: Literal["static-top", "fixed-top", "fixed-bottom"] = "static-top",
    header: Optional[TagChildArg] = None,
    footer: Optional[TagChildArg] = None,
    bg: Optional[str] = None,
    inverse: bool = False,
    collapsible: bool = True,
    fluid: bool = True,
    window_title: Union[str, MISSING_TYPE] = MISSING,
    lang: Optional[str] = None
) -> Tag:

    return tags.html(
        get_window_title(title, window_title),
        tags.body(
            navs_bar(
                *args,
                title=title,
                id=id,
                selected=selected,
                position=position,
                header=header,
                footer=footer,
                bg=bg,
                inverse=inverse,
                collapsible=collapsible,
                fluid=fluid
            )
        ),
        lang=lang,
    )


def get_window_title(
    title: Optional[Union[str, Tag, TagList]],
    window_title: Union[str, MISSING_TYPE] = MISSING,
) -> Optional[HTMLDependency]:
    if title is not None and isinstance(window_title, MISSING_TYPE):
        # Try to infer window_title from contents of title
        window_title = " ".join(_find_characters(title))
        if not window_title:
            warn(
                "Unable to infer a `window_title` default from `title`. Consider providing a character string to `window_title`."
            )

    if isinstance(window_title, MISSING_TYPE):
        return None
    else:
        return head_content(tags.title(window_title))


@doc(
    "Create a fluid page.",
    parameters=_params,
    returns="A UI element.",
    see_also=[
        ":func:`~shiny.ui.page_fixed`",
        ":func:`~shiny.ui.page_bootstrap`",
        ":func:`~shiny.ui.page_navbar`",
    ],
)
def page_fluid(
    *args: Any, title: Optional[str] = None, lang: Optional[str] = None, **kwargs: str
) -> Tag:
    return page_bootstrap(
        div({"class": "container-fluid"}, *args, **kwargs), title=title, lang=lang
    )


@doc(
    "Create a fixed page.",
    parameters=_params,
    returns="A UI element.",
    see_also=[
        ":func:`~shiny.ui.page_fluid`",
        ":func:`~shiny.ui.page_bootstrap`",
        ":func:`~shiny.ui.page_navbar`",
    ],
)
def page_fixed(
    *args: Any, title: Optional[str] = None, lang: Optional[str] = None, **kwargs: str
) -> Tag:
    return page_bootstrap(
        div({"class": "container"}, *args, **kwargs), title=title, lang=lang
    )


@doc(
    "Create a Bootstrap UI page container.",
    parameters=_params,
    returns="A UI element.",
    see_also=[
        ":func:`~shiny.ui.page_fluid`",
        ":func:`~shiny.ui.page_navbar`",
    ],
)
def page_bootstrap(
    *args: Any, title: Optional[str] = None, lang: Optional[str] = None
) -> Tag:
    # TODO: implement theme (just Bootswatch for now?)
    page = TagList(*bootstrap_deps(), *args)
    head = tags.title(title) if title else None
    return tags.html(tags.head(head), tags.body(page), lang=lang)


def _find_characters(x: Any) -> List[str]:
    if isinstance(x, str):
        return [x]
    elif isinstance(x, list):
        return [y for y in x if isinstance(y, str)]
    else:
        return []
