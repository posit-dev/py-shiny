from __future__ import annotations

from enum import Enum
from typing import Dict, Iterable, Literal, Optional, Tuple, TypeVar, Union, cast
from warnings import warn

from htmltools import Tag, TagAttrs, TagAttrValue, TagChild, css

from .._docstring import add_example
from ._html_deps_shinyverse import components_dependencies
from ._layout import wrap_all_in_gap_spaced_container
from ._tag import consolidate_attrs
from .css import CssUnit, as_css_unit
from .fill import as_fill_item

T = TypeVar("T")


Breakpoint = Literal["xs", "sm", "md", "lg", "xl", "xxl"]
"""
References
----------
* [Available Bootstrap breakpoints](https://getbootstrap.com/docs/5.3/layout/breakpoints/#available-breakpoints)
"""


breakpoints: Tuple[Breakpoint, ...] = ("xs", "sm", "md", "lg", "xl", "xxl")


BreakpointsSoft = Dict[Breakpoint, Union[Iterable[T], T, None]]
BreakpointsOptional = Dict[Breakpoint, Union[Iterable[T], None]]
BreakpointsComplete = Dict[Breakpoint, Iterable[T]]
BreakpointsUser = Union[BreakpointsSoft[T], Iterable[T], T, None]


@add_example()
def layout_columns(
    *args: TagChild | TagAttrs,
    col_widths: BreakpointsUser[int] = None,
    row_heights: BreakpointsUser[CssUnit] = None,
    fill: bool = True,
    fillable: bool = True,
    gap: Optional[CssUnit] = None,
    class_: Optional[str] = None,
    height: Optional[CssUnit] = None,
    **kwargs: TagAttrValue,
) -> Tag:
    """
    Create responsive, column-based grid layouts, based on a 12-column grid.

    Parameters
    ----------
    *args
        Child elements or attributes to be added to the layout.
    col_widths
        The widths of the columns, possibly at different breakpoints. Can be one of the
        following:

        * `None` (the default): Automatically determines a sensible number of columns
          based on the number of children given to the layout.
        * A list or tuple of integers between 1 and 12, where each element represents
          the number of columns for the relevant UI element. Column widths are recycled
          to extend the values in `col_widths` to match the actual number of items in
          the layout, and children are wrapped onto the next row when a row exceeds 12
          column units. For example, `col_widths=(4, 8, 12)` allocates 4 columns to the
          first element, 8 columns to the second element, and 12 columns to the third
          element (which wraps to the next row). Negative values are also allowed, and
          are treated as empty columns. For example, `col_widths=(-2, 8, -2)` would
          allocate 8 columns to an element (with 2 empty columns on either side).
        * A dictionary of column widths at different breakpoints. The keys should be
          one of `"xs"`, `"sm"`, `"md"`, `"lg"`, `"xl"`, or `"xxl"`, and the values are
          either of the above. For example, `col_widths={"sm": (3, 3, 6), "lg": (4)}`.
    row_heights
        The heights of the rows, possibly at different breakpoints. Can be one of the
        following:

        * A numeric vector, where each value represents the
          [fractional unit](https://css-tricks.com/introduction-fr-css-unit/)
          (`fr`) height of the relevant row. If there are more rows than values
          provided, the pattern will be repeated. For example, `row_heights=(1, 2)`
          allows even rows to take up twice as much space as odd rows.
        * A list of numeric or CSS length units, where each value represents the height
          of the relevant row. If more rows are needed than values provided, the pattern
          will repeat. For example, `row_heights=["auto", 1]` allows the height of odd
          rows to be driven my it's contents and even rows to be
          [`1fr`](https://css-tricks.com/introduction-fr-css-unit/).
        * A single string containing CSS length units. In this case, the value is
          supplied directly to `grid-auto-rows`.
        * A dictionary of row heights at different breakpoints, where each key is a
          breakpoint name (one of `"xs"`, `"sm"`, `"md"`, `"lg"`, `"xl"`, or `"xxl"`)
          and where the values may be any of the above options.
    fill
        Whether or not to allow the layout to grow/shrink to fit a fillable container
        with an opinionated height (e.g., :func:`~shiny.ui.page_fillable`).
    fillable
        Whether or not each element is wrapped in a fillable container.
    gap
        Any valid CSS unit to use for the gap between columns.
    class_
        CSS class(es) to apply to the containing element.
    height
        Any valid CSS unit to use for the height.
    **kwargs
        Additional attributes to apply to the containing element.

    Returns
    -------
    :
        An :class:`~htmltools.Tag` element.

    See Also
    --------
    * :func:`~shiny.ui.layout_column_wrap` for laying out elements into a uniform grid.

    Reference
    --------
    * [Bootstrap CSS Grid](https://getbootstrap.com/docs/5.3/layout/grid/)
    * [Bootstrap Breakpoints](https://getbootstrap.com/docs/5.3/layout/breakpoints/)
    """
    attrs, children = consolidate_attrs(*args, class_=class_, **kwargs)

    col_widths_spec = as_col_spec(col_widths, len(children))

    # Create the bslib-layout-columns element
    tag = Tag(
        "bslib-layout-columns",
        {
            "class": "bslib-grid grid bslib-mb-spacing",
            "style": css(
                gap=as_css_unit(gap),
                height=as_css_unit(height),
            ),
        },
        col_widths_attrs(col_widths_spec),
        attrs,
        row_heights_attrs(row_heights),
        *wrap_all_in_gap_spaced_container(children, fillable, "bslib-grid-item"),
        components_dependencies(),
    )

    # Apply fill to the outer layout (fillable is applied to the children)
    if fill:
        tag = as_fill_item(tag)

    return tag


def as_col_spec(
    col_widths: BreakpointsUser[int],
    n_kids: int,
) -> BreakpointsOptional[int] | None:
    if col_widths is None:
        return None

    if not isinstance(col_widths, Dict):
        return {"md": validate_col_width(col_widths, n_kids, "md")}

    ret: BreakpointsOptional[int] = {}
    col_widths_items = cast(BreakpointsSoft[int], col_widths).items()

    for brk, value in col_widths_items:
        if brk not in breakpoints:
            raise ValueError(
                f"Breakpoint '{brk}' is not valid. Valid breakpoints are: {', '.join(breakpoints)}'."
            )

        if value is None:
            ret[brk] = None
        elif isinstance(value, (int, Iterable)):
            ret[brk] = validate_col_width(value, n_kids, brk)
        else:
            raise TypeError(
                f"Invalid type for value at breakpoint '{brk}'. Expected int or Iterable[int]."
            )

    return ret


def validate_col_width(
    x: Iterable[int] | int, n_kids: int, break_name: Breakpoint
) -> Iterable[int]:
    if isinstance(x, int):
        y = [x]
    else:
        y = x

    if not all(isinstance(i, int) for i in y):
        raise ValueError(
            f"Column values at breakpoint '{break_name}' must be integers. Values greater than 0 indicate width, and negative values indicate a column offset."
        )

    if any(i == 0 for i in y):
        raise ValueError(
            f"Column values at breakpoint '{break_name}' must be greater than 0 to indicate width, or negative to indicate a column offset."
        )

    if not any(b > 0 for b in y):
        raise ValueError(
            f"Column values at breakpoint '{break_name}' must include at least one positive integer width."
        )

    if len(list(y)) > n_kids:
        warn(
            f"More column widths than children at breakpoint '{break_name}', extra widths will be ignored."
        )

    return y


def col_widths_attrs(col_widths: BreakpointsOptional[int] | None) -> TagAttrs:
    ret: Dict[str, TagAttrValue] = {}
    if col_widths is None:
        return ret

    for break_name, value in col_widths.items():
        if isinstance(break_name, Enum):
            break_name = break_name.value
        break_name = f"col-widths-{break_name}"
        if value is None:
            ret[break_name] = ""
        else:
            ret[break_name] = ",".join([str(v) for v in value])

    return ret


def maybe_fr_unit(x: CssUnit) -> str:
    if isinstance(x, float):
        x = round(x)

    if isinstance(x, int):
        return f"{x}fr"

    return x


def row_heights_attrs(
    x: BreakpointsUser[CssUnit],
) -> TagAttrs:
    if x is None:
        return {"style": "", "class": ""}

    if isinstance(x, (int, float, str)):  # CssUnit
        x = [x]

    if hasattr(x, "__iter__") and not isinstance(x, Dict):
        # For a single row_heights, we use the same value across all breakpoints,
        # including mobile
        height = " ".join([maybe_fr_unit(h) for h in x])
        return {
            "style": css(
                **{"--bslib-grid--row-heights": height},
            ),
            "class": "",
        }

    x = cast(BreakpointsSoft[CssUnit], x)

    # Remove any None values from x
    x_complete = {k: v for k, v in x.items() if v is not None}

    # We use classes to activate CSS variables at the right breakpoints. Note: Mobile
    # row height is derived from xs or defaults to auto in the CSS, so we don't need the
    # class to activate it
    classes = [
        f"bslib-grid--row-heights--{brk}" for brk in x_complete.keys() if brk != "xs"
    ]

    # Create CSS variables, treating numeric values as fractional units, passing strings
    css_vars: Dict[str, str] = {}
    for brk, heights in x_complete.items():
        var = f"--bslib-grid--row-heights--{brk}"

        if isinstance(heights, CssUnit):
            heights = [heights]

        value = " ".join([maybe_fr_unit(h) for h in heights])
        css_vars[var] = value

    return {
        "style": css(**css_vars),
        "class": " ".join(classes),
    }
