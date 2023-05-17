from __future__ import annotations

import numbers
import random
from typing import Optional

from htmltools import HTML, Tag, TagAttrs, TagAttrValue, TagChild, TagList, css, div
from htmltools import svg as svgtags
from htmltools import tags

from ..._deprecated import warn_deprecated
from ..._typing_extensions import Literal
from ...session import Session, require_active_session

# from ._color import get_color_contrast
from ._css import CssUnit, trinary, validate_css_unit
from ._fill import bind_fill_role
from ._htmldeps import sidebar_dependency
from ._utils import consolidate_attrs


class Sidebar:
    def __init__(
        self,
        tag: Tag,
        collapse_tag: Optional[Tag],
        position: Literal["left", "right"],
        open: Literal["desktop", "open", "closed", "always"],
        width: CssUnit,
        max_height_mobile: Optional[str | float],
    ):
        self.tag = tag
        self.collapse_tag = collapse_tag
        self.position = position
        self.open = open
        self.width = width
        self.max_height_mobile = max_height_mobile

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
    title: TagChild | str | numbers.Number = None,
    bg: Optional[str] = None,
    fg: Optional[str] = None,
    class_: Optional[str] = None,  # TODO-future; Consider using `**kwargs` instead
    max_height_mobile: Optional[str | float] = None,
) -> Sidebar:
    # TODO-future; validate `open`, bg, fg, class_, max_height_mobile

    if id is None and open != "always":
        # but always provide id when collapsible for accessibility reasons
        id = f"bslib-sidebar-{random.randint(1000, 10000)}"

    # TODO-future; implement
    # if fg is None and bg is not None:
    #     fg = get_color_contrast(bg)
    # if bg is None and fg is not None:
    #     bg = get_color_contrast(fg)

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


def layout_sidebar(
    sidebar: Sidebar,
    *args: TagChild | TagAttrs,
    fillable: bool = False,
    fill: bool = True,
    bg: Optional[str] = None,
    fg: Optional[str] = None,
    border: Optional[bool] = None,
    border_radius: Optional[bool] = None,
    border_color: Optional[str] = None,
    height: Optional[CssUnit] = None,
    **kwargs: TagAttrValue,
) -> Tag:
    assert isinstance(sidebar, Sidebar)

    # TODO-future; implement
    # if fg is None and bg is not None:
    #     fg = get_color_contrast(bg)
    # if bg is None and fg is not None:
    #     bg = get_color_contrast(fg)

    main = div(
        {"role": "main", "class": "main", "style": css(background_color=bg, color=fg)},
        *args,
        **kwargs,
    )
    main = bind_fill_role(main, container=fillable)

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
        sidebar_init_js(),
        data_bslib_sidebar_init="true" if sidebar.open != "always" else None,
        data_bslib_sidebar_open=sidebar.open,
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

    return res


# @describeIn sidebar Toggle a `sidebar()` state during an active Shiny user
#   session.
# @param session A Shiny session object (the default should almost always be
#   used).
# @export
def sidebar_toggle(
    id: str,
    open: Literal["toggle", "open", "closed", "always"] | bool | None = None,
    session: Session | None = None,
) -> None:
    session = require_active_session(session)

    method: Literal["toggle", "open", "close"]
    if open is None or open == "toggle":
        method = "toggle"
    elif open is True or open == "open":
        method = "open"
    elif open is False or open == "closed":
        method = "close"
    else:
        if open == "always" or open == "desktop":
            raise ValueError(
                f"`open = '{open}'` is not supported by `sidebar_toggle()`"
            )
        raise ValueError(
            "open must be NULL (or 'toggle'), TRUE (or 'open'), or FALSE (or 'closed')"
        )

    def callback() -> None:
        session.send_input_message(id, {"method": method})

    session.on_flush(callback, once=True)


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


def sidebar_init_js() -> Tag:
    # Note: if we want to avoid inline `<script>` tags in the future for
    # initialization code, we might be able to do so by turning the sidebar layout
    # container into a web component
    return tags.script(
        {"data-bslib-sidebar-init": True},
        "bslib.Sidebar.initCollapsibleAll()",
    )


########################################################


def panel_sidebar(
    *args: TagChild | TagAttrs,
    width: int = 4,
    **kwargs: TagAttrValue,
) -> Sidebar:
    """Deprecated. Please use `ui.sidebar()` instead of `ui.panel_sidebar()`."""
    warn_deprecated("`panel_sidebar()` is deprecated. Please use `sidebar()` instead.")
    return sidebar(
        *args,
        # id="bslib-panel-sidebar",
        width=f"{int(width / 12 * 100)}%",
        **kwargs,
    )


def panel_main(
    *args: TagChild | TagAttrs,
    width: int = 8,
    **kwargs: TagAttrValue,
) -> TagList:
    """Deprecated. Please supply `*args` directly to `layout_sidebar()` instead."""
    warn_deprecated(
        "`panel_main()` is deprecated. Please supply `*args` directly to `layout_sidebar()` instead."
    )
    # warn if keys are being ignored
    attrs, children = consolidate_attrs(*args, **kwargs)
    if len(attrs) > 0:
        warn_deprecated(
            "`*args: TagAttrs` or `**kwargs: TagAttrValue` values supplied to `panel_main()` are being ignored"
        )

    return TagList(*children)
