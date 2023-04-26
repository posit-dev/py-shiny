from __future__ import annotations

from typing import NamedTuple

from htmltools import TagAttrs, TagChild


class ChildrenAndAttrs(NamedTuple):
    children: list[TagChild]
    attrs: list[TagAttrs]


def separate_args_into_children_and_attrs(
    *args: TagChild | TagAttrs,
) -> ChildrenAndAttrs:
    children: list[TagChild] = []
    attrs: list[TagAttrs] = []

    for arg in args:
        if isinstance(arg, dict):
            attrs.append(arg)
        else:
            children.append(arg)

    return ChildrenAndAttrs(children, attrs)
