from __future__ import annotations

import typing

from htmltools import TagAttrs, TagAttrValue, TagChild, div

from shiny._typing_extensions import TypeGuard

T = typing.TypeVar("T", bound=TagChild)

# Export this type from htmltools
TagAttrDict = typing.Dict[str, str]


def consolidate_attrs(
    *args: T | TagAttrs,
    **kwargs: TagAttrValue,
) -> tuple[TagAttrDict, list[T]]:
    tag = div(*args, **kwargs)
    # While returning `tag.children` works, it is nice to have a minimal type hint
    children = typing.cast(list[T], tag.children)
    return (tag.attrs, children)


def is_01_scalar(x: object) -> TypeGuard[float]:
    return isinstance(x, float) and x >= 0.0 and x <= 1.0
