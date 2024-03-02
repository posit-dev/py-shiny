from __future__ import annotations

from typing import Optional, Protocol

from htmltools import (
    HTML,
    Tag,
    TagAttrs,
    TagAttrValue,
    TagChild,
    TagFunction,
    TagList,
    css,
    div,
    tags,
)

from .._docstring import add_example
from .._utils import private_random_id
from ..types import MISSING, MISSING_TYPE
from ._html_deps_shinyverse import components_dependencies
from ._tag import consolidate_attrs
from ._tooltip import tooltip
from .css._css_unit import CssUnit, as_css_padding, as_css_unit
from .fill import as_fill_item, as_fillable_container

# TODO-barret-future; Update header to return CardHeader class. Same for footer. Then we
# can check `*args` for a CardHeader class and move it to the top. And footer to the
# bottom. Can throw error if multiple headers/footers are provided or could concatenate.


__all__ = (
    "CardItem",
    "card",
    "card_header",
    "card_footer",
)

############################################################################
# Experimental+ full implementation
############################################################################
# Reasons for experimental implementations:
# * Missing parameter of `wrapper=`
# * Missing helper function `card_body()`
############################################################################


@add_example()
def card(
    *args: TagChild | TagAttrs | CardItem,
    full_screen: bool = False,
    height: Optional[CssUnit] = None,
    max_height: Optional[CssUnit] = None,
    min_height: Optional[CssUnit] = None,
    fill: bool = True,
    class_: Optional[str] = None,
    # wrapper: WrapperCallable | None | MISSING_TYPE = MISSING,
    **kwargs: TagAttrValue,
) -> Tag:
    """
    A Bootstrap card component

    A general purpose container for grouping related UI elements together with a border
    and optional padding. To learn more about `card()`s, see [this
    article](https://rstudio.github.io/bslib/articles/cards.html).

    Parameters
    ----------
    *args
        UI elements.
    full_screen
        If `True`, an icon will appear when hovering over the card body. Clicking the
        icon expands the card to fit viewport size.
    height,max_height,min_height
        Any valid CSS unit (e.g., `height="200px"`). Doesn't apply when a card is made
        `full_screen`.
    fill
        Whether or not to allow the card to grow/shrink to fit a fillable container with
        an opinionated height (e.g., :func:`~shiny.ui.page_fillable`).
    class_
        Additional CSS classes for the returned Tag.
    **kwargs
        HTML attributes on the returned Tag.

    Returns
    -------
    :
        An :func:`~shiny.ui.tags.div` tag.

    See Also
    --------
    * :func:`~shiny.ui.card_header` for creating a header within the card.
    * :func:`~shiny.ui.card_footer` for creating a footer within the card.
    """
    # * :func:`~shiny.ui.layout_column_wrap` for laying out multiple cards
    #   (or multiple columns inside a card).
    return _card_impl(
        *args,
        full_screen=full_screen,
        height=height,
        max_height=max_height,
        min_height=min_height,
        fill=fill,
        class_=class_,
        wrapper=MISSING,
        **kwargs,
    )


def _card_impl(
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
    Common implementation method between `shiny.ui.card()` and `shiny.experimental.ui.card()`.

    Experimental implements the parameter `wrapper=`. Main does not as `card_body()` is not in `main`.
    """
    # TODO-question Should card_body() ever exist in main?
    # Barret: Yes? Need to customize fill/fillable content (ex: Fixed height for item B where content = A, B, C; fill = TRUE, fillable = TRUE).
    if isinstance(wrapper, MISSING_TYPE):
        wrapper = card_body

    attrs, children = consolidate_attrs(*args, class_=class_, **kwargs)
    children = _wrap_children_in_card(*children, wrapper=wrapper)

    if full_screen and "id" not in attrs:
        attrs["id"] = private_random_id("bslib_card")

    tag = div(
        {
            "class": "card bslib-card bslib-mb-spacing",
            "style": css(
                height=as_css_unit(height),
                max_height=as_css_unit(max_height),
                min_height=as_css_unit(min_height),
            ),
            "data-bslib-card-init": True,
            "data-full-screen": "false" if full_screen else None,
        },
        *children,
        attrs,
        _full_screen_toggle(attrs["id"]) if full_screen else None,
        components_dependencies(),
        _card_js_init(),
    )
    if fill:
        tag = as_fill_item(tag)
    tag = as_fillable_container(tag)

    return tag


def _card_js_init() -> Tag:
    return tags.script(
        {"data-bslib-card-init": True},
        "window.bslib.Card.initializeAllCards();",
    )


def _full_screen_toggle(id_controls: TagAttrValue) -> Tag:
    return tooltip(
        tags.button(
            {
                "class": "bslib-full-screen-enter badge rounded-pill",
                "aria-expanded": "false",
                "aria-controls": id_controls,
                "aria-label": "Expand card",
            },
            _full_screen_toggle_icon(),
        ),
        "Expand",
    )


# via bsicons::bs_icon("arrows-fullscreen")
def _full_screen_toggle_icon() -> HTML:
    # https://www.visiwig.com/icons/
    # https://www.visiwig.com/icons-license/
    return HTML(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" style="height:1em;width:1em;fill:currentColor;" aria-hidden="true" role="img"><path d="M20 5C20 4.4 19.6 4 19 4H13C12.4 4 12 3.6 12 3C12 2.4 12.4 2 13 2H21C21.6 2 22 2.4 22 3V11C22 11.6 21.6 12 21 12C20.4 12 20 11.6 20 11V5ZM4 19C4 19.6 4.4 20 5 20H11C11.6 20 12 20.4 12 21C12 21.6 11.6 22 11 22H3C2.4 22 2 21.6 2 21V13C2 12.4 2.4 12 3 12C3.6 12 4 12.4 4 13V19Z"/></svg>'
    )


# https://mypy.readthedocs.io/en/stable/protocols.html#callback-protocols
class WrapperCallable(Protocol):
    """
    A callable that wraps children into a :class:`~shiny.ui.CardItem`.
    """

    def __call__(self, *args: TagChild) -> CardItem:
        """
        Wraps children into a :class:`~shiny.ui.CardItem`.

        Parameters
        ----------
        *args
            `TagChild` children to wrap.

        Returns
        -------
        :
            A :class:`~shiny.ui.CardItem` object.
        """
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


@add_example()
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
) -> CardItem:
    # For a general overview of the :func:`~shiny.ui.card` API, see [this article](https://rstudio.github.io/bslib/articles/cards.html).
    """
    Card body container

    A general container for the "main content" of a :func:`~shiny.ui.card`. This component is designed
    to be provided as direct children to :func:`~shiny.ui.card`.

    Parameters
    ----------
    *args
        Contents to the card's body. Or tag attributes that are supplied to the
        resolved :class:`~htmltools.Tag` object.
    fillable
        Whether or not the card item should be a fillable (i.e. flexbox) container.
    min_height,max_height,max_height_full_screen
        Any valid CSS length unit. If `max_height_full_screen` is missing, it is set to
        `max_height`.
    height
        Any valid CSS unit (e.g., `height="200px"`). Doesn't apply when a card is made
        `full_screen` (in this case, consider setting a `height` in
        `card_body()`).
    padding
        Padding to use for the body. This can be a numeric vector
        (which will be interpreted as pixels) or a character vector with valid CSS
        lengths. The length can be between one and four. If one, then that value
        will be used for all four sides. If two, then the first value will be used
        for the top and bottom, while the second value will be used for left and
        right. If three, then the first will be used for top, the second will be
        left and right, and the third will be bottom. If four, then the values will
        be interpreted as top, right, bottom, and left respectively.
    gap
        A CSS length unit defining the `gap` (i.e., spacing) between elements provided
        to `*args`. This argument is only applicable when `fillable = TRUE`.
    fill
        Whether to allow this element to grow/shrink to fit its `card` container.
    class_
        Additional CSS classes for the returned Tag.
    **kwargs
        Additional HTML attributes for the returned Tag.

    Returns
    -------
    :
        A :class:`~shiny.ui.CardItem` object.

    See Also
    --------
    * :func:`~shiny.ui.layout_column_wrap` for laying out multiple cards
        (or multiple columns inside a card).
    * :func:`~shiny.ui.card` for creating a card component.
    * :func:`~shiny.ui.card_header` for creating a header within the card.
    * :func:`~shiny.experimental.ui.card_title` for creating a title within the card body.
    * :func:`~shiny.ui.card_footer` for creating a footer within the card.
    """
    if isinstance(max_height_full_screen, MISSING_TYPE):
        max_height_full_screen = max_height

    div_style_args = {
        "min-height": as_css_unit(min_height),
        "--bslib-card-body-max-height": as_css_unit(max_height),
        "--bslib-card-body-max-height-full-screen": as_css_unit(max_height_full_screen),
        "margin-top": "auto",
        "margin-bottom": "auto",
        # .card-body already adds `flex: 1 1 auto` so make sure to override it
        "flex": "1 1 auto" if fill else "0 0 auto",
        "padding": as_css_padding(padding),
        "gap": as_css_unit(gap),
        "height": as_css_unit(height),
    }
    tag = tags.div(
        {
            "class": "card-body bslib-gap-spacing",
            "style": css(**div_style_args),
        },
        *args,
        class_=class_,
        **kwargs,
    )

    if fill:
        tag = as_fill_item(tag)
    if fillable:
        tag = as_fillable_container(tag)

    return CardItem(tag)


############################################################################
# Full implementations
############################################################################


class CardItem:
    """
    A wrapper around a :class:`~htmltools.Tag` object that represents the content of a
    card item (e.g., :func:`~shiny.ui.card_header` or
    :func:`~shiny.ui.card_footer`).

    This class is used to allow for consecutive non-card items to be bundled into a
    single group within :func:`~shiny.ui.card`.

    Parameters
    ----------
    item
        A :class:`~htmltools.Tag` object that represents the content of a card item
        (e.g., :func:`~shiny.ui.card_header` or
        :func:`~shiny.ui.card_footer`).

    See Also
    --------
    * :func:`~shiny.ui.card` for creating a card component.
    * :func:`~shiny.ui.card_header` for creating a header within a card.
    * :func:`~shiny.ui.card_footer` for creating a footer within a card.
    """

    def __init__(
        self,
        item: TagChild,
    ):
        self._item = item

    def resolve(self) -> TagChild:
        """
        Resolves an object with the `CardItem` class by returning the `item` provided at initialization.

        Returns
        -------
        :
            The `item` provided at initialization.
        """
        return self._item

    def tagify(self) -> TagList:
        """
        Tagify the `item`

        Returns
        -------
        :
            A tagified :class:`~htmltools.TagList` object.
        """
        return TagList(self.resolve()).tagify()


@add_example()
def card_header(
    *args: TagChild | TagAttrs,
    container: TagFunction = tags.div,
    **kwargs: TagAttrValue,
) -> CardItem:
    """
    Card header container

    A general container for the "header" of a :func:`~shiny.ui.card`. This component is designed
    to be provided as a direct child to :func:`~shiny.ui.card`.

    The header has a different background color and border than the rest of the card.

    Parameters
    ----------
    *args
        Contents to the header container. Or tag attributes that are supplied to the
        resolved :class:`~htmltools.Tag` object.
    container
        Method for the returned Tag object. Defaults to :func:`~shiny.ui.tags.div`.
    **kwargs
        Additional HTML attributes for the returned Tag.

    Returns
    -------
    :
        A :class:`~shiny.ui.CardItem` object.

    See Also
    --------
    * :func:`~shiny.ui.card` for creating a card component.
    * :func:`~shiny.ui.card_footer` for creating a footer within the card.
    """
    return CardItem(
        container({"class": "card-header"}, *args, **kwargs),
    )


@add_example()
def card_footer(
    *args: TagChild | TagAttrs,
    **kwargs: TagAttrValue,
) -> CardItem:
    """
    Card footer container

    A general container for the "footer" of a :func:`~shiny.ui.card`. This component is designed
    to be provided as a direct child to :func:`~shiny.ui.card`.

    The footer has a different background color and border than the rest of the card.

    Parameters
    ----------
    *args
        Contents to the footer container. Or tag attributes that are supplied to the
        resolved :class:`~htmltools.Tag` object.
    **kwargs
        Additional HTML attributes for the returned Tag.

    Returns
    -------
    :
        A :class:`~shiny.ui.CardItem` object.

    See Also
    --------
    * :func:`~shiny.ui.card` for creating a card component.
    * :func:`~shiny.ui.card_footer` for creating a footer within the card.
    """
    return CardItem(
        tags.div({"class": "card-footer"}, *args, **kwargs),
    )
