from __future__ import annotations

from typing import Literal, Optional, Dict, Union, List

from htmltools import Tag, TagAttrs, TagAttrValue, TagChild, css

from ..types import MISSING, MISSING_TYPE
from ._html_deps_shinyverse import web_component_dependency
from ._tag import consolidate_attrs
from .css import CssUnit, as_css_unit
from .fill import as_fill_item, as_fillable_container


from json import dumps as toJSON
from warnings import warn as warn

ColWidthsUserSpec = Optional[Dict[str, Union[List[int], None]]]


def layout_columns(
    *args: TagChild | TagAttrs,
    col_widths: ColWidthsUserSpec = None,
    # row_heights: CssUnit | None | MISSING_TYPE = MISSING,
    fill: bool = True,
    fillable: bool = True,
    gap: Optional[CssUnit] = None,
    class_: Optional[str] = None,
    height: Optional[CssUnit] = None,
    **kwargs: TagAttrValue,
) -> Tag:
    attrs, children = consolidate_attrs(*args, class_=class_, **kwargs)

    col_widths = validate_col_spec(col_widths, len(children))

    # Create the bslib-layout-columns element
    tag = Tag(
        "bslib-layout-columns",
        *children,
        attrs,
        web_component_dependency(),
        class_=f"bslib-grid grid {class_ or ''}",
        col_widths=json_col_spec(col_widths),
        style=css(
            gap=as_css_unit(gap),
            height=as_css_unit(height),
            # row_heights=as_css_unit(row_heights),
        ),
    )

    # Apply fill and fillable
    if fill:
        tag = as_fill_item(tag)
    if fillable:
        tag = as_fillable_container(tag)

    return tag


Breakpoints = Literal["xs", "sm", "md", "lg", "xl"]
BreakpointsDict = Dict[Union[Breakpoints, str], Union[List[int], int, None]]


def validate_col_spec(
    col_widths: BreakpointsDict | List[int] | None,
    n_kids: int,
) -> BreakpointsDict | None:
    if col_widths is None:
        return None

    if isinstance(col_widths, list):
        col_widths = {"md": col_widths}

    for break_name, bk in col_widths.items():
        if bk is None:
            continue

        if isinstance(bk, int):
            bk = [bk]
            col_widths[break_name] = bk

        if any(b == 0 for b in bk):
            raise ValueError(
                "Column values must be greater than 0 to indicate width, or negative to indicate a column offset."
            )

        if not any(b > 0 for b in bk):
            raise ValueError(
                "Column values must include at least one positive integer width."
            )

        if len(bk) > n_kids:
            warn(
                f"More column widths than children at breakpoint '{break_name}', extra widths will be ignored."
            )

    return col_widths


def json_col_spec(col_widths: ColWidthsUserSpec) -> Optional[str]:
    if col_widths is None:
        return None

    return toJSON(col_widths, default=lambda x: "null" if x is None else x)
