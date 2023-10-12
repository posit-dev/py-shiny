from __future__ import annotations

from typing import Optional

from htmltools import Tag, TagAttrs, TagAttrValue, TagChild

from .._docstring import add_example
from .css_unit._css_unit import CssUnit

# TODO-barret; Remove experimental from docs
# TODO-barret; API-examples

__all__ = ("value_box",)

# When future value_box changes are made to `showcase_layout`, `theme_color`... remove experimental method.


@add_example()
def value_box(
    title: TagChild,
    value: TagChild,
    *args: TagChild | TagAttrs,
    showcase: Optional[TagChild] = None,
    # showcase_layout: Callable[[TagChild, Tag], CardItem] | None = None,
    full_screen: bool = False,
    # theme_color: Optional[str] = "primary",
    height: Optional[CssUnit] = None,
    max_height: Optional[CssUnit] = None,
    fill: bool = True,
    class_: Optional[str] = None,
    **kwargs: TagAttrValue,
) -> Tag:
    """
    Value box

    An opinionated (:func:`~shiny.ui.card`-powered) box, designed for
    displaying a `value` and `title`. Optionally, a `showcase` can provide for context
    for what the `value` represents (for example, it could hold an icon, or even a
    :func:`~shiny.ui.output_plot`).

    Parameters
    ----------
    title,value
        A string, number, or :class:`~htmltools.Tag` child to display as
        the title or value of the value box. The `title` appears above the `value`.
    *args
        Unnamed arguments may be any :class:`~htmltools.Tag` children to display below
        `value`. Named arguments are passed to :func:`~shiny.ui.card` as
        element attributes.
    showcase
        A :class:`~htmltools.Tag` child to showcase (e.g., an icon, a
        :func:`~shiny.ui.output_plot`, etc).
    height,max_height
        Any valid CSS unit (e.g., `height="200px"`). Doesn't apply when a card is made
        `full_screen`.
    fill
        Whether to allow the value box to grow/shrink to fit a fillable container with
        an opinionated height (e.g., :func:`~shiny.ui.page_fillable`).
    class_
        Utility classes for customizing the appearance of the summary card. Use `bg-*`
        and `text-*` classes (e.g, `"bg-danger"` and `"text-light"`) to customize the
        background/foreground colors.
    **kwargs
        Additional attributes to pass to :func:`~shiny.ui.card`.

    Returns
    -------
    :
        A :func:`~shiny.ui.card`

    See Also
    --------
    * :func:`~shiny.ui.card`
    """
    # showcase_layout
    #     Either :func:`~shiny.experimental.ui.showcase_left_center` or
    #     :func:`~shiny.experimental.ui.showcase_top_right`.
    # theme_color
    #     A theme color to use for the background color. Should match a name in the
    #     Bootstrap Sass variable `$theme-colors` (e.g., `"secondary"`, `"success"`,
    #     `"danger"`, etc).
    # height,max_height
    #     Any valid CSS unit (e.g., `height="200px"`). Doesn't apply when a card is made
    #     `full_screen` (in this case, consider setting a `height` in
    #     :func:`~shiny.experimental.ui.card_body`).

    # Move down to avoid circular import
    from ..experimental.ui._valuebox import value_box as x_value_box

    return x_value_box(
        title,
        value,
        *args,
        showcase=showcase,
        # showcase_layout=showcase_layout,
        full_screen=full_screen,
        # theme_color=theme_color,
        height=height,
        max_height=max_height,
        fill=fill,
        class_=class_,
        **kwargs,
    )
