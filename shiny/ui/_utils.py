from typing import Optional, Union

from htmltools import (
    tags,
    Tag,
    TagList,
    TagChildArg,
    TagChild,
    HTMLDependency,
    head_content,
)

from ..types import MISSING, MISSING_TYPE


def shiny_input_label(id: str, label: TagChildArg = None) -> Tag:
    cls = "control-label" + ("" if label else " shiny-label-null")
    return tags.label(label, class_=cls, id=id + "-label", for_=id)


def get_window_title(
    title: Optional[Union[str, Tag, TagList]],
    window_title: Union[str, MISSING_TYPE] = MISSING,
) -> Optional[HTMLDependency]:
    if title is not None and isinstance(window_title, MISSING_TYPE):
        window_title = _find_child_strings(title)

    if isinstance(window_title, MISSING_TYPE):
        return None
    else:
        return head_content(tags.title(window_title))


def _find_child_strings(x: Union[Tag, TagList, TagChild]) -> str:
    if isinstance(x, Tag) and x.name not in ("script", "style"):
        x = x.children
    if isinstance(x, TagList):
        strings = [_find_child_strings(y) for y in x]
        return " ".join(filter(lambda x: x != "", strings))
    if isinstance(x, str):
        return x
    return ""
