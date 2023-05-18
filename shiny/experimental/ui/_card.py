from __future__ import annotations

from typing import Optional

from htmltools import Tag, TagAttrs, TagAttrValue, TagChild, css, div, tags

from ...types import MISSING, MISSING_TYPE
from ._card_full_screen import full_screen_toggle
from ._card_item import CardItem, WrapperCallable, card_body, wrap_children_in_card
from ._css import CssUnit, validate_css_unit
from ._fill import bind_fill_role
from ._htmldeps import card_dependency
from ._utils import consolidate_attrs


# A Bootstrap card component
#
# A general purpose container for grouping related UI elements together with a
# border and optional padding. To learn more about [card()]s, see [this
# article](https://rstudio.github.io/bslib/articles/cards.html).
#
# @param ... Unnamed arguments can be any valid child of an [htmltools
#   tag][htmltools::tags] (which includes card items such as [card_body()].
#   Named arguments become HTML attributes on returned UI element.
# @param full_screen If `TRUE`, an icon will appear when hovering over the card
#   body. Clicking the icon expands the card to fit viewport size.
# @param height Any valid [CSS unit][htmltools::validateCssUnit] (e.g.,
#   `height="200px"`). Doesn't apply when a card is made `full_screen`
#   (in this case, consider setting a `height` in [card_body()]).
# @param max_height Any valid [CSS unit][htmltools::validateCssUnit] (e.g.,
#   `max_height="200px"`). Doesn't apply when a card is made `full_screen`
#   (in this case, consider setting a `max_height` in [card_body()]).
# @param fill Whether or not to allow the card to grow/shrink to fit a
#   fillable container with an opinionated height (e.g., `page_fillable()`).
# @param class Additional CSS classes for the returned UI element.
# @param wrapper A function (which returns a UI element) to call on unnamed
#   arguments in `...` which are not already card item(s) (like
#   [card_header()], [card_body()], etc.). Note that non-card items are grouped
#   together into one `wrapper` call (e.g. given `card("a", "b",
#   card_body("c"), "d")`, `wrapper` would be called twice, once with `"a"` and
#   `"b"` and once with `"d"`).
#
# @return A [htmltools::div()] tag.
#
# @export
# @seealso [card_body()] for putting stuff inside the card.
# @seealso [navs_tab_card()] for cards with multiple tabs.
# @seealso [layout_column_wrap()] for laying out multiple cards (or multiple
#   columns inside a card).
# @examples
#
# library(htmltools)
#
# if (interactive()) {
#   card(
#     full_screen = TRUE,
#     card_header(
#       "This is the header"
#     ),
#     card_body(
#       p("This is the body."),
#       p("This is still the body.")
#     ),
#     card_footer(
#       "This is the footer"
#     )
#   )
# }
#
def card(
    *args: TagChild | TagAttrs | CardItem,
    full_screen: bool = False,
    height: Optional[CssUnit] = None,
    max_height: Optional[CssUnit] = None,
    fill: bool = True,
    class_: Optional[str] = None,
    wrapper: WrapperCallable | None | MISSING_TYPE = MISSING,
    **kwargs: TagAttrValue,
) -> Tag:
    if isinstance(wrapper, MISSING_TYPE):
        wrapper = card_body

    attrs, children = consolidate_attrs(*args, class_=class_, **kwargs)
    children = wrap_children_in_card(*children, wrapper=wrapper)

    tag = div(
        {
            "class": "card bslib-card",
            "style": css(
                height=validate_css_unit(height),
                max_height=validate_css_unit(max_height),
            ),
            "data-bslib-card-init": True,
        },
        *children,
        attrs,
        full_screen_toggle() if full_screen else None,
        card_dependency(),
        card_js_init(),
    )

    return bind_fill_role(tag, container=True, item=fill)


def card_js_init() -> Tag:
    return tags.script(
        {"data-bslib-card-init": True},
        "window.bslib.Card.initializeAllCards();",
    )
