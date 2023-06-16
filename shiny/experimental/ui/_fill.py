from __future__ import annotations

from typing import Optional, TypeVar

from htmltools import Tag, TagChild, Tagifiable, css

from ..._typing_extensions import Literal, Protocol, runtime_checkable
from ._css_unit import CssUnit, validate_css_unit
from ._htmldeps import fill_dependency
from ._tag import tag_add_style, tag_prepend_class, tag_remove_class

"""
examples:
    - [ ] remove_all_fill
    - [ ] is_fill_carrier
    - [ ] is_fillable_container
    - [ ] is_fill_item
    - [ ] FillingLayout
"""


__all__ = (
    "bind_fill_role",
    "as_fill_carrier",
    "as_fillable_container",
    "as_fill_item",
    "remove_all_fill",
    "is_fill_carrier",
    "is_fillable_container",
    "is_fill_item",
    "FillingLayout",
)

TagFillingLayoutT = TypeVar("TagFillingLayoutT", bound="Tag | FillingLayout")
TagT = TypeVar("TagT", bound="Tag")


fill_item_class = "html-fill-item"
fill_container_class = "html-fill-container"

# We're currently not supporting the div(as_fillable_container()) API, in order to keep
# the function easier to understand. If we do implement something like that, we should
# use a different name, because the function is conceptually different, and it also is
# behaviorally different (it doesn't include the HTML dependency.)

# TODO-future-approach: bind_fill_role() should return None?
# From @wch:
# > For functions like this, which modify the original object, I think the Pythonic way
# > of doing things is to return None, to make it clearer that the object is modified in
# > place.
# From @schloerke:
# > It makes for a very clunky interface. Keeping as is for now.
# > Should we copy the tag before modifying it? (If we are not doing that elsewhere, then I am hesitant to start here.)
# > If it is not utilizing `nonlocal foo`, then it should be returned. Even if it is altered in-place


def _add_role(
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
    """
    Allow tags to intelligently fill their container

    Create fill containers and items. If a fill item is a direct child of a fill
    container, and that container has an opinionated height, then the item is allowed to
    grow and shrink to its container's size.

    Parameters
    ----------
    tag
        a T object.
    item
        whether or not to treat `tag` as a fill item.
    container
        whether or not to treat `x` as a fill container. Note, this will set the CSS
        `display` property on the tag to `flex` which can change how its direct children
        are rendered. Thus, one should be careful not to mark a tag as a fill container
        when it needs to rely on other `display` behavior.
    overwrite
        whether or not to override previous calls to
        `bind_fill_role()` (e.g., to remove the item/container role from a tag).

    Returns
    -------
    :
        The original tag object (`tag`) with additional attributes (and a
        `~shiny.ui.HtmlDependency`).
    """
    tag = _add_role(
        tag,
        condition=item,
        class_=fill_item_class,
        overwrite=overwrite,
    )
    tag = _add_role(
        tag,
        condition=container,
        class_=fill_container_class,
        overwrite=overwrite,
    )
    return tag


###########################################


# Test and/or coerce fill behavior

# TODO-future; When `css_selector` can be implemented, the three parameters below should be added where appropriate
# @param class A character vector of class names to add to the tag.
# @param style A character vector of CSS properties to add to the tag.
# @param css_selector A character string containing a CSS selector for
#   targeting particular (inner) tag(s) of interest. For more details on what
#   selector(s) are supported, see [tagAppendAttributes()].


def as_fill_carrier(
    tag: TagFillingLayoutT,
    *,
    min_height: Optional[CssUnit] = None,
    max_height: Optional[CssUnit] = None,
    gap: Optional[CssUnit] = None,
    # class_: Optional[str] = None,
    # style: Optional[str] = None,
    # css_selector: Optional[str],
) -> TagFillingLayoutT:
    """
    Make a tag a fill carrier

    Filling layouts are built on the foundation of _fillable containers_ and _fill
    items_ (_fill carriers_ are both _fillable containers_ and _fill items_). This is
    why most UI components (e.g., :func:`~shiny.experiemental.ui.card`,
    :func:`~shiny.experiemental.ui.card_body()`,
    :func:`~shiny.experiemental.ui.layout_sidebar()`) possess both `fillable` and `fill`
    arguments (to control their fill behavior). However, sometimes it's useful to add,
    remove, and/or test fillable/fill properties on arbitrary `~htmltools.Tag`, which
    these functions are designed to do.

    Parameters
    ----------
    tag
        a Tag object.
    min_height,max_height,gap
        Any valid CSS unit (e.g., `150`) to be applied to `tag`.

    See Also
    --------
    * :func:`~shiny.experimental.ui.as_fill_item`
    * :func:`~shiny.experimental.ui.as_fillable_container`
    * :func:`~shiny.experimental.ui.remove_all_fill`
    * :func:`~shiny.experimental.ui.is_fill_carrier`
    * :func:`~shiny.experimental.ui.is_fill_item`
    * :func:`~shiny.experimental.ui.is_fillable_container`
    """
    return _add_filling_attrs(
        tag,
        item=True,
        container=True,
        min_height=min_height,
        max_height=max_height,
        gap=gap,
    )


def as_fillable_container(
    tag: TagFillingLayoutT,
    *,
    min_height: Optional[CssUnit] = None,
    max_height: Optional[CssUnit] = None,
    gap: Optional[CssUnit] = None,
    # class_: Optional[str] = None,
    # style: Optional[str] = None,
    # css_selector: Optional[str] = None,
) -> TagFillingLayoutT:
    """
    Coerce a tag to be a fillable container

    Filling layouts are built on the foundation of _fillable containers_ and _fill
    items_ (_fill carriers_ are both _fillable containers_ and _fill items_). This is
    why most UI components (e.g., :func:`~shiny.experiemental.ui.card`,
    :func:`~shiny.experiemental.ui.card_body()`,
    :func:`~shiny.experiemental.ui.layout_sidebar()`) possess both `fillable` and `fill`
    arguments (to control their fill behavior). However, sometimes it's useful to add,
    remove, and/or test fillable/fill properties on arbitrary `~htmltools.Tag`, which
    these functions are designed to do.

    Parameters
    ----------
    tag
        a Tag object.
    min_height,max_height,gap
        Any valid CSS unit (e.g., `150`) to be applied to `tag`.


    See Also
    --------
    * :func:`~shiny.experimental.ui.as_fill_carrier`
    * :func:`~shiny.experimental.ui.as_fill_item`
    * :func:`~shiny.experimental.ui.as_fillable_container`
    * :func:`~shiny.experimental.ui.remove_all_fill`
    * :func:`~shiny.experimental.ui.is_fill_carrier`
    * :func:`~shiny.experimental.ui.is_fill_item`
    * :func:`~shiny.experimental.ui.is_fillable_container`
    """
    return _add_filling_attrs(
        tag,
        container=True,
        min_height=min_height,
        max_height=max_height,
        gap=gap,
    )


def as_fill_item(
    tag: TagFillingLayoutT,
    *,
    min_height: Optional[CssUnit] = None,
    max_height: Optional[CssUnit] = None,
    # class_: Optional[str] = None,
    # style: Optional[str] = None,
    # css_selector: Optional[str] = None,
) -> TagFillingLayoutT:
    """
    Coerce a tag to a fill item

    Filling layouts are built on the foundation of _fillable containers_ and _fill
    items_ (_fill carriers_ are both _fillable containers_ and _fill items_). This is
    why most UI components (e.g., :func:`~shiny.experiemental.ui.card`,
    :func:`~shiny.experiemental.ui.card_body()`,
    :func:`~shiny.experiemental.ui.layout_sidebar()`) possess both `fillable` and `fill`
    arguments (to control their fill behavior). However, sometimes it's useful to add,
    remove, and/or test fillable/fill properties on arbitrary `~htmltools.Tag`, which
    these functions are designed to do.

    Parameters
    ----------
    tag
        a Tag object.
    min_height,max_height
        Any valid CSS unit (e.g., `150`) to be applied to `tag`.


    See Also
    --------
    * :func:`~shiny.experimental.ui.as_fill_carrier`
    * :func:`~shiny.experimental.ui.as_fillable_container`
    * :func:`~shiny.experimental.ui.remove_all_fill`
    * :func:`~shiny.experimental.ui.is_fill_carrier`
    * :func:`~shiny.experimental.ui.is_fill_item`
    * :func:`~shiny.experimental.ui.is_fillable_container`
    """
    return _add_filling_attrs(
        tag,
        item=True,
        min_height=min_height,
        max_height=max_height,
    )


def remove_all_fill(tag: TagFillingLayoutT) -> TagFillingLayoutT:
    """
    Remove any filling layouts from a tag

    Filling layouts are built on the foundation of _fillable containers_ and _fill
    items_ (_fill carriers_ are both _fillable containers_ and _fill items_). This is
    why most UI components (e.g., :func:`~shiny.experiemental.ui.card`,
    :func:`~shiny.experiemental.ui.card_body()`,
    :func:`~shiny.experiemental.ui.layout_sidebar()`) possess both `fillable` and `fill`
    arguments (to control their fill behavior). However, sometimes it's useful to add,
    remove, and/or test fillable/fill properties on arbitrary `~htmltools.Tag`, which
    these functions are designed to do.

    Parameters
    ----------
    tag
        a Tag object.


    See Also
    --------
    * :func:`~shiny.experimental.ui.as_fill_carrier`
    * :func:`~shiny.experimental.ui.as_fill_item`
    * :func:`~shiny.experimental.ui.as_fillable_container`
    * :func:`~shiny.experimental.ui.is_fill_carrier`
    * :func:`~shiny.experimental.ui.is_fill_item`
    * :func:`~shiny.experimental.ui.is_fillable_container`
    """

    if isinstance(tag, FillingLayout):
        return tag.remove_all_fill()

    return bind_fill_role(
        tag,
        item=False,
        container=False,
        overwrite=True,
    )


def is_fill_carrier(x: Tag | FillingLayout) -> bool:
    """
    Test a tag for being a fill carrier

    Filling layouts are built on the foundation of _fillable containers_ and _fill
    items_ (_fill carriers_ are both _fillable containers_ and _fill items_). This is
    why most UI components (e.g., :func:`~shiny.experiemental.ui.card`,
    :func:`~shiny.experiemental.ui.card_body()`,
    :func:`~shiny.experiemental.ui.layout_sidebar()`) possess both `fillable` and `fill`
    arguments (to control their fill behavior). However, sometimes it's useful to add,
    remove, and/or test fillable/fill properties on arbitrary `~htmltools.Tag`, which
    these functions are designed to do.

    Parameters
    ----------
    tag
        a Tag object.


    See Also
    --------
    * :func:`~shiny.experimental.ui.as_fill_carrier`
    * :func:`~shiny.experimental.ui.as_fill_item`
    * :func:`~shiny.experimental.ui.as_fillable_container`
    * :func:`~shiny.experimental.ui.remove_all_fill`
    * :func:`~shiny.experimental.ui.is_fill_item`
    * :func:`~shiny.experimental.ui.is_fillable_container`
    """
    return is_fillable_container(x) and is_fill_item(x)


def is_fillable_container(x: TagChild | FillingLayout) -> bool:
    """
    Test a tag for being a fillable container

    Filling layouts are built on the foundation of _fillable containers_ and _fill
    items_ (_fill carriers_ are both _fillable containers_ and _fill items_). This is
    why most UI components (e.g., :func:`~shiny.experiemental.ui.card`,
    :func:`~shiny.experiemental.ui.card_body()`,
    :func:`~shiny.experiemental.ui.layout_sidebar()`) possess both `fillable` and `fill`
    arguments (to control their fill behavior). However, sometimes it's useful to add,
    remove, and/or test fillable/fill properties on arbitrary `~htmltools.Tag`, which
    these functions are designed to do.

    Parameters
    ----------
    tag
        a Tag object.
    min_height,max_height,gap
        Any valid CSS unit (e.g., `150`) to be applied to `tag`.


    See Also
    --------
    * :func:`~shiny.experimental.ui.as_fill_carrier`
    * :func:`~shiny.experimental.ui.as_fill_item`
    * :func:`~shiny.experimental.ui.as_fillable_container`
    * :func:`~shiny.experimental.ui.remove_all_fill`
    * :func:`~shiny.experimental.ui.is_fill_item`
    * :func:`~shiny.experimental.ui.is_fillable_container`
    """
    # TODO-future; Handle widgets
    # # won't actually work until (htmltools#334) gets fixed
    # renders_to_tag_class(x, fill_container_class, ".html-widget")

    return _is_fill_layout(x, layout="fillable")


def is_fill_item(x: TagChild | FillingLayout) -> bool:
    """
    Test a tag for being a fill item

    Filling layouts are built on the foundation of _fillable containers_ and _fill
    items_ (_fill carriers_ are both _fillable containers_ and _fill items_). This is
    why most UI components (e.g., :func:`~shiny.experiemental.ui.card`,
    :func:`~shiny.experiemental.ui.card_body()`,
    :func:`~shiny.experiemental.ui.layout_sidebar()`) possess both `fillable` and `fill`
    arguments (to control their fill behavior). However, sometimes it's useful to add,
    remove, and/or test fillable/fill properties on arbitrary `~htmltools.Tag`, which
    these functions are designed to do.

    Parameters
    ----------
    tag
        a Tag object.


    See Also
    --------
    * :func:`~shiny.experimental.ui.as_fill_carrier`
    * :func:`~shiny.experimental.ui.as_fill_item`
    * :func:`~shiny.experimental.ui.as_fillable_container`
    * :func:`~shiny.experimental.ui.remove_all_fill`
    * :func:`~shiny.experimental.ui.is_fill_carrier`
    * :func:`~shiny.experimental.ui.is_fillable_container`
    """
    # TODO-future; Handle widgets
    # # won't actually work until (htmltools#334) gets fixed
    # renders_to_tag_class(x, fill_item_class, ".html-widget")

    return _is_fill_layout(x, layout="fill")


def _is_fill_layout(
    x: TagChild | FillingLayout,
    layout: Literal["fill", "fillable"],
    # recurse: bool = True,
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
        f"`_is_fill_layout(x=)` must be a `Tag` or implement the `FillingLayout` protocol methods TODO-barret expand on method names. Received object of type: `{type(x).__name__}`"
    )


T = TypeVar("T")


@runtime_checkable
class FillingLayout(Protocol):
    def add_class(
        self: T,
        class_: str,
        # *,
        # # Currently Unused
        # css_selector: Optional[str] = None,
        # Currently Unused
        **kwargs: object,
    ) -> T:
        ...

    def add_style(
        self: T,
        style: str,
        # *,
        # # Currently Unused
        # css_selector: Optional[str] = None,
        # Currently Unused
        **kwargs: object,
    ) -> T:
        ...

    def is_fill_item(self) -> bool:
        ...

    def is_fillable_container(self) -> bool:
        ...

    def as_fill_item(
        self: T,
    ) -> T:
        ...

    def as_fillable_container(
        self: T,
    ) -> T:
        ...

    def remove_all_fill(
        self: T,
    ) -> T:
        ...


def _style_units_to_str(**kwargs: CssUnit | None) -> str | None:
    style_items: dict[str, CssUnit] = {}
    for k, v in kwargs.items():
        if v is not None:
            style_items[k] = validate_css_unit(v)

    return css(**style_items)


def _add_filling_attrs(
    tag: TagFillingLayoutT,
    item: Optional[bool] = None,
    container: Optional[bool] = None,
    **kwargs: CssUnit | None,
) -> TagFillingLayoutT:
    new_style = _style_units_to_str(**kwargs)

    if isinstance(tag, FillingLayout):
        if new_style:
            tag.add_style(new_style)
        if item:
            tag.as_fill_item()
        if container:
            tag.as_fillable_container()
        return tag

    # Tag
    tag = tag_add_style(tag, new_style)
    return bind_fill_role(tag, item=item, container=container)
