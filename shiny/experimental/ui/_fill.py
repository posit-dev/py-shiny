from __future__ import annotations

from typing import Optional, TypeVar

from htmltools import Tag, TagChild, Tagifiable

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


# TODO-future-approach:
# From @wch:
# > For functions like this, which modify the original object, I think the Pythonic way
# > of doing things is to return None, to make it clearer that the object is modified in
# > place.
# From @schloerke:
# > It makes for a very clunky interface. Keeping as is for now.
# > Should we copy the tag before modifying it? (If we are not doing that elsewhere, then I am hesitant to start here.)


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
def bind_fill_role(
    tag: TagT,
    *,
    item: Optional[bool] = None,
    container: Optional[bool] = None,
    overwrite: bool = False,
) -> TagT:
    if item is not None:
        if item:
            tag_prepend_class(tag, "html-fill-item")
        else:
            if overwrite:
                tag_remove_class(tag, "html-fill-item")

    if container is not None:
        if container:
            tag_prepend_class(tag, "html-fill-container")
            tag.append(fill_dependency())
        else:
            if overwrite:
                tag_remove_class(tag, "html-fill-container")

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
    x: TagT,
    *,
    min_height: Optional[CssUnit] = None,
    max_height: Optional[CssUnit],
    gap: Optional[CssUnit] = None,
    class_: Optional[str] = None,
    style: Optional[str] = None,
    # css_selector: Optional[str],
) -> TagT:
    x = as_fillable_container(
        x,
        min_height=min_height,
        max_height=max_height,
        gap=gap,
        class_=class_,
        style=style,
        # css_selector=css_selector,
    )
    return bind_fill_role(
        x,
        item=True,
        # css_selector=css_selector,
    )


# @rdname as_fill_carrier
# @export
def as_fillable_container(
    x: TagT,
    *,
    min_height: Optional[CssUnit] = None,
    max_height: Optional[CssUnit] = None,
    gap: Optional[CssUnit] = None,
    class_: Optional[str] = None,
    style: Optional[str] = None,
    # css_selector: Optional[str] = None,
) -> TagT:
    x = bind_fill_role(
        x,
        container=True,
        # css_selector=css_selector,
    )

    x = tag_add_style(
        x,
        style=style,
        min_height=validate_css_unit(min_height),
        max_height=validate_css_unit(max_height),
        gap=validate_css_unit(gap),
    )
    if class_:
        x.add_class(class_)

    return x


# @rdname as_fill_carrier
# @export
def as_fill_item(
    x: TagT,
    *,
    min_height: Optional[CssUnit] = None,
    max_height: Optional[CssUnit] = None,
    class_: Optional[str] = None,
    style: Optional[str] = None,
    # css_selector: Optional[str] = None,
) -> TagT:
    x = bind_fill_role(
        x,
        item=True,
        # css_selector=css_selector,
    )

    x = tag_add_style(
        x,
        style=style,
        min_height=validate_css_unit(min_height),
        max_height=validate_css_unit(max_height),
    )
    if class_:
        x.add_class(class_)
    return x


# @rdname as_fill_carrier
# @export
def remove_all_fill(x: TagT) -> TagT:
    return bind_fill_role(
        x,
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
def is_fillable_container(x: TagChild) -> bool:
    # TODO-future; Handle widgets
    # # won't actually work until (htmltools#334) gets fixed
    # renders_to_tag_class(x, "html-fill-container", ".html-widget")

    return renders_to_tag_class(x, "html-fill-container")


def is_fill_item(x: TagChild) -> bool:
    # TODO-future; Handle widgets
    # # won't actually work until (htmltools#334) gets fixed
    # renders_to_tag_class(x, "html-fill-item", ".html-widget")

    return renders_to_tag_class(x, "html-fill-item")


def renders_to_tag_class(
    x: TagChild,
    class_: str,
    #  selector: Optional[str]= None,
) -> bool:
    # if isinstance(x, TagFunction):
    #     x = x()

    if isinstance(x, Tagifiable):
        x = x.tagify()

    if not isinstance(x, Tag):
        # TODO: should this be an error?
        return False
    return x.has_class(class_)
