from __future__ import annotations

from pathlib import PurePath
from typing import Optional

from htmltools import HTMLDependency, Tag


def bind_fill_role(
    tag: Tag,
    *,
    item: Optional[bool] = None,
    container: Optional[bool] = None,
) -> Tag:
    if item is not None:
        if item:
            tag.add_class("html-fill-item")
        else:
            # TODO: this remove_class method doesn't exist, but that's what we want
            # tag.remove_class("html-fill-item")
            ...

    if container is not None:
        if container:
            tag.add_class("html-fill-container")
            tag.append(fill_dependencies_x())
        else:
            # TODO: this remove_class method doesn't exist, but that's what we want
            # tag.remove_class("html-fill-container")
            ...

    return tag


ex_www_path = PurePath(__file__).parent.parent / "www"


def fill_dependencies_x() -> HTMLDependency:
    return HTMLDependency(
        "htmltools-fill-x",
        "0.0.0.0",
        source={"package": "shiny", "subdir": str(ex_www_path)},
        stylesheet={"href": "fill.css"},
    )
