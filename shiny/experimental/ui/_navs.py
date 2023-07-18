from __future__ import annotations

__all__ = (
    "navset_bar",
    "navset_tab_card",
    "navset_pill_card",
)

import copy
from typing import Any, Literal, Optional, Sequence, cast

from htmltools import MetadataNode, Tag, TagChild, TagList, css, div, tags

from ..._namespaces import resolve_id
from ..._utils import private_random_int
from ...types import NavSetArg
from ...ui._html_dependencies import bootstrap_deps
from ._card import CardItem, card, card_body, card_footer, card_header
from ._css_unit import CssUnit, as_css_padding, as_css_unit
from ._fill import as_fill_carrier
from ._sidebar import Sidebar, layout_sidebar
from ._tag import tag_add_style


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

        nav, content = _render_navset(
            *self.args, ul_class=ul_class, id=id, selected=self.selected, context={}
        )
        return self.layout(nav, content).tagify()

    # Types must match output of `_render_navset() -> Tuple[Tag, Tag]`
    def layout(self, nav: Tag, content: Tag) -> TagList | Tag:
        return TagList(nav, self.header, content, self.footer)


# -----------------------------------------------------------------------------
# Navigation containers
# -----------------------------------------------------------------------------


class NavSetCard(NavSet):
    placement: Literal["above", "below"]
    sidebar: Optional[Sidebar]

    def __init__(
        self,
        *args: NavSetArg,
        ul_class: str,
        id: Optional[str],
        selected: Optional[str],
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
        self.sidebar = sidebar
        self.placement = placement

    def layout(self, nav: Tag, content: Tag) -> Tag:
        # navs = [child for child in content.children if isinstance(child, Nav)]
        # not_navs = [child for child in content.children if child not in navs]
        content_val: Tag | CardItem = content

        if self.sidebar:
            content_val = navset_card_body(content, sidebar=self.sidebar)

        if self.placement == "below":
            # TODO-carson; have carson double check this change
            return card(
                card_header(self.header) if self.header else None,
                content_val,
                card_body(self.footer, fillable=False, fill=False)
                if self.footer
                else None,
                card_footer(nav),
            )
        else:
            # TODO-carson; have carson double check this change
            return card(
                card_header(nav),
                card_body(self.header, fill=False, fillable=False)
                if self.header
                else None,
                content_val,
                card_footer(self.footer) if self.footer else None,
            )


def navset_card_body(content: Tag, sidebar: Optional[Sidebar] = None) -> CardItem:
    content = _make_tabs_fillable(content, fillable=True, gap=0, padding=0)
    if sidebar:
        return layout_sidebar(
            sidebar,
            content,
            fillable=True,
            border=False,
        )
    else:
        return CardItem(content)


def navset_tab_card(
    *args: NavSetArg,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    sidebar: Optional[Sidebar] = None,
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
    * ~shiny.ui.nav
    * ~shiny.ui.nav_menu
    * ~shiny.ui.nav_control
    * ~shiny.ui.nav_spacer
    * ~shiny.experimental.ui.navset_bar
    * ~shiny.ui.navset_tab
    * ~shiny.ui.navset_pill
    * ~shiny.experimental.ui.navset_pill_card
    * ~shiny.ui.navset_hidden

    Example
    -------
    See :func:`~shiny.ui.nav`
    """

    return NavSetCard(
        *args,
        ul_class="nav nav-tabs card-header-tabs",
        id=resolve_id(id) if id else None,
        selected=selected,
        sidebar=sidebar,
        header=header,
        footer=footer,
        placement="above",
    )


def navset_pill_card(
    *args: NavSetArg,
    id: Optional[str] = None,
    selected: Optional[str] = None,
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
    * ~shiny.ui.nav
    * ~shiny.ui.nav_menu
    * ~shiny.ui.nav_control
    * ~shiny.ui.nav_spacer
    * ~shiny.experimental.ui.navset_bar
    * ~shiny.ui.navset_tab
    * ~shiny.ui.navset_pill
    * ~shiny.experimental.ui.navset_tab_card
    * ~shiny.ui.navset_hidden

    Example
    -------
    See :func:`~shiny.ui.nav`
    """

    return NavSetCard(
        *args,
        ul_class="nav nav-pills card-header-pills",
        id=resolve_id(id) if id else None,
        selected=selected,
        sidebar=sidebar,
        header=header,
        footer=footer,
        placement=placement,
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
    collapsible: bool
    fluid: bool

    def __init__(
        self,
        *args: NavSetArg | MetadataNode,
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
        # TODO-bslib: default to 'auto', like we have in R (parse color via webcolors?)
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
        self.sidebar = sidebar
        self.fillable = fillable
        self.gap = gap
        self.padding = padding

        self.position = position
        self.bg = bg
        self.inverse = inverse
        self.collapsible = collapsible
        self.fluid = fluid

    def layout(self, nav: Tag, content: Tag) -> TagList:
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

        content = _make_tabs_fillable(
            content, self.fillable, gap=self.gap, padding=self.padding, navbar=True
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
                content_div = as_fill_carrier(content_div)
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
            content_div = as_fill_carrier(content_div)

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
    content = as_fill_carrier(content)

    for child in content.children:
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
        child = tag_add_style(child, styles)
        child = as_fill_carrier(child)

    return content


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
    # TODO-bslib: default to 'auto', like we have in R (parse color via webcolors?)
    inverse: bool = False,
    collapsible: bool = True,
    fluid: bool = True,
) -> NavSetBar:
    """
    Render nav items as a navbar.

    Parameters
    ----------
    *args
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
    * ~shiny.ui.page_navbar
    * ~shiny.ui.nav
    * ~shiny.ui.nav_menu
    * ~shiny.ui.nav_control
    * ~shiny.ui.nav_spacer
    * ~shiny.ui.navset_tab
    * ~shiny.ui.navset_pill
    * ~shiny.experimental.ui.navset_tab_card
    * ~shiny.experimental.ui.navset_pill_card
    * ~shiny.ui.navset_hidden

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
        collapsible=collapsible,
        fluid=fluid,
    )


# -----------------------------------------------------------------------------
# Utilities for rendering navs
# -----------------------------------------------------------------------------\
def _render_navset(
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


# # Card definition was gutted for bslib version.
# # * Bootstrap deps are not added

# def card(*args: TagChild, header: TagChild = None, footer: TagChild = None) -> Tag:
#     if header:
#         header = div(header, class_="card-header")
#     if footer:
#         footer = div(footer, class_="card-footer")

#     return div(
#         header,
#         div(*args, class_="card-body"),
#         footer,
#         bootstrap_deps(),
#         class_="card",
#     )
