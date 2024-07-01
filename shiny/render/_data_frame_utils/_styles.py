from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Literal, NotRequired, Required

from ..._typing_extensions import TypedDict
from ...types import Jsonifiable, ListOrTuple
from ._utils import to_bool_tuple_or_none, to_int_tuple_or_none, to_intstr_tuple_or_none

if TYPE_CHECKING:
    import pandas as pd

    DataFrameValue = pd.DataFrame

    StyleFn = Callable[[DataFrameValue], list["StyleInfo"]]

else:
    StyleFn = Callable
    DataFrameValue = object

# great_tables's StyleInfo
# @dataclass(frozen=True)
# class StyleInfo:
#     locname: str
#     locnum: int
#     grpname: str | None = None
#     colname: str | None = None
#     rownum: int | None = None
#     colnum: int | None = None
#     styles: list[CellStyle] = field(default_factory=list)


# https://typing.readthedocs.io/en/latest/spec/typeddict.html#alternative-syntax
# Use alternative syntax for TypedDict to avoid key error with `class`:
StyleInfoBody = TypedDict(
    "StyleInfoBody",
    {
        "location": Required[Literal["body"]],
        "rows": NotRequired[int | ListOrTuple[int] | ListOrTuple[bool] | None],
        "cols": NotRequired[int | str | ListOrTuple[str | int] | None],
        "style": NotRequired[dict[str, Jsonifiable] | None],
        "class": NotRequired[str | None],
    },
)
StyleInfo = StyleInfoBody

BrowserStyleInfoBody = TypedDict(
    "BrowserStyleInfo",
    {
        "location": Required[Literal["body"]],
        "rows": Required[tuple[int, ...] | None],
        "cols": Required[tuple[int, ...] | None],
        "style": Required[dict[str, Jsonifiable] | None],
        "class": Required[str | None],
    },
)
BrowserStyleInfo = BrowserStyleInfoBody


def columns_to_browser_columns(
    columns: ListOrTuple[int | str] | None,
    browser_column_names: ListOrTuple[str],
) -> tuple[int, ...] | None:

    if columns is None:
        return None

    ret: list[int] = []
    browser_column_names_set = set(browser_column_names)
    ncol = len(browser_column_names)

    for col in columns:
        if isinstance(col, str):
            if col not in browser_column_names_set:
                raise ValueError(
                    f"Style column '{col}' not found in data frame column names"
                )
            ret.append(browser_column_names.index(col))
        else:
            if col < 0:
                raise ValueError(f"Style column index `{col}` must be non-negative")
            if col >= ncol:
                raise ValueError(
                    f"Style column index `{col}` out of range (max: {ncol - 1})"
                )
            ret.append(col)

    return tuple(ret)


def style_info_to_browser_style_info(
    info: StyleInfo,
    *,
    browser_column_names: ListOrTuple[str],
) -> BrowserStyleInfo:
    if not isinstance(info, dict):
        raise ValueError("`StyleInfo` objects must be a dictionary. Received: ", info)

    location = info.get("location", None)
    if location != "body":
        raise ValueError(f"Unsupported `StyleInfo` location: {location}")

    rows = info.get("rows", None)
    if rows is not None:
        if isinstance(rows, (bool, int)):
            rows = (rows,)
        if not isinstance(rows, (list, tuple)):
            raise ValueError(
                "`StyleInfo` `rows` value must be a list, tuple, or scalar"
            )
        if len(rows) > 0:
            if isinstance(rows[0], bool):
                # Validate that all elements are bools
                rows = to_bool_tuple_or_none(
                    rows  # pyright: ignore[reportGeneralTypeIssues]
                )
            elif isinstance(rows[0], int):
                # Validate that all elements are ints
                rows = to_int_tuple_or_none(
                    rows  # pyright: ignore[reportGeneralTypeIssues]
                )

    rows = to_int_tuple_or_none(info.get("rows", None))

    cols = to_intstr_tuple_or_none(info.get("cols", None))
    cols = columns_to_browser_columns(cols, browser_column_names)

    style = info.get("style", None)
    if style is not None:
        if isinstance(style, str):
            raise ValueError(
                "`StyleInfo` `style` value must be a dictionary of key-value pairs, not a style string"
            )
        assert isinstance(style, dict)

    class_ = info.get("class_", None)
    if class_ is not None:
        assert isinstance(class_, str), "`StyleInfo` `class` value must be a string"

    if style is None and class_ is None:
        raise ValueError("`StyleInfo` objects must at least have `style` or `class`")

    return {
        "location": location,
        "rows": rows,
        "cols": cols,
        "style": style,
        "class": class_,
    }


def as_style_infos(
    infos: StyleInfo | list[StyleInfo] | StyleFn | None,
) -> list[StyleInfo] | StyleFn:

    if callable(infos):
        return infos

    if not infos:
        return []

    if not isinstance(infos, list):
        infos = [infos]

    return infos


def as_browser_style_infos(
    infos: list[StyleInfo] | StyleFn,
    *,
    data: DataFrameValue,
) -> list[BrowserStyleInfo]:
    browser_column_names = data.columns.tolist()

    if callable(infos):
        style_infos = infos(data)
    else:
        style_infos = infos

    if not style_infos:
        return []

    if not isinstance(style_infos, list):
        style_infos = [style_infos]

    return [
        style_info_to_browser_style_info(
            info,
            browser_column_names=browser_column_names,
        )
        for info in style_infos
    ]
