from __future__ import annotations

from typing import Optional

from htmltools import TagChild, css, div

from ._card_item import CardItem, as_card_item
from ._css import CssUnit, validate_css_unit
from ._fill import bind_fill_role


# Card items
#
# Components designed to be provided as direct children of a [card()]. For a
# general overview of the [card()] API, see [this
# article](https://rstudio.github.io/bslib/articles/cards.html).
#
# @param ... Unnamed arguments can be any valid child of an [htmltools
#   tag][htmltools::tags]. Named arguments become HTML attributes on returned
#   UI element.
# @param min_height,max_height,max_height_full_screen Any valid [CSS length
#   unit][htmltools::validateCssUnit()].
# @param fillable Whether or not the card item should be a fillable (i.e.
#   flexbox) container.
# @param fill Whether to allow this element to grow/shrink to fit its `card()`
#   container.
# @param gap A [CSS length unit][htmltools::validateCssUnit()] defining the
#   `gap` (i.e., spacing) between elements provided to `...`. This argument is only applicable when `fillable = TRUE`
# @inheritParams card
#
# @return An [htmltools::div()] tag.
#
# @export
# @seealso [card()] for creating a card component.
# @seealso [navs_tab_card()] for cards with multiple tabs.
# @seealso [layout_column_wrap()] for laying out multiple cards (or multiple
#   columns inside a card).
#
# @describeIn card_body A general container for the "main content" of a [card()].
def card_body(
    *args: TagChild,
    fillable: bool = True,
    min_height: Optional[CssUnit] = None,
    max_height: Optional[CssUnit] = None,
    max_height_full_screen: Optional[CssUnit] = "__max_height__",
    height: Optional[CssUnit] = None,
    gap: Optional[CssUnit] = None,
    fill: bool = True,
    class_: Optional[str] = None,
    **kwargs: TagChild,
) -> CardItem:
    if max_height_full_screen == "__max_height__":
        max_height_full_screen = max_height
    if fillable:
        # TODO-future: Make sure shiny >= v1.7.4
        # TODO-future: Make sure htmlwidgets >= 1.6.0
        ...
    div_style_args = {
        "min-height": validate_css_unit(min_height),
        "--bslib-card-body-max-height": validate_css_unit(max_height),
        "--bslib-card-body-max-height-full-screen": validate_css_unit(
            max_height_full_screen
        ),
        "margin-top": "auto",
        "margin-bottom": "auto",
        # .card-body already adds `flex: 1 1 auto` so make sure to override it
        "flex": "1 1 auto" if fill else "0 0 auto",
        "gap": validate_css_unit(gap),
        "height": validate_css_unit(height),
    }
    tag = div(
        *args,
        {"class": "card-body"},
        {"style": css(**div_style_args)},
        **kwargs,
    )

    tag = bind_fill_role(tag, item=fill, container=fillable)

    # Make sure user has the opportunity to override the classes added by bindFillRole()
    if class_ is not None:
        tag.add_class(class_)

    return as_card_item(tag)
