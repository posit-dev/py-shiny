from __future__ import annotations

import base64
import mimetypes
from typing import Optional, Protocol

from htmltools import Tag, TagAttrs, TagAttrValue, TagChild, Tagifiable, css, tags

from shiny._typing_extensions import Literal, TypeGuard

from ._css import CssUnit, validate_css_unit
from ._fill import bind_fill_role


class CardItem:
    def __init__(
        self,
        item: Tagifiable,
    ):
        self.item = item

    def tagify(self) -> Tag:
        return self.item.tagify()


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
    tag = tags.div(
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


# @describeIn card_body Mark an object as a card item. This will prevent the
#   [card()] from putting the object inside a `wrapper` (i.e., a
#   `card_body()`).
# @param x an object to test (or coerce to) a card item.
# @export
def as_card_item(x: Tag) -> CardItem:
    return CardItem(item=x)


def is_card_item(x: object) -> TypeGuard[CardItem]:
    return isinstance(x, CardItem)


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


# @describeIn card_body Similar to `card_header()` but without the border and background color.
# @param container a function to generate an HTML element.
# @export


# https://mypy.readthedocs.io/en/stable/protocols.html#callback-protocols
class TagCallable(Protocol):  # Should this be exported from htmltools?
    def __call__(
        self, *args: TagChild | TagAttrs, _add_ws: bool = True, **kwargs: TagAttrValue
    ) -> Tag:
        ...


def card_title(
    *args: TagChild | TagAttrs, container: TagCallable = tags.h5, **kwargs: TagAttrValue
) -> Tag:
    return container(*args, **kwargs)


# @describeIn card_body A header (with border and background color) for the `card()`. Typically appears before a `card_body()`.
# @param container a function that generates an [htmltools tag][htmltools::tags].
# @export
def card_header(
    *args: TagChild | TagAttrs,
    class_: Optional[str] = None,
    container: TagCallable = tags.div,
    **kwargs: TagAttrValue,
) -> CardItem:
    return as_card_item(
        container({"class": "card-header"}, {"class": class_}, *args, **kwargs)
    )


# @describeIn card_body A header (with border and background color) for the `card()`. Typically appears after a `card_body()`.
# @export
def card_footer(
    *args: TagChild | TagAttrs, class_: Optional[str] = None, **kwargs: TagAttrValue
) -> CardItem:
    return as_card_item(
        tags.div({"class": "card-footer"}, {"class": class_}, *args, **kwargs)
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
    def __call__(self, *args: Tag) -> Tagifiable:
        ...


def card_image(
    file: Optional[str],
    *args: TagChild | TagAttrs,
    href: Optional[str] = None,
    border_radius: Literal["top", "bottom", "all", "none"] = "top",
    mime_type: Optional[str] = None,
    class_: Optional[str] = None,
    height: Optional[CssUnit] = None,
    fill: bool = True,
    width: Optional[CssUnit] = None,
    container: ImgContainer = card_body,
    **kwargs: TagAttrValue,
) -> Tagifiable:
    src = None
    if file is not None:
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
        {"src": src},
        {"class": "img-fluid"},
        {"class": card_class_map.get(border_radius, None)},
        {
            "style": css(
                height=validate_css_unit(height),
                width=validate_css_unit(width),
            )
        },
        *args,
        **kwargs,
    )

    image = bind_fill_role(image, item=fill)
    if class_ is not None:
        image.add_class(class_)

    if href is not None:
        image = bind_fill_role(tags.a(image, href=href), container=True, item=True)

    if callable(container):
        image = container(image)

    return image
