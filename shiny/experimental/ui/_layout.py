from __future__ import annotations

# import pdb
from typing import Optional

from htmltools import TagAttrValue, TagChild, css, div

from shiny._typing_extensions import Literal

from ._css import CssUnit, validate_css_unit
from ._fill import bind_fill_role


# A grid-like, column-first, layout
#
# Wraps a 1d sequence of UI elements into a 2d grid. The number of columns (and
# rows) in the grid dependent on the column `width` as well as the size of the
# display. For more explanation and illustrative examples, see [here](https://rstudio.github.io/bslib/articles/cards.html#multiple-cards)
#
# @param ... Unnamed arguments should be UI elements (e.g., [card()])
#   Named arguments become attributes on the containing [htmltools::tag] element.
# @param width The desired width of each card, which can be any of the
#  following:
#   * A (unit-less) number between 0 and 1.
#     * This should be specified as `1/num`, where `num` represents the number
#       of desired columns.
#   * A [CSS length unit][htmltools::validateCssUnit()]
#     * Either the minimum (when `fixed_width=FALSE`) or fixed width
#       (`fixed_width=TRUE`).
#   * `NULL`
#     * Allows power users to set the `grid-template-columns` CSS property
#       manually, either via a `style` attribute or a CSS stylesheet.
# @param fixed_width Whether or not to interpret the `width` as a minimum
#   (`fixed_width=FALSE`) or fixed (`fixed_width=TRUE`) width when it is a CSS
#   length unit.
# @param heights_equal If `"all"` (the default), every card in every row of the
#   grid will have the same height. If `"row"`, then every card in _each_ row
#   of the grid will have the same height, but heights may vary between rows.
# @param fill Whether or not to allow the layout to grow/shrink to fit a
#   fillable container with an opinionated height (e.g., `page_fillable()`).
# @param fillable Whether or not each element is wrapped in a fillable container.
# @param height_mobile Any valid CSS unit to use for the height when on mobile
#   devices (or narrow windows).
# @inheritParams card
# @inheritParams card_body
#
# @export
# @examples
#
# x <- card("A simple card")
# # Always has 2 columns (on non-mobile)
# layout_column_wrap(1/2, x, x, x)
# # Has three columns when viewport is wider than 750px
# layout_column_wrap("250px", x, x, x)
#
def layout_column_wrap(
    width: Optional[CssUnit],
    *args: TagChild,  # `TagAttrs` are not allowed here
    fixed_width: bool = False,
    heights_equal: Literal["all", "row"] = "all",
    fill: bool = True,
    fillable: bool = True,
    height: Optional[CssUnit] = None,
    height_mobile: Optional[CssUnit] = None,
    gap: Optional[CssUnit] = None,
    class_: Optional[str] = None,  # Applies after `bind_fill_role()`
    **kwargs: TagAttrValue,
):
    attribs = kwargs
    children = args

    colspec: str | None = None
    if width is not None:
        width_num = float(width)
        if width_num > 0.0 and width_num <= 1.0:
            num_cols = 1.0 / width_num
            if not num_cols.is_integer():
                raise ValueError(
                    "Could not interpret width argument; see ?layout_column_wrap"
                )
            colspec = " ".join(["1fr" for _ in range(int(num_cols))])
        else:
            width_css_unit = validate_css_unit(width)
            if fixed_width:
                colspec = f"repeat(auto-fit, minmax({width_css_unit}, 1fr))"
            else:
                colspec = f"repeat(auto-fit, minmax(0, {width_css_unit}))"

    # Use a new dict so that we don't mutate the original `children` dict
    upgraded_children: list[TagChild] = []
    for child_value in children:
        upgraded_children.append(
            bind_fill_role(
                div(bind_fill_role(div(child_value), container=fillable, item=True)),
                container=True,
            )
        )
    tag_style_css = {
        "grid-template-columns": colspec,
        "grid-auto-rows": "1fr" if (heights_equal == "all") else None,
        # Always provide the `height:auto` default so that the CSS variable
        # doesn't get inherited in a scenario like
        # layout_column_wrap(height=200, layout, layout_column_wrap(...))
        "--bslib-column-wrap-height": validate_css_unit(
            "auto" if height is None else height
        ),
        "--bslib-column-wrap-height-mobile": validate_css_unit(
            "auto" if height_mobile is None else height_mobile
        ),
        "gap": validate_css_unit(gap),
    }

    tag = div(
        {
            "class": "bslib-column-wrap",
            "style": css(**tag_style_css),
        },
        *upgraded_children,
        **attribs,
    )
    # pdb.set_trace()

    tag = bind_fill_role(tag, item=fill)
    # Give the user an opportunity to override the classes added by bind_fill_role()
    if class_ is not None:
        tag.add_class(class_)

    return tag
