from __future__ import annotations

from typing import Optional

from htmltools import Tag

from ._htmldeps import fill_dependency
from ._tag import tag_prepend_class, tag_remove_class


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
    item: Optional[bool] = None,
    container: Optional[bool] = None,
) -> Tag:
    if item is not None:
        if item:
            # TODO-barret: Find a way to allow users to pass `class_` within `**kwargs`, rather than
            # manually handling it so that it can override the classes added by `bind_fill_role()`.
            # Ex: `card_body()`, `card_image()`, `card()`, `layout_column_wrap()` and by extension `value_box()` or any method that calls the first four
            tag_prepend_class(tag, "html-fill-item")
        else:
            tag_remove_class(tag, "html-fill-item")

    if container is not None:
        if container:
            tag_prepend_class(tag, "html-fill-container")
            tag.append(fill_dependency())
        else:
            tag_remove_class(tag, "html-fill-container")

    return tag
