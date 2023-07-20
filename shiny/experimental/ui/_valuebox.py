from __future__ import annotations

from typing import Callable, Optional

from htmltools import Tag, TagAttrs, TagAttrValue, TagChild, css, div, tags

from ._card import CardItem, card, card_body
from ._css_unit import CssUnit, as_css_unit, as_width_unit
from ._fill import as_fill_carrier
from ._htmldeps import value_box_dependency
from ._layout import layout_column_wrap
from ._utils import consolidate_attrs, is_01_scalar

__all__ = (
    "value_box",
    "showcase_left_center",
    "showcase_top_right",
)


# TODO-maindocs; @add_example()
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
    """
    Value box

    An opinionated (:func:`~shiny.experimental.ui.card`-powered) box, designed for
    displaying a `value` and `title`. Optionally, a `showcase` can provide for context
    for what the `value` represents (for example, it could hold an icon, or even a
    :func:`~shiny.ui.output_plot`).

    Parameters
    ----------
    title,value
        A string, number, or :class:`~htmltools.Tag` child to display as
        the title or value of the value box. The `title` appears above the `value`.
    *args
        Unnamed arguments may be any :class:`~htmltools.Tag` children to display below
        `value`. Named arguments are passed to :func:`~shiny.experimental.ui.card` as
        element attributes.
    showcase
        A :class:`~htmltools.Tag` child to showcase (e.g., an icon, a
        :func:`~shiny.ui.output_plot`, etc).
    showcase_layout
        Either :func:`~shiny.experimental.ui.showcase_left_center` or
        :func:`~shiny.experimental.ui.showcase_top_right`.
    theme_color
        A theme color to use for the background color. Should match a name in the
        Bootstrap Sass variable `$theme-colors` (e.g., `"secondary"`, `"success"`,
        `"danger"`, etc).
    height,max_height
        Any valid CSS unit (e.g., `height="200px"`). Doesn't apply when a card is made
        `full_screen` (in this case, consider setting a `height` in
        :func:`~shiny.experimental.ui.card_body`).
    fill
        Whether to allow the value box to grow/shrink to fit a fillable container with
        an opinionated height (e.g., :func:`~shiny.experimental.ui.page_fillable`).
    class_
        Utility classes for customizing the appearance of the summary card. Use `bg-*`
        and `text-*` classes (e.g, `"bg-danger"` and `"text-light"`) to customize the
        background/foreground colors.
    **kwargs
        Additional attributes to pass to :func:`~shiny.experimental.ui.card`.

    Returns
    -------
    :
        A :func:`~shiny.experimental.ui.card`

    See Also
    --------
    * :func:`~shiny.experimental.ui.card`
    """
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
        title = tags.p(str(title), class_="h6 mb-1")
    if isinstance(title, (str, int, float)):
        value = tags.p(str(value), class_="h2 mb-2")

    contents = div(
        title,
        value,
        *children,
        class_="value-box-area",
    )
    contents = as_fill_carrier(contents)

    if showcase is not None:
        contents = showcase_layout(showcase, contents)

    return card(
        contents,
        attrs,
        value_box_dependency(),
        full_screen=full_screen,
        height=height,
        max_height=max_height,
        fill=fill,
    )


# TODO-maindocs; @add_example()
def showcase_left_center(
    width: CssUnit = "30%",
    max_height: CssUnit = "100px",
    max_height_full_screen: CssUnit = "67%",
) -> Callable[[TagChild | TagAttrs, Tag], CardItem]:
    """
    Left center showcase for a value box

    Gives the showcase a width and centers it vertically.

    Parameters
    ----------
    width
        A proportion (i.e., a number between 0 and 1) of available width to allocate to
        the showcase. Or, A vector of length 2 valid CSS unit defining the width of each
        column (for `showcase_left_center()` the 1st unit defines the showcase width and
        for `showcase_top_right` the 2nd unit defines the showcase width). Note that any
        units supported by the CSS grid `grid-template-columns` property may be used
        (e.g., `fr` units).
    max_height,max_height_full_screen
        A proportion (i.e., a number between 0 and 1) or any valid CSS unit defining the
        showcase max_height.

    Returns
    -------
    :
        A function that takes a showcase and contents and returns a :func:`~shiny.experimental.ui.card_body`
    """
    return _showcase_layout(
        width=width,
        max_height=max_height,
        max_height_full_screen=max_height_full_screen,
        top_right=False,
    )


# TODO-maindocs; @add_example()
def showcase_top_right(
    width: CssUnit = "30%",
    max_height: CssUnit = "75px",
    max_height_full_screen: CssUnit = "67%",
) -> Callable[[TagChild | TagAttrs, Tag], CardItem]:
    """
    Top right showcase for a value box

    Gives the showcase a width and in the top right corner.

    Parameters
    ----------
    width
        A proportion (i.e., a number between 0 and 1) of available width to allocate to
        the showcase. Or, A vector of length 2 valid CSS unit defining the width of each
        column (for `showcase_left_center()` the 1st unit defines the showcase width and
        for `showcase_top_right` the 2nd unit defines the showcase width). Note that any
        units supported by the CSS grid `grid-template-columns` property may be used
        (e.g., `fr` units).
    max_height,max_height_full_screen
        A proportion (i.e., a number between 0 and 1) or any valid CSS unit defining the
        showcase max_height.

    Returns
    -------
    :
        A function that takes a showcase and contents and returns a :func:`~shiny.experimental.ui.card_body`
    """

    if is_01_scalar(width):
        width = 1 - width
    return _showcase_layout(
        width=width,
        max_height=max_height,
        max_height_full_screen=max_height_full_screen,
        top_right=True,
    )


def _showcase_layout(
    width: CssUnit,
    max_height: CssUnit,
    max_height_full_screen: CssUnit,
    top_right: bool,
) -> Callable[[TagChild | TagAttrs, Tag], CardItem]:
    # Do not "magically" turn `0.3` into `"30%"` as it is not clear to the user when it happens
    width_css_unit = as_width_unit(width)
    max_height_css_unit = as_css_unit(max_height)
    max_height_full_screen_css_unit = as_css_unit(max_height_full_screen)

    def _layout(showcase: TagChild | TagAttrs, contents: Tag) -> CardItem:
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

        width_fs = " ".join(width_fs)

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

    return _layout
