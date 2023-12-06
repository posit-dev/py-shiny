from __future__ import annotations

from typing import Iterable, Literal, Optional, Dict, TypedDict, Union, cast

from htmltools import Tag, TagAttrs, TagAttrValue, TagChild, css

from ._html_deps_shinyverse import web_component_dependency
from ._tag import consolidate_attrs
from .css import CssUnit, as_css_unit
from .fill import as_fill_item, as_fillable_container


from json import dumps as toJSON
from warnings import warn as warn

ColWidthsUserSpec = Optional[Dict[str, Union[Iterable[int], int, None]]]
ColWidthsSpec = Optional[Dict[str, Union[Iterable[int], None]]]
RowHeightsUserSpec = Optional[Dict[str, Union[Iterable[CssUnit], CssUnit]]]


def layout_columns(
    *args: TagChild | TagAttrs,
    col_widths: ColWidthsUserSpec = None,
    row_heights: RowHeightsUserSpec = None,
    fill: bool = True,
    fillable: bool = True,
    gap: Optional[CssUnit] = None,
    class_: Optional[str] = None,
    height: Optional[CssUnit] = None,
    **kwargs: TagAttrValue,
) -> Tag:
    attrs, children = consolidate_attrs(*args, class_=class_, **kwargs)

    col_widths = validate_col_spec(col_widths, len(children))
    row_heights_attr = row_heights_css_vars(row_heights)

    # Create the bslib-layout-columns element
    tag = Tag(
        "bslib-layout-columns",
        *children,
        {
            "class": "bslib-grid grid",
        },
        attrs,
        web_component_dependency(),
        class_=row_heights_attr["classes"],
        col_widths=json_col_spec(col_widths),
        style=css(
            gap=as_css_unit(gap),
            height=as_css_unit(height),
            **row_heights_attr["style"],
        ),
    )

    # Apply fill and fillable
    if fill:
        tag = as_fill_item(tag)
    if fillable:
        tag = as_fillable_container(tag)

    return tag


Breakpoints = Literal["xs", "sm", "md", "lg", "xl"]
BreakpointsIntDict = Dict[Union[Breakpoints, str], Union[Iterable[int], int, None]]


def validate_col_spec(
    col_widths: Union[BreakpointsIntDict, Iterable[int], int, None],
    n_kids: int,
) -> ColWidthsSpec | None:
    if col_widths is None:
        return None

    if not isinstance(col_widths, Dict):
        col_widths = {"md": col_widths}

    col_widths = cast(BreakpointsIntDict, col_widths)

    for break_name, bk in col_widths.items():
        if bk is None:
            continue

        if isinstance(bk, int):
            bk = (bk,)
            col_widths[break_name] = bk

        if any(b == 0 for b in bk):
            raise ValueError(
                "Column values must be greater than 0 to indicate width, or negative to indicate a column offset."
            )

        if not any(b > 0 for b in bk):
            raise ValueError(
                "Column values must include at least one positive integer width."
            )

        if len(list(bk)) > n_kids:
            warn(
                f"More column widths than children at breakpoint '{break_name}', extra widths will be ignored."
            )

    return cast(ColWidthsSpec, col_widths)


def json_col_spec(col_widths: ColWidthsSpec) -> Optional[str]:
    if col_widths is None:
        return None

    return toJSON(col_widths, default=lambda x: "null" if x is None else x)


BreakpointsCssUnitDict = Dict[
    Union[Breakpoints, str], Union[Iterable[CssUnit], CssUnit]
]


class RowHeightsDict(TypedDict):
    style: Dict[str, str]
    classes: str


def maybe_fr_unit(x: CssUnit) -> str:
    if isinstance(x, float):
        x = round(x)

    if isinstance(x, int):
        return f"{x}fr"

    return x


def row_heights_css_vars(
    x: BreakpointsCssUnitDict | None,
) -> RowHeightsDict:
    if x is None:
        return {"style": {}, "classes": ""}

    if isinstance(x, CssUnit):
        x = {"xs": [x], "sm": [x]}

    if hasattr(x, "__iter__") and not isinstance(x, Dict):
        x = {"xs": x, "sm": x}

    # We use classes to activate CSS variables at the right breakpoints. Note: Mobile
    # row height is derived from xs or defaults to auto in the CSS, so we don't need the
    # class to activate it
    classes = [f"bslib-grid--row-heights--{brk}" for brk in x.keys() if brk != "xs"]

    # Create CSS variables, treating numeric values as fractional units, passing strings
    css_vars: Dict[str, str] = {}
    for brk, heights in x.items():
        var = f"--bslib-grid--row-heights--{brk}"

        if isinstance(heights, CssUnit):
            heights = [heights]

        value = " ".join([maybe_fr_unit(h) for h in heights])
        css_vars[var] = value

    return {
        "style": css_vars,
        "classes": " ".join(classes),
    }
