from __future__ import annotations

import pdb
from typing import Optional, Protocol

from htmltools import HTML, Tag, TagChild, css, div, tags

from shiny._typing_extensions import TypeGuard

from ._css import CssUnit, validate_css_unit
from ._fill import bind_fill_role
from ._htmldeps import card_full_screen_dep


class CardItem:
    def __init__(
        self,
        item: Tag,
    ):
        self.item = item

    def tagify(self) -> Tag:
        return self.item.tagify()


# @describeIn card_body Mark an object as a card item. This will prevent the
#   [card()] from putting the object inside a `wrapper` (i.e., a
#   `card_body()`).
# @param x an object to test (or coerce to) a card item.
# @export
def as_card_item(x: Tag) -> CardItem:
    return CardItem(item=x)


def is_card_item(x: object) -> TypeGuard[CardItem]:
    return isinstance(x, CardItem)


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
    *args: TagChild,
    full_screen: bool = False,
    height: Optional[CssUnit] = None,
    max_height: Optional[CssUnit] = None,
    fill: bool = True,
    class_: Optional[str] = None,
    wrapper: WrapperCallable | None = None,
    **kwargs: TagChild,
) -> Tag:
    if wrapper is None:
        wrapper = card_body

    children = as_card_items(*args, wrapper=wrapper)

    # pdb.set_trace()

    tag = div(
        {"class": "card bslib-card"},
        {
            "style": css(
                height=validate_css_unit(height),
                max_height=validate_css_unit(max_height),
            )
        },
        **kwargs,  # !!!attribs
    )
    tag.append(*children)  # !!!children
    if full_screen:
        tag.append(full_screen_toggle())
    tag.append(card_js_init())

    tag = bind_fill_role(tag, container=True, item=fill)
    if class_ is not None:
        tag.add_class(class_)
    return tag


# https://mypy.readthedocs.io/en/stable/protocols.html#callback-protocols
class WrapperCallable(Protocol):
    def __call__(self, *args: TagChild) -> CardItem:
        ...


def as_card_items(
    *children: TagChild | None, wrapper: WrapperCallable | None
) -> list[CardItem] | list[TagChild]:
    # We don't want NULLs creating empty card bodies
    children_vals = [child for child in children if child is not None]

    if not callable(wrapper):
        return children_vals

    # Any children that are `is.card_item` should be included verbatim. Any
    # children that are not, should be wrapped in card_body(). Consecutive children
    # that are not card_item, should be wrapped in a single card_body().
    state = "asis"  # "wrap" | "asis"
    new_children: list[CardItem] = []
    children_to_wrap: list[TagChild] = []

    def wrap_children():
        nonlocal children_to_wrap
        wrapped_children = wrapper(*children_to_wrap)
        new_children.append(wrapped_children)
        children_to_wrap = []

    for child in children_vals:
        if is_card_item(child):
            if state == "wrap":
                wrap_children()
            state = "asis"
            new_children.append(child)
        else:
            # Not a card, collect it for wrapping
            state = "wrap"
            children_to_wrap.append(child)
    if state == "wrap":
        wrap_children()

    return new_children


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


def card_js_init() -> Tag:
    return tags.script(
        {"data-bslib-card-needs-init": ""},
        HTML(
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
    """
        ),
    )


def full_screen_toggle() -> Tag:
    return tags.span(
        {"class_": "bslib-full-screen-enter"},
        {"class_": "badge rounded-pill bg-dark"},
        {"data-bs-toggle": "tooltip"},
        {"data-bs-placement": "bottom"},
        {"title": "Expand"},
        full_screen_toggle_icon(),
        card_full_screen_dep(),
    )


# via bsicons::bs_icon("arrows-fullscreen")
def full_screen_toggle_icon() -> HTML:
    return HTML(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" class="bi bi-arrows-fullscreen " style="height:1em;width:1em;fill:currentColor;" aria-hidden="true" role="img" ><path fill-rule="evenodd" d="M5.828 10.172a.5.5 0 0 0-.707 0l-4.096 4.096V11.5a.5.5 0 0 0-1 0v3.975a.5.5 0 0 0 .5.5H4.5a.5.5 0 0 0 0-1H1.732l4.096-4.096a.5.5 0 0 0 0-.707zm4.344 0a.5.5 0 0 1 .707 0l4.096 4.096V11.5a.5.5 0 1 1 1 0v3.975a.5.5 0 0 1-.5.5H11.5a.5.5 0 0 1 0-1h2.768l-4.096-4.096a.5.5 0 0 1 0-.707zm0-4.344a.5.5 0 0 0 .707 0l4.096-4.096V4.5a.5.5 0 1 0 1 0V.525a.5.5 0 0 0-.5-.5H11.5a.5.5 0 0 0 0 1h2.768l-4.096 4.096a.5.5 0 0 0 0 .707zm-4.344 0a.5.5 0 0 1-.707 0L1.025 1.732V4.5a.5.5 0 0 1-1 0V.525a.5.5 0 0 1 .5-.5H4.5a.5.5 0 0 1 0 1H1.732l4.096 4.096a.5.5 0 0 1 0 .707z"></path></svg>'
    )
