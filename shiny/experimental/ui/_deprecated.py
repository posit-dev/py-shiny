from __future__ import annotations

from typing import Optional

from htmltools import TagAttrs, TagAttrValue, TagChild, TagFunction, Tagifiable, tags

from ..._deprecated import warn_deprecated
from ...types import MISSING, MISSING_TYPE
from ...ui import CardItem
from ...ui import card as main_card
from ...ui._card import card_body as main_card_body  # FIXME after #1506
from ...ui.css import CssUnit


def card(
    *args: TagChild | TagAttrs | CardItem,
    full_screen: bool = False,
    height: Optional[CssUnit] = None,
    max_height: Optional[CssUnit] = None,
    min_height: Optional[CssUnit] = None,
    fill: bool = True,
    class_: Optional[str] = None,
    wrapper: MISSING_TYPE = MISSING,
    **kwargs: TagAttrValue,
):
    """Deprecated. Please use :func:`~shiny.ui.card()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.card()` was deprecated in shiny 1.0.0. "
        "Card components are now available in the main shiny namespace. "
        "Please use `shiny.ui.card()` instead."
    )
    return main_card(
        *args,
        full_screen=full_screen,
        height=height,
        max_height=max_height,
        min_height=min_height,
        fill=fill,
        class_=class_,
        id=None,
        **kwargs,
    )


def card_body(
    *args: TagChild | TagAttrs,
    fillable: bool = True,
    min_height: Optional[CssUnit] = None,
    max_height: Optional[CssUnit] = None,
    max_height_full_screen: Optional[CssUnit] | MISSING_TYPE = MISSING,
    height: Optional[CssUnit] = None,
    padding: Optional[CssUnit | list[CssUnit]] = None,
    gap: Optional[CssUnit] = None,
    fill: bool = True,
    class_: Optional[str] = None,
    **kwargs: TagAttrValue,
):
    """Deprecated. Please use :func:`~shiny.ui.card_body()` instead."""
    warn_deprecated(
        "`shiny.experimental.ui.card_body()` was deprecated in shiny 1.0.0. "
        "Card components are now available in the main shiny namespace. "
        "Please use `shiny.ui.card_body()` instead."
    )
    return main_card_body(
        *args,
        fillable=fillable,
        min_height=min_height,
        max_height=max_height,
        max_height_full_screen=max_height_full_screen,
        height=height,
        padding=padding,
        gap=gap,
        fill=fill,
        class_=class_,
        **kwargs,
    )


def card_title(
    *args: TagChild | TagAttrs,
    container: TagFunction = tags.h5,
    **kwargs: TagAttrValue,
) -> Tagifiable:
    """
    Deprecated. Please use :func:`~shiny.ui.tags.h5()` instead.

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
    warn_deprecated(
        "`shiny.experimental.ui.card_title()` was deprecated in shiny 1.0.0 "
        "and will be removed in a future version of shiny. "
        "Please use `shiny.ui.tags.h5()` instead."
    )
    return container(*args, **kwargs)


__all__ = (
    "card",
    "card_body",
)
