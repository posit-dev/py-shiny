from __future__ import annotations

from typing import Iterable, Literal, Optional, cast

from htmltools import Tag, TagAttrs, TagAttrValue, TagChild, css, div

from .._deprecated import warn_deprecated
from .._docstring import add_example
from ..types import MISSING, MISSING_TYPE
from ._html_deps_shinyverse import components_dependencies
from ._tag import consolidate_attrs
from ._utils import is_01_scalar
from .css import CssUnit, as_css_unit
from .css._css_unit import isinstance_cssunit
from .fill import as_fill_item, as_fillable_container


@add_example()
def layout_column_wrap(
    *args: TagChild | TagAttrs,
    width: CssUnit | None | MISSING_TYPE = MISSING,
    fixed_width: bool = False,
    heights_equal: Literal["all", "row"] = "all",
    fill: bool = True,
    fillable: bool = True,
    height: Optional[CssUnit] = None,
    min_height: Optional[CssUnit] = None,
    max_height: Optional[CssUnit] = None,
    height_mobile: Optional[CssUnit] = None,
    gap: Optional[CssUnit] = None,
    class_: Optional[str] = None,
    **kwargs: TagAttrValue,
) -> Tag:
    # For
    # more explanation and illustrative examples, see
    # [here](https://rstudio.github.io/bslib/articles/cards.html#multiple-cards)
    """
    A grid-like, column-first layout

    Wraps a 1d sequence of UI elements into a 2d grid. The number of columns
    (and rows) in the grid depends on the column width and the size of the display.

    Parameters
    ----------
    *args
        Unnamed arguments should be UI elements (e.g.,
        :func:`~shiny.ui.card`). Named arguments become attributes on the
        containing :class:`~htmltools.Tag` element.
    width
        The desired width of each card. It can be one of the following:

        * A (unit-less) number between 0 and 1, specified as `1/num`, where `num`
          represents the number of desired columns.
        * A CSS length unit representing either the minimum (when `fixed_width=False`)
          or fixed width (`fixed_width=True`).
        * `None`, which allows power users to set the `grid-template-columns` CSS
          property manually, either via a `style` attribute or a CSS stylesheet.
        * If missing, a value of `200px` will be used.
    fixed_width
        When `width` is greater than 1 or is a CSS length unit, e.g., `"200px"`,
        `fixed_width` indicates whether that `width` value represents the absolute size
        of each column (`fixed_width=TRUE`) or the minimum size of a column
        (`fixed_width=FALSE`).

        When `fixed_width=FALSE`, new columns are added to a row when `width` space is
        available and columns will never exceed the container or viewport size.

        When `fixed_width=TRUE`, all columns will be exactly `width` wide, which may
        result in columns overflowing the parent container.
    heights_equal
        If `"all"` (the default), every card in every row of the grid will have the same
        height. If `"row"`, then every card in _each_ row of the grid will have the same
        height, but heights may vary between rows.
    fill
        Whether or not to allow the layout to grow/shrink to fit a fillable container
        with an opinionated height (e.g., :func:`~shiny.ui.page_fillable`).
    fillable
        Whether or not each element is wrapped in a fillable container.
    height,max_height,min_height
        A valid CSS unit (e.g., `height="200px"`). Use `min_height` and `max_height` in
        a filling layout to ensure that the layout container does not shrink below a
        `min_height` or grow beyond a `max_height`.
    height_mobile
        Any valid CSS unit to use for the height when on mobile devices (or narrow
        windows).
    gap
        Any valid CSS unit to use for the gap between columns.
    class_
        A CSS class to apply to the containing element.
    **kwargs
        Additional attributes to apply to the containing element.

    Returns
    -------
    :
        A :class:`~htmltools.Tag` element.

    See Also
    --------
    * :func:`~shiny.ui.layout_columns` for laying out elements into a responsive
      12-column grid.
    """
    attrs, children = consolidate_attrs(*args, class_=class_, **kwargs)

    # TODO-future; Remove this when we remove `shiny.experimental.ui.layout_column_wrap()`
    if isinstance(width, MISSING_TYPE):
        if len(children) > 0 and (
            children[0] is None or is_probably_a_css_unit(children[0])
        ):
            # Code changed from
            #   `layout_column_wrap(width, *args)`
            # to
            #   `layout_column_wrap(*args, width)`.
            # Provide deprecation warning

            # Assume an unnamed first argument that matches our expectations for
            # `width` is actually the width argument, with a warning
            warn_deprecated(
                "`layout_column_wrap(*args, width=)`'s `width` parameter must be named."
            )
            width = cast(CssUnit, children[0])
            children = children[1:]
        else:
            width = "200px"

    colspec: str | None = None
    if width is not None:
        if is_01_scalar(width) and width > 0.0:
            num_cols = 1.0 / width
            if not num_cols.is_integer():
                raise ValueError(
                    "Could not interpret `layout_column_wrap(width=)` argument"
                )
            colspec = " ".join(["1fr" for _ in range(int(num_cols))])
        else:
            width_css_unit = as_css_unit(width)
            if fixed_width:
                colspec = f"repeat(auto-fit, minmax({width_css_unit}, 1fr))"
            else:
                colspec = f"repeat(auto-fit, minmax(min({width_css_unit}, 100%), 1fr))"

    tag_style_css = {
        "grid-template-columns": colspec,
        "grid-auto-rows": "1fr" if (heights_equal == "all") else None,
        # Always provide the `height:auto` default so that the CSS variable
        # doesn't get inherited in a scenario like
        # layout_column_wrap(height=200, layout, layout_column_wrap(...))
        "--bslib-grid-height": as_css_unit("auto" if height is None else height),
        "--bslib-grid-height-mobile": as_css_unit(
            "auto" if height_mobile is None else height_mobile
        ),
        "gap": as_css_unit(gap),
        "min-height": as_css_unit(min_height),
        "max-height": as_css_unit(max_height),
    }

    tag = div(
        {
            "class": "bslib-grid bslib-mb-spacing",
            "style": css(**tag_style_css),
        },
        attrs,
        *wrap_all_in_gap_spaced_container(children, fillable),
        components_dependencies(),
    )
    if fill:
        tag = as_fill_item(tag)

    return tag


def is_probably_a_css_unit(x: TagChild) -> bool:
    if isinstance(x, str):
        return False
    if isinstance_cssunit(x):
        return True
    return False


def wrap_all_in_gap_spaced_container(
    children: Iterable[TagChild],
    fillable: bool = True,
    class_: Optional[str] = None,
) -> list[TagChild]:
    item_class = "bslib-gap-spacing"
    if class_ is not None:
        item_class = f"{item_class} {class_}"

    # Use a new list so that we don't mutate the original `children`
    wrapped_children: list[TagChild] = []
    for child_value in children:
        child = div({"class": item_class}, child_value)
        if fillable:
            child = as_fillable_container(child)
        wrapped_children.append(child)

    return wrapped_children
