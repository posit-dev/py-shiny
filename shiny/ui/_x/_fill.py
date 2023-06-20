from __future__ import annotations

from typing import TypeVar

from htmltools import Tag

from ._htmldeps import fill_dependency
from ._tag import tag_prepend_class

__all__ = (
    "as_fillable_container",
    "as_fill_item",
)

TagT = TypeVar("TagT", bound="Tag")


FILL_ITEM_CLASS = "html-fill-item"
FILL_CONTAINER_CLASS = "html-fill-container"


def as_fillable_container(
    tag: TagT,
) -> TagT:
    tag_prepend_class(tag, FILL_CONTAINER_CLASS)
    tag.append(fill_dependency())
    return tag


def as_fill_item(
    tag: TagT,
) -> TagT:
    tag_prepend_class(tag, FILL_ITEM_CLASS)
    tag.append(fill_dependency())
    return tag
