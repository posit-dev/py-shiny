from __future__ import annotations

from typing import Optional, overload

from htmltools import (
    HTMLDependency,
    Tag,
    TagChild,
    TagList,
    TagNode,
    head_content,
    tags,
)

from ..types import MISSING, MISSING_TYPE


def shiny_input_label(id: str, label: TagChild = None) -> Tag:
    cls = "control-label" + ("" if label else " shiny-label-null")
    return tags.label(label, class_=cls, id=id + "-label", for_=id)


@overload
def get_window_title(
    title: None,
    window_title: MISSING_TYPE,
) -> None:
    ...


@overload
def get_window_title(
    title: None,
    window_title: str,
) -> HTMLDependency:
    ...


@overload
def get_window_title(
    title: str | Tag | TagList,
    window_title: str | MISSING_TYPE,
) -> HTMLDependency:
    ...


def get_window_title(
    title: Optional[str | Tag | TagList],
    window_title: str | MISSING_TYPE = MISSING,
) -> Optional[HTMLDependency]:
    if title is not None and isinstance(window_title, MISSING_TYPE):
        window_title = _find_child_strings(title)

    if isinstance(window_title, MISSING_TYPE):
        return None
    else:
        return head_content(tags.title(window_title))


def _find_child_strings(x: TagList | TagNode) -> str:
    if isinstance(x, Tag) and x.name not in ("script", "style"):
        x = x.children
    if isinstance(x, TagList):
        strings = [_find_child_strings(y) for y in x]
        return " ".join(filter(lambda x: x != "", strings))
    if isinstance(x, str):
        return x
    return ""
