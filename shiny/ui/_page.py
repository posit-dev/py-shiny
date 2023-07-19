from __future__ import annotations

__all__ = (
    "page_navbar",
    "page_fluid",
    "page_fixed",
    "page_bootstrap",
)

from typing import Literal, Optional, Sequence

from htmltools import MetadataNode, Tag, TagAttrs, TagChild, TagList, div, tags

from .._docstring import add_example
from .._namespaces import resolve_id
from ..types import MISSING, MISSING_TYPE, NavSetArg
from ._html_dependencies import bootstrap_deps
from ._navs import navset_bar
from ._utils import get_window_title


def page_navbar(
    *args: NavSetArg | MetadataNode | Sequence[MetadataNode],
    title: Optional[str | Tag | TagList] = None,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    position: Literal["static-top", "fixed-top", "fixed-bottom"] = "static-top",
    header: Optional[TagChild] = None,
    footer: Optional[TagChild] = None,
    bg: Optional[str] = None,
    inverse: bool = False,
    collapsible: bool = True,
    fluid: bool = True,
    window_title: str | MISSING_TYPE = MISSING,
    lang: Optional[str] = None,
) -> Tag:
    """
    Create a page with a navbar and a title.

    Parameters
    ----------

    args
        UI elements.
    title
        The browser window title (defaults to the host URL of the page). Can also be set
        as a side effect via :func:`~shiny.ui.panel_title`.
    id
        If provided, will create an input value that holds the currently selected nav
        item.
    selected
        Choose a particular nav item to select by default value (should match it's
        ``value``).
    position
        Determines whether the navbar should be displayed at the top of the page with
        normal scrolling behavior ("static-top"), pinned at the top ("fixed-top"), or
        pinned at the bottom ("fixed-bottom"). Note that using "fixed-top" or
        "fixed-bottom" will cause the navbar to overlay your body content, unless you
        add padding (e.g., ``tags.style("body {padding-top: 70px;}")``).
    header
        UI to display above the selected content.
    footer
        UI to display below the selected content.
    bg
        Background color of the navbar (a CSS color).
    inverse
        Either ``True`` for a light text color or ``False`` for a dark text color.
    collapsible
        ``True`` to automatically collapse the navigation elements into an expandable menu on mobile devices or narrow window widths.
    fluid
        ``True`` to use fluid layout; ``False`` to use fixed layout.
    window_title
        The browser's window title (defaults to the host URL of the page). Can also be
        set as a side effect via :func:`~shiny.ui.panel_title`.
    lang
        ISO 639-1 language code for the HTML page, such as ``"en"`` or ``"ko"``. This
        will be used as the lang in the ``<html>`` tag, as in ``<html lang="en">``. The
        default, `None`, results in an empty string.

    Returns
    -------
    :
        A UI element.

    See Also
    -------
    :func:`~shiny.ui.nav`
    :func:`~shiny.ui.nav_menu`
    :func:`~shiny.ui.navset_bar`
    :func:`~shiny.ui.page_fluid`

    Example
    -------
    See :func:`~shiny.ui.nav`.
    """

    return tags.html(
        get_window_title(title, window_title),
        tags.body(
            navset_bar(
                *args,
                title=title,
                id=resolve_id(id) if id else None,
                selected=selected,
                position=position,
                header=header,
                footer=footer,
                bg=bg,
                inverse=inverse,
                collapsible=collapsible,
                fluid=fluid,
            )
        ),
        lang=lang,
    )


@add_example()
def page_fluid(
    *args: TagChild | TagAttrs,
    title: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: str,
) -> Tag:
    """
    Create a fluid page.

    Parameters
    ----------

    args
        UI elements.
    title
        The browser window title (defaults to the host URL of the page). Can also be set
        as a side effect via :func:`~shiny.ui.panel_title`.
    lang
        ISO 639-1 language code for the HTML page, such as ``"en"`` or ``"ko"``. This
        will be used as the lang in the ``<html>`` tag, as in ``<html lang="en">``. The
        default, `None`, results in an empty string.
    kwargs
        Attributes on the page level container.

    Returns
    -------
    :
        A UI element.

    See Also
    -------
    :func:`~shiny.ui.page_fixed`
    :func:`~shiny.ui.page_bootstrap`
    :func:`~shiny.ui.page_navbar`
    """

    return page_bootstrap(
        div({"class": "container-fluid"}, *args, **kwargs), title=title, lang=lang
    )


@add_example()
def page_fixed(
    *args: TagChild | TagAttrs,
    title: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: str,
) -> Tag:
    """
    Create a fixed page.

    Parameters
    ----------

    args
        UI elements.
    title
        The browser window title (defaults to the host URL of the page). Can also be set
        as a side effect via :func:`~shiny.ui.panel_title`.
    lang
        ISO 639-1 language code for the HTML page, such as ``"en"`` or ``"ko"``. This
        will be used as the lang in the ``<html>`` tag, as in ``<html lang="en">``. The
        default, `None`, results in an empty string.
    kwargs
        Attributes on the page level container.

    Returns
    -------
    :
        A UI element.

    See Also
    -------
    :func:`~shiny.ui.page_fluid`
    :func:`~shiny.ui.page_bootstrap`
    :func:`~shiny.ui.page_navbar`
    """

    return page_bootstrap(
        div({"class": "container"}, *args, **kwargs), title=title, lang=lang
    )


# TODO: implement theme (just Bootswatch for now?)
def page_bootstrap(
    *args: TagChild | TagAttrs, title: Optional[str] = None, lang: Optional[str] = None
) -> Tag:
    """
    Create a Bootstrap UI page container.

    Parameters
    ----------

    args
        UI elements.
    title
        The browser window title (defaults to the host URL of the page). Can also be set
        as a side effect via :func:`~shiny.ui.panel_title`.
    lang
        ISO 639-1 language code for the HTML page, such as ``"en"`` or ``"ko"``. This
        will be used as the lang in the ``<html>`` tag, as in ``<html lang="en">``. The
        default, `None`, results in an empty string.

    Returns
    -------
    :
        A UI element.

    See Also
    -------
    :func:`~shiny.ui.page_fluid`
    :func:`~shiny.ui.page_navbar`
    """
    head = tags.title(title) if title else None
    return tags.html(tags.head(head), tags.body(*bootstrap_deps(), *args), lang=lang)
