from __future__ import annotations

from typing import Callable, Optional

from htmltools import Tag, TagAttrs, TagAttrValue, TagChild, css, div

from ._card import card, card_body
from ._card_item import CardItem
from ._css import CssUnit, validate_css_unit
from ._fill import as_fill_carrier
from ._layout import layout_column_wrap
from ._utils import consolidate_attrs, is_01_scalar


# It seems to be to use % over fr here since there is no gap on the grid
def to_width_unit(x: str | float | int) -> str:
    if isinstance(x, (int, float)):
        return validate_css_unit(x)

    if isinstance(x, str) and x.endswith("%") and x.count("%") == 1:
        x1_num = float(x[:-1])
        x2_num = 100 - x1_num
        return f"{x1_num}% {x2_num}%"

    # TODO-bslib: validateCssUnit() should maybe support fr units?
    # return(paste(x, collapse = " "))
    return validate_css_unit(x)


def value_box(
    title: TagChild,
    value: TagChild,
    *args: TagChild | TagAttrs,
    showcase: Optional[TagChild] = None,
    showcase_layout: Callable[[TagChild, Tag], CardItem] | None = None,
    full_screen: bool = False,
    theme_color: Optional[str] = "primary",
    height: Optional[CssUnit] = None,
    max_height: Optional[CssUnit] = None,
    fill: bool = True,
    class_: Optional[str] = None,
    **kwargs: TagAttrValue,
) -> Tag:
    attrs, children = consolidate_attrs(
        # Must be before `attrs` so that `class_` is applied before any `attrs` values
        {"class": "bslib-value-box border-0"},
        {"class": f"bg-{theme_color}"} if theme_color else None,
        *args,
        class_=class_,
        **kwargs,
    )

    if showcase_layout is None:
        showcase_layout = showcase_left_center()
    if isinstance(title, (str, int, float)):
        title = div(str(title), class_="h6 mb-1")
    if isinstance(title, (str, int, float)):
        value = div(str(value), class_="h2 mb-2")

    contents = div(
        title,
        value,
        *children,
        class_="value-box-area",
    )
    contents = as_fill_carrier(contents)

    if showcase is not None:
        contents = showcase_layout(showcase, contents)

    # Must use `class_` in `card()` as it must be applied after `bind_fill_role()`

    return card(
        contents,
        attrs,
        full_screen=full_screen,
        height=height,
        max_height=max_height,
        fill=fill,
    )


# @param width one of the following:
#   * A proportion (i.e., a number between 0 and 1) of available width to
#     allocate to the showcase.
#   * A vector of length 2 valid [CSS unit][htmltools::validateCssUnit] defining
#     the width of each column (for `showcase_left_center()` the 1st unit defines
#     the showcase width and for `showcase_top_right` the 2nd unit defines the
#     showcase width). Note that any units supported by the CSS grid
#     `grid-template-columns` property may be used (e.g., `fr` units).
# @param max_height,max_height_full_screen A proportion (i.e., a number between
#   0 and 1) or any valid [CSS unit][htmltools::validateCssUnit] defining the
#   showcase max_height.
#
# @export
# @rdname value_box
def showcase_left_center(
    width: CssUnit = "30%",
    max_height: CssUnit = "100px",
    max_height_full_screen: CssUnit = "67%",
) -> Callable[[TagChild | TagAttrs, Tag], CardItem]:
    return showcase_layout_(
        width=width,
        max_height=max_height,
        max_height_full_screen=max_height_full_screen,
        top_right=False,
    )


# @export
# @rdname value_box
def showcase_top_right(
    width: CssUnit = "30%",
    max_height: CssUnit = "75px",
    max_height_full_screen: CssUnit = "67%",
) -> Callable[[TagChild | TagAttrs, Tag], CardItem]:
    if is_01_scalar(width):
        width = 1 - width
    return showcase_layout_(
        width=width,
        max_height=max_height,
        max_height_full_screen=max_height_full_screen,
        top_right=True,
    )


def showcase_layout_(
    width: CssUnit,
    max_height: CssUnit,
    max_height_full_screen: CssUnit,
    top_right: bool,
) -> Callable[[TagChild | TagAttrs, Tag], CardItem]:
    # Do not "magically" turn `0.3` into `"30%"` as it is not clear to the user when it happens
    width_css_unit = to_width_unit(width)
    max_height_css_unit = validate_css_unit(max_height)
    max_height_full_screen_css_unit = validate_css_unit(max_height_full_screen)

    def _showcase_layout(showcase: TagChild | TagAttrs, contents: Tag) -> CardItem:
        css_args = {
            "--bslib-value-box-max-height": max_height_css_unit,
            "--bslib-value-box-max-height-full-screen": max_height_full_screen_css_unit,
        }
        showcase_container = div(
            showcase,
            {"class": "value-box-showcase overflow-hidden"},
            {"class": "showcase-top-right"} if top_right else None,
            style=css(**css_args),
        )
        showcase_container = as_fill_carrier(showcase_container)

        if not top_right:
            contents.add_class("border-start")

        items = [showcase_container, contents]
        width_fs = ["1fr", "auto"]
        if top_right:
            items = reversed(items)
            width_fs = reversed(width_fs)

        layout_css_args = {
            "--bslib-value-box-widths": width_css_unit,
            "--bslib-value-box-widths-full-screen": width_fs,
        }
        return card_body(
            layout_column_wrap(
                None,  # width
                *items,
                style=css(**layout_css_args),
                gap=0,
                heights_equal="row",
                class_="value-box-grid",
            ),
            style=css(padding=0),
        )

    return _showcase_layout
