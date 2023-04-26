from __future__ import annotations

from typing import NamedTuple, Optional

from htmltools import Tag, TagAttrs, TagAttrValue, TagChild, css, div, tags

from shiny.types import MISSING, MISSING_TYPE

from ._card_full_screen import full_screen_toggle
from ._card_item import CardItem, WrapperCallable, card_body, wrap_children_in_card
from ._css import CssUnit, validate_css_unit
from ._fill import bind_fill_role

# class Page:
#     x: Tag
#     def __init__(
#         self,
#         x: Tag,
#     ):
#         self.x = x


# class Fragment:
#     x: Tag
#     page: Page
#     def __init__(
#         self,
#         x: Tag,
#         page: Page,
#     ):
#         self.x = x
#         self.page = page


# def as_fragment(x: Tag, page: Page) -> Fragment:
#     return Fragment(x=x, page=page)


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
    class_: Optional[str] = None,  # Applies after `bind_fill_role()`
    wrapper: WrapperCallable | None | MISSING_TYPE = MISSING,
    **kwargs: TagAttrValue,
) -> Tag:
    if isinstance(wrapper, MISSING_TYPE):
        wrapper = card_body

    children, attrs = separate_args_into_children_and_attrs(*args)
    children = wrap_children_in_card(*children, wrapper=wrapper)

    tag = div(
        *children,
        *attrs,
        full_screen_toggle() if full_screen else None,
        card_js_init(),
        {
            "class": "card bslib-card",
            "style": css(
                height=validate_css_unit(height),
                max_height=validate_css_unit(max_height),
            ),
        },
        **kwargs,
    )

    tag = bind_fill_role(tag, container=True, item=fill)
    # Give the user an opportunity to override the classes added by bind_fill_role()
    if class_ is not None:
        tag.add_class(class_)
    return tag


class ChildrenAndAttrs(NamedTuple):
    children: list[TagChild | CardItem]
    attrs: list[TagAttrs]


def separate_args_into_children_and_attrs(
    *args: TagChild | TagAttrs | CardItem,
) -> ChildrenAndAttrs:
    children: list[TagChild | CardItem] = []
    attrs: list[TagAttrs] = []

    for arg in args:
        if isinstance(arg, dict):
            attrs.append(arg)
        else:
            children.append(arg)

    return ChildrenAndAttrs(children, attrs)


def card_js_init() -> Tag:
    return tags.script(
        {"data-bslib-card-needs-init": True},
        """\
      var thisScript = document.querySelector('script[data-bslib-card-needs-init]');
      if (!thisScript) throw new Error('Failed to register card() resize observer');

      thisScript.removeAttribute('data-bslib-card-needs-init');

      var card = $(thisScript).parents('.card').last();
      if (!card) throw new Error('Failed to register card() resize observer');

      // Let Shiny know to trigger resize when the card size changes
      // TODO: shiny could/should do this itself (rstudio/shiny#3682)
      var resizeEvent = window.document.createEvent('UIEvents');
      resizeEvent.initUIEvent('resize', true, false, window, 0);
      var ro = new ResizeObserver(() => { window.dispatchEvent(resizeEvent); });
      ro.observe(card[0]);

      // Enable tooltips (for the expand icon)
      var tooltipList = card[0].querySelectorAll('[data-bs-toggle=\"tooltip\"]');
      tooltipList.forEach(function(x) { new bootstrap.Tooltip(x); });

      // In some complex fill-based layouts with multiple outputs (e.g., plotly),
      // shiny initializes with the correct sizing, but in-between the 1st and last
      // renderValue(), the size of the output containers can change, meaning every
      // output but the 1st gets initialized with the wrong size during their
      // renderValue(); and then after the render phase, shiny won't know trigger a
      // resize since all the widgets will return to their original size
      // (and thus, Shiny thinks there isn't any resizing to do).
      // We workaround that situation by manually triggering a resize on the binding
      // when the output container changes (this way, if the size is different during
      // the render phase, Shiny will know about it)
      $(document).on('shiny:value', function(x) {
        var el = x.binding.el;
        if (card[0].contains(el) && !$(el).data('bslib-output-observer')) {
          var roo = new ResizeObserver(x.binding.onResize);
          roo.observe(el);
          $(el).data('bslib-output-observer', true);
        }
      });
    """,
    )
