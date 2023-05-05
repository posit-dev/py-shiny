from __future__ import annotations

import typing

from htmltools import TagAttrs

T = typing.TypeVar("T")


def split_args_into_attrs_and_not_attrs(
    *args: T | TagAttrs,
) -> tuple[list[TagAttrs], list[T]]:
    not_attrs: list[T] = []
    attrs: list[TagAttrs] = []

    for arg in args:
        # If is TagAttrs...
        if isinstance(arg, dict):
            arg = typing.cast(TagAttrs, arg)
            attrs.append(arg)
        else:
            # If is TagChild / T...
            not_attrs.append(arg)

    return (attrs, not_attrs)
