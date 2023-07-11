from __future__ import annotations

from typing import TypeVar

from htmltools import Tag

TagT = TypeVar("TagT", bound="Tag")

# Tag.add_class(x: str) -> Self[Tag]:
#     cls = self.attrs.get("class")
#     if cls:
#         x = cls + " " + x
#     self.attrs["class"] = x
#     return self


# Do not export
# "Prepend" version of `tag.add_class(class_)`
def tag_prepend_class(tag: TagT, *class_: str | None) -> TagT:
    classes = (
        *class_,
        tag.attrs.get("class"),
    )
    classes = [c for c in classes if c is not None]
    if len(classes) == 0:
        return tag
    tag.attrs["class"] = " ".join(classes)
    return tag
