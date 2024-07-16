from __future__ import annotations

from typing import Optional

from htmltools import TagAttrs, TagAttrValue, TagChild

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


__all__ = (
    "card",
    "card_body",
)
