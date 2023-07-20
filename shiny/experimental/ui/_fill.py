from __future__ import annotations

from typing import Literal, Optional, Protocol, TypeVar, runtime_checkable

from htmltools import Tag, TagChild, Tagifiable, css

from ._css_unit import CssUnit, as_css_unit
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


FILL_ITEM_CLASS = "html-fill-item"
FILL_CONTAINER_CLASS = "html-fill-container"

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
        whether or not to override previous filling layout calls (e.g., to remove the
        item/container role from a tag).

    Returns
    -------
    :
        The original :class:`~htmltools.Tag` object (`tag`) with additional attributes
        (and an :class:`~htmltools.HtmlDependency`).
    """
    tag = _add_role(
        tag,
        condition=item,
        class_=FILL_ITEM_CLASS,
        overwrite=overwrite,
    )
    tag = _add_role(
        tag,
        condition=container,
        class_=FILL_CONTAINER_CLASS,
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
    why most UI components (e.g., :func:`~shiny.experimental.ui.card`,
    :func:`~shiny.experimental.ui.card_body`,
    :func:`~shiny.experimental.ui.layout_sidebar`) possess both `fillable` and `fill`
    arguments (to control their fill behavior). However, sometimes it's useful to add,
    remove, and/or test fillable/fill properties on arbitrary :class:`~htmltools.Tag`,
    which these functions are designed to do.

    Parameters
    ----------
    tag
        a Tag object.
    min_height,max_height,gap
        Any valid CSS unit (e.g., `150`) to be applied to `tag`.

    Returns
    -------
    :
        The original :class:`~htmltools.Tag` object (`tag`) with additional attributes
        (and an :class:`~htmltools.HtmlDependency`).

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
    why most UI components (e.g., :func:`~shiny.experimental.ui.card`,
    :func:`~shiny.experimental.ui.card_body`,
    :func:`~shiny.experimental.ui.layout_sidebar`) possess both `fillable` and `fill`
    arguments (to control their fill behavior). However, sometimes it's useful to add,
    remove, and/or test fillable/fill properties on arbitrary :class:`~htmltools.Tag`,
    which these functions are designed to do.

    Parameters
    ----------
    tag
        a Tag object.
    min_height,max_height,gap
        Any valid CSS unit (e.g., `150`) to be applied to `tag`.

    Returns
    -------
    :
        The original :class:`~htmltools.Tag` object (`tag`) with additional attributes
        (and an :class:`~htmltools.HtmlDependency`).

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
    why most UI components (e.g., :func:`~shiny.experimental.ui.card`,
    :func:`~shiny.experimental.ui.card_body`,
    :func:`~shiny.experimental.ui.layout_sidebar`) possess both `fillable` and `fill`
    arguments (to control their fill behavior). However, sometimes it's useful to add,
    remove, and/or test fillable/fill properties on arbitrary :class:`~htmltools.Tag`,
    which these functions are designed to do.

    Parameters
    ----------
    tag
        a Tag object.
    min_height,max_height
        Any valid CSS unit (e.g., `150`) to be applied to `tag`.

    Returns
    -------
    :
        The original :class:`~htmltools.Tag` object (`tag`) with additional attributes
        (and an :class:`~htmltools.HtmlDependency`).

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
    why most UI components (e.g., :func:`~shiny.experimental.ui.card`,
    :func:`~shiny.experimental.ui.card_body`,
    :func:`~shiny.experimental.ui.layout_sidebar`) possess both `fillable` and `fill`
    arguments (to control their fill behavior). However, sometimes it's useful to add,
    remove, and/or test fillable/fill properties on arbitrary :class:`~htmltools.Tag`,
    which these functions are designed to do.

    Parameters
    ----------
    tag
        a Tag object.

    Returns
    -------
    :
        The original :class:`~htmltools.Tag` object with filling layout attributes
        removed.


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


def is_fill_carrier(tag: Tag | FillingLayout) -> bool:
    """
    Test a tag for being a fill carrier

    Filling layouts are built on the foundation of _fillable containers_ and _fill
    items_ (_fill carriers_ are both _fillable containers_ and _fill items_). This is
    why most UI components (e.g., :func:`~shiny.experimental.ui.card`,
    :func:`~shiny.experimental.ui.card_body`,
    :func:`~shiny.experimental.ui.layout_sidebar`) possess both `fillable` and `fill`
    arguments (to control their fill behavior). However, sometimes it's useful to add,
    remove, and/or test fillable/fill properties on arbitrary :class:`~htmltools.Tag`,
    which these functions are designed to do.

    Parameters
    ----------
    tag
        a Tag object.

    Returns
    -------
    :
        Whether or not `tag` is a fill carrier.

    See Also
    --------
    * :func:`~shiny.experimental.ui.as_fill_carrier`
    * :func:`~shiny.experimental.ui.as_fill_item`
    * :func:`~shiny.experimental.ui.as_fillable_container`
    * :func:`~shiny.experimental.ui.remove_all_fill`
    * :func:`~shiny.experimental.ui.is_fill_item`
    * :func:`~shiny.experimental.ui.is_fillable_container`
    """
    return is_fillable_container(tag) and is_fill_item(tag)


def is_fillable_container(tag: TagChild | FillingLayout) -> bool:
    """
    Test a tag for being a fillable container

    Filling layouts are built on the foundation of _fillable containers_ and _fill
    items_ (_fill carriers_ are both _fillable containers_ and _fill items_). This is
    why most UI components (e.g., :func:`~shiny.experimental.ui.card`,
    :func:`~shiny.experimental.ui.card_body`,
    :func:`~shiny.experimental.ui.layout_sidebar`) possess both `fillable` and `fill`
    arguments (to control their fill behavior). However, sometimes it's useful to add,
    remove, and/or test fillable/fill properties on arbitrary :class:`~htmltools.Tag`,
    which these functions are designed to do.

    Parameters
    ----------
    tag
        a Tag object.

    Returns
    -------
    :
        Whether or not `tag` is a fillable container.


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
    # renders_to_tag_class(x, FILL_CONTAINER_CLASS, ".html-widget")

    return _is_fill_layout(tag, layout="fillable")


def is_fill_item(tag: TagChild | FillingLayout) -> bool:
    """
    Test a tag for being a fill item

    Filling layouts are built on the foundation of _fillable containers_ and _fill
    items_ (_fill carriers_ are both _fillable containers_ and _fill items_). This is
    why most UI components (e.g., :func:`~shiny.experimental.ui.card`,
    :func:`~shiny.experimental.ui.card_body`,
    :func:`~shiny.experimental.ui.layout_sidebar`) possess both `fillable` and `fill`
    arguments (to control their fill behavior). However, sometimes it's useful to add,
    remove, and/or test fillable/fill properties on arbitrary :class:`~htmltools.Tag`,
    which these functions are designed to do.

    Parameters
    ----------
    tag
        a Tag object.

    Returns
    -------
    :
        Whether or not `tag` is a fill item.

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
    # renders_to_tag_class(x, FILL_ITEM_CLASS, ".html-widget")

    return _is_fill_layout(tag, layout="fill")


def _is_fill_layout(
    tag: TagChild | FillingLayout,
    layout: Literal["fill", "fillable"],
    # recurse: bool = True,
) -> bool:
    if not isinstance(tag, (Tag, Tagifiable, FillingLayout)):
        return False

    # tag: Tag | FillingLayout | Tagifiable

    if layout == "fill":
        if isinstance(tag, Tag):
            return tag.has_class(FILL_ITEM_CLASS)
        if isinstance(tag, FillingLayout):
            return tag.is_fill_item()

    elif layout == "fillable":
        if isinstance(tag, Tag):
            return tag.has_class(FILL_CONTAINER_CLASS)
        if isinstance(tag, FillingLayout):
            return tag.is_fillable_container()

    # tag: Tagifiable and not (Tag or FillingLayout)
    raise TypeError(
        f"`_is_fill_layout(tag=)` must be a `Tag` or implement the `FillingLayout` protocol methods. Received object of type: `{type(tag).__name__}`"
    )


T = TypeVar("T")


@runtime_checkable
class FillingLayout(Protocol):
    """
    Generic protocol for filling layouts objects
    """

    def add_class(
        self: T,
        class_: str,
        # *,
        # # Currently Unused
        # css_selector: Optional[str] = None,
        # Currently Unused
        **kwargs: object,
    ) -> T:
        """
        Generic method to handle adding a CSS `class` to an object

        Parameters
        ----------
        class_
            A character vector of class names to add to the tag.
        **kwargs
            Possible future arguments

        Returns
        -------
        :
            The updated object.
        """
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
        """
        Generic method to handle adding a CSS `style` to an object

        Parameters
        ----------
        style
            A character vector of CSS properties to add to the tag.
        **kwargs
            Possible future arguments

        Returns
        -------
        :
            The updated object.
        """
        ...

    def is_fill_item(self) -> bool:
        """
        Generic method to handle testing if an object is a fill item

        Returns
        -------
        :
            Whether or not the object is a fill item
        """
        ...

    def is_fillable_container(self) -> bool:
        """
        Generic method to handle testing if an object is a fillable container

        Returns
        -------
        :
            Whether or not the object is a fillable container
        """
        ...

    def as_fill_item(
        self: T,
    ) -> T:
        """
        Generic method to handle coercing an object to a fill item

        Returns
        -------
        :
            The updated object.
        """
        ...

    def as_fillable_container(
        self: T,
    ) -> T:
        """
        Generic method to handle coercing an object to a fillable container

        Returns
        -------
        :
            The updated object.
        """
        ...

    def remove_all_fill(
        self: T,
    ) -> T:
        """
        Generic method to handle removing all fill properties from an object

        Returns
        -------
        :
            The updated object.
        """
        ...


def _style_units_to_str(**kwargs: CssUnit | None) -> str | None:
    style_items: dict[str, CssUnit] = {}
    for k, v in kwargs.items():
        if v is not None:
            style_items[k] = as_css_unit(v)

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
