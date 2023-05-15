from __future__ import annotations

import numbers
import random
from typing import Optional

from htmltools import Tag, TagAttrs, TagChild, css, div
from htmltools import svg as svgtags
from htmltools import tags

from shiny._typing_extensions import Literal

from ._color import get_color_contrast
from ._css import CssUnit, trinary, validate_css_unit
from ._fill import bind_fill_role
from ._htmldeps import sidebar_dependency


class Sidebar:
    def __init__(
        self,
        tag: Tag,
        collapse_tag: Optional[Tag],
        position: Literal["left", "right"],
        open: Literal["desktop", "open", "closed", "always"],
        width: int,
        max_height_mobile: Optional[str | float],
    ):
        self.tag = tag
        self.collapse_tag = collapse_tag
        self.position = position
        self.open = open
        self.width = width
        self.max_height_mobile = max_height_mobile


def sidebar(
    *args: TagChild | TagAttrs,
    width: int = 250,
    position: Literal["left", "right"] = "left",
    open: Literal["desktop", "open", "closed", "always"] = "desktop",
    id: Optional[str] = None,
    title: TagChild | str | numbers.Number = None,
    bg: Optional[str] = None,
    fg: Optional[str] = None,
    class_: Optional[str] = None,  # TODO-future; Consider using `**kwargs` instead
    max_height_mobile: Optional[str | float] = None,
) -> Sidebar:
    # TODO: validate `open`, bg, fg, class_, max_height_mobile
    # TODO: Add type annotations

    if id is None and open != "always":
        # but always provide id when collapsible for accessibility reasons
        id = f"bslib-sidebar-{random.randint(1000, 10000)}"

    if fg is None and bg is not None:
        fg = get_color_contrast(bg)
    if bg is None and fg is not None:
        bg = get_color_contrast(fg)

    if isinstance(title, str) or isinstance(title, numbers.Number):
        title = div(str(title), class_="sidebar-title")

    collapse_tag = None
    if open != "always":
        collapse_tag = tags.button(
            collapse_icon(),
            class_="collapse-toggle",
            type="button",
            title="Toggle sidebar",
            style=css(background_color=bg, color=fg),
            aria_expanded=trinary(open in ["open", "desktop"]),
            aria_controls=id,
        )

    tag = div(
        div(title, *args, class_="sidebar-content"),
        {"class": "bslib-sidebar-input"} if id is not None else None,
        {"class": "sidebar"},
        id=id,
        role="complementary",
        class_=class_,
        style=css(background_color=bg, color=fg),
    )

    return Sidebar(
        tag=tag,
        collapse_tag=collapse_tag,
        position=position,
        open=open,
        width=width,
        max_height_mobile=max_height_mobile,
    )


def collapse_icon() -> Tag:
    return tags.svg(
        svgtags.path(
            fill_rule="evenodd",
            d="M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z",
        ),
        xmlns="http://www.w3.org/2000/svg",
        viewBox="0 0 16 16",
        class_="bi bi-chevron-down collapse-icon",
        style="fill:currentColor;",
        aria_hidden="true",
        role="img",
    )


def layout_sidebar(
    sidebar: Sidebar,
    *args: TagChild | TagAttrs,
    fillable: bool = False,
    fill: bool = True,
    bg: Optional[str] = None,
    fg: Optional[str] = None,
    border: Optional[str] = None,
    border_radius: Optional[bool] = None,
    border_color: Optional[str] = None,
    height: Optional[CssUnit] = None,
) -> Tag:
    # TODO: validate sidebar object, border, border_radius, colors

    if fg is None and bg is not None:
        fg = get_color_contrast(bg)
    if bg is None and fg is not None:
        bg = get_color_contrast(fg)

    main = div(
        *args,
        role="main",
        class_="main",
        style=css(background_color=bg, color=fg),
    )

    main = bind_fill_role(main, container=fillable)

    contents = [main, sidebar.tag, sidebar.collapse_tag]

    right = sidebar.position == "right"

    max_height_mobile = sidebar.max_height_mobile or (
        "250px" if height is None else "50%"
    )

    res = div(
        sidebar_dependency(),
        sidebar_js_init(),
        {"class": "bslib-sidebar-layout"},
        {"class": "sidebar-right"} if right else None,
        {"class": "sidebar-collapsed"} if sidebar.open == "closed" else None,
        *contents,
        data_sidebar_init_auto_collapse="true" if sidebar.open == "desktop" else None,
        data_bslib_sidebar_border=trinary(border),
        data_bslib_sidebar_border_radius=trinary(border_radius),
        style=css(
            __bslib_sidebar_width=validate_css_unit(sidebar.width),
            __bs_card_border_color=border_color,
            height=validate_css_unit(height),
            __bslib_sidebar_max_height_mobile=validate_css_unit(max_height_mobile),
        ),
    )

    res = bind_fill_role(res, item=fill)

    # res <- as.card_item(res)
    # as_fragment(
    #     tag_require(res, version = 5, caller = "layout_sidebar()")
    # )
    return res


def sidebar_js_init() -> Tag:
    return tags.script(
        {"data_bslib_sidebar_init": True},
        """
        var thisScript = document.querySelector('script[data-bslib-sidebar-init]');
        thisScript.removeAttribute('data-bslib-sidebar-init');

        // If this layout is the innermost layout, then allow it to add CSS
        // variables to it and its ancestors (counting how parent layouts there are)
        var thisLayout = $(thisScript).parent();
        var noChildLayouts = thisLayout.find('.bslib-sidebar-layout').length === 0;
        if (noChildLayouts) {
        var parentLayouts = thisLayout.parents('.bslib-sidebar-layout');
        // .add() sorts the layouts in DOM order (i.e., innermost is last)
        var layouts = thisLayout.add(parentLayouts);
        var ctrs = {left: 0, right: 0};
        layouts.each(function(i, x) {
            $(x).css('--bslib-sidebar-counter', i);
            var right = $(x).hasClass('sidebar-right');
            $(x).css('--bslib-sidebar-overlap-counter', right ? ctrs.right : ctrs.left);
            right ? ctrs.right++ : ctrs.left++;
        });
        }

        // If sidebar is marked open='desktop', collapse sidebar if on mobile
        if (thisLayout.data('sidebarInitAutoCollapse')) {
        var initCollapsed = thisLayout.css('--bslib-sidebar-js-init-collapsed');
        if (initCollapsed === 'true') {
            thisLayout.addClass('sidebar-collapsed');
            thisLayout.find('.collapse-toggle').attr('aria-expanded', 'false');
        }
        }
        """,
    )
