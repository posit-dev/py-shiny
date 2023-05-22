from __future__ import annotations

import base64
import io
import mimetypes
from pathlib import Path, PurePath
from typing import Optional

from htmltools import (
    HTML,
    Tag,
    TagAttrs,
    TagAttrValue,
    TagChild,
    TagList,
    css,
    div,
    tags,
)

from ..._typing_extensions import Literal, Protocol
from ...types import MISSING, MISSING_TYPE
from ._css_unit import CssUnit, validate_css_unit
from ._fill import as_fill_carrier, bind_fill_role
from ._htmldeps import card_dependency
from ._utils import consolidate_attrs

__all__ = (
    "CardItem",
    "card",
    "card_body",
    "card_title",
    "card_header",
    "card_footer",
    "card_image",
)


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
    children = _wrap_children_in_card(*children, wrapper=wrapper)

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
        _full_screen_toggle() if full_screen else None,
        card_dependency(),
        _card_js_init(),
    )

    return bind_fill_role(tag, container=True, item=fill)


def _card_js_init() -> Tag:
    return tags.script(
        {"data-bslib-card-init": True},
        "window.bslib.Card.initializeAllCards();",
    )


def _full_screen_toggle() -> Tag:
    return tags.span(
        {
            "class": "bslib-full-screen-enter badge rounded-pill bg-dark",
            "data-bs-toggle": "tooltip",
            "data-bs-placement": "bottom",
            "title": "Expand",
        },
        _full_screen_toggle_icon(),
    )


# via bsicons::bs_icon("arrows-fullscreen")
def _full_screen_toggle_icon() -> HTML:
    return HTML(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" class="bi bi-arrows-fullscreen " style="height:1em;width:1em;fill:currentColor;" aria-hidden="true" role="img" ><path fill-rule="evenodd" d="M5.828 10.172a.5.5 0 0 0-.707 0l-4.096 4.096V11.5a.5.5 0 0 0-1 0v3.975a.5.5 0 0 0 .5.5H4.5a.5.5 0 0 0 0-1H1.732l4.096-4.096a.5.5 0 0 0 0-.707zm4.344 0a.5.5 0 0 1 .707 0l4.096 4.096V11.5a.5.5 0 1 1 1 0v3.975a.5.5 0 0 1-.5.5H11.5a.5.5 0 0 1 0-1h2.768l-4.096-4.096a.5.5 0 0 1 0-.707zm0-4.344a.5.5 0 0 0 .707 0l4.096-4.096V4.5a.5.5 0 1 0 1 0V.525a.5.5 0 0 0-.5-.5H11.5a.5.5 0 0 0 0 1h2.768l-4.096 4.096a.5.5 0 0 0 0 .707zm-4.344 0a.5.5 0 0 1-.707 0L1.025 1.732V4.5a.5.5 0 0 1-1 0V.525a.5.5 0 0 1 .5-.5H4.5a.5.5 0 0 1 0 1H1.732l4.096 4.096a.5.5 0 0 1 0 .707z"></path></svg>'
    )


############################################################################


class CardItem:
    def __init__(
        self,
        x: TagChild,
    ):
        self._x = x

    def resolve(self) -> TagChild:
        return self._x

    def tagify(self) -> TagList:
        return TagList(self._x).tagify()


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
    *args: TagChild | TagAttrs,
    fillable: bool = True,
    min_height: Optional[CssUnit] = None,
    max_height: Optional[CssUnit] = None,
    max_height_full_screen: Optional[CssUnit] | MISSING_TYPE = MISSING,
    height: Optional[CssUnit] = None,
    gap: Optional[CssUnit] = None,
    fill: bool = True,
    class_: Optional[str] = None,
    **kwargs: TagAttrValue,
) -> CardItem:
    if isinstance(max_height_full_screen, MISSING_TYPE):
        max_height_full_screen = max_height

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
    tag = tags.div(
        *args,
        {
            "class": "card-body",
            "style": css(**div_style_args),
        },
        class_=class_,
        **kwargs,
    )

    return CardItem(
        bind_fill_role(tag, item=fill, container=fillable),
    )


# https://mypy.readthedocs.io/en/stable/protocols.html#callback-protocols
class WrapperCallable(Protocol):
    def __call__(self, *args: TagChild) -> CardItem:
        ...


def _as_card_items(
    *children: TagChild | CardItem | None,  # `TagAttrs` are not allowed here
    wrapper: WrapperCallable | None,
) -> list[CardItem]:
    # We don't want `None`s creating empty card bodies
    children_vals = [child for child in children if child is not None]

    attrs, children_vals = consolidate_attrs(*children_vals)
    if len(attrs) > 0:
        raise ValueError("`TagAttrs` are not allowed in `_as_card_items(*children=)`.")

    if not callable(wrapper):
        ret: list[CardItem] = []
        for child in children_vals:
            if isinstance(child, CardItem):
                ret.append(child)
            else:
                ret.append(CardItem(child))
        return ret

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
        if isinstance(child, CardItem):
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


def _wrap_children_in_card(
    *children: TagChild | CardItem | None,  # `TagAttrs` are not allowed here
    wrapper: WrapperCallable | None,
) -> list[TagChild]:
    card_items = _as_card_items(*children, wrapper=wrapper)
    tag_children = [card_item.resolve() for card_item in card_items]
    return tag_children


# @describeIn card_body Similar to `card_header()` but without the border and background color.
# @param container a function to generate an HTML element.
# @export


# https://mypy.readthedocs.io/en/stable/protocols.html#callback-protocols
class TagCallable(Protocol):  # Should this be exported from htmltools?
    def __call__(
        self,
        *args: TagChild | TagAttrs,
        _add_ws: bool = True,
        **kwargs: TagAttrValue,
    ) -> Tag:
        ...


def card_title(
    *args: TagChild | TagAttrs,
    container: TagCallable = tags.h5,
    **kwargs: TagAttrValue,
) -> Tag:
    return container(*args, **kwargs)


# @describeIn card_body A header (with border and background color) for the `card()`. Typically appears before a `card_body()`.
# @param container a function that generates an [htmltools tag][htmltools::tags].
# @export
def card_header(
    *args: TagChild | TagAttrs,
    container: TagCallable = tags.div,
    **kwargs: TagAttrValue,
) -> CardItem:
    return CardItem(
        container({"class": "card-header"}, *args, **kwargs),
    )


# @describeIn card_body A header (with border and background color) for the `card()`. Typically appears after a `card_body()`.
# @export
def card_footer(
    *args: TagChild | TagAttrs,
    **kwargs: TagAttrValue,
) -> CardItem:
    return CardItem(
        tags.div({"class": "card-footer"}, *args, **kwargs),
    )


# @describeIn card_body Include static (i.e., pre-generated) images.
# @param file a file path pointing an image. The image will be base64 encoded
# and provided to the `src` attribute of the `<img>`. Alternatively, you may
# set this value to `NULL` and provide the `src` yourself.
# @param href an optional URL to link to.
# @param border_radius where to apply `border-radius` on the image.
# @param mime_type the mime type of the `file`.
# @param container a function to generate an HTML element to contain the image.
# @param width Any valid [CSS unit][htmltools::validateCssUnit] (e.g., `width="100%"`).
# @export


class ImgContainer(Protocol):
    def __call__(self, *args: Tag) -> CardItem:
        ...


def card_image(
    file: str | Path | PurePath | io.BytesIO | None,
    *args: TagChild | TagAttrs,
    href: Optional[str] = None,
    border_radius: Literal["top", "bottom", "all", "none"] = "top",
    mime_type: Optional[str] = None,
    class_: Optional[str] = None,
    height: Optional[CssUnit] = None,
    fill: bool = True,
    width: Optional[CssUnit] = None,
    # Required so that multiple `card_images()` are not put in the same `card()`
    container: ImgContainer = card_body,
    **kwargs: TagAttrValue,
) -> CardItem:
    src = None
    if file is not None:
        if isinstance(file, io.BytesIO):
            b64_str = base64.b64encode(file.read()).decode("utf-8")
            if mime_type is None:
                raise ValueError(
                    "`mime_type` must be provided when passing an in-memory buffer"
                )
            src = f"data:{mime_type};base64,{b64_str}"

        elif isinstance(file, (str, Path, PurePath)):
            with open(file, "rb") as img_file:
                b64_str = base64.b64encode(img_file.read()).decode("utf-8")
                if mime_type is None:
                    mime_type = mimetypes.guess_type(file)[0]
                src = f"data:{mime_type};base64,{b64_str}"

    card_class_map = {
        "all": "card-img",
        "top": "card-img-top",
        "bottom": "card-img-bottom",
    }

    image = tags.img(
        {
            "src": src,
            "class": "img-fluid",
            "style": css(
                height=validate_css_unit(height),
                width=validate_css_unit(width),
            ),
        },
        {"class": card_class_map.get(border_radius, None)},
        *args,
        class_=class_,
        **kwargs,
    )

    image = bind_fill_role(image, item=fill)

    if href is not None:
        image = as_fill_carrier(tags.a(image, href=href))

    if container:
        return container(image)
    else:
        return CardItem(image)
