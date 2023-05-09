from __future__ import annotations

import typing

from htmltools import TagAttrs, TagAttrValue, TagChild, div

T = typing.TypeVar("T", bound=TagChild)

# Export this type from htmltools
TagAttrDict = typing.Dict[str, str]


# TODO-barret; leverage `consolidate_attrs()` with `class_` and `**kwargs`
def consolidate_attrs(
    *args: T | TagAttrs,
    **kwargs: TagAttrValue,
) -> tuple[TagAttrDict, list[T]]:
    tag = div(*args, **kwargs)
    # While returning `tag.children` works, it is nice to have a minimal type hint
    children = typing.cast(list[T], tag.children)
    return (tag.attrs, children)
