from __future__ import annotations

from typing import Optional

from htmltools import Tag

from ._htmldeps import fill_dependency


# TODO-future:
# From @wch:
# > For functions like this, which modify the original object, I think the Pythonic way
# > of doing things is to return None, to make it clearer that the object is modified in
# > place.
# From @schloerke:
# > It makes for a very clunky interface. Keeping as is for now.
# > Should we copy the tag before modifying it? (If we are not doing that elsewhere, then I am hesitant to start here.)
def bind_fill_role(
    tag: Tag,
    *,
    # TODO: change `item` and `container` to `fill` and `fillable` respectively
    item: Optional[bool] = None,
    container: Optional[bool] = None,
) -> Tag:
    if item is not None:
        if item:
            # TODO-barret; prepend the `html-fill-item` so that the class value has least preference. This would make it so that `class_` is handled properly within python and the tag could easily use `tag.add_attrs(*args, **kwargs)` to add the overriding classes and attributes
            # TODO-barret: Find a way to allow users to pass `class_` within `**kwargs`, rather than
            # manually handling it so that it can override the classes added by `bind_fill_role()`.
            # Ex: `card_body()`, `card_image()`, `card()`, `layout_column_wrap()` and by extension `value_box()` or any method that calls the first four
            tag.add_class("html-fill-item")
        else:
            # TODO: this remove_class method doesn't exist, but that's what we want
            # tag.remove_class("html-fill-item")
            ...

    if container is not None:
        if container:
            tag.add_class("html-fill-container")
            tag.append(fill_dependency())
        else:
            # TODO: this remove_class method doesn't exist, but that's what we want
            # tag.remove_class("html-fill-container")
            ...

    return tag
