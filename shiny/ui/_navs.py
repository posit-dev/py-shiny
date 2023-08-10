from __future__ import annotations

__all__ = (
    "nav",
    "nav_menu",
    "nav_control",
    "nav_spacer",
    "navset_tab",
    "navset_tab_card",
    "navset_pill",
    "navset_pill_card",
    "navset_pill_list",
    "navset_hidden",
    "navset_bar",
)

import copy
import re
from typing import Any, Literal, Optional, Sequence, cast

from htmltools import MetadataNode, Tag, TagChild, TagList, div, tags

from .._docstring import add_example
from .._namespaces import resolve_id
from .._utils import private_random_int
from ..types import NavSetArg
from ._bootstrap import column, row
from ._html_dependencies import bootstrap_deps, nav_spacer_deps


# -----------------------------------------------------------------------------
# Navigation items
# -----------------------------------------------------------------------------
class Nav:
    nav: Tag
    content: Optional[Tag]

    def __init__(self, nav: Tag, content: Optional[Tag] = None) -> None:
        self.nav = nav
        # nav_control()/nav_spacer() have None as their content
        self.content = content

    def resolve(
        self, selected: Optional[str], context: dict[str, Any]
    ) -> tuple[TagChild, TagChild]:
        # Nothing to do for nav_control()/nav_spacer()
        if self.content is None:
            return self.nav, None

        # At least currently, in the case where both nav and content are tags
        # (i.e., nav()), the nav always has a child <a> tag...I'm not sure if
        # there's a way to statically type this
        nav = copy.deepcopy(self.nav)
        a_tag = cast(Tag, nav.children[0])
        if context.get("is_menu", False):
            a_tag.add_class("dropdown-item")
        else:
            a_tag.add_class("nav-link")
            nav.add_class("nav-item")

        # Hyperlink the nav to the content
        content = copy.copy(self.content)
        if "tabsetid" in context and "index" in context:
            id = f"tab-{context['tabsetid']}-{context['index']}"
            content.attrs["id"] = id
            a_tag.attrs["href"] = f"#{id}"

        # Mark the nav/content as active if it should be
        if isinstance(selected, str) and selected == self.get_value():
            content.add_class("active")
            a_tag.add_class("active")

        nav.children[0] = a_tag

        return nav, content

    def get_value(self) -> Optional[str]:
        if self.content is None:
            return None
        a_tag = cast(Tag, self.nav.children[0])
        return a_tag.attrs.get("data-value", None)

    def tagify(self) -> None:
        raise NotImplementedError(
            "nav() items must appear within navset_*() container."
        )


@add_example()
def nav(
    title: TagChild,
    *args: TagChild,
    value: Optional[str] = None,
    icon: TagChild = None,
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
        :func:`~shiny.ui.navset_tab`).
    icon
        An icon to appear inline with the button/link.

    See Also
    -------
    ~shiny.ui.nav_menu
    ~shiny.ui.nav_control
    ~shiny.ui.nav_spacer
    ~shiny.ui.navset_bar
    ~shiny.ui.navset_tab
    ~shiny.ui.navset_pill
    ~shiny.ui.navset_tab_card
    ~shiny.ui.navset_pill_card
    ~shiny.ui.navset_hidden
    """
    if value is None:
        value = str(title)

    # N.B. at this point, we don't have enough info to link the nav to the content
    # or add relevant classes. That's done later by consumers (i.e. nav containers)
    link = tags.a(
        icon,
        title,
        data_bs_toggle="tab",  # Bootstrap 5
        data_toggle="tab",  # Needed for shiny.js' insert-tab handler
        data_value=value,
        role="tab",
    )

    return Nav(
        tags.li(link),
        div(*args, class_="tab-pane", role="tabpanel", data_value=value),
    )


def nav_control(*args: TagChild) -> Nav:
    """
    Place a control in the navigation container.

    Parameters
    ----------
    *args
        UI elements to display as the nav item.

    See Also
    -------
    ~shiny.ui.nav
    ~shiny.ui.nav_menu
    ~shiny.ui.nav_spacer
    ~shiny.ui.navset_bar
    ~shiny.ui.navset_tab
    ~shiny.ui.navset_pill
    ~shiny.ui.navset_tab_card
    ~shiny.ui.navset_pill_card
    ~shiny.ui.navset_hidden
    Example
    -------
    See :func:`~shiny.ui.nav`
    """
    return Nav(tags.li(*args))


def nav_spacer() -> Nav:
    """
    Create space between nav items.

    See Also
    -------
    ~shiny.ui.nav
    ~shiny.ui.nav_menu
    ~shiny.ui.nav_control
    ~shiny.ui.navset_bar
    ~shiny.ui.navset_tab
    ~shiny.ui.navset_pill
    ~shiny.ui.navset_tab_card
    ~shiny.ui.navset_pill_card
    ~shiny.ui.navset_hidden

    Example
    -------
    See :func:`~shiny.ui.nav`
    """

    return Nav(tags.li(nav_spacer_deps(), class_="bslib-nav-spacer"))


class NavMenu:
    nav_controls: list[NavSetArg]
    title: TagChild
    value: str
    align: Literal["left", "right"]

    def __init__(
        self,
        *args: NavSetArg | str,
        title: TagChild,
        value: str,
        align: Literal["left", "right"] = "left",
    ) -> None:
        self.nav_controls = [menu_string_as_nav(x) for x in args]
        self.title = title
        self.value = value
        self.align = align

    def resolve(
        self,
        selected: Optional[str],
        context: dict[str, Any],
    ) -> tuple[TagChild, TagChild]:
        nav, content = render_navset(
            *self.nav_controls,
            ul_class=f"dropdown-menu {'dropdown-menu-right' if self.align == 'right' else ''}",
            id=None,
            selected=selected,
            context={**context, "is_menu": True},
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
        for x in self.nav_controls:
            val = x.get_value()
            if val:
                return val
        return None

    def tagify(self) -> None:
        raise NotImplementedError("nav_menu() must appear within navset_*() container.")


def menu_string_as_nav(x: str | NavSetArg) -> NavSetArg:
    if not isinstance(x, str):
        return x

    if re.match(r"^\-+$", x):
        nav = tags.li(class_="dropdown-divider")
    else:
        nav = tags.li(x, class_="dropdown-header")

    return Nav(nav)


def nav_menu(
    title: TagChild,
    *args: Nav | str,
    value: Optional[str] = None,
    icon: TagChild = None,
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
        :func:`~shiny.ui.navset_tab`).
    icon
        An icon to appear inline with the button/link.
    align
        Horizontal alignment of the dropdown menu relative to dropdown toggle.

    Returns
    -------
    :
        A UI element representing both the navigation menu.

    See Also
    -------
    ~shiny.ui.nav
    ~shiny.ui.nav_control
    ~shiny.ui.nav_spacer
    ~shiny.ui.navset_bar
    ~shiny.ui.navset_tab
    ~shiny.ui.navset_pill
    ~shiny.ui.navset_tab_card
    ~shiny.ui.navset_pill_card
    ~shiny.ui.navset_hidden
    Example
    -------
    See :func:`~shiny.ui.nav`
    """
    if value is None:
        value = str(title)

    return NavMenu(
        *args,
        title=TagList(icon, title),
        value=value,
        align=align,
    )


class NavSet:
    args: tuple[NavSetArg | MetadataNode]
    ul_class: str
    id: Optional[str]
    selected: Optional[str]
    header: TagChild
    footer: TagChild

    def __init__(
        self,
        *args: NavSetArg | MetadataNode,
        ul_class: str,
        id: Optional[str],
        selected: Optional[str],
        header: TagChild = None,
        footer: TagChild = None,
    ) -> None:
        self.args = args
        self.ul_class = ul_class
        self.id = id
        self.selected = selected
        self.header = header
        self.footer = footer

    def tagify(self) -> TagList | Tag:
        id = self.id
        ul_class = self.ul_class
        if id is not None:
            ul_class += " shiny-tab-input"

        nav, content = render_navset(
            *self.args, ul_class=ul_class, id=id, selected=self.selected, context={}
        )
        return self.layout(nav, content).tagify()

    def layout(self, nav: TagChild, content: TagChild) -> TagList | Tag:
        return TagList(nav, self.header, content, self.footer)


# -----------------------------------------------------------------------------
# Navigation containers
# -----------------------------------------------------------------------------
def navset_tab(
    *args: NavSetArg,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: TagChild = None,
    footer: TagChild = None,
) -> NavSet:
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
    ~shiny.ui.nav_control
    ~shiny.ui.nav_spacer
    ~shiny.ui.navset_bar
    ~shiny.ui.navset_pill
    ~shiny.ui.navset_tab_card
    ~shiny.ui.navset_pill_card
    ~shiny.ui.navset_hidden

    Example
    -------
    See :func:`~shiny.ui.nav`
    """

    return NavSet(
        *args,
        ul_class="nav nav-tabs",
        id=resolve_id(id) if id else None,
        selected=selected,
        header=header,
        footer=footer,
    )


def navset_pill(
    *args: NavSetArg,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: TagChild = None,
    footer: TagChild = None,
) -> NavSet:
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
    ~shiny.ui.nav_control
    ~shiny.ui.nav_spacer
    ~shiny.ui.navset_bar
    ~shiny.ui.navset_tab
    ~shiny.ui.navset_tab_card
    ~shiny.ui.navset_pill_card
    ~shiny.ui.navset_hidden

    Example
    -------
    See :func:`~shiny.ui.nav`
    """

    return NavSet(
        *args,
        ul_class="nav nav-pills",
        id=resolve_id(id) if id else None,
        selected=selected,
        header=header,
        footer=footer,
    )


@add_example()
def navset_hidden(
    *args: NavSetArg,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: TagChild = None,
    footer: TagChild = None,
) -> NavSet:
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
    ~shiny.ui.nav_control
    ~shiny.ui.nav_spacer
    ~shiny.ui.navset_tab
    ~shiny.ui.navset_tab_card
    ~shiny.ui.navset_pill
    ~shiny.ui.navset_pill_card
    ~shiny.ui.navset_pill_list
    ~shiny.ui.navset_bar
    """

    return NavSet(
        *args,
        ul_class="nav nav-hidden",
        id=resolve_id(id) if id else None,
        selected=selected,
        header=header,
        footer=footer,
    )


class NavSetCard(NavSet):
    placement: Literal["above", "below"]

    def __init__(
        self,
        *args: NavSetArg,
        ul_class: str,
        id: Optional[str],
        selected: Optional[str],
        header: TagChild = None,
        footer: TagChild = None,
        placement: Literal["above", "below"] = "above",
    ) -> None:
        super().__init__(
            *args,
            ul_class=ul_class,
            id=id,
            selected=selected,
            header=header,
            footer=footer,
        )
        self.placement = placement

    def layout(self, nav: TagChild, content: TagChild) -> Tag:
        if self.placement == "below":
            return card(self.header, content, self.footer, footer=nav)
        else:
            return card(self.header, content, self.footer, header=nav)


def navset_tab_card(
    *args: NavSetArg,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: TagChild = None,
    footer: TagChild = None,
) -> NavSetCard:
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
    ~shiny.ui.nav_control
    ~shiny.ui.nav_spacer
    ~shiny.ui.navset_bar
    ~shiny.ui.navset_tab
    ~shiny.ui.navset_pill
    ~shiny.ui.navset_pill_card
    ~shiny.ui.navset_hidden

    Example
    -------
    See :func:`~shiny.ui.nav`
    """

    return NavSetCard(
        *args,
        ul_class="nav nav-tabs card-header-tabs",
        id=resolve_id(id) if id else None,
        selected=selected,
        header=header,
        footer=footer,
        placement="above",
    )


def navset_pill_card(
    *args: NavSetArg,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: TagChild = None,
    footer: TagChild = None,
    placement: Literal["above", "below"] = "above",
) -> NavSetCard:
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
    ~shiny.ui.nav_control
    ~shiny.ui.nav_spacer
    ~shiny.ui.navset_bar
    ~shiny.ui.navset_tab
    ~shiny.ui.navset_pill
    ~shiny.ui.navset_tab_card
    ~shiny.ui.navset_hidden

    Example
    -------
    See :func:`~shiny.ui.nav`
    """

    return NavSetCard(
        *args,
        ul_class="nav nav-pills card-header-pills",
        id=resolve_id(id) if id else None,
        selected=selected,
        header=header,
        footer=footer,
        placement=placement,
    )


class NavSetPillList(NavSet):
    well: bool
    widths: tuple[int, int]

    def __init__(
        self,
        *args: NavSetArg | MetadataNode,
        ul_class: str,
        id: Optional[str],
        selected: Optional[str],
        header: TagChild = None,
        footer: TagChild = None,
        well: bool = True,
        widths: tuple[int, int] = (4, 8),
    ) -> None:
        super().__init__(
            *args,
            ul_class=ul_class,
            id=id,
            selected=selected,
            header=header,
            footer=footer,
        )
        self.well = well
        self.widths = widths

    def layout(self, nav: TagChild, content: TagChild) -> Tag:
        widths = self.widths
        return row(
            column(widths[0], nav, class_="well" if self.well else None),
            column(widths[1], self.header, content, self.footer),
        )


def navset_pill_list(
    *args: NavSetArg | MetadataNode,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: TagChild = None,
    footer: TagChild = None,
    well: bool = True,
    widths: tuple[int, int] = (4, 8),
) -> NavSet:
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
    widths
        Column widths of the navigation list and tabset content areas respectively.

    See Also
    -------
    ~shiny.ui.nav
    ~shiny.ui.nav_menu
    ~shiny.ui.nav_control
    ~shiny.ui.nav_spacer
    ~shiny.ui.navset_tab
    ~shiny.ui.navset_tab_card
    ~shiny.ui.navset_pill
    ~shiny.ui.navset_pill_card
    ~shiny.ui.navset_hidden
    ~shiny.ui.navset_bar
    ~shiny.ui.navset_hidden

    Example
    -------
    See :func:`~shiny.ui.nav`
    """

    return NavSetPillList(
        *args,
        ul_class="nav nav-pills nav-stacked",
        id=resolve_id(id) if id else None,
        selected=selected,
        header=header,
        footer=footer,
        well=well,
        widths=widths,
    )


class NavSetBar(NavSet):
    title: TagChild
    position: Literal["static-top", "fixed-top", "fixed-bottom", "sticky-top"]
    bg: Optional[str]
    inverse: bool
    collapsible: bool
    fluid: bool

    def __init__(
        self,
        *args: NavSetArg | MetadataNode,
        ul_class: str,
        title: TagChild,
        id: Optional[str],
        selected: Optional[str],
        position: Literal[
            "static-top", "fixed-top", "fixed-bottom", "sticky-top"
        ] = "static-top",
        header: TagChild = None,
        footer: TagChild = None,
        bg: Optional[str] = None,
        # TODO: default to 'auto', like we have in R (parse color via webcolors?)
        inverse: bool = False,
        collapsible: bool = True,
        fluid: bool = True,
    ) -> None:
        super().__init__(
            *args,
            ul_class=ul_class,
            id=id,
            selected=selected,
            header=header,
            footer=footer,
        )
        self.title = title
        self.position = position
        self.bg = bg
        self.inverse = inverse
        self.collapsible = collapsible
        self.fluid = fluid

    def layout(self, nav: TagChild, content: TagChild) -> TagList:
        nav_container = div(
            {"class": "container-fluid" if self.fluid else "container"},
            tags.a({"class": "navbar-brand", "href": "#"}, self.title),
        )
        if self.collapsible:
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
        nav_final = tags.nav({"class": "navbar navbar-expand-md"}, nav_container)

        if self.position != "static-top":
            nav_final.add_class(self.position)

        nav_final.add_class(f"navbar-{'dark' if self.inverse else 'light'}")

        if self.bg:
            nav_final.attrs["style"] = "background-color: " + self.bg
        else:
            nav_final.add_class(f"bg-{'dark' if self.inverse else 'light'}")

        return TagList(
            nav_final,
            div(
                row(self.header) if self.header else None,
                content,
                row(self.footer) if self.footer else None,
                class_="container-fluid" if self.fluid else "container",
            ),
        )


def navset_bar(
    *args: NavSetArg | MetadataNode | Sequence[MetadataNode],
    title: TagChild,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    position: Literal[
        "static-top", "fixed-top", "fixed-bottom", "sticky-top"
    ] = "static-top",
    header: TagChild = None,
    footer: TagChild = None,
    bg: Optional[str] = None,
    # TODO: default to 'auto', like we have in R (parse color via webcolors?)
    inverse: bool = False,
    collapsible: bool = True,
    fluid: bool = True,
) -> NavSetBar:
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
        ``True`` to automatically collapse the navigation elements into an expandable menu on mobile devices or narrow window widths.
    fluid
        ``True`` to use fluid layout; ``False`` to use fixed layout.

    See Also
    -------
    ~shiny.ui.page_navbar
    ~shiny.ui.nav
    ~shiny.ui.nav_menu
    ~shiny.ui.nav_control
    ~shiny.ui.nav_spacer
    ~shiny.ui.navset_tab
    ~shiny.ui.navset_pill
    ~shiny.ui.navset_tab_card
    ~shiny.ui.navset_pill_card
    ~shiny.ui.navset_hidden

    Example
    -------
    See :func:`~shiny.ui.nav`.
    """

    # If args contains any lists, flatten them into args.
    new_args: Sequence[NavSetArg | MetadataNode] = []
    for arg in args:
        if isinstance(arg, (list, tuple)):
            new_args.extend(arg)
        else:
            new_args.append(cast(NavSetArg, arg))

    return NavSetBar(
        *new_args,
        ul_class="nav navbar-nav",
        id=resolve_id(id) if id else None,
        selected=selected,
        title=title,
        position=position,
        header=header,
        footer=footer,
        bg=bg,
        inverse=inverse,
        collapsible=collapsible,
        fluid=fluid,
    )


# -----------------------------------------------------------------------------
# Utilities for rendering navs
# -----------------------------------------------------------------------------\
def render_navset(
    *items: NavSetArg | MetadataNode,
    ul_class: str,
    id: Optional[str],
    selected: Optional[str],
    context: dict[str, Any],
) -> tuple[Tag, Tag]:
    tabsetid = private_random_int(1000, 10000)

    # Separate MetadataNodes from NavSetArgs.
    metadata_args = [x for x in items if isinstance(x, MetadataNode)]
    navset_args = [x for x in items if not isinstance(x, MetadataNode)]

    # If the user hasn't provided a selected value, use the first one
    if selected is None:
        for x in navset_args:
            selected = x.get_value()
            if selected is not None:
                break

    ul_tag = tags.ul(
        bootstrap_deps(),
        metadata_args,
        class_=ul_class,
        id=id,
        data_tabsetid=tabsetid,
    )
    div_tag = div(class_="tab-content", data_tabsetid=tabsetid)
    for i, x in enumerate(navset_args):
        nav, contents = x.resolve(
            selected, {**context, "tabsetid": tabsetid, "index": i}
        )
        ul_tag.append(nav)
        div_tag.append(contents)

    return ul_tag, div_tag


def card(*args: TagChild, header: TagChild = None, footer: TagChild = None) -> Tag:
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
