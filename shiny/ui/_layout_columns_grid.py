from __future__ import annotations

from json import dumps as toJSON
from typing import Dict, Iterable, Literal, Optional, TypedDict, TypeVar, Union, cast
from warnings import warn as warn

from htmltools import Tag, TagAttrs, TagAttrValue, TagChild, css, div

from ._html_deps_shinyverse import web_component_dependency
from ._tag import consolidate_attrs
from .css import CssUnit, as_css_unit
from .fill import as_fill_item, as_fillable_container

T = TypeVar("T")

Breakpoints = Literal["xs", "sm", "md", "lg", "xl", "xxl"]
"""
References
----------
* [Available Bootstrap breakpoints](https://getbootstrap.com/docs/5.3/layout/breakpoints/#available-breakpoints)
"""

BreakpointsSoft = Dict[Breakpoints, Union[Iterable[T], T, None]]
BreakpointsOptional = Dict[Breakpoints, Union[Iterable[T], None]]
BreakpointsComplete = Dict[Breakpoints, Iterable[T]]
BreakpointsUser = Union[BreakpointsSoft[T], Iterable[T], T, None]


def layout_columns_grid(
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
    attrs, children = consolidate_attrs(*args, class_=class_, **kwargs)

    col_widths_spec = as_col_spec(col_widths, len(children))

    # Create the bslib-layout-columns element
    tag = Tag(
        "bslib-layout-columns",
        {
            "class": "bslib-grid grid",
            "col-widths": json_col_spec(col_widths_spec),
            "style": css(
                gap=as_css_unit(gap),
                height=as_css_unit(height),
            ),
        },
        attrs,
        row_heights_attrs(row_heights),
        *wrap_all_in_grid_item_container(children, fillable),
        web_component_dependency(),
    )

    # Apply fill and fillable
    if fill:
        tag = as_fill_item(tag)
    if fillable:
        tag = as_fillable_container(tag)

    return tag


def wrap_all_in_grid_item_container(
    children: Iterable[TagChild],
    fillable: bool = True,
    class_: Optional[str] = None,
) -> list[TagChild]:
    item_class = "bslib-grid-item bslib-gap-spacing"
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


def validate_col_width(
    x: Iterable[int] | int, n_kids: int, break_name: str
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
        if brk not in ["xs", "sm", "md", "lg", "xl", "xxl"]:
            raise ValueError(
                f"Breakpoint '{brk}' is not valid. Valid breakpoints are: 'xs', 'sm', 'md', 'lg', 'xl', 'xxl'."
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


def json_col_spec(col_widths: BreakpointsOptional[int] | None) -> Optional[str]:
    if col_widths is None:
        return None

    return toJSON(col_widths, default=lambda x: "null" if x is None else x)


def maybe_fr_unit(x: CssUnit) -> str:
    if isinstance(x, float):
        x = round(x)

    if isinstance(x, int):
        return f"{x}fr"

    return x


RowHeightsDict = TypedDict("RowHeightsDict", {"style": Dict[str, str], "class": str})


def row_heights_attrs(
    x: BreakpointsUser[CssUnit],
) -> TagAttrs:
    if x is None:
        return {"style": "", "class": ""}

    if isinstance(x, CssUnit):
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
