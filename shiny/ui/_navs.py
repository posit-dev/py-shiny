from __future__ import annotations

__all__ = (
    "nav_panel",
    "nav_menu",
    "nav_control",
    "nav_spacer",
    "navset_tab",
    "navset_card_tab",
    "navset_pill",
    "navset_underline",
    "navset_card_pill",
    "navset_card_underline",
    "navset_pill_list",
    "navset_hidden",
    "navset_bar",
    # Deprecated - 2023-08-15
    "navset_pill_card",
    "navset_tab_card",
    "nav",
)

import collections.abc
import copy
import re
from typing import Any, Literal, Optional, Sequence, cast

from htmltools import MetadataNode, Tag, TagAttrs, TagChild, TagList, css, div, tags

from .._deprecated import warn_deprecated
from .._docstring import add_example, no_example
from .._namespaces import resolve_id_or_none
from .._utils import private_random_int
from ..types import NavSetArg
from ._bootstrap import column, row
from ._card import CardItem, WrapperCallable, card, card_body, card_footer, card_header
from ._html_deps_shinyverse import components_dependencies
from ._sidebar import Sidebar, layout_sidebar
from .css import CssUnit, as_css_padding, as_css_unit
from .fill import as_fill_item, as_fillable_container


# -----------------------------------------------------------------------------
# Navigation items
# -----------------------------------------------------------------------------
class NavPanel:
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
def nav_panel(
    title: TagChild,
    *args: TagChild,
    value: Optional[str] = None,
    icon: TagChild = None,
) -> NavPanel:
    """
    Create a nav item pointing to some internal content.

    Parameters
    ----------
    title
        A title to display. Can be a character string or UI elements (i.e., tags).
    *args
        UI elements to display when the item is active.
    value
        The value of the item. Use this value to determine whether the item is active
        (when an ``id`` is provided to the nav container) or to programmatically
        select the item (e.g., :func:`~shiny.ui.update_navs`). You can also
        provide the value to the ``selected`` argument of the navigation container
        (e.g., :func:`~shiny.ui.navset_tab`).
    icon
        An icon to appear inline with the button/link.

    See Also
    --------
    * :func:`~shiny.ui.nav_menu`
    * :func:`~shiny.ui.nav_control`
    * :func:`~shiny.ui.nav_spacer`
    * :func:`~shiny.ui.navset_bar`
    * :func:`~shiny.ui.navset_tab`
    * :func:`~shiny.ui.navset_pill`
    * :func:`~shiny.ui.navset_underline`
    * :func:`~shiny.ui.navset_card_tab`
    * :func:`~shiny.ui.navset_card_pill`
    * :func:`~shiny.ui.navset_card_underline`
    * :func:`~shiny.ui.navset_pill_list`
    * :func:`~shiny.ui.navset_hidden`
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

    return NavPanel(
        tags.li(link),
        div(*args, class_="tab-pane", role="tabpanel", data_value=value),
    )


@no_example()
def nav_control(*args: TagChild) -> NavPanel:
    """
    Place a control in the navigation container.

    Parameters
    ----------
    *args
        UI elements to display as the nav item.

    See Also
    --------
    * :func:`~shiny.ui.nav_panel`
    * :func:`~shiny.ui.nav_menu`
    * :func:`~shiny.ui.nav_spacer`
    * :func:`~shiny.ui.navset_bar`
    * :func:`~shiny.ui.navset_tab`
    * :func:`~shiny.ui.navset_pill`
    * :func:`~shiny.ui.navset_underline`
    * :func:`~shiny.ui.navset_card_tab`
    * :func:`~shiny.ui.navset_card_pill`
    * :func:`~shiny.ui.navset_card_underline`
    * :func:`~shiny.ui.navset_pill_list`
    * :func:`~shiny.ui.navset_hidden`

    Example
    -------
    See :func:`~shiny.ui.nav_panel`
    """
    return NavPanel(tags.li(*args))


@no_example()
def nav_spacer() -> NavPanel:
    """
    Create space between nav items.

    See Also
    --------
    * :func:~shiny.ui.nav_panel
    * :func:~shiny.ui.nav_menu
    * :func:~shiny.ui.nav_control
    * :func:~shiny.ui.navset_bar
    * :func:~shiny.ui.navset_tab
    * :func:~shiny.ui.navset_pill
    * :func:~shiny.ui.navset_underline
    * :func:~shiny.ui.navset_card_tab
    * :func:~shiny.ui.navset_card_pill
    * :func:~shiny.ui.navset_card_underline
    * :func:~shiny.ui.navset_pill_list
    * :func:~shiny.ui.navset_hidden

    Example
    -------
    See :func:`~shiny.ui.nav_panel`
    """

    return NavPanel(tags.li(components_dependencies(), class_="bslib-nav-spacer"))


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
            # `.dropdown-menu-right` is for Bootstrap 3; BS5 uses `.dropdown-menu-end`
            ul_class=f"dropdown-menu{' dropdown-menu-end' if self.align == 'right' else ''}",
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

    return NavPanel(nav)


@no_example()
def nav_menu(
    title: TagChild,
    *args: NavPanel | str,
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
        A collection of nav items (e.g., :func:`~shiny.ui.nav_panel`) and/or strings.
        Strings will be rendered as a section header unless the string is a set
        of two or more hyphens (e.g., ``---``), in which case it will be rendered
        as a divider.
    value
        The value of the item. Use this value to determine whether the item is active
        (when an ``id`` is provided to the nav container) or to programmatically
        select the item (e.g., :func:`~shiny.ui.update_navs`). You can also
        provide the value to the ``selected`` argument of the navigation container
        (e.g., :func:`~shiny.ui.navset_tab`).
    icon
        An icon to appear inline with the button/link.
    align
        Horizontal alignment of the dropdown menu relative to dropdown toggle.

    Returns
    -------
    :
        A UI element representing both the navigation menu.

    See Also
    --------
    * :func:~shiny.ui.nav_panel
    * :func:~shiny.ui.nav_control
    * :func:~shiny.ui.nav_spacer
    * :func:~shiny.ui.navset_bar
    * :func:~shiny.ui.navset_tab
    * :func:~shiny.ui.navset_pill
    * :func:~shiny.ui.navset_underline
    * :func:~shiny.ui.navset_card_tab
    * :func:~shiny.ui.navset_card_pill
    * :func:~shiny.ui.navset_card_underline
    * :func:~shiny.ui.navset_pill_list
    * :func:~shiny.ui.navset_hidden

    Example
    -------
    See :func:`~shiny.ui.nav_panel`
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
    args: tuple[NavSetArg | MetadataNode | Sequence[MetadataNode], ...]
    ul_class: str
    id: Optional[str]
    selected: Optional[str]
    header: TagChild
    footer: TagChild

    def __init__(
        self,
        *args: NavSetArg | MetadataNode | Sequence[MetadataNode],
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

    def layout(self, nav: Tag, content: Tag) -> TagList | Tag:
        return TagList(nav, self.header, content, self.footer)


# -----------------------------------------------------------------------------
# Navigation containers
# -----------------------------------------------------------------------------
@no_example()
def navset_tab(
    *args: NavSetArg | MetadataNode | Sequence[MetadataNode],
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
        A collection of nav items (e.g., :func:`shiny.ui.nav_panel`).
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
    * :func:`~shiny.ui.nav_panel`
    * :func:`~shiny.ui.nav_menu`
    * :func:`~shiny.ui.nav_control`
    * :func:`~shiny.ui.nav_spacer`
    * :func:`~shiny.ui.navset_bar`
    * :func:`~shiny.ui.navset_pill`
    * :func:`~shiny.ui.navset_underline`
    * :func:`~shiny.ui.navset_card_tab`
    * :func:`~shiny.ui.navset_card_pill`
    * :func:`~shiny.ui.navset_card_underline`
    * :func:`~shiny.ui.navset_pill_list`
    * :func:`~shiny.ui.navset_hidden`

    Example
    -------
    See :func:`~shiny.ui.nav_panel`
    """

    return NavSet(
        *args,
        ul_class="nav nav-tabs",
        id=resolve_id_or_none(id),
        selected=selected,
        header=header,
        footer=footer,
    )


@no_example()
def navset_pill(
    *args: NavSetArg | MetadataNode | Sequence[MetadataNode],
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
        A collection of nav items (e.g., :func:`shiny.ui.nav_panel`).
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
    * :func:`~shiny.ui.nav_panel`
    * :func:`~shiny.ui.nav_menu`
    * :func:`~shiny.ui.nav_control`
    * :func:`~shiny.ui.nav_spacer`
    * :func:`~shiny.ui.navset_bar`
    * :func:`~shiny.ui.navset_tab`
    * :func:`~shiny.ui.navset_underline`
    * :func:`~shiny.ui.navset_card_tab`
    * :func:`~shiny.ui.navset_card_pill`
    * :func:`~shiny.ui.navset_card_underline`
    * :func:`~shiny.ui.navset_pill_list`
    * :func:`~shiny.ui.navset_hidden`

    Example
    -------
    See :func:`~shiny.ui.nav_panel`
    """

    return NavSet(
        *args,
        ul_class="nav nav-pills",
        id=resolve_id_or_none(id),
        selected=selected,
        header=header,
        footer=footer,
    )


@no_example()
def navset_underline(
    *args: NavSetArg | MetadataNode | Sequence[MetadataNode],
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: TagChild = None,
    footer: TagChild = None,
) -> NavSet:
    """
    Render nav items whose active/focused navigation links are styled with an underline.

    Parameters
    ----------
    *args
        A collection of nav items (e.g., :func:`shiny.ui.nav_panel`).
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
    * :func:`~shiny.ui.nav_panel`
    * :func:`~shiny.ui.nav_menu`
    * :func:`~shiny.ui.nav_control`
    * :func:`~shiny.ui.nav_spacer`
    * :func:`~shiny.ui.navset_bar`
    * :func:`~shiny.ui.navset_tab`
    * :func:`~shiny.ui.navset_pill`
    * :func:`~shiny.ui.navset_card_tab`
    * :func:`~shiny.ui.navset_card_pill`
    * :func:`~shiny.ui.navset_card_underline`
    * :func:`~shiny.ui.navset_pill_list`
    * :func:`~shiny.ui.navset_hidden`

    Example
    -------
    See :func:`~shiny.ui.nav_panel`
    """
    return NavSet(
        *args,
        ul_class="nav nav-underline",
        id=resolve_id_or_none(id),
        selected=selected,
        header=header,
        footer=footer,
    )


@add_example()
def navset_hidden(
    *args: NavSetArg | MetadataNode | Sequence[MetadataNode],
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
        A collection of nav items (e.g., :func:`shiny.ui.nav_panel`).
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
    * :func:`~shiny.ui.nav_panel`
    * :func:`~shiny.ui.nav_menu`
    * :func:`~shiny.ui.nav_control`
    * :func:`~shiny.ui.nav_spacer`
    * :func:`~shiny.ui.navset_bar`
    * :func:`~shiny.ui.navset_tab`
    * :func:`~shiny.ui.navset_pill`
    * :func:`~shiny.ui.navset_underline`
    * :func:`~shiny.ui.navset_card_tab`
    * :func:`~shiny.ui.navset_card_pill`
    * :func:`~shiny.ui.navset_card_underline`
    * :func:`~shiny.ui.navset_pill_list`
    """

    return NavSet(
        *args,
        ul_class="nav nav-hidden",
        id=resolve_id_or_none(id),
        selected=selected,
        header=header,
        footer=footer,
    )


class NavSetCard(NavSet):
    placement: Literal["above", "below"]
    sidebar: Optional[Sidebar]
    title: Optional[TagChild]

    def __init__(
        self,
        *args: NavSetArg | MetadataNode | Sequence[MetadataNode],
        ul_class: str,
        id: Optional[str],
        selected: Optional[str],
        title: Optional[TagChild] = None,
        sidebar: Optional[Sidebar] = None,
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
        self.title = title
        self.sidebar = sidebar
        self.placement = placement

    def layout(self, nav: Tag, content: Tag) -> Tag:
        content = _make_tabs_fillable(content, fillable=True, gap=0, padding=0)

        contents: list[CardItem] = wrap_each_content(
            [
                child
                for child in [self.header, content, self.footer]
                if child is not None
            ]
        )

        # If there is a sidebar, make a size 1 array of the layout_sidebar content
        if self.sidebar:
            contents = [
                layout_sidebar(
                    self.sidebar,
                    *contents,
                    fillable=True,
                    border=False,
                )
            ]

        nav_items = [*navset_title(self.title), nav]

        return card(
            card_header(*nav_items) if self.placement == "above" else None,
            *contents,
            card_footer(*nav_items) if self.placement == "below" else None,
        )


@no_example()
def navset_card_tab(
    *args: NavSetArg | MetadataNode | Sequence[MetadataNode],
    id: Optional[str] = None,
    selected: Optional[str] = None,
    title: Optional[TagChild] = None,
    sidebar: Optional[Sidebar] = None,
    header: TagChild = None,
    footer: TagChild = None,
) -> NavSetCard:
    """
    Render nav items as a tabset inside a card container.

    Parameters
    ----------
    *args
        A collection of nav items (e.g., :func:`shiny.ui.nav_panel`).
    id
        If provided, will create an input value that holds the currently selected nav
        item.
    selected
        Choose a particular nav item to select by default value (should match it's
        ``value``).
    sidebar
        A `Sidebar` component to display on every `nav()` page.
    header
        UI to display above the selected content.
    footer
        UI to display below the selected content.

    See Also
    --------
    * :func:`~shiny.ui.nav_panel`
    * :func:`~shiny.ui.nav_menu`
    * :func:`~shiny.ui.nav_control`
    * :func:`~shiny.ui.nav_spacer`
    * :func:`~shiny.ui.navset_bar`
    * :func:`~shiny.ui.navset_tab`
    * :func:`~shiny.ui.navset_pill`
    * :func:`~shiny.ui.navset_underline`
    * :func:`~shiny.ui.navset_card_pill`
    * :func:`~shiny.ui.navset_card_underline`
    * :func:`~shiny.ui.navset_pill_list`
    * :func:`~shiny.ui.navset_hidden`

    Example
    -------
    See :func:`~shiny.ui.nav_panel`
    """

    return NavSetCard(
        *args,
        ul_class="nav nav-tabs card-header-tabs",
        id=resolve_id_or_none(id),
        selected=selected,
        title=title,
        sidebar=sidebar,
        header=header,
        footer=footer,
        placement="above",
    )


@no_example()
def navset_card_pill(
    *args: NavSetArg | MetadataNode | Sequence[MetadataNode],
    id: Optional[str] = None,
    selected: Optional[str] = None,
    title: Optional[TagChild] = None,
    sidebar: Optional[Sidebar] = None,
    header: TagChild = None,
    footer: TagChild = None,
    placement: Literal["above", "below"] = "above",
) -> NavSetCard:
    """
    Render nav items as a pillset inside a card container.

    Parameters
    ----------
    *args
        A collection of nav items (e.g., :func:`shiny.ui.nav_panel`).
    id
        If provided, will create an input value that holds the currently selected nav
        item.
    selected
        Choose a particular nav item to select by default value (should match it's
        ``value``).
    sidebar
        A :class:`shiny.ui.Sidebar` component to display on every :func:`~shiny.ui.nav_panel` page.
    header
        UI to display above the selected content.
    footer
        UI to display below the selected content.
    placement
        Placement of the nav items relative to the content.

    See Also
    --------
    * :func:`~shiny.ui.nav_panel`
    * :func:`~shiny.ui.nav_menu`
    * :func:`~shiny.ui.nav_control`
    * :func:`~shiny.ui.nav_spacer`
    * :func:`~shiny.ui.navset_bar`
    * :func:`~shiny.ui.navset_tab`
    * :func:`~shiny.ui.navset_pill`
    * :func:`~shiny.ui.navset_underline`
    * :func:`~shiny.ui.navset_card_tab`
    * :func:`~shiny.ui.navset_card_underline`
    * :func:`~shiny.ui.navset_pill_list`
    * :func:`~shiny.ui.navset_hidden`

    Example
    -------
    See :func:`~shiny.ui.nav_panel`
    """

    return NavSetCard(
        *args,
        ul_class="nav nav-pills card-header-pills",
        id=resolve_id_or_none(id),
        selected=selected,
        title=title,
        sidebar=sidebar,
        header=header,
        footer=footer,
        placement=placement,
    )


@no_example()
def navset_card_underline(
    *args: NavSetArg | MetadataNode | Sequence[MetadataNode],
    id: Optional[str] = None,
    selected: Optional[str] = None,
    title: Optional[TagChild] = None,
    sidebar: Optional[Sidebar] = None,
    header: TagChild = None,
    footer: TagChild = None,
    placement: Literal["above", "below"] = "above",
) -> NavSetCard:
    """
    Render nav items inside a card container. Active/focused navigation links are styled with an underline.

    Parameters
    ----------
    *args
        A collection of nav items (e.g., :func:`shiny.ui.nav_panel`).
    id
        If provided, will create an input value that holds the currently selected nav
        item.
    selected
        Choose a particular nav item to select by default value (should match it's
        ``value``).
    sidebar
        A :class:`shiny.ui.Sidebar` component to display on every :func:`~shiny.ui.nav_panel` page.
    header
        UI to display above the selected content.
    footer
        UI to display below the selected content.
    placement
        Placement of the nav items relative to the content.

    See Also
    --------
    * :func:`~shiny.ui.nav_panel`
    * :func:`~shiny.ui.nav_menu`
    * :func:`~shiny.ui.nav_control`
    * :func:`~shiny.ui.nav_spacer`
    * :func:`~shiny.ui.navset_bar`
    * :func:`~shiny.ui.navset_tab`
    * :func:`~shiny.ui.navset_pill`
    * :func:`~shiny.ui.navset_underline`
    * :func:`~shiny.ui.navset_card_tab`
    * :func:`~shiny.ui.navset_card_pill`
    * :func:`~shiny.ui.navset_pill_list`
    * :func:`~shiny.ui.navset_hidden`

    Example
    -------
    See :func:`~shiny.ui.nav_panel`
    """
    return NavSetCard(
        *args,
        ul_class="nav nav-underline",
        id=resolve_id_or_none(id),
        selected=selected,
        title=title,
        sidebar=sidebar,
        header=header,
        footer=footer,
        placement=placement,
    )


class NavSetPillList(NavSet):
    well: bool
    widths: tuple[int, int]

    def __init__(
        self,
        *args: NavSetArg | MetadataNode | Sequence[MetadataNode],
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


@no_example()
def navset_pill_list(
    *args: NavSetArg | MetadataNode | Sequence[MetadataNode],
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
        A collection of nav items (e.g., :func:`shiny.ui.nav_panel`).
    id
        If provided, will create an input value that holds the currently selected nav
        item.
    selected
        Choose a particular nav item to select by default value (should match its
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
    --------
    * :func:`~shiny.ui.nav_panel`
    * :func:`~shiny.ui.nav_menu`
    * :func:`~shiny.ui.nav_control`
    * :func:`~shiny.ui.nav_spacer`
    * :func:`~shiny.ui.navset_bar`
    * :func:`~shiny.ui.navset_tab`
    * :func:`~shiny.ui.navset_pill`
    * :func:`~shiny.ui.navset_underline`
    * :func:`~shiny.ui.navset_card_tab`
    * :func:`~shiny.ui.navset_card_pill`
    * :func:`~shiny.ui.navset_card_underline`
    * :func:`~shiny.ui.navset_hidden`

    Example
    -------
    See :func:`~shiny.ui.nav_panel`
    """

    return NavSetPillList(
        *args,
        ul_class="nav nav-pills nav-stacked",
        id=resolve_id_or_none(id),
        selected=selected,
        header=header,
        footer=footer,
        well=well,
        widths=widths,
    )


class NavSetBar(NavSet):
    title: TagChild
    sidebar: Optional[Sidebar]
    fillable: bool | list[str]
    gap: Optional[CssUnit]
    padding: Optional[CssUnit | list[CssUnit]]
    position: Literal["static-top", "fixed-top", "fixed-bottom", "sticky-top"]
    bg: Optional[str]
    inverse: bool
    underline: bool
    collapsible: bool
    fluid: bool

    def __init__(
        self,
        *args: NavSetArg | MetadataNode | Sequence[MetadataNode],
        ul_class: str,
        title: TagChild,
        id: Optional[str],
        selected: Optional[str],
        sidebar: Optional[Sidebar] = None,
        fillable: bool | list[str] = False,
        gap: Optional[CssUnit],
        padding: Optional[CssUnit | list[CssUnit]],
        position: Literal[
            "static-top", "fixed-top", "fixed-bottom", "sticky-top"
        ] = "static-top",
        header: TagChild = None,
        footer: TagChild = None,
        bg: Optional[str] = None,
        # TODO: default to 'auto', like we have in R (parse color via webcolors?)
        inverse: bool = False,
        underline: bool = True,
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
        self.sidebar = sidebar
        self.fillable = fillable
        self.gap = gap
        self.padding = padding
        self.position = position
        self.bg = bg
        self.inverse = inverse
        self.underline = underline
        self.collapsible = collapsible
        self.fluid = fluid

    def layout(self, nav: Tag, content: Tag) -> TagList:
        nav_container = div(
            {"class": "container-fluid" if self.fluid else "container"},
            tags.span({"class": "navbar-brand"}, self.title),
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

        # bslib supports navbar-default/navbar-inverse (which is no longer
        # a thing in Bootstrap 5) in a way that's still useful, especially Bootswatch.
        nav_final.add_class(f"navbar-{'inverse' if self.inverse else 'default'}")

        if self.bg:
            nav_final.add_style(f"background-color: {self.bg} !important;")

        content = _make_tabs_fillable(
            content,
            self.fillable,
            gap=self.gap,
            padding=self.padding,
            navbar=True,
        )

        # 2023-05-11; Do not wrap `row()` around `self.header` and `self.footer`
        contents: list[TagChild] = [
            child for child in [self.header, content, self.footer] if child is not None
        ]

        if self.sidebar is None:
            content_div = div(
                *contents,
                class_="container-fluid" if self.fluid else "container",
            )
            # If fillable is truthy, the .container also needs to be fillable
            if self.fillable:
                content_div = as_fillable_container(as_fill_item(content_div))
        else:
            content_div = div(
                # In the fluid case, the sidebar layout should be flush (i.e.,
                # the .container-fluid class adds padding that we don't want)
                {"class": "container"} if not self.fluid else None,
                layout_sidebar(
                    self.sidebar,
                    contents,
                    fillable=self.fillable is not False,
                    border_radius=False,
                    border=not self.fluid,
                ),
            )
            # Always have the sidebar layout fill its parent (in this case
            # fillable controls whether the _main_ content portion is fillable)
            content_div = as_fillable_container(as_fill_item(content_div))

        return TagList(nav_final, content_div)


# Given a .tab-content container, mark each relevant .tab-pane as a fill container/item.
def _make_tabs_fillable(
    content: Tag,
    fillable: bool | list[str] = True,
    gap: Optional[CssUnit] = None,
    padding: Optional[CssUnit | list[CssUnit]] = None,
    navbar: bool = False,
) -> Tag:
    if not fillable:
        return content

    # Even if only one .tab-pane wants fillable behavior, the .tab-content
    # must to be a fillable container.
    content = as_fillable_container(as_fill_item(content))

    for i, child in enumerate(content.children):
        # Only work on Tags
        if not isinstance(child, Tag):
            continue
        # Only work on .tab-pane children
        if not child.has_class("tab-pane"):
            continue
        # If `fillable` is a list, only fill the .tab-pane if its data-value is contained in `fillable`
        if isinstance(fillable, list):
            child_attr = child.attrs.get("data-value")
            if child_attr is None or child_attr not in fillable:
                continue
        styles = css(
            gap=as_css_unit(gap),
            padding=as_css_padding(padding),
            __bslib_navbar_margin="0;" if navbar else None,
        )
        child = as_fillable_container(as_fill_item(child))
        child.add_style(cast(str, styles))
        child.add_class("bslib-gap-spacing")

        content.children[i] = child

    return content


# TODO-future; Content should not be indented unless when called from `page_navbar()`
@no_example()
def navset_bar(
    *args: NavSetArg | MetadataNode | Sequence[MetadataNode],
    title: TagChild,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    sidebar: Optional[Sidebar] = None,
    fillable: bool | list[str] = True,
    gap: Optional[CssUnit] = None,
    padding: Optional[CssUnit | list[CssUnit]] = None,
    position: Literal[
        "static-top", "fixed-top", "fixed-bottom", "sticky-top"
    ] = "static-top",
    header: TagChild = None,
    footer: TagChild = None,
    bg: Optional[str] = None,
    # TODO: default to 'auto', like we have in R (parse color via webcolors?)
    inverse: bool = False,
    underline: bool = True,
    collapsible: bool = True,
    fluid: bool = True,
) -> NavSetBar:
    """
    Render nav items as a navbar.

    Parameters
    ----------
    *args
        A collection of nav items (e.g., :func:`shiny.ui.nav_panel`).
    title
        Title to display in the navbar.
    id
        If provided, will create an input value that holds the currently selected nav
        item.
    selected
        Choose a particular nav item to select by default value (should match it's
        ``value``).
    sidebar
        A :class:`~shiny.ui.Sidebar` component to display on every :func:`~shiny.ui.nav_panel` page.
    fillable
        Whether or not to allow fill items to grow/shrink to fit the browser window. If
        `True`, all `nav()` pages are fillable. A character vector, matching the value
        of `nav()`s to be filled, may also be provided. Note that, if a `sidebar` is
        provided, `fillable` makes the main content portion fillable.
    gap
        A CSS length unit defining the gap (i.e., spacing) between elements provided to
        `*args`.
    padding
        Padding to use for the body. This can be a numeric vector (which will be
        interpreted as pixels) or a character vector with valid CSS lengths. The length
        can be between one and four. If one, then that value will be used for all four
        sides. If two, then the first value will be used for the top and bottom, while
        the second value will be used for left and right. If three, then the first will
        be used for top, the second will be left and right, and the third will be
        bottom. If four, then the values will be interpreted as top, right, bottom, and
        left respectively.
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
    --------
    * :func:`~shiny.ui.page_navbar`
    * :func:`~shiny.ui.nav_panel`
    * :func:`~shiny.ui.nav_menu`
    * :func:`~shiny.ui.nav_control`
    * :func:`~shiny.ui.nav_spacer`
    * :func:`~shiny.ui.navset_tab`
    * :func:`~shiny.ui.navset_pill`
    * :func:`~shiny.ui.navset_underline`
    * :func:`~shiny.ui.navset_card_tab`
    * :func:`~shiny.ui.navset_card_pill`
    * :func:`~shiny.ui.navset_card_underline`
    * :func:`~shiny.ui.navset_pill_list`
    * :func:`~shiny.ui.navset_hidden`

    Example
    -------
    See :func:`~shiny.ui.nav_panel`.
    """

    # If args contains any lists, flatten them into args.
    new_args: Sequence[NavSetArg | MetadataNode] = []
    for arg in args:
        if isinstance(arg, (list, tuple)):
            new_args.extend(arg)
        else:
            new_args.append(cast(NavSetArg, arg))

    ul_class = "nav navbar-nav"
    if underline:
        ul_class += " nav-underline"

    return NavSetBar(
        *new_args,
        ul_class=ul_class,
        id=resolve_id_or_none(id),
        selected=selected,
        sidebar=sidebar,
        fillable=fillable,
        gap=gap,
        padding=padding,
        title=title,
        position=position,
        header=header,
        footer=footer,
        bg=bg,
        inverse=inverse,
        underline=underline,
        collapsible=collapsible,
        fluid=fluid,
    )


# -----------------------------------------------------------------------------
# Utilities for rendering navs
# -----------------------------------------------------------------------------\
def render_navset(
    *items: NavSetArg | MetadataNode | Sequence[MetadataNode],
    ul_class: str,
    id: Optional[str],
    selected: Optional[str],
    context: dict[str, Any],
) -> tuple[Tag, Tag]:
    tabsetid = private_random_int(1000, 10000)

    # Separate MetadataNodes from NavSetArgs.
    metadata_args: list[MetadataNode] = []
    navset_args: list[NavSetArg] = []

    for item in items:
        if isinstance(item, MetadataNode):
            metadata_args.append(item)
        elif isinstance(item, collections.abc.Sequence) and all(
            isinstance(x, MetadataNode) for x in item
        ):
            # Above we needed to use collections.abc.Sequence for runtime checks, as
            # typing.Sequence does not work for runtime checks.
            metadata_args.extend(item)
        else:
            # pyright needs a little help with type inference here.
            navset_args.append(cast(NavSetArg, item))

    # If the user hasn't provided a selected value, use the first one
    if selected is None:
        for x in navset_args:
            selected = x.get_value()
            if selected is not None:
                break

    ul_tag = tags.ul(
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


def wrap_each_content(
    contents: list[TagChild], wrapper: WrapperCallable = card_body
) -> list[CardItem]:
    ret: list[CardItem] = []
    for content_item in contents:
        if isinstance(content_item, CardItem):
            ret.append(content_item)
        else:
            ret.append(wrapper(content_item))
    return ret


def navset_title(
    title: TagChild | None,
) -> list[TagChild | TagAttrs]:
    """Note: Return value should be spread into parent container."""

    if title is None:
        return [None]

    title_attrs: TagAttrs = {"class": "bslib-navs-card-title"}
    return [title_attrs, tags.span(title)]


##############################################
# Deprecated
##############################################
# Deprecated 2023-08-15
def navset_pill_card(
    *args: NavSetArg,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: TagChild = None,
    footer: TagChild = None,
    placement: Literal["above", "below"] = "above",
) -> NavSetCard:
    """Deprecated. Please use `navset_card_pill()` instead of `navset_pill_card()`."""
    warn_deprecated(
        "`navset_pill_card()` is deprecated. "
        "This method will be removed in a future version, "
        "please use :func:`~shiny.ui.navset_card_pill` instead."
    )
    return navset_card_pill(
        *args,
        id=id,
        selected=selected,
        header=header,
        footer=footer,
        placement=placement,
    )


# Deprecated 2023-08-15
def navset_tab_card(
    *args: NavSetArg,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: TagChild = None,
    footer: TagChild = None,
) -> NavSetCard:
    """Deprecated. Please use `navset_card_tab()` instead of `navset_tab_card()`."""
    warn_deprecated(
        "`navset_tab_card()` is deprecated. "
        "This method will be removed in a future version, "
        "please use :func:`~shiny.ui.navset_card_tab` instead."
    )
    return navset_card_tab(
        *args,
        id=id,
        selected=selected,
        header=header,
        footer=footer,
    )


# Deprecated 2023-12-07
@no_example()
def nav(
    title: TagChild,
    *args: TagChild,
    value: Optional[str] = None,
    icon: TagChild = None,
) -> NavPanel:
    """Deprecated. Please use `nav_panel()` instead of `nav()`."""
    warn_deprecated(
        "`nav()` is deprecated. "
        "This method will be removed in a future version, "
        "please use :func:`~shiny.ui.nav_panel` instead."
    )
    return nav_panel(
        title,
        *args,
        value=value,
        icon=icon,
    )
