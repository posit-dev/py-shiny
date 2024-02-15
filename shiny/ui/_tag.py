from __future__ import annotations

from typing import TypeVar, cast, overload

from htmltools import TagAttrs, TagAttrValue, TagChild, div

TagChildT = TypeVar("TagChildT", bound=TagChild)


# If no children are provided, it will not be able to infer the type of `TagChildT`.
# Using `TagChild`
@overload
def consolidate_attrs(
    *args: TagAttrs,
    **kwargs: TagAttrValue,
) -> tuple[TagAttrs, list[TagChild]]: ...


# Same as original definition
@overload
def consolidate_attrs(
    *args: TagChildT | TagAttrs,
    **kwargs: TagAttrValue,
) -> tuple[TagAttrs, list[TagChildT]]: ...


def consolidate_attrs(
    *args: TagChildT | TagAttrs,
    **kwargs: TagAttrValue,
) -> tuple[TagAttrs, list[TagChildT]]:
    tag = div(*args, **kwargs)

    # `TagAttrs` currently isn't compatible with `htmltools._core.TagAttrDict`
    # https://github.com/posit-dev/py-htmltools/pull/55
    # Convert to a plain dict to avoid getting custom methods from TagAttrDict
    # Cast to `TagAttrs` so that `Tag` functions will accept the dictionary.
    attrs = cast(TagAttrs, dict(tag.attrs))

    # Do not alter children structure (like `TagList` does)
    children = [child for child in args if not isinstance(child, dict)]
    return (attrs, children)


@overload
def trinary(x: None) -> None: ...


@overload
def trinary(x: bool | str) -> str: ...


def trinary(x: bool | str | None) -> None | str:
    if x is None:
        return None
    elif x:
        return "true"
    else:
        return "false"
