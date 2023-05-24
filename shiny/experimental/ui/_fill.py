from __future__ import annotations

from typing import Optional, TypeVar

from htmltools import Tag, TagChild, Tagifiable

from ..._typing_extensions import Literal, Protocol, runtime_checkable
from ._css import CssUnit, validate_css_unit
from ._htmldeps import fill_dependency
from ._tag import tag_add_style, tag_prepend_class, tag_remove_class

__all__ = (
    "bind_fill_role",
    "as_fill_carrier",
    "as_fillable_container",
    "as_fill_item",
    "remove_all_fill",
    "is_fill_carrier",
    "is_fillable_container",
    "is_fill_item",
)

TagT = TypeVar("TagT", bound="Tag")


fill_item_class = "html-fill-item"
fill_container_class = "html-fill-container"

# TODO-future-approach: bind_fill_role() should return None?
# From @wch:
# > For functions like this, which modify the original object, I think the Pythonic way
# > of doing things is to return None, to make it clearer that the object is modified in
# > place.
# From @schloerke:
# > It makes for a very clunky interface. Keeping as is for now.
# > Should we copy the tag before modifying it? (If we are not doing that elsewhere, then I am hesitant to start here.)
# > If it is not utilizing `nonlocal foo`, then it should be returned. Even if it is altered in-place


# Allow tags to intelligently fill their container
#
# Create fill containers and items. If a fill item is a direct child of a fill
# container, and that container has an opinionated height, then the item is
# allowed to grow and shrink to its container's size.
#
# @param x a [tag()] object. Can also be a valid [tagQuery()] input if
#   `.cssSelector` is specified.
# @param ... currently unused.
# @param item whether or not to treat `x` as a fill item.
# @param container whether or not to treat `x` as a fill container. Note this
#   will the CSS `display` property on the tag to `flex`, which changes the way
#   it does layout of it's direct children. Thus, one should be careful not to
#   mark a tag as a fill container when it needs to rely on other `display`
#   behavior.
# @param overwrite whether or not to override previous calls to
#   `bindFillRole()` (e.g., to remove the item/container role from a tag).
# @param .cssSelector A character string containing a CSS selector for
#   targeting particular (inner) tag(s) of interest. For more details on what
#   selector(s) are supported, see [tagAppendAttributes()].
#
# @returns The original tag object (`x`) with additional attributes (and a
#   [htmlDependency()]).
#
# @export
# @examples
#
# tagz <- div(
#   id = "outer",
#   style = css(
#     height = "600px",
#     border = "3px red solid"
#   ),
#   div(
#     id = "inner",
#     style = css(
#       height = "400px",
#       border = "3px blue solid"
#     )
#   )
# )
#
# # Inner doesn't fill outer
# if (interactive()) browsable(tagz)
#
# tagz <- bindFillRole(tagz, container = TRUE)
# tagz <- bindFillRole(tagz, item = TRUE, .cssSelector = "#inner")
#
# # Inner does fill outer
# if (interactive()) browsable(tagz)
#
def add_role(
    tag: TagT, *, condition: bool | None, class_: str, overwrite: bool = False
) -> TagT:
    if condition is None:
        return tag

    # Remove the class if it already exists and we're going to add it,
    # or if we're requiring it to be removed
    if (condition and tag.has_class(class_)) or overwrite:
        tag = tag_remove_class(tag, class_)

    if condition:
        tag = tag_prepend_class(tag, class_)
        tag.append(fill_dependency())
    return tag


def bind_fill_role(
    tag: TagT,
    *,
    item: Optional[bool] = None,
    container: Optional[bool] = None,
    overwrite: bool = False,
) -> TagT:
    tag = add_role(
        tag,
        condition=item,
        class_=fill_item_class,
        overwrite=overwrite,
    )
    tag = add_role(
        tag,
        condition=container,
        class_=fill_container_class,
        overwrite=overwrite,
    )
    return tag


###########################################


# Test and/or coerce fill behavior
#
# @description Filling layouts in bslib are built on the foundation of fillable
# containers and fill items (fill carriers are both fillable and
# fill). This is why most bslib components (e.g., [card()], [card_body()],
# [layout_sidebar()]) possess both `fillable` and `fill` arguments (to control
# their fill behavior). However, sometimes it's useful to add, remove, and/or
# test fillable/fill properties on arbitrary [htmltools::tag()], which these
# functions are designed to do.
#
# @references <https://rstudio.github.io/bslib/articles/filling.html>
#
# @details Although `as_fill()`, `as_fillable()`, and `as_fill_carrier()`
# can work with non-tag objects that have a [as.tags] method (e.g., htmlwidgets),
# they return the "tagified" version of that object
#
# @return
#   * For `as_fill()`, `as_fillable()`, and `as_fill_carrier()`: the _tagified_
#     version `x`, with relevant tags modified to possess the relevant fill
#     properties.
#   * For `is_fill()`, `is_fillable()`, and `is_fill_carrier()`: a logical vector,
#     with length matching the number of top-level tags that possess the relevant
#     fill properties.
#
# @param x a [htmltools::tag()].
# @param ... currently ignored.
# @param min_height,max_height Any valid [CSS unit][htmltools::validateCssUnit]
#   (e.g., `150`).
# @param gap Any valid [CSS unit][htmltools::validateCssUnit].
# @param class A character vector of class names to add to the tag.
# @param style A character vector of CSS properties to add to the tag.
# @param css_selector A character string containing a CSS selector for
#   targeting particular (inner) tag(s) of interest. For more details on what
#   selector(s) are supported, see [tagAppendAttributes()].
# @export
def as_fill_carrier(
    tag: TagT,
    *,
    min_height: Optional[CssUnit] = None,
    max_height: Optional[CssUnit] = None,
    gap: Optional[CssUnit] = None,
    class_: Optional[str] = None,
    style: Optional[str] = None,
    # css_selector: Optional[str],
) -> TagT:
    tag = _add_class_and_styles(
        tag,
        class_=class_,
        style=style,
        min_height=min_height,
        max_height=max_height,
        gap=gap,
    )
    return bind_fill_role(
        tag,
        item=True,
        container=True,
        # css_selector=css_selector,
    )


# @rdname as_fill_carrier
# @export
def as_fillable_container(
    tag: TagT,
    *,
    min_height: Optional[CssUnit] = None,
    max_height: Optional[CssUnit] = None,
    gap: Optional[CssUnit] = None,
    class_: Optional[str] = None,
    style: Optional[str] = None,
    # css_selector: Optional[str] = None,
) -> TagT:
    tag = _add_class_and_styles(
        tag,
        class_=class_,
        style=style,
        min_height=validate_css_unit(min_height),
        max_height=validate_css_unit(max_height),
        gap=validate_css_unit(gap),
    )
    return bind_fill_role(
        tag,
        container=True,
        # css_selector=css_selector,
    )


# @rdname as_fill_carrier
# @export
def as_fill_item(
    tag: TagT,
    *,
    min_height: Optional[CssUnit] = None,
    max_height: Optional[CssUnit] = None,
    class_: Optional[str] = None,
    style: Optional[str] = None,
    # css_selector: Optional[str] = None,
) -> TagT:
    tag = _add_class_and_styles(
        tag,
        class_=class_,
        style=style,
        min_height=validate_css_unit(min_height),
        max_height=validate_css_unit(max_height),
    )
    return bind_fill_role(
        tag,
        item=True,
        # css_selector=css_selector,
    )


# @rdname as_fill_carrier
# @export
def remove_all_fill(tag: TagT) -> TagT:
    return bind_fill_role(
        tag,
        item=False,
        container=False,
        overwrite=True,
    )


# @rdname as_fill_carrier
# @export
def is_fill_carrier(x: Tag) -> bool:
    return is_fillable_container(x) and is_fill_item(x)


# @rdname as_fill_carrier
# @export
def is_fillable_container(x: TagChild | FillingLayout) -> bool:
    # TODO-future; Handle widgets
    # # won't actually work until (htmltools#334) gets fixed
    # renders_to_tag_class(x, fill_container_class, ".html-widget")

    return is_fill_layout(x, layout="fillable")


def is_fill_item(x: TagChild | FillingLayout) -> bool:
    # TODO-future; Handle widgets
    # # won't actually work until (htmltools#334) gets fixed
    # renders_to_tag_class(x, fill_item_class, ".html-widget")

    return is_fill_layout(x, layout="fill")


def is_fill_layout(
    x: TagChild | FillingLayout,
    layout: Literal["fill", "fillable"],
    recurse: bool = True,
) -> bool:
    if not isinstance(x, (Tag, Tagifiable, FillingLayout)):
        return False

    # x: Tag | FillingLayout | Tagifiable

    if layout == "fill":
        if isinstance(x, Tag):
            return x.has_class(fill_item_class)
        if isinstance(x, FillingLayout):
            return x.is_fill_item()

    elif layout == "fillable":
        if isinstance(x, Tag):
            return x.has_class(fill_container_class)
        if isinstance(x, FillingLayout):
            return x.is_fillable_container()

    # x: Tagifiable and not (Tag or FillingLayout)
    raise TypeError(
        f"`is_fill_layout(x=)` must be a `Tag` or implement the `FillingLayout` protocol methods TODO-barret expand on method names. Received object of type: `{type(x).__name__}`"
    )


@runtime_checkable
class FillingLayout(Protocol):
    def is_fill_item(self) -> bool:
        raise NotImplementedError()

    def is_fillable_container(self) -> bool:
        raise NotImplementedError()


def _add_class_and_styles(
    tag: TagT,
    *,
    class_: Optional[str] = None,
    style: Optional[str] = None,
    # css_selector: Optional[str] = None,
    **kwargs: Optional[CssUnit],
) -> TagT:
    if style or (len(kwargs) > 0):
        style_items: dict[str, CssUnit] = {}
        for k, v in kwargs.items():
            if v is not None:
                style_items[k] = validate_css_unit(v)
        tag = tag_add_style(
            tag,
            style=style,
            **style_items,
        )
    if class_:
        tag.add_class(class_)
    return tag
