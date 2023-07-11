from __future__ import annotations

import typing
from typing import overload

from htmltools import TagAttrs, TagAttrValue, TagChild, div

from ..._typing_extensions import TypeGuard

TagChildT = typing.TypeVar("TagChildT", bound=TagChild)


# If no children are provided, it will not be able to infer the type of `TagChildT`.
# Using `TagChild`
@overload
def consolidate_attrs(
    *args: TagAttrs,
    **kwargs: TagAttrValue,
) -> tuple[TagAttrs, list[TagChild]]:
    ...


# Same as original definition
@overload
def consolidate_attrs(
    *args: TagChildT | TagAttrs,
    **kwargs: TagAttrValue,
) -> tuple[TagAttrs, list[TagChildT]]:
    ...


def consolidate_attrs(
    *args: TagChildT | TagAttrs,
    **kwargs: TagAttrValue,
) -> tuple[TagAttrs, list[TagChildT]]:
    tag = div(*args, **kwargs)

    # `TagAttrs` currently isn't compatible with `htmltools._core.TagAttrDict`
    # https://github.com/rstudio/py-htmltools/pull/55
    # Convert to a plain dict to avoid getting custom methods from TagAttrDict
    # Cast to `TagAttrs` so that `Tag` functions will accept the dictionary.
    attrs = typing.cast(TagAttrs, dict(tag.attrs))

    # Do not alter children structure (like `TagList` does)
    children = [child for child in args if not isinstance(child, dict)]
    return (attrs, children)


def is_01_scalar(x: object) -> TypeGuard[float]:
    return isinstance(x, (int, float)) and x >= 0.0 and x <= 1.0


@overload
def trinary(x: None) -> None:
    ...


@overload
def trinary(x: bool | str) -> str:
    ...


def trinary(x: bool | str | None) -> None | str:
    if x is None:
        return None
    elif x:
        return "true"
    else:
        return "false"
