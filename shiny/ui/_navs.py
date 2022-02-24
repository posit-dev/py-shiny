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

from .._docstring import add_example
from ._html_dependencies import nav_deps


@add_example()
def nav(
    title: Any,
    *args: TagChildArg,
    value: Optional[str] = None,
    icon: TagChildArg = None,
) -> JSXTag:
    """
    Create a nav item pointing to some internal content.

    Parameters
    ----------
    title
        A title to display. Can be a character string or UI elements (i.e., tags).
    args
        UI elements to display when the item is active.
    value
        The value of the item. This is used to determine whether the item is active
        (when an ``id`` is provided to the nav container), programmatically select the
        item (e.g., :func:`~shiny.ui.update_navs`), and/or be provided to the
        ``selected`` argument of the navigation container (e.g.,
        :func:`~shiny.ui.navs_tab`).
    icon
        An icon to appear inline with the button/link.
    Returns
    -------
        A UI element representing both the navigation link as well as the content it
        links to.

    See Also
    -------
    ~shiny.ui.nav_menu
    ~shiny.ui.nav_content
    ~shiny.ui.nav_item
    ~shiny.ui.nav_spacer
    ~shiny.ui.navs_bar
    ~shiny.ui.navs_tab
    ~shiny.ui.navs_pill
    ~shiny.ui.navs_tab_card
    ~shiny.ui.navs_pill_card
    ~shiny.ui.navs_hidden
    """
    if not value:
        value = title
    return _nav_tag("Nav", *args, value=value, title=TagList(icon, title))


def nav_menu(
    title: TagChildArg,
    *args: TagChildArg,
    value: Optional[str] = None,
    icon: TagChildArg = None,
    align: Literal["left", "right"] = "left",
) -> JSXTag:
    """
    Create a menu of nav items.

    Parameters
    ----------
    title
        A title to display. Can be a character string or UI elements (i.e., tags).
    args
        A collection of nav items (e.g., :func:`~shiny.ui.nav`) and/or strings.
        Strings will be rendered as a section header unless the string is a set
        of two or more hyphens (e.g., ``---``), in which case it will be rendered
        as a divider.
    value
        The value of the item. This is used to determine whether the item is active
        (when an ``id`` is provided to the nav container), programmatically select the
        item (e.g., :func:`~shiny.ui.update_navs`), and/or be provided to the
        ``selected`` argument of the navigation container (e.g.,
        :func:`~shiny.ui.navs_tab`).
    icon
        An icon to appear inline with the button/link.
    align
        Horizontal alignment of the dropdown menu relative to dropdown toggle.

    Returns
    -------
    A UI element representing both the navigation menu.

    See Also
    -------
    ~shiny.ui.nav
    ~shiny.ui.nav_item
    ~shiny.ui.nav_spacer
    ~shiny.ui.navs_bar
    ~shiny.ui.navs_tab
    ~shiny.ui.navs_pill
    ~shiny.ui.navs_tab_card
    ~shiny.ui.navs_pill_card
    ~shiny.ui.navs_hidden

    Example
    -------
    See :func:`~shiny.ui.nav`
    """
    if not value:
        value = str(title)
    return _nav_tag(
        "NavMenu", *args, value=value, title=TagList(icon, title), align=align
    )


def nav_content(value: str, *args: TagChildArg, icon: TagChildArg = None) -> JSXTag:
    """
    Create a nav item pointing to some internal content with no title.

    Mainly useful when used inside :func:`~shiny.ui.navs_hidden`

    Parameters
    ----------
    value
        The value of the item. This is used to determine whether the item is active
    args
        UI elements to display when the item is active.
    icon
        An optional icon.

    Returns
    -------
    A UI element.

    See Also
    --------
    ~shiny.ui.navs_hidden

    Example
    -------
    See :func:`~shiny.ui.nav`
    """

    return nav(None, *args, value=value, icon=icon)


def nav_item(*args: TagChildArg) -> JSXTag:
    """
    Create a nav item.

    Parameters
    ----------
    args
        UI elements to display as the nav item.

    Returns
    -------
    A UI element.

    See Also
    -------
    ~shiny.ui.nav
    ~shiny.ui.nav_menu
    ~shiny.ui.nav_content
    ~shiny.ui.nav_spacer
    ~shiny.ui.navs_bar
    ~shiny.ui.navs_tab
    ~shiny.ui.navs_pill
    ~shiny.ui.navs_tab_card
    ~shiny.ui.navs_pill_card
    ~shiny.ui.navs_hidden

    Example
    -------
    See :func:`~shiny.ui.nav`
    """
    return _nav_tag("NavItem", *args)


def nav_spacer() -> JSXTag:
    """
    Create space between nav items.

    Returns
    -------
    A UI element.

    See Also
    -------
    ~shiny.ui.nav
    ~shiny.ui.nav_menu
    ~shiny.ui.nav_content
    ~shiny.ui.nav_item
    ~shiny.ui.navs_bar
    ~shiny.ui.navs_tab
    ~shiny.ui.navs_pill
    ~shiny.ui.navs_tab_card
    ~shiny.ui.navs_pill_card
    ~shiny.ui.navs_hidden

    Example
    -------
    See :func:`~shiny.ui.nav`
    """
    return _nav_tag("NavSpacer")


def navs_tab(
    *args: TagChildArg,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: Optional[TagChildArg] = None,
    footer: Optional[TagChildArg] = None,
) -> JSXTag:
    """
    Render nav items as a tabset.

    Parameters
    ----------
    args
        A collection of nav items (e.g., :func:`shiny.ui.nav`).
    id
        If provided, will create an input value that holds the currently selected nav
        item.
    selected
        Choose a particular nav item to select by default value (should match it's
        ``value``).
    header
        UI to display above the selected content.
    footer
        UI to display below the selected content.

    Returns
    -------
    A UI element.

    See Also
    -------
    ~shiny.ui.nav
    ~shiny.ui.nav_menu
    ~shiny.ui.nav_content
    ~shiny.ui.nav_item
    ~shiny.ui.nav_spacer
    ~shiny.ui.navs_bar
    ~shiny.ui.navs_pill
    ~shiny.ui.navs_tab_card
    ~shiny.ui.navs_pill_card
    ~shiny.ui.navs_hidden

    Example
    -------
    See :func:`~shiny.ui.nav`
    """

    return _nav_tag(
        "Navs",
        *args,
        type="tabs",
        id=id,
        selected=selected,
        header=header,
        footer=footer,
    )


def navs_tab_card(
    *args: TagChildArg,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: Optional[TagChildArg] = None,
    footer: Optional[TagChildArg] = None,
) -> JSXTag:
    """
    Render nav items as a tabset inside a card container.

    Parameters
    ----------
    args
        A collection of nav items (e.g., :func:`shiny.ui.nav`).
    id
        If provided, will create an input value that holds the currently selected nav
        item.
    selected
        Choose a particular nav item to select by default value (should match it's
        ``value``).
    header
        UI to display above the selected content.
    footer
        UI to display below the selected content.

    Returns
    -------
    A UI element.

    See Also
    -------
    ~shiny.ui.nav
    ~shiny.ui.nav_menu
    ~shiny.ui.nav_content
    ~shiny.ui.nav_item
    ~shiny.ui.nav_spacer
    ~shiny.ui.navs_bar
    ~shiny.ui.navs_tab
    ~shiny.ui.navs_pill
    ~shiny.ui.navs_pill_card
    ~shiny.ui.navs_hidden

    Example
    -------
    See :func:`~shiny.ui.nav`
    """

    return _nav_tag(
        "NavsCard",
        *args,
        type="tabs",
        id=id,
        selected=selected,
        header=header,
        footer=footer,
    )


def navs_pill(
    *args: TagChildArg,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: Optional[TagChildArg] = None,
    footer: Optional[TagChildArg] = None,
) -> JSXTag:
    """
    Render nav items as a pillset.

    Parameters
    ----------
    args
        A collection of nav items (e.g., :func:`shiny.ui.nav`).
    id
        If provided, will create an input value that holds the currently selected nav
        item.
    selected
        Choose a particular nav item to select by default value (should match it's
        ``value``).
    header
        UI to display above the selected content.
    footer
        UI to display below the selected content.

    Returns
    -------
    A UI element.

    See Also
    -------
    ~shiny.ui.nav
    ~shiny.ui.nav_menu
    ~shiny.ui.nav_content
    ~shiny.ui.nav_item
    ~shiny.ui.nav_spacer
    ~shiny.ui.navs_bar
    ~shiny.ui.navs_tab
    ~shiny.ui.navs_tab_card
    ~shiny.ui.navs_pill_card
    ~shiny.ui.navs_hidden

    Example
    -------
    See :func:`~shiny.ui.nav`
    """

    return _nav_tag(
        "Navs",
        *args,
        type="pills",
        id=id,
        selected=selected,
        header=header,
        footer=footer,
    )


def navs_pill_card(
    *args: TagChildArg,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: Optional[TagChildArg] = None,
    footer: Optional[TagChildArg] = None,
    placement: Literal["above", "below"] = "above",
) -> JSXTag:
    """
    Render nav items as a pillset inside a card container.

    Parameters
    ----------
    args
        A collection of nav items (e.g., :func:`shiny.ui.nav`).
    id
        If provided, will create an input value that holds the currently selected nav
        item.
    selected
        Choose a particular nav item to select by default value (should match it's
        ``value``).
    header
        UI to display above the selected content.
    footer
        UI to display below the selected content.
    placement
        Placement of the nav items relative to the content.

    Returns
    -------
    A UI element.

    See Also
    -------
    ~shiny.ui.nav
    ~shiny.ui.nav_menu
    ~shiny.ui.nav_content
    ~shiny.ui.nav_item
    ~shiny.ui.nav_spacer
    ~shiny.ui.navs_bar
    ~shiny.ui.navs_tab
    ~shiny.ui.navs_pill
    ~shiny.ui.navs_tab_card
    ~shiny.ui.navs_hidden

    Example
    -------
    See :func:`~shiny.ui.nav`
    """

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
    """
    Render nav items as a vertical pillset.

    Parameters
    ----------
    args
        A collection of nav items (e.g., :func:`shiny.ui.nav`).
    id
        If provided, will create an input value that holds the currently selected nav
        item.
    selected
        Choose a particular nav item to select by default value (should match it's
        ``value``).
    header
        UI to display above the selected content.
    footer
        UI to display below the selected content.
    well
        ``True`` to place a well (gray rounded rectangle) around the navigation list.
    fluid
        ``True`` to use fluid layout; `False` to use fixed layout.
    widths
        Column widths of the navigation list and tabset content areas respectively.

    Returns
    -------
    A UI element.

    See Also
    -------
    ~shiny.ui.nav
    ~shiny.ui.nav_menu
    ~shiny.ui.nav_content
    ~shiny.ui.nav_item
    ~shiny.ui.nav_spacer
    ~shiny.ui.navs_tab
    ~shiny.ui.navs_tab_card
    ~shiny.ui.navs_pill
    ~shiny.ui.navs_pill_card
    ~shiny.ui.navs_hidden
    ~shiny.ui.navs_bar
    ~shiny.ui.navs_hidden

    Example
    -------
    See :func:`~shiny.ui.nav`
    """

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


@add_example()
def navs_hidden(
    *args: TagChildArg,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: Optional[TagChildArg] = None,
    footer: Optional[TagChildArg] = None,
) -> JSXTag:
    """
    Render nav contents without the nav items.

    Parameters
    ----------
    args
        A collection of nav items (e.g., :func:`shiny.ui.nav`).
    id
        If provided, will create an input value that holds the currently selected nav
        item.
    selected
        Choose a particular nav item to select by default value (should match it's
        ``value``).
    header
        UI to display above the selected content.
    footer
        UI to display below the selected content.

    Returns
    -------
    A UI element.

    See Also
    --------
    ~shiny.ui.nav
    ~shiny.ui.nav_menu
    ~shiny.ui.nav_content
    ~shiny.ui.nav_item
    ~shiny.ui.nav_spacer
    ~shiny.ui.navs_tab
    ~shiny.ui.navs_tab_card
    ~shiny.ui.navs_pill
    ~shiny.ui.navs_pill_card
    ~shiny.ui.navs_pill_list
    ~shiny.ui.navs_bar
    """

    return _nav_tag(
        "Navs",
        *args,
        type="hidden",
        id=id,
        selected=selected,
        header=header,
        footer=footer,
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
    """
    Render nav items as a navbar.

    Parameters
    ----------
    args
        A collection of nav items (e.g., :func:`shiny.ui.nav`).
    title
        Title to display in the navbar.
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
        ``True`` to automatically collapse the navigation elements into a menu when the
        width of the browser is less than 940 pixels (useful for viewing on smaller
        touchscreen device)
    fluid
        ``True`` to use fluid layout; ``False`` to use fixed layout.

    Returns
    -------
    A UI element.

    See Also
    -------
    ~shiny.ui.page_navbar
    ~shiny.ui.nav
    ~shiny.ui.nav_menu
    ~shiny.ui.nav_content
    ~shiny.ui.nav_item
    ~shiny.ui.nav_spacer
    ~shiny.ui.navs_tab
    ~shiny.ui.navs_pill
    ~shiny.ui.navs_tab_card
    ~shiny.ui.navs_pill_card
    ~shiny.ui.navs_hidden

    Example
    -------
    See :func:`~shiny.ui.nav`.
    """

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
