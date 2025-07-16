from __future__ import annotations

import base64
import io
import mimetypes
from pathlib import Path, PurePath
from typing import Literal, Optional, Protocol

from htmltools import Tag, TagAttrs, TagAttrValue, Tagifiable, css, tags

from ..._docstring import add_example
from ...ui._card import CardItem, card_body
from ...ui.css import CssUnit, as_css_unit
from ...ui.fill import as_fill_item, as_fillable_container

__all__ = ("card_image",)

############################################################################


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
    # TODO-future: Must be updated to match rstudio/bslib#1076 before moving from exp.
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
