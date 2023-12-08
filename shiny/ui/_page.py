from __future__ import annotations

__all__ = (
    "page_sidebar",
    "page_navbar",
    "page_fillable",
    "page_fluid",
    "page_fixed",
    "page_bootstrap",
    "page_output",
)

from typing import Literal, Optional, Sequence

from htmltools import (
    MetadataNode,
    Tag,
    TagAttrs,
    TagAttrValue,
    TagChild,
    TagList,
    css,
    div,
    head_content,
    tags,
)

from .._docstring import add_example
from .._namespaces import resolve_id_or_none
from ..types import MISSING, MISSING_TYPE, NavSetArg
from ._html_deps_external import bootstrap_deps
from ._html_deps_py_shiny import page_output_dependency
from ._html_deps_shinyverse import components_dependency
from ._navs import navset_bar
from ._sidebar import Sidebar, layout_sidebar
from ._tag import consolidate_attrs
from ._utils import get_window_title
from .css import CssUnit, as_css_padding, as_css_unit
from .fill._fill import as_fillable_container


def page_sidebar(
    sidebar: Sidebar,
    *args: TagChild | TagAttrs,
    title: Optional[str | Tag | TagList] = None,
    fillable: bool = True,
    fillable_mobile: bool = False,
    window_title: str | MISSING_TYPE = MISSING,
    lang: Optional[str] = None,
    **kwargs: TagAttrValue,
) -> Tag:
    """
    Create a page with a sidebar and a title.

    Parameters
    ----------
    sidebar
        Content to display in the sidebar.
    *args
        UI elements.
    title
        A title to display at the top of the page.
    fillable
        Whether or not the main content area should be considered a fillable
        (i.e., flexbox) container.
    fillable_mobile
        Whether or not ``fillable`` should apply on mobile devices.
    window_title
        The browser's window title (defaults to the host URL of the page). Can also be
        set as a side effect via :func:`~shiny.ui.panel_title`.
    lang
        ISO 639-1 language code for the HTML page, such as ``"en"`` or ``"ko"``. This
        will be used as the lang in the ``<html>`` tag, as in ``<html lang="en">``. The
        default, `None`, results in an empty string.
    **kwargs
        Additional attributes passed to :func:`~shiny.ui.layout_sidebar`.

    Returns
    -------
    :
        A UI element.
    """

    if isinstance(title, str):
        title = tags.h1(title, class_="bslib-page-title")

    attrs, children = consolidate_attrs(*args, **kwargs)

    return page_fillable(
        {"class": "bslib-page-sidebar"},
        title,
        layout_sidebar(
            sidebar,
            *children,
            # Make the main area background white instead of the default gray.
            {"style": "--bslib-shiny-preset-main-bg: white"},
            attrs,
            fillable=fillable,
            border=False,
            border_radius=False,
        ),
        get_window_title(title, window_title=window_title),
        padding=0,
        gap=0,
        lang=lang,
        fillable_mobile=fillable_mobile,
    )


def page_navbar(
    *args: NavSetArg | MetadataNode | Sequence[MetadataNode],
    title: Optional[str | Tag | TagList] = None,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    sidebar: Optional[Sidebar] = None,
    # Only page_navbar gets enhanced treatement for `fillable`
    # If an `*args`'s `data-value` attr string is in `fillable`, then the component is fillable
    fillable: bool | list[str] = True,
    fillable_mobile: bool = False,
    gap: Optional[CssUnit] = None,
    padding: Optional[CssUnit | list[CssUnit]] = None,
    position: Literal["static-top", "fixed-top", "fixed-bottom"] = "static-top",
    header: Optional[TagChild] = None,
    footer: Optional[TagChild] = None,
    bg: Optional[str] = None,
    inverse: bool = False,
    underline: bool = True,
    collapsible: bool = True,
    fluid: bool = True,
    window_title: str | MISSING_TYPE = MISSING,
    lang: Optional[str] = None,
) -> Tag:
    """
    Create a page with a navbar and a title.

    Parameters
    ----------
    *args
        UI elements.
    title
        The browser window title (defaults to the host URL of the page). Can also be set
        as a side effect via :func:`~shiny.ui.panel_title`.
    id
        If provided, will create an input value that holds the currently selected nav
        item.
    selected
        Choose a particular nav item to select by default value (should match its
        ``value``).
    sidebar
        A :func:`~shiny.ui.sidebar` component to display on every page.
    fillable
        Whether or not the main content area should be considered a fillable
        (i.e., flexbox) container.
    fillable_mobile
        Whether or not ``fillable`` should apply on mobile devices.
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
        ``True`` to automatically collapse the elements into an expandable menu on mobile devices or narrow window widths.
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
    * :func:`~shiny.ui.nav`
    * :func:`~shiny.ui.nav_menu`
    * :func:`~shiny.ui.navset_bar`
    * :func:`~shiny.ui.page_fluid`

    Example
    -------
    See :func:`~shiny.ui.nav`.
    """
    if sidebar is not None and not isinstance(sidebar, Sidebar):
        raise TypeError(
            "`sidebar=` is not a `Sidebar` instance. Use `ui.sidebar(...)` to create one."
        )

    pageClass = "bslib-page-navbar"
    if sidebar is not None:
        pageClass += " has-page-sidebar"

    tagAttrs: TagAttrs = {"class": pageClass}

    page_args = (
        tagAttrs,
        navset_bar(
            *args,
            title=title,
            id=resolve_id_or_none(id),
            selected=selected,
            sidebar=sidebar,
            fillable=fillable,
            gap=gap,
            padding=padding,
            position=position,
            header=header,
            footer=footer,
            bg=bg,
            inverse=inverse,
            underline=underline,
            collapsible=collapsible,
            fluid=fluid,
        ),
        get_window_title(title, window_title=window_title),
    )
    page_kwargs = {
        "title": None,
        "lang": lang,
    }

    # If a sidebar is provided, we want the layout_sidebar(fill = TRUE) component
    # (which is a sibling of the <nav>) to always fill the page
    if fillable is False and sidebar is None:
        return page_bootstrap(
            *page_args,
            **page_kwargs,
        )

    else:
        return page_fillable(
            *page_args,
            fillable_mobile=fillable_mobile,
            padding=0,
            gap=0,
            **page_kwargs,
        )


def page_fillable(
    *args: TagChild | TagAttrs,
    padding: Optional[CssUnit | list[CssUnit]] = None,
    gap: Optional[CssUnit] = None,
    fillable_mobile: bool = False,
    title: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: TagAttrValue,
) -> Tag:
    """
    Create a fillable page.

    Parameters
    ----------
    *args
        UI elements.
    padding
        Padding to use for the body. See :func:`~shiny.ui.css_unit.as_css_padding`
        for more details.
    fillable_mobile
        Whether or not the page should fill the viewport's height on mobile devices
        (i.e., narrow windows).
    gap
        A CSS length unit passed through :func:`~shiny.ui.css_unit.as_css_unit`
        defining the `gap` (i.e., spacing) between elements provided to `*args`.
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
    * :func:`~shiny.ui.page_fluid`
    * :func:`~shiny.ui.page_fixed`
    """
    attrs, children = consolidate_attrs(*args, **kwargs)

    style = css(padding=as_css_padding(padding), gap=as_css_unit(gap))

    page = page_bootstrap(
        head_content(tags.style("html { height: 100%; }")),
        {"class": "bslib-page-fill bslib-gap-spacing", "style": style},
        {"class": "bslib-flow-mobile"} if not fillable_mobile else None,
        attrs,
        *children,
        components_dependency(),
        title=title,
        lang=lang,
    )

    # page returns a <html> tag, but we need to make the <body> fillable
    body = page.children[1]
    if not isinstance(body, Tag) or body.name != "body":
        raise ValueError("Expected a <body> tag")

    page.children[1] = as_fillable_container(body)

    return page


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
    *args
        UI elements.
    title
        The browser window title (defaults to the host URL of the page). Can also be set
        as a side effect via :func:`~shiny.ui.panel_title`.
    lang
        ISO 639-1 language code for the HTML page, such as ``"en"`` or ``"ko"``. This
        will be used as the lang in the ``<html>`` tag, as in ``<html lang="en">``. The
        default, `None`, results in an empty string.
    **kwargs
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
    *args
        UI elements.
    title
        The browser window title (defaults to the host URL of the page). Can also be set
        as a side effect via :func:`~shiny.ui.panel_title`.
    lang
        ISO 639-1 language code for the HTML page, such as ``"en"`` or ``"ko"``. This
        will be used as the lang in the ``<html>`` tag, as in ``<html lang="en">``. The
        default, `None`, results in an empty string.
    **kwargs
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
    *args: TagChild | TagAttrs,
    title: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: TagAttrValue,
) -> Tag:
    """
    Create a Bootstrap UI page container.

    Parameters
    ----------
    *args
        UI elements.
    title
        The browser window title (defaults to the host URL of the page). Can also be set
        as a side effect via :func:`~shiny.ui.panel_title`.
    lang
        ISO 639-1 language code for the HTML page, such as ``"en"`` or ``"ko"``. This
        will be used as the lang in the ``<html>`` tag, as in ``<html lang="en">``. The
        default, `None`, results in an empty string.
    **kwargs
        Attributes on the the `<body>` tag.

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
    return tags.html(
        tags.head(head),
        tags.body(*bootstrap_deps(), *args, **kwargs),
        lang=lang,
    )


def page_output(id: str) -> Tag:
    """
    Create a page container where the entire body is a UI output.

    Parameters
    ----------
    id
        An output id.

    Returns
    -------
    :
        A UI element which is meant to be used as a page container.
    """
    return tags.html(
        tags.head(),
        tags.body(id=id, class_="shiny-page-output"),
        page_output_dependency(),
        lang="en",
    )
