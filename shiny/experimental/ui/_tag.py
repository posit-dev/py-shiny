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
def tag_prepend_class(tag: TagT, class_: str) -> TagT:
    cls = tag.attrs.get("class")
    if cls:
        # Prepend the class!
        class_ = class_ + " " + cls
    tag.attrs["class"] = class_
    return tag


def tag_remove_class(tag: TagT, x: str) -> TagT:
    """
    Remove a class value from the HTML class attribute.

    Parameters
    ----------
    class_
        The class name to remove.

    Returns
    -------
    :
        The modified tag.
    """
    cls = tag.attrs.get("class")
    if not cls:
        return tag
    if x == cls:
        tag.attrs.pop("class")
        return tag

    tag.attrs["class"] = " ".join(
        [cls_val for cls_val in cls.split(" ") if cls_val != x]
    )
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
    collapse_
        Character to use to collapse properties into a single string; likely "" (the
        default) for style attributes, and either "\n" or None for style blocks.
    **kwargs
        Named style properties, where the name is the property name and the argument is
        the property value. These values are sent to `~htmltools.css` to be formatted.

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
