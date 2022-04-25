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

import copy
import re
import sys
from typing import Optional, Tuple, List, Union, NamedTuple, cast, Any

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

from htmltools import tags, Tag, TagList, TagChildArg, div

from ._bootstrap import row, column
from .._docstring import add_example
from ._html_dependencies import bootstrap_deps
from .._utils import private_random_int

# -----------------------------------------------------------------------------
# Navigation items
# -----------------------------------------------------------------------------
class Nav(NamedTuple):
    nav: Tag
    # nav_item()/nav_spacer() have None as their content
    content: Optional[Tag]

    def render(
        self, selected: Optional[str], id: str, is_menu: bool = False
    ) -> Tuple[Tag, Optional[Tag]]:
        """
        Add appropriate tag attributes to nav/content tags when linking to internal content.
        """

        x = copy.copy(self)

        # Nothing to do for nav_item()/nav_spacer()
        if x.content is None:
            return x.nav, None

        # At least currently, in the case where both nav and content are tags
        # (i.e., nav()), the nav always has a child <a> tag...I'm not sure if
        # there's a way to statically type this
        a_tag = cast(Tag, x.nav.children[0])
        if is_menu:
            a_tag.add_class("dropdown-item")
        else:
            a_tag.add_class("nav-link")
            x.nav.add_class("nav-item")

        # Hyperlink the nav to the content
        x.content.attrs["id"] = id
        a_tag.attrs["href"] = f"#{id}"

        # Mark the nav/content as active if it should be
        if isinstance(selected, str) and selected == self.get_value():
            x.content.add_class("active")
            a_tag.add_class("active")

        x.nav.children[0] = a_tag

        return x.nav, x.content

    def get_value(self) -> Optional[str]:
        if self.content is None:
            return None
        a_tag = cast(Tag, self.nav.children[0])
        return a_tag.attrs.get("data-value", None)


@add_example()
def nav(
    title: Union[str, Tag, TagList, None],
    *args: TagChildArg,
    value: Optional[str] = None,
    icon: TagChildArg = None,
) -> Nav:
    """
    Create a nav item pointing to some internal content.

    Parameters
    ----------
    title
        A title to display. Can be a character string or UI elements (i.e., tags).
    *args
        UI elements to display when the item is active.
    value
        The value of the item. This is used to determine whether the item is active
        (when an ``id`` is provided to the nav container), programmatically select the
        item (e.g., :func:`~shiny.ui.update_navs`), and/or be provided to the
        ``selected`` argument of the navigation container (e.g.,
        :func:`~shiny.ui.navs_tab`).
    icon
        An icon to appear inline with the button/link.

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
        value = str(title)

    # N.B. at this point, we don't have enough info to link the nav to the content
    # or add relevant classes. That's done later by consumers (i.e. nav containers)
    link = tags.a(
        icon,
        title,
        data_bs_toggle="tab",
        data_value=value,
        role="tab",
    )

    return Nav(
        nav=tags.li(link),
        content=div(*args, class_="tab-pane", role="tabpanel", data_value=value),
    )


def nav_content(value: str, *args: TagChildArg) -> Nav:
    """
    Create a nav item pointing to some internal content with no title.

    Mainly useful when used inside :func:`~shiny.ui.navs_hidden`

    Parameters
    ----------
    value
        The value of the item. This is used to determine whether the item is active
    *args
        UI elements to display when the item is active.
    icon
        An optional icon.

    See Also
    --------
    ~shiny.ui.navs_hidden

    Example
    -------
    See :func:`~shiny.ui.nav`
    """
    return nav(None, *args, value=value)


def nav_item(*args: TagChildArg) -> Nav:
    """
    Create a nav item.

    Parameters
    ----------
    *args
        UI elements to display as the nav item.

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
    return Nav(nav=tags.li(*args), content=None)


def nav_spacer() -> Nav:
    """
    Create space between nav items.

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

    return Nav(nav=tags.li(class_="bslib-nav-spacer"), content=None)


class NavMenu:
    def __init__(
        self,
        *args: Union[Nav, str],
        title: TagChildArg,
        value: Optional[str] = None,
        align: Literal["left", "right"] = "left",
    ) -> None:
        self.nav_items: List[Nav] = [menu_string_as_nav(x) for x in args]
        self.title = title
        self.value = value
        self.align = align

    def render(self, selected: Optional[str], **kwargs: Any) -> Tuple[Tag, TagList]:
        nav, content = render_tabset(
            *self.nav_items,
            ul_class=f"dropdown-menu {'dropdown-menu-right' if self.align == 'right' else ''}",
            id=None,
            selected=selected,
            is_menu=True,
        )

        active = False
        for tab in content.children:
            if isinstance(tab, Tag) and tab.has_class("active"):
                active = True
                break

        return (
            tags.li(
                tags.a(
                    self.title,
                    class_=f"nav-link dropdown-toggle {'active' if active else ''}",
                    data_bs_toggle="dropdown",
                    # N.B. this value is only relevant for locating the insertion/removal
                    # of items inside the nav container
                    data_value=self.value,
                    href="#",
                    role="button",
                ),
                nav,
                class_="nav-item dropdown",
            ),
            content.children,
        )

    def get_value(self) -> Optional[str]:
        return None


def menu_string_as_nav(x: Union[str, Nav]) -> Nav:
    if not isinstance(x, str):
        return x

    if re.match(r"^\-+$", x):
        nav = tags.li(class_="dropdown-divider")
    else:
        nav = tags.li(x, class_="dropdown-header")

    return Nav(nav=nav, content=None)


def nav_menu(
    title: TagChildArg,
    *args: Union[Nav, str],
    value: Optional[str] = None,
    icon: TagChildArg = None,
    align: Literal["left", "right"] = "left",
) -> NavMenu:
    """
    Create a menu of nav items.

    Parameters
    ----------
    title
        A title to display. Can be a character string or UI elements (i.e., tags).
    *args
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
    return NavMenu(
        *args,
        title=TagList(icon, title),
        value=value,
        align=align,
    )


# -----------------------------------------------------------------------------
# Navigation containers
# -----------------------------------------------------------------------------
def navs_tab(
    *args: Union[Nav, NavMenu],
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: TagChildArg = None,
    footer: TagChildArg = None,
) -> TagList:
    """
    Render nav items as a tabset.

    Parameters
    ----------
    *args
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

    nav, content = render_tabset(
        *args, ul_class="nav nav-tabs", id=id, selected=selected
    )
    return TagList(nav, header, content, footer)


def navs_pill(
    *args: Union[Nav, NavMenu],
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: TagChildArg = None,
    footer: TagChildArg = None,
) -> TagList:
    """
    Render nav items as a pillset.

    Parameters
    ----------
    *args
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

    nav, content = render_tabset(
        *args, ul_class="nav nav-pills", id=id, selected=selected
    )
    return TagList(nav, header, content, footer)


@add_example()
def navs_hidden(
    *args: Union[Nav, NavMenu],
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: TagChildArg = None,
    footer: TagChildArg = None,
) -> TagList:
    """
    Render nav contents without the nav items.

    Parameters
    ----------
    *args
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

    nav, content = render_tabset(
        *args, ul_class="nav nav-hidden", id=id, selected=selected
    )
    return TagList(nav, header, content, footer)


def navs_tab_card(
    *args: Union[Nav, NavMenu],
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: TagChildArg = None,
    footer: TagChildArg = None,
) -> Tag:
    """
    Render nav items as a tabset inside a card container.

    Parameters
    ----------
    *args
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

    nav, content = render_tabset(
        *args, ul_class="nav nav-tabs card-header-tabs", id=id, selected=selected
    )
    return card(header, content, footer, header=nav)


def navs_pill_card(
    *args: Union[Nav, NavMenu],
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: TagChildArg = None,
    footer: TagChildArg = None,
    placement: Literal["above", "below"] = "above",
) -> Tag:
    """
    Render nav items as a pillset inside a card container.

    Parameters
    ----------
    *args
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

    nav, content = render_tabset(
        *args, ul_class="nav nav-pills card-header-pills", id=id, selected=selected
    )

    if placement == "below":
        return card(header, content, footer, footer=nav)
    else:
        return card(header, content, footer, header=nav)


def navs_pill_list(
    *args: Union[Nav, NavMenu],
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: TagChildArg = None,
    footer: TagChildArg = None,
    well: bool = True,
    widths: Tuple[int, int] = (4, 8),
) -> Tag:
    """
    Render nav items as a vertical pillset.

    Parameters
    ----------
    *args
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

    nav, content = render_tabset(
        *args, ul_class="nav nav-pills nav-stacked", id=id, selected=selected
    )
    return row(
        column(widths[0], nav, class_="well" if well else None),
        column(widths[1], header, content, footer),
    )


def navs_bar(
    *args: Union[Nav, NavMenu],
    title: TagChildArg,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    position: Literal[
        "static-top", "fixed-top", "fixed-bottom", "sticky-top"
    ] = "static-top",
    header: TagChildArg = None,
    footer: TagChildArg = None,
    bg: Optional[str] = None,
    # TODO: default to 'auto', like we have in R (parse color via webcolors?)
    inverse: bool = False,
    collapsible: bool = True,
    fluid: bool = True,
) -> TagList:
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

    nav, content = render_tabset(
        *args, ul_class="nav navbar-nav", id=id, selected=selected
    )

    nav_container = div(
        {"class": "container-fluid" if fluid else "container"},
        tags.a({"class": "navbar-brand", "href": "#"}, title),
    )
    if collapsible:
        collapse_id = "navbar-collapse-" + private_random_int(1000, 10000)
        nav_container.append(
            tags.button(
                tags.span(class_="navbar-toggler-icon"),
                class_="navbar-toggler",
                type="button",
                data_bs_toggle="collapse",
                data_bs_target="#" + collapse_id,
                aria_controls=collapse_id,
                aria_expanded="false",
                aria_label="Toggle navigation",
            )
        )
        nav = div(nav, id=collapse_id, class_="collapse navbar-collapse")

    nav_container.append(nav)
    nav_final = tags.nav({"class": "navbar"}, nav_container)

    if position != "static-top":
        nav_final.add_class(position)

    if bg:
        nav_final.attrs["style"] = "background-color: " + bg

    if inverse:
        nav_final.add_class("navbar-dark")

    return TagList(
        nav_final,
        div(
            row(header) if header else None,
            content,
            row(footer) if footer else None,
            class_="container-fluid" if fluid else "container",
        ),
    )


# -----------------------------------------------------------------------------
# Utilities for rendering navs
# -----------------------------------------------------------------------------\
def render_tabset(
    *items: Union[Nav, NavMenu],
    ul_class: str,
    id: Optional[str],
    selected: Optional[str],
    is_menu: bool = False,
) -> Tuple[Tag, Tag]:

    tabsetid = private_random_int(1000, 10000)

    if id is not None:
        ul_class += " shiny-tab-input"

    # If the user hasn't provided a selected value, use the first one
    if selected is None:
        for x in items:
            selected = x.get_value()
            if selected is not None:
                break

    ul_tag = tags.ul(bootstrap_deps(), class_=ul_class, id=id, data_tabsetid=tabsetid)
    div_tag = div(class_="tab-content", data_tabsetid=tabsetid)
    for i, x in enumerate(items):
        nav, contents = x.render(selected, id=f"tab-{tabsetid}-{i}", is_menu=is_menu)
        ul_tag.append(nav)
        div_tag.append(contents)

    return ul_tag, div_tag


def card(
    *args: TagChildArg, header: TagChildArg = None, footer: TagChildArg = None
) -> Tag:
    if header:
        header = div(header, class_="card-header")
    if footer:
        footer = div(footer, class_="card-footer")

    return div(
        header,
        div(*args, class_="card-body"),
        footer,
        bootstrap_deps(),
        class_="card",
    )
