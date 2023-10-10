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


def tag_remove_class(tag: TagT, *class_: str | None) -> TagT:
    """
    Remove a class value from the HTML class attribute.

    Parameters
    ----------
    *class_
        The class name to remove.

    Returns
    -------
    :
        The modified tag.
    """
    cls = tag.attrs.get("class")
    # If no class values to remove from, quit
    if not cls:
        return tag

    # Remove any `None` values
    set_to_remove = {c for c in class_ if c is not None}

    # If no classes to remove, quit
    if len(set_to_remove) == 0:
        return tag

    # Get new set of classes
    # Order matters, otherwise we could use `set()` subtraction: `set(cls.split(" ")) - set(class_)`
    new_cls: list[str] = []
    for cls_val in cls.split(" "):
        if cls_val not in set_to_remove:
            new_cls.append(cls_val)

    # If no classes left, remove the attribute
    if len(new_cls) == 0:
        # If here, `attrs.class` must exist
        tag.attrs.pop("class")
        return tag

    # Otherwise, set the new class
    tag.attrs["class"] = " ".join(new_cls)
    return tag


def tag_add_style(
    tag: TagT,
    *style: str | None,
) -> TagT:
    """
    Add a style value(s) to the HTML style attribute.

    Parameters
    ----------
    *style
        CSS properties and values already properly formatted. Each should already contain trailing semicolons.

    See Also
    --------
    ~htmltools.css

    Returns
    -------
    :
        The modified tag.
    """
    styles = (
        tag.attrs.get("style"),
        *style,
    )
    non_none_style_tuple = (s for s in styles if s is not None)
    style_str = "".join(non_none_style_tuple)

    if style_str:
        tag.attrs["style"] = style_str
    return tag
