from __future__ import annotations

import random
from typing import Literal, Optional

from htmltools import Tag, TagAttrs, TagAttrValue, TagChild, TagList, css, div
from htmltools import svg as svgtags
from htmltools import tags

# from ._color import get_color_contrast
from ._css_unit import CssUnit, as_css_padding, as_css_unit
from ._fill import as_fill_item, as_fillable_container
from ._htmldeps import sidebar_dependency
from ._utils import consolidate_attrs, trinary


class Sidebar:
    def __init__(
        self,
        tag: Tag,
        collapse_tag: Optional[Tag],
        position: Literal["left", "right"],
        open: Literal["desktop", "open", "closed", "always"],
        width: CssUnit,
        max_height_mobile: Optional[str | float],
        color_fg: Optional[str],
        color_bg: Optional[str],
    ):
        self.tag = tag
        self.collapse_tag = collapse_tag
        self.position = position
        self.open = open
        self.width = width
        self.max_height_mobile = max_height_mobile
        self.color_fg = color_fg
        self.color_bg = color_bg

    # # This does not contain the `collapse_tag`
    # # The `Sidebar` class should use it's fields, not this method
    # def tagify(self) -> Tag:
    #     return self.tag.tagify()


def sidebar(
    *args: TagChild | TagAttrs,
    width: CssUnit = 250,
    position: Literal["left", "right"] = "left",
    open: Literal["desktop", "open", "closed", "always"] = "desktop",
    id: Optional[str] = None,
    title: TagChild | str = None,
    bg: Optional[str] = None,
    fg: Optional[str] = None,
    class_: Optional[str] = None,  # TODO-future; Consider using `**kwargs` instead
    max_height_mobile: Optional[str | float] = None,
) -> Sidebar:
    # See [this article](https://rstudio.github.io/bslib/articles/sidebars.html)
    #   to learn more.
    # TODO-future; If color contrast is implemented. Docs for `bg` and `fg`:
    #     If only one of either is provided, an
    #     accessible contrasting color is provided for the opposite color, e.g. setting
    #     `bg` chooses an appropriate `fg` color.
    # TODO-future; validate `open`, bg, fg, class_, max_height_mobile

    if id is None and open != "always":
        # but always provide id when collapsible for accessibility reasons
        id = f"bslib-sidebar-{random.randint(1000, 10000)}"

    # TODO-future; implement
    # if fg is None and bg is not None:
    #     fg = get_color_contrast(bg)
    # if bg is None and fg is not None:
    #     bg = get_color_contrast(fg)

    if isinstance(title, (str, int, float)):
        title = div(str(title), class_="sidebar-title")

    collapse_tag = None
    # Code
    if open != "always":
        collapse_tag = tags.button(
            _collapse_icon(),
            class_="collapse-toggle",
            type="button",
            title="Toggle sidebar",
            aria_expanded=trinary(open in ["open", "desktop"]),
            aria_controls=id,
        )

    tag = div(
        div(
            title,
            {"class": "sidebar-content"},
            *args,
        ),
        {"class": "bslib-sidebar-input"} if id is not None else None,
        {"class": "sidebar"},
        id=id,
        role="complementary",
        class_=class_,
    )

    return Sidebar(
        tag=tag,
        collapse_tag=collapse_tag,
        position=position,
        open=open,
        width=width,
        max_height_mobile=max_height_mobile,
        color_fg=fg,
        color_bg=bg,
    )


# TODO-maindocs; @add_example()
def layout_sidebar(
    sidebar: Sidebar,
    content: PanelMain,
    fillable: bool = True,
    fill: bool = True,
    bg: Optional[str] = None,
    fg: Optional[str] = None,
    border: Optional[bool] = None,
    border_radius: Optional[bool] = None,
    border_color: Optional[str] = None,
    gap: Optional[CssUnit] = None,
    padding: Optional[CssUnit | list[CssUnit]] = None,
    height: Optional[CssUnit] = None,
    **kwargs: TagAttrValue,
) -> Tag:
    attrs, _ = consolidate_attrs(**content.attrs, **kwargs)

    main = div(
        {
            "role": "main",
            "class": f"main{' bslib-gap-spacing' if fillable else ''}",
            ""
            "style": css(
                background_color=bg,
                color=fg,
                gap=as_css_unit(gap),
                padding=as_css_padding(padding),
            ),
        },
        attrs,
        content,
    )
    if fillable:
        main = as_fillable_container(main)

    max_height_mobile = sidebar.max_height_mobile or (
        "250px" if height is None else "50%"
    )

    res = div(
        {"class": "bslib-sidebar-layout"},
        {"class": "sidebar-right"} if sidebar.position == "right" else None,
        {"class": "sidebar-collapsed"} if sidebar.open == "closed" else None,
        main,
        sidebar.tag,
        sidebar.collapse_tag,
        sidebar_dependency(),
        _sidebar_init_js(),
        data_bslib_sidebar_init="true" if sidebar.open != "always" else None,
        data_bslib_sidebar_open=sidebar.open,
        data_bslib_sidebar_border=trinary(border),
        data_bslib_sidebar_border_radius=trinary(border_radius),
        style=css(
            __bslib_sidebar_width=as_css_unit(sidebar.width),
            __bslib_sidebar_bg=as_css_unit(sidebar.color_bg),
            __bslib_sidebar_fg=as_css_unit(sidebar.color_fg),
            __bs_card_border_color=border_color,
            height=as_css_unit(height),
            __bslib_sidebar_max_height_mobile=as_css_unit(max_height_mobile),
        ),
    )
    if fill:
        res = as_fill_item(res)

    return res


# _sidebar_func = sidebar


def _collapse_icon() -> Tag:
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


def _sidebar_init_js() -> Tag:
    # Note: if we want to avoid inline `<script>` tags in the future for
    # initialization code, we might be able to do so by turning the sidebar layout
    # container into a web component
    return tags.script(
        {"data-bslib-sidebar-init": True},
        "bslib.Sidebar.initCollapsibleAll()",
    )


###################################################################


class PanelSidebar:
    # Store `attrs` for `layout_sidebar()` to retrieve
    def __init__(
        self, *args: TagChild | TagAttrs, width: int = 4, **kwargs: TagAttrValue
    ) -> None:
        self.args = args
        self.kwargs = kwargs
        self.width = width

    def get_sidebar(self, position: Literal["left", "right"] = "left") -> Sidebar:
        return sidebar(
            *self.args,
            width=f"{int(self.width / 12 * 100)}%",
            position=position,
            open="always",
            **self.kwargs,
        )

    # Hopefully this is never used. But it makes it Tagifiable to allow us to not expose
    # `Sidebar` and `PanelSidebar` classes
    def tagify(self) -> Tag:
        return self.get_sidebar().tag.tagify()


class PanelMain:
    # Store `attrs` for `layout_sidebar()` to retrieve
    attrs: TagAttrs
    # Return `children` in `layout_sidebar()` via `.tagify()` method
    children: list[TagChild]

    def __init__(self, *, attrs: TagAttrs, children: list[TagChild]) -> None:
        self.attrs = attrs
        self.children = children

    def tagify(self) -> TagList:
        return TagList(self.children).tagify()
