from __future__ import annotations

from typing import TypeVar

from htmltools import Tag

from ..._docstring import add_example
from .._html_deps_shinyverse import fill_dependency
from .._tag import tag_prepend_class, tag_remove_class

__all__ = (
    "as_fillable_container",
    "as_fill_item",
    "remove_all_fill",
    "is_fill_item",
    "is_fillable_container",
)

TagT = TypeVar("TagT", bound="Tag")


FILL_ITEM_CLASS = "html-fill-item"
FILL_CONTAINER_CLASS = "html-fill-container"


@add_example()
def as_fillable_container(
    tag: TagT,
) -> TagT:
    tag_prepend_class(tag, FILL_CONTAINER_CLASS)
    tag.append(fill_dependency())
    return tag


@add_example()
def as_fill_item(
    tag: TagT,
) -> TagT:
    """
    Coerce a tag to a fill item

    Filling layouts are built on the foundation of _fillable containers_ and _fill
    items_ (_fill carriers_ are both _fillable containers_ and _fill items_). This is
    why most UI components (e.g., :func:`~shiny.ui.card`,
    :func:`~shiny.ui.layout_sidebar`) possess both `fillable` and `fill` arguments (to
    control their fill behavior). However, sometimes it's useful to add, remove, and/or
    test fillable/fill properties on arbitrary :class:`~htmltools.Tag`, which these
    functions are designed to do.

    Parameters
    ----------
    tag
        a Tag object.

    Returns
    -------
    :
        The original :class:`~htmltools.Tag` object (`tag`) with additional attributes
        (and an :class:`~htmltools.HTMLDependency`).

    See Also
    --------
    * :func:`~shiny.ui.fill.as_fillable_container`
    * :func:`~shiny.ui.fill.remove_all_fill`
    * :func:`~shiny.ui.fill.is_fill_item`
    * :func:`~shiny.ui.fill.is_fillable_container`
    """
    tag_prepend_class(tag, FILL_ITEM_CLASS)
    tag.append(fill_dependency())
    return tag


def remove_all_fill(
    tag: TagT,
) -> TagT:
    """
    Remove any filling layouts from a tag

    Filling layouts are built on the foundation of _fillable containers_ and _fill
    items_ (_fill carriers_ are both _fillable containers_ and _fill items_). This is
    why most UI components (e.g., :func:`~shiny.ui.card`,
    :func:`~shiny.ui.layout_sidebar`) possess both `fillable` and `fill` arguments (to
    control their fill behavior). However, sometimes it's useful to add, remove, and/or
    test fillable/fill properties on arbitrary :class:`~htmltools.Tag`, which these
    functions are designed to do.

    Parameters
    ----------
    tag
        a Tag object.

    Returns
    -------
    :
        The original :class:`~htmltools.Tag` object with filling layout attributes
        removed.


    See Also
    --------
    * :func:`~shiny.ui.fill.as_fill_item`
    * :func:`~shiny.ui.fill.as_fillable_container`
    * :func:`~shiny.ui.fill.is_fill_item`
    * :func:`~shiny.ui.fill.is_fillable_container`
    """

    tag_remove_class(tag, FILL_CONTAINER_CLASS)
    tag_remove_class(tag, FILL_ITEM_CLASS)
    return tag


def is_fillable_container(tag: object) -> bool:
    """
    Test a tag for being a fillable container

    Filling layouts are built on the foundation of _fillable containers_ and _fill
    items_ (_fill carriers_ are both _fillable containers_ and _fill items_). This is
    why most UI components (e.g., :func:`~shiny.ui.card`, :func:`~shiny.ui.card_body`,
    :func:`~shiny.ui.layout_sidebar`) possess both `fillable` and `fill` arguments (to
    control their fill behavior). However, sometimes it's useful to add, remove, and/or
    test fillable/fill properties on arbitrary :class:`~htmltools.Tag`, which these
    functions are designed to do.

    Parameters
    ----------
    tag
        a Tag object.

    Returns
    -------
    :
        Whether or not `tag` is a fillable container.


    See Also
    --------
    * :func:`~shiny.ui.fill.as_fill_item`
    * :func:`~shiny.ui.fill.as_fillable_container`
    * :func:`~shiny.ui.fill.remove_all_fill`
    * :func:`~shiny.ui.fill.is_fill_item`
    * :func:`~shiny.ui.fill.is_fillable_container`
    """
    # TODO-future; Handle widgets
    # # won't actually work until (htmltools#334) gets fixed
    # renders_to_tag_class(x, FILL_CONTAINER_CLASS, ".html-widget")

    return isinstance(tag, Tag) and tag.has_class(FILL_CONTAINER_CLASS)


def is_fill_item(tag: object) -> bool:
    """
    Test a tag for being a fill item

    Filling layouts are built on the foundation of _fillable containers_ and _fill
    items_ (_fill carriers_ are both _fillable containers_ and _fill items_). This is
    why most UI components (e.g., :func:`~shiny.ui.card`, :func:`~shiny.ui.card_body`,
    :func:`~shiny.ui.layout_sidebar`) possess both `fillable` and `fill` arguments (to
    control their fill behavior). However, sometimes it's useful to add, remove, and/or
    test fillable/fill properties on arbitrary :class:`~htmltools.Tag`, which these
    functions are designed to do.

    Parameters
    ----------
    tag
        a Tag object.

    Returns
    -------
    :
        Whether or not `tag` is a fill item.

    See Also
    --------
    * :func:`~shiny.ui.fill.as_fill_item`
    * :func:`~shiny.ui.fill.as_fillable_container`
    * :func:`~shiny.ui.fill.remove_all_fill`
    * :func:`~shiny.ui.fill.is_fillable_container`
    """
    # TODO-future; Handle widgets
    # # won't actually work until (htmltools#334) gets fixed
    # renders_to_tag_class(x, FILL_ITEM_CLASS, ".html-widget")

    return isinstance(tag, Tag) and tag.has_class(FILL_ITEM_CLASS)
