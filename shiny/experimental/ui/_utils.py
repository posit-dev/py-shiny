from __future__ import annotations

import typing

from htmltools import TagAttrs, TagAttrValue, TagChild, div

from ..._typing_extensions import TypeGuard

TagChildT = typing.TypeVar("TagChildT", bound=TagChild)


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
    return isinstance(x, float) and x >= 0.0 and x <= 1.0
