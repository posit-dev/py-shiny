from __future__ import annotations

import numbers
from typing import Callable, Optional

from htmltools import Tag, TagAttrs, TagChild, css, div

from shiny._typing_extensions import TypeGuard

from ._card import CardItem, card, card_body
from ._css import CssUnit, validate_css_unit
from ._fill import bind_fill_role
from ._layout import layout_column_wrap


def is_01_scalar(x: object) -> TypeGuard[float]:
    return isinstance(x, float) and x >= 0.0 and x <= 1.0


# It seems to be to use % over fr here since there is no gap on the grid
def validate_width_unit(x: str | float) -> str:
    if is_01_scalar(x):
        scaled_x = 100 * x
        scaled_not_x = 100 * (1 - x)
        return f"{scaled_x}% {scaled_not_x}%"

    # TODO: validateCssUnit() should maybe support fr units?
    # return(paste(x, collapse = " "))
    return str(x)


def validate_height_unit(x: str | float) -> str:
    if is_01_scalar(x):
        return f"{100 * x}%"

    height_unit = validate_css_unit(x)
    assert height_unit is not None
    return height_unit


def value_box(
    title: TagChild | str | numbers.Number,
    value: TagChild | str | numbers.Number,
    *args: TagChild | TagAttrs,
    showcase: Optional[TagChild] = None,
    showcase_layout: Callable[[TagChild, Tag], CardItem] | None = None,
    full_screen: bool = False,
    theme_color: Optional[str] = "primary",
    height: Optional[CssUnit] = None,
    max_height: Optional[CssUnit] = None,
    fill: bool = True,
    class_: Optional[str] = None,
    **kwargs: TagChild | TagAttrs,
) -> Tag:
    if showcase_layout is None:
        showcase_layout = showcase_left_center()
    if isinstance(title, str) or isinstance(title, numbers.Number):
        title = div(str(title), class_="h6 mb-1")
    if isinstance(value, str) or isinstance(value, numbers.Number):
        value = div(str(value), class_="h2 mb-2")

    attribs = kwargs
    children = args

    contents = div(
        title,
        value,
        *children,
        class_="value-box-area",
    )
    contents = bind_fill_role(contents, container=True, item=True)

    if showcase is not None:
        contents = showcase_layout(showcase, contents)

    theme_class_str = f" bg-{theme_color}" if theme_color else ""
    class_str = f" {class_}" if class_ is not None else ""

    return card(
        contents,
        class_=f"bslib-value-box border-0{theme_class_str}{class_str}",
        full_screen=full_screen,
        height=height,
        max_height=max_height,
        fill=fill,
        **attribs,
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
    width: float = 0.3,
    max_height: CssUnit = "100px",
    max_height_full_screen: CssUnit = 0.67,
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
    width: float = 0.3,
    max_height: CssUnit = "75px",
    max_height_full_screen: CssUnit = 0.67,
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
    width_css_unit = validate_width_unit(width)
    max_height_css_unit = validate_height_unit(max_height)
    max_height_full_screen_css_unit = validate_height_unit(max_height_full_screen)

    def _showcase_layout(showcase: TagChild | TagAttrs, contents: Tag) -> CardItem:
        css_args = {
            "--bslib-value-box-max-height": max_height_css_unit,
            "--bslib-value-box-max-height-full-screen": max_height_full_screen_css_unit,
        }
        showcase_container = div(
            showcase,
            {"class_": "value-box-showcase"},
            {"class_": "overflow-hidden"},
            {"class_": "showcase-top-right"} if top_right else None,
            style=css(**css_args),
        )
        showcase_container = bind_fill_role(
            showcase_container, container=True, item=True
        )

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
