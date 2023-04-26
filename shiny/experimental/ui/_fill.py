from __future__ import annotations

from typing import Optional

from htmltools import Tag

from ._htmldeps import fill_dependencies


# TODO-future: Find a way to allow users to pass `class_` within `**kwargs`, rather than
# manually handling it so that it can override the classes added by `bind_fill_role()`.
# Ex: `card_body()`, `card_image()`, `card()`, `layout_column_wrap()` and by extension `value_box()` or any method that calls the first four
def bind_fill_role(
    tag: Tag,
    *,
    # TODO: change `item` and `container` to `fill` and `fillable` respectively
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
            tag.append(fill_dependencies())
        else:
            # TODO: this remove_class method doesn't exist, but that's what we want
            # tag.remove_class("html-fill-container")
            ...

    return tag
