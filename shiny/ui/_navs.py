__all__ = (
    "nav",
    "nav_menu",
    "nav_content",
    "nav_item",
    "nav_spacer",
    "navs_tab",
    "navs_tab_card",
    "navs_pill",
    "navs_pill_card",
    "navs_pill_list",
    "navs_hidden",
    "navs_bar",
)

import sys
from typing import Optional, Any, Tuple

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

from htmltools import jsx_tag_create, JSXTag, TagList, TagChildArg, JSXTagAttrArg

from .._docstring import doc
from ._html_dependencies import nav_deps

_common_params = {
    "title": "A title to display. Can be a character string or UI elements (i.e., tags).",
    "value": """
    The value of the item. This is used to determine whether the item is active (when
    an ``id`` is provided to the nav container), programmatically select the item (e.g.,
    :func:`~shiny.ui.update_navs`), and/or be provided to the ``selected`` argument of
    the navigation container (e.g., :func:`~shiny.ui.navs_tab`).
    """,
}


def see_also(this_fn: str):
    fns = list(__all__)
    fns.remove(this_fn)
    return [f":func:`~shiny.ui.{fn}`" for fn in fns]


@doc(
    "Create a nav item pointing to some internal content.",
    parameters={
        **_common_params,
        "args": "UI elements to display when the item is active.",
    },
    returns="""
    A UI element representing both the navigation link as well as the content it links
    to.
    """,
    see_also=see_also("nav"),
)
def nav(
    title: Any,
    *args: TagChildArg,
    value: Optional[str] = None,
    icon: TagChildArg = None,
) -> JSXTag:
    if not value:
        value = title
    return _nav_tag("Nav", *args, value=value, title=TagList(icon, title))


@doc(
    "Create a menu of nav items.",
    parameters={
        **_common_params,
        "args": """
        A collection of nav items (e.g., :func:`~shiny.ui.nav`) and/or strings.
        Strings will be rendered as a section header unless the string is a set
        of two or more hyphens (e.g., ``---``), in which case it will be rendered
        as a divider.
        """,
        "align": "Horizontal alignment of the dropdown menu relative to dropdown toggle.",
    },
    returns="A UI element representing both the navigation menu.",
    note="See :func:`~shiny.ui.nav` for an example.",
    see_also=see_also("nav_menu"),
)
def nav_menu(
    title: TagChildArg,
    *args: TagChildArg,
    value: Optional[str] = None,
    icon: TagChildArg = None,
    align: Literal["left", "right"] = "left",
) -> JSXTag:
    if not value:
        value = str(title)
    return _nav_tag(
        "NavMenu", *args, value=value, title=TagList(icon, title), align=align
    )


def nav_content(value: str, *args: TagChildArg, icon: TagChildArg = None) -> JSXTag:
    return nav(None, *args, value=value, icon=icon)


@doc(
    "Create a nav item.",
    parameters={
        **_common_params,
        "args": "UI elements to display as the nav item.",
    },
    returns="A UI element.",
    note="See :func:`~shiny.ui.nav` for an example.",
    see_also=see_also("nav_item"),
)
def nav_item(*args: TagChildArg) -> JSXTag:
    return _nav_tag("NavItem", *args)


@doc(
    "Create space between nav items.",
    returns="A UI element.",
    see_also=see_also("nav_spacer"),
)
def nav_spacer() -> JSXTag:
    return _nav_tag("NavSpacer")


_navs_params = {
    **_common_params,
    "args": "A collection of nav items (e.g., :func:`shiny.ui.nav`).",
    "id": """
    If provided, will create an input value that holds the currently selected nav item.
    """,
    "selected": """
    Choose a particular nav item to select by default value (should match it's ``value``).
    """,
    "header": "UI to display above the selected content.",
    "footer": "UI to display below the selected content.",
    "placement": "Placement of the nav items relative to the content.",
    "fluid": "`True` to use fluid layout; `False` to use fixed layout.",
}


@doc(
    "Render a collection of nav items as a tabset.",
    parameters=_navs_params,
    returns="A UI element.",
    note="See :func:`~shiny.ui.nav` for an example.",
    see_also=see_also("navs_tab"),
)
def navs_tab(
    *args: TagChildArg,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: Optional[TagChildArg] = None,
    footer: Optional[TagChildArg] = None,
) -> JSXTag:
    return _nav_tag(
        "Navs",
        *args,
        type="tabs",
        id=id,
        selected=selected,
        header=header,
        footer=footer,
    )


@doc(
    "Render a collection of nav items as a tabset inside a card container.",
    parameters=_navs_params,
    returns="A UI element.",
    note="See :func:`~shiny.ui.nav` for an example.",
    see_also=see_also("navs_tab_card"),
)
def navs_tab_card(
    *args: TagChildArg,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: Optional[TagChildArg] = None,
    footer: Optional[TagChildArg] = None,
) -> JSXTag:
    return _nav_tag(
        "NavsCard",
        *args,
        type="tabs",
        id=id,
        selected=selected,
        header=header,
        footer=footer,
    )


@doc(
    "Render a collection of nav items as a pillset.",
    parameters=_navs_params,
    returns="A UI element.",
    note="See :func:`~shiny.ui.nav` for an example.",
    see_also=see_also("navs_pill"),
)
def navs_pill(
    *args: TagChildArg,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: Optional[TagChildArg] = None,
    footer: Optional[TagChildArg] = None,
) -> JSXTag:
    return _nav_tag(
        "Navs",
        *args,
        type="pills",
        id=id,
        selected=selected,
        header=header,
        footer=footer,
    )


@doc(
    "Render a collection of nav items as a pillset inside a card container.",
    parameters=_navs_params,
    returns="A UI element.",
    note="See :func:`~shiny.ui.nav` for an example.",
    see_also=see_also("navs_pill_card"),
)
def navs_pill_card(
    *args: TagChildArg,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: Optional[TagChildArg] = None,
    footer: Optional[TagChildArg] = None,
    placement: Literal["above", "below"] = "above",
) -> JSXTag:
    return _nav_tag(
        "NavsCard",
        *args,
        type="pills",
        id=id,
        selected=selected,
        header=header,
        footer=footer,
        placement=placement,
    )


@doc(
    "Render a collection of nav items as a vertical pillset.",
    parameters={
        **_navs_params,
        "well": "``True`` to place a well (gray rounded rectangle) around the navigation list.",
        "widths": "Column widths of the navigation list and tabset content areas respectively.",
    },
    returns="A UI element.",
    see_also=see_also("navs_pill_list"),
)
def navs_pill_list(
    *args: TagChildArg,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: Optional[TagChildArg] = None,
    footer: Optional[TagChildArg] = None,
    well: bool = True,
    fluid: bool = True,
    widths: Tuple[int, int] = (4, 8),
) -> JSXTag:
    return _nav_tag(
        "NavsList",
        *args,
        id=id,
        selected=selected,
        header=header,
        footer=footer,
        well=well,
        fluid=fluid,
        widthNav=widths[0],
        widthContent=widths[1],
    )


@doc(
    "Render nav contents without the nav items.",
    parameters=_navs_params,
    returns="A UI element.",
    see_also=see_also("navs_hidden"),
)
def navs_hidden(
    *args: TagChildArg,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: Optional[TagChildArg] = None,
    footer: Optional[TagChildArg] = None,
) -> JSXTag:
    return _nav_tag(
        "Navs",
        *args,
        type="hidden",
        id=id,
        selected=selected,
        header=header,
        footer=footer,
    )


navs_bar_params = {
    **_navs_params,
    "title": "Title to display in the navbar.",
    "position": """
    Determines whether the navbar should be displayed at the top of the page with
    normal scrolling behavior ("static-top"), pinned at the top ("fixed-top"), or
    pinned at the bottom ("fixed-bottom"). Note that using "fixed-top" or
    "fixed-bottom" will cause the navbar to overlay your body content, unless you
    add padding (e.g., ``tags.style("body {padding-top: 70px;}")``).
    """,
    "bg": "Background color of the navbar (a CSS color).",
    "inverse": """
    Either ``True`` for a light text color or ``False`` for a dark text color.
    """,
    "collapsible": """
    ``True`` to automatically collapse the navigation elements into a menu when the
    width of the browser is less than 940 pixels (useful for viewing on smaller
    touchscreen device)
    """,
}


@doc(
    "Render a collection of nav items as a navbar.",
    parameters=navs_bar_params,
    returns="A UI element.",
    note="See :func:`~shiny.ui.nav` for an example.",
    see_also=[":func:`~shiny.ui.page_navbar`"] + see_also("navs_bar"),
)
def navs_bar(
    *args: TagChildArg,
    title: Optional[TagChildArg] = None,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    position: Literal["static-top", "fixed-top", "fixed-bottom"] = "static-top",
    header: Optional[TagChildArg] = None,
    footer: Optional[TagChildArg] = None,
    bg: Optional[str] = None,
    # TODO: default to 'auto', like we have in R
    inverse: bool = False,
    collapsible: bool = True,
    fluid: bool = True,
) -> JSXTag:
    return _nav_tag(
        "NavsBar",
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
        fluid=fluid,
    )


def _nav_tag(name: str, *args: TagChildArg, **kwargs: JSXTagAttrArg) -> JSXTag:
    tag = jsx_tag_create("bslib." + name)
    return tag(nav_deps(), *args, **kwargs)
