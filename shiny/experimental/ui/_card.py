from __future__ import annotations

import base64
import io
import mimetypes
from pathlib import Path, PurePath
from typing import Literal, Optional, Protocol

from htmltools import (
    Tag,
    TagAttrs,
    TagAttrValue,
    TagChild,
    TagFunction,
    Tagifiable,
    css,
    tags,
)

from ..._docstring import add_example
from ...types import MISSING, MISSING_TYPE
from ...ui._card import CardItem, WrapperCallable, _card_impl, card_body
from ...ui.css import CssUnit, as_css_unit
from ...ui.fill import as_fill_item, as_fillable_container

__all__ = (
    # Worried about `wrapper`
    "card",
    # Do not want to expose card_body yet
    "card_body",
    # Questioning:
    "card_title",
    "card_image",
)


def card(
    *args: TagChild | TagAttrs | CardItem,
    full_screen: bool = False,
    height: Optional[CssUnit] = None,
    max_height: Optional[CssUnit] = None,
    min_height: Optional[CssUnit] = None,
    fill: bool = True,
    class_: Optional[str] = None,
    wrapper: WrapperCallable | None | MISSING_TYPE = MISSING,
    **kwargs: TagAttrValue,
) -> Tag:
    """
    A Bootstrap card component

    A card is a general purpose container that groups related UI elements together with a border
    and optional padding. To learn more about `card()`s, see [the bslib card
    article](https://rstudio.github.io/bslib/articles/cards.html).

    Parameters
    ----------
    *args
        Unnamed arguments can be any valid child of an :class:`~htmltools.Tag` (This
        includes card items such as :func:`~shiny.experimental.ui.card_body`).
    full_screen
        If `True`, an icon will appear when the user's pointer hovers over the card body. Clicking the
        icon expands the card to fit viewport size.
    height, max_height, min_height
        Any valid CSS unit (e.g., `height="200px"`). These will not apply when a card is made
        `full_screen`. In this case, consider setting a `height` in
        :func:`~shiny.experimental.ui.card_body`.
    fill
        Whether or not to allow the card to grow/shrink to fit a fillable container with
        an opinionated height (e.g., :func:`~shiny.ui.page_fillable`).
    class_
        Additional CSS classes for the returned Tag.
    wrapper
        A function that returns a UI element to call on any unnamed arguments in `*args`
        that are not already card item(s) (like
        :func:`~shiny.ui.card_header`,
        :func:`~shiny.experimental.ui.card_body`, etc.). Note that non-card items are
        grouped together into one `wrapper` call (e.g. given `card("a", "b",
        card_body("c"), "d")`, `wrapper` would be called twice, once with `"a"` and
        `"b"` and once with `"d"`).
    **kwargs
        HTML attributes on the returned Tag.

    Returns
    -------
    :
        A :func:`~shiny.ui.tags.div` tag.

    See Also
    --------
    * :func:`~shiny.ui.layout_column_wrap` for laying out multiple cards
      or multiple columns inside a card.
    * :func:`~shiny.ui.card_header` for creating a header within a card.
    * :func:`~shiny.experimental.ui.card_title` for creating a title within a card body.
    * :func:`~shiny.experimental.ui.card_body` for putting content inside a card.
    * :func:`~shiny.ui.card_footer` for creating a footer within a card.
    * :func:`~shiny.experimental.ui.card_image` for adding an image to a card.
    """
    return _card_impl(
        *args,
        full_screen=full_screen,
        height=height,
        max_height=max_height,
        min_height=min_height,
        fill=fill,
        class_=class_,
        wrapper=wrapper,
        **kwargs,
    )


############################################################################


@add_example()
def card_title(
    *args: TagChild | TagAttrs,
    container: TagFunction = tags.h5,
    **kwargs: TagAttrValue,
) -> Tagifiable:
    """
    A card title container

    :func:`~shiny.experimental.ui.card_title` creates a general container for the "title" of
    a :func:`~shiny.ui.card`. This component is designed
    to be provided as a direct child to :func:`~shiny.ui.card`.

    Parameters
    ----------
    *args
        Contents to appear in the card's title, or tag attributes to pass to the
        resolved :class:`~htmltools.Tag` object.
    container
        Method for the returned :class:`~htmltools.Tag` object. Defaults to
        :func:`~shiny.ui.tags.h5`.
    **kwargs
        Additional HTML attributes for the returned :class:`~htmltools.Tag` object.

    Returns
    -------
    :
        An :class:`~htmltools.Tag` object.

    See Also
    --------
    * :func:`~shiny.ui.card` for creating a card component.
    * :func:`~shiny.ui.card_header` for creating a header within a card.
    * :func:`~shiny.experimental.ui.card_body` for putting content inside a card.
    * :func:`~shiny.ui.card_footer` for creating a footer within a card.
    * :func:`~shiny.experimental.ui.card_image` for adding an image to a card.
    """
    return container(*args, **kwargs)


class ImgContainer(Protocol):
    """
    A callable that wraps the return value of `card_image()`. To isolate your object in a card, return a :class:`~shiny.ui.CardItem`.
    """

    def __call__(self, *args: Tag) -> Tagifiable:
        """
        Wraps the return value of `card_image()`.

        Parameters
        ----------
        *args
            The return value of `card_image()`.

        Returns
        -------
        :
            A tagifiable object, such as a :class:`~htmltools.Tag` or
            :class:`~shiny.ui.CardItem` object.
        """
        ...


@add_example()
def card_image(
    file: str | Path | PurePath | io.BytesIO | None,
    *args: TagAttrs,
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
) -> Tagifiable:
    """
    A card image container

    :func:`~shiny.experimental.ui.card_image` creates a general container for an image within a
    :func:`~shiny.ui.card`. This component is designed to be
    provided as a direct child to :func:`~shiny.ui.card`.

    Parameters
    ----------
    file
        A file path pointing to an image. The image will be base64 encoded and provided to
        the `src` attribute of the `<img>` tag. Alternatively, you may set this value to
        `None` and provide the `src` yourself via `*args:TagAttrs` or
        `**kwargs:TagAttrValue` (e.g., `{"src": "HOSTED_PATH_TO_IMAGE"}` or
        `src="HOSTED_PATH_TO_IMAGE"`).
    *args
        A dictionary of tag attributes that are supplied to the resolved
        :class:`~htmltools.Tag` object.
    href
        An optional URL to link to.
    border_radius
        Where to apply `border-radius` on the image.
    mime_type
        The mime type of the `file`.
    class_
        Additional CSS classes for the resolved :class:`~htmltools.Tag` object.
    height
        Any valid CSS unit (e.g., `height="200px"`). `height` will not apply when a card is made
        `full_screen`. In this case, consider setting a `height` in
        :func:`~shiny.experimental.ui.card_body`.
    fill
        Whether to allow this element to grow/shrink to fit its `card` container.
    width
        Any valid CSS unit (e.g., `width="100%"`).
    container
        Method to wrap the returned :class:`~htmltools.Tag` object. Defaults to
        :func:`~shiny.experimental.ui.card_body`.
        If :func:`~shiny.experimental.ui.card_body` is used, each image will be in separate cards. If
        the `container` method does not return a :class:`~shiny.ui.CardItem`, it
        allows for consecutive non-`CardItem` objects to be bundled into a single
        :func:`~shiny.experimental.ui.card_body` within :func:`~shiny.ui.card`.
    **kwargs
        Additional HTML attributes for the resolved :class:`~htmltools.Tag`.
    """
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
                height=as_css_unit(height),
                width=as_css_unit(width),
            ),
        },
        {"class": card_class_map.get(border_radius, None)},
        *args,
        class_=class_,
        **kwargs,
    )

    if fill:
        image = as_fill_item(image)

    if href is not None:
        image = as_fillable_container(
            as_fill_item(
                tags.a(
                    image,
                    href=href,
                )
            )
        )

    if container:
        return container(image)
    else:
        return CardItem(image)
