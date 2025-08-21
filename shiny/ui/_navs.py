from __future__ import annotations

import collections.abc
import copy
import re
from typing import Any, Literal, Optional, Sequence, TypeVar, cast

from htmltools import (
    HTML,
    MetadataNode,
    Tag,
    TagAttrs,
    TagAttrValue,
    TagChild,
    TagList,
    css,
    div,
    tags,
)

from .._deprecated import warn_deprecated
from .._docstring import add_example
from .._namespaces import resolve_id_or_none
from .._utils import private_random_int
from ..bookmark import restore_input
from ..types import DEPRECATED, MISSING, MISSING_TYPE, NavSetArg
from ._bootstrap import column, row
from ._card import CardItem, WrapperCallable, card, card_body, card_footer, card_header
from ._html_deps_shinyverse import components_dependencies
from ._sidebar import Sidebar, layout_sidebar
from .css import CssUnit, as_css_padding, as_css_unit
from .fill import as_fill_item, as_fillable_container

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
    "navbar_options",
)

T = TypeVar("T")


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

    def get_value(self) -> str | None:
        if self.content is None:
            return None
        a_tag = cast(Tag, self.nav.children[0])
        data_value_attr = a_tag.attrs.get("data-value", None)
        if isinstance(data_value_attr, HTML):
            data_value_attr = str(data_value_attr)
        return data_value_attr

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
        select the item (e.g., :func:`~shiny.ui.update_navset`). You can also
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


@add_example()
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


@add_example()
def nav_spacer() -> NavPanel:
    """
    Create space between nav items.

    See Also
    --------
    * :func:`~shiny.ui.nav_panel`
    * :func:`~shiny.ui.nav_menu`
    * :func:`~shiny.ui.nav_control`
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

    def get_value(self) -> str | None:
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


@add_example()
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
        select the item (e.g., :func:`~shiny.ui.update_navset`). You can also
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
    * :func:`~shiny.ui.nav_panel`
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
        id_resolved = resolve_id_or_none(id)
        selected = restore_input(id_resolved, selected)

        self.args = args
        self.ul_class = ul_class
        self.id = id_resolved
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
@add_example()
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
        id=id,
        selected=selected,
        header=header,
        footer=footer,
    )


@add_example()
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
        id=id,
        selected=selected,
        header=header,
        footer=footer,
    )


@add_example()
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
        id=id,
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
        id=id,
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
        full_screen: bool = False,
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
        self.full_screen = full_screen
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
            full_screen=self.full_screen,
        )


@add_example()
def navset_card_tab(
    *args: NavSetArg | MetadataNode | Sequence[MetadataNode],
    id: Optional[str] = None,
    selected: Optional[str] = None,
    title: Optional[TagChild] = None,
    sidebar: Optional[Sidebar] = None,
    full_screen: bool = False,
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
    full_screen
        If `True`, an icon will appear when hovering over the card body. Clicking the
        icon expands the card to fit viewport size.
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
        id=id,
        selected=selected,
        title=title,
        sidebar=sidebar,
        full_screen=full_screen,
        header=header,
        footer=footer,
        placement="above",
    )


@add_example()
def navset_card_pill(
    *args: NavSetArg | MetadataNode | Sequence[MetadataNode],
    id: Optional[str] = None,
    selected: Optional[str] = None,
    title: Optional[TagChild] = None,
    sidebar: Optional[Sidebar] = None,
    full_screen: bool = False,
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
    full_screen
        If `True`, an icon will appear when hovering over the card body. Clicking the
        icon expands the card to fit viewport size.
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
        id=id,
        selected=selected,
        title=title,
        sidebar=sidebar,
        full_screen=full_screen,
        header=header,
        footer=footer,
        placement=placement,
    )


@add_example()
def navset_card_underline(
    *args: NavSetArg | MetadataNode | Sequence[MetadataNode],
    id: Optional[str] = None,
    selected: Optional[str] = None,
    title: Optional[TagChild] = None,
    sidebar: Optional[Sidebar] = None,
    full_screen: bool = False,
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
    full_screen
        If `True`, an icon will appear when hovering over the card body. Clicking the
        icon expands the card to fit viewport size.
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
        id=id,
        selected=selected,
        title=title,
        sidebar=sidebar,
        full_screen=full_screen,
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


@add_example()
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
        id=id,
        selected=selected,
        header=header,
        footer=footer,
        well=well,
        widths=widths,
    )


NavbarOptionsPositionType = Literal[
    "static-top", "fixed-top", "fixed-bottom", "sticky-top"
]
NavbarOptionsThemeType = Literal["auto", "light", "dark"]


class NavbarOptions:
    position: NavbarOptionsPositionType
    bg: Optional[str]
    theme: NavbarOptionsThemeType
    underline: bool
    collapsible: bool
    attrs: dict[str, Any]
    _is_default: dict[str, bool]

    def __init__(
        self,
        *,
        position: NavbarOptionsPositionType | MISSING_TYPE = MISSING,
        bg: str | None | MISSING_TYPE = MISSING,
        theme: NavbarOptionsThemeType | MISSING_TYPE = MISSING,
        underline: bool | MISSING_TYPE = MISSING,
        collapsible: bool | MISSING_TYPE = MISSING,
        **attrs: TagAttrValue,
    ):
        self._is_default = {}

        self.position = self._maybe_default("position", position, default="static-top")
        self.bg = self._maybe_default("bg", bg, default=None)
        self.theme = self._maybe_default("theme", theme, default="auto")
        self.underline = self._maybe_default("underline", underline, default=True)
        self.collapsible = self._maybe_default("collapsible", collapsible, default=True)

        if "inverse" in attrs:
            warn_deprecated(
                "`navbar_options()` does not support `inverse`, please use `theme` instead."
            )
            del attrs["inverse"]

        self.attrs = attrs

    def _maybe_default(self, name: str, value: Any, default: Any):
        if isinstance(value, MISSING_TYPE):
            self._is_default[name] = True
            return default
        return value

    def __eq__(self, other: Any):
        if not isinstance(other, NavbarOptions):
            return False

        return (
            self.position == other.position
            and self.bg == other.bg
            and self.theme == other.theme
            and self.underline == other.underline
            and self.collapsible == other.collapsible
            and self.attrs == other.attrs
        )

    def __repr__(self):
        fields: list[str] = []
        for key, value in self.__dict__.items():
            if key == "_is_default":
                continue
            if not self._is_default.get(key, False):
                if key == "attrs" and len(value) == 0:
                    continue
                fields.append(f"{key}={value!r}")

        return f"navbar_options({', '.join(fields)})"


@add_example()
def navbar_options(
    position: NavbarOptionsPositionType | MISSING_TYPE = MISSING,
    bg: str | None | MISSING_TYPE = MISSING,
    theme: NavbarOptionsThemeType | MISSING_TYPE = MISSING,
    underline: bool | MISSING_TYPE = MISSING,
    collapsible: bool | MISSING_TYPE = MISSING,
    **attrs: TagAttrValue,
) -> NavbarOptions:
    """
    Configure the appearance and behavior of the navbar.

    ## Navbar style with Bootstrap 5 and Bootswatch themes

    In Shiny v1.3.0, the default navbar colors for Bootswatch themes are less
    opinionated by default and follow light or dark mode (see
    :func:`~shiny.ui.input_dark_mode`).

    You can use `ui.navbar_options()` to adjust the colors of the navbar when using a
    Bootswatch preset theme with Bootstrap 5. For example, the [Bootswatch documentation
    for the Flatly theme](https://bootswatch.com/flatly/) shows 4 navbar variations.
    Inspecting the source code for the first example reveals the following markup:

    ```html
    <nav class="navbar navbar-expand-lg bg-primary" data-bs-theme="dark">
      <!-- all of the navbar html -->
    </nav>
    ```

    Note that this navbar uses the `bg-primary` class for a dark navy background. The
    navbar's white text is controlled by the `data-bs-theme="dark"` attribute, which is
    used by Bootstrap for light text on a _dark_ background. In Shiny, you can achieve
    this look with:

    ```python
    ui.page_navbar(
      theme=ui.Theme(version=5, preset="flatly"),
      navbar_options=ui.navbar_options(class="bg-primary", theme="dark")
    )
    ```

    This particular combination of `class="bg-primary"` and `theme="dark"` works well
    for most Bootswatch presets. Note that in Shiny Express, `theme` and
    `navbar_options` both are set using :func:`~shiny.express.ui.page_opts`.

    Another variation from the Flatly documentation features a navbar with dark text on a
    light background:

    ```python
    ui.page_navbar(
      theme = ui.Theme(version=5, preset="flatly"),
      navbar_options = ui.navbar_options(class="bg-light", theme="light")
    )
    ```

    The above options set navbar foreground and background colors that are always the
    same in both light and dark modes. To customize the navbar colors used in light or
    dark mode, you can use the `$navbar-light-bg` and `$navbar-dark-bg` Sass variables.
    When provided, Shiny will automatically choose to use light or dark text as the
    foreground color.

    ```python
    ui.page_navbar(
        theme=(
            ui.Theme(version=5, preset = "flatly")
            .add_defaults(
                navbar_light_bg="#18BC9C", # flatly's success color (teal)
                navbar_dark_bg="#2C3E50"   # flatly's primary color (navy)
            )
        )
      )
    )
    ```

    Finally, you can also use the `$navbar-bg` Sass variable to set the navbar
    background color for both light and dark modes:

    ```python
    ui.page_navbar(
        theme=ui.Theme(version=5, preset="flatly").add_defaults(navbar_bg="#E74C3C") # flatly's red
    )
    ```

    Parameters
    -----------
    position
        Determines whether the navbar should be displayed at the top of the page with
        normal scrolling behavior (`"static-top"`), pinned at the top (`"fixed-top"`),
        or pinned at the bottom (`"fixed-bottom"`). Note that using `"fixed-top"` or
        `"fixed-bottom"` will cause the navbar to overlay your body content, unless you
        add padding (e.g., `tags.style("body {padding-top: 70px;}")`)
    bg
        Background color of the navbar (a CSS color).
    theme
        The navbar theme: either `"dark"` for a light text color (on a **dark**
        background) or `"light"` for a dark text color (on a **light** background). If
        `"auto"` (the default) and `bg` is provided, the best contrast to `bg` is
        chosen.
    underline
        If `True`, adds an underline effect to the navbar.
    collapsible
        If `True`, automatically collapses the elements into an expandable menu on
        mobile devices or narrow window widths.
    attrs
        Additional HTML attributes to apply to the navbar container element.

    Returns:
    --------
    NavbarOptions
        A NavbarOptions object configured with the specified options.
    """
    return NavbarOptions(
        position=position,
        bg=bg,
        theme=theme,
        underline=underline,
        collapsible=collapsible,
        **attrs,
    )


def navbar_options_resolve_deprecated(
    options_user: Optional[NavbarOptions] = None,
    position: NavbarOptionsPositionType | MISSING_TYPE = DEPRECATED,
    bg: str | None | MISSING_TYPE = DEPRECATED,
    inverse: bool | MISSING_TYPE = DEPRECATED,
    underline: bool | MISSING_TYPE = DEPRECATED,
    collapsible: bool | MISSING_TYPE = DEPRECATED,
    fn_caller: str = "navset_bar",
) -> NavbarOptions:
    options_user = options_user if options_user is not None else navbar_options()

    options_old = {
        "position": position,
        "bg": bg,
        "inverse": inverse,
        "collapsible": collapsible,
        "underline": underline,
    }
    options_old = {
        k: v for k, v in options_old.items() if not isinstance(v, MISSING_TYPE)
    }

    args_deprecated = list(options_old.keys())

    if not args_deprecated:
        return options_user

    args_deprecated = ", ".join([f"`{arg}`" for arg in args_deprecated])
    warn_deprecated(
        "In shiny v1.3.0, the arguments of "
        f"`{fn_caller}()` for navbar options (including {args_deprecated}) "
        f"have been consolidated into a single `navbar_options` argument."
    )

    if "inverse" in options_old:
        inverse_old = options_old["inverse"]
        del options_old["inverse"]

        if not isinstance(inverse_old, bool):
            raise ValueError(f"Invalid `inverse` value: {inverse}")

        options_old["theme"] = "dark" if inverse_old else "light"

    options_resolved = {
        k: v
        for k, v in vars(options_user).items()
        if k != "_is_default" and not options_user._is_default.get(k, False)
    }

    ignored: list[str] = []
    for opt in options_old:
        if opt not in options_resolved:
            options_resolved[opt] = options_old[opt]
        elif options_old[opt] != options_resolved[opt]:
            ignored.append("inverse" if opt == "theme" else opt)

    if ignored:
        warn_deprecated(
            f"`{', '.join(ignored)}` {'was' if len(ignored) == 1 else 'were'} provided twice: "
            "once directly and once in `navbar_options`.\n"
            "The deprecated direct option(s) will be ignored and the values from `navbar_options` will be used."
        )

    attrs = options_resolved.pop("attrs", {})

    return navbar_options(**options_resolved, **attrs)


class NavSetBar(NavSet):
    title: TagChild
    sidebar: Optional[Sidebar]
    fillable: bool | list[str]
    gap: Optional[CssUnit]
    padding: Optional[CssUnit | list[CssUnit]]
    fluid: bool
    navbar_options: NavbarOptions
    # Internal ----
    _is_page_level: bool

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
        fluid: bool = True,
        header: TagChild = None,
        footer: TagChild = None,
        navbar_options: Optional[NavbarOptions] = None,
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
        self.navbar_options = (
            navbar_options if navbar_options is not None else NavbarOptions()
        )
        self.fluid = fluid
        self._is_page_level = False

    def layout(self, nav: Tag, content: Tag) -> TagList:
        nav_container = div(
            {"class": "container-fluid" if self.fluid else "container"},
            tags.span({"class": "navbar-brand"}, self.title),
        )
        if self.navbar_options.collapsible:
            collapse_id = "navbar-collapse-" + nav_random_int()
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
        nav_final = tags.nav(
            {"class": "navbar navbar-expand-md"},
            nav_container,
            {"data-bs-theme": self.navbar_options.theme},
            **self.navbar_options.attrs,
        )

        if self.navbar_options.position != "static-top":
            nav_final.add_class(self.navbar_options.position)

        # bslib supports navbar-default/navbar-inverse (which is no longer
        # a thing in Bootstrap 5) in a way that's still useful, especially Bootswatch.
        nav_final.add_class(
            "navbar-inverse"
            if self.navbar_options.theme == "dark"
            else "navbar-default"
        )

        if self.navbar_options.bg:
            nav_final.add_style(
                f"background-color: {self.navbar_options.bg} !important;"
            )

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
            tab_content = contents
            if self._is_page_level:
                # TODO-future: This could also be applied to the non-sidebar page layout above
                from ._page import page_main_container

                tab_content = page_main_container(
                    *contents, fillable=self.fillable is not False
                )

            content_div = div(
                # In the fluid case, the sidebar layout should be flush (i.e.,
                # the .container-fluid class adds padding that we don't want)
                {"class": "container"} if not self.fluid else None,
                layout_sidebar(
                    self.sidebar,
                    tab_content,
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
@add_example()
def navset_bar(
    *args: NavSetArg | MetadataNode | Sequence[MetadataNode],
    title: TagChild,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    sidebar: Optional[Sidebar] = None,
    fillable: bool | list[str] = True,
    gap: Optional[CssUnit] = None,
    padding: Optional[CssUnit | list[CssUnit]] = None,
    header: TagChild = None,
    footer: TagChild = None,
    navbar_options: Optional[NavbarOptions] = None,
    fluid: bool = True,
    # Deprecated -- v1.3.0 2025-01 ----
    position: NavbarOptionsPositionType | MISSING_TYPE = DEPRECATED,
    bg: str | None | MISSING_TYPE = DEPRECATED,
    inverse: bool | MISSING_TYPE = DEPRECATED,
    underline: bool | MISSING_TYPE = DEPRECATED,
    collapsible: bool | MISSING_TYPE = DEPRECATED,
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
        `*args`. This value is only used when the navbar is `fillable`.
    padding
        Padding to use for the body. This can be a numeric vector (which will be
        interpreted as pixels) or a character vector with valid CSS lengths. The length
        can be between one and four. If one, then that value will be used for all four
        sides. If two, then the first value will be used for the top and bottom, while
        the second value will be used for left and right. If three, then the first will
        be used for top, the second will be left and right, and the third will be
        bottom. If four, then the values will be interpreted as top, right, bottom, and
        left respectively. This value is only used when the navbar is `fillable`.
    header
        UI to display above the selected content.
    footer
        UI to display below the selected content.
    fluid
        ``True`` to use fluid layout; ``False`` to use fixed layout.
    navbar_options
        Configure the appearance and behavior of the navbar using
        :func:`~shiny.ui.navbar_options` to set properties like position, background
        color, and more.

        `navbar_options` was added in v1.3.0 and replaces deprecated arguments
        `position`, `bg`, `inverse`, `collapsible`, and `underline`.
    position
        Deprecated in v1.3.0. Please use `navbar_options` instead; see
        :func:`~shiny.ui.navbar_options` for details.

        Determines whether the navbar should be displayed at the top of the page with
        normal scrolling behavior ("static-top"), pinned at the top ("fixed-top"), or
        pinned at the bottom ("fixed-bottom"). Note that using "fixed-top" or
        "fixed-bottom" will cause the navbar to overlay your body content, unless you
        add padding (e.g., ``tags.style("body {padding-top: 70px;}")``).
    bg
        Deprecated in v1.3.0. Please use `navbar_options` instead; see
        :func:`~shiny.ui.navbar_options` for details.

        Background color of the navbar (a CSS color).
    inverse
        Deprecated in v1.3.0. Please use `navbar_options` instead; see
        :func:`~shiny.ui.navbar_options` for details.

        Either ``True`` for a light text color or ``False`` for a dark text color.
    collapsible
        Deprecated in v1.3.0. Please use `navbar_options` instead; see
        :func:`~shiny.ui.navbar_options` for details.

        ``True`` to automatically collapse the elements into an expandable menu on
        mobile devices or narrow window widths.

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

    navbar_opts = navbar_options_resolve_deprecated(
        fn_caller="navset_bar",
        options_user=navbar_options or NavbarOptions(),
        position=position,
        bg=bg,
        inverse=inverse,
        underline=underline,
        collapsible=collapsible,
    )

    ul_class = "nav navbar-nav"
    if navbar_opts.underline:
        ul_class += " nav-underline"
    return NavSetBar(
        *new_args,
        ul_class=ul_class,
        id=id,
        selected=selected,
        sidebar=sidebar,
        fillable=fillable,
        gap=gap,
        padding=padding,
        title=title,
        header=header,
        footer=footer,
        fluid=fluid,
        navbar_options=navbar_opts,
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
    tabsetid = nav_random_int()

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


def nav_random_int() -> str:
    return private_random_int(1000, 1000000)
