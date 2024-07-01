from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Literal, NotRequired, Required

from ..._typing_extensions import TypedDict
from ...types import Jsonifiable, ListOrTuple

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
        "cols": NotRequired[
            str | int | ListOrTuple[str] | ListOrTuple[int] | ListOrTuple[bool] | None
        ],
        "style": NotRequired[dict[str, Jsonifiable] | None],
        "class": NotRequired[str | None],
    },
)
StyleInfo = StyleInfoBody

BrowserStyleInfoBody = TypedDict(
    "BrowserStyleInfoBody",
    {
        "location": Required[Literal["body"]],
        "rows": Required[tuple[int, ...] | None],
        "cols": Required[tuple[int, ...] | None],
        "style": Required[dict[str, Jsonifiable] | None],
        "class": Required[str | None],
    },
)
BrowserStyleInfo = BrowserStyleInfoBody


def style_info_to_browser_style_info(
    info: StyleInfo,
    *,
    nrow: int,
    browser_column_names: ListOrTuple[str],
) -> BrowserStyleInfo:
    if not isinstance(info, dict):
        raise TypeError("`StyleInfo` objects must be a dictionary. Received: ", info)

    location = info.get("location", None)
    if location != "body":
        raise ValueError(f"Unsupported `StyleInfo` location: {location}")

    rows = style_info_rows(info, nrow=nrow)
    cols = style_info_cols(info, browser_column_names=browser_column_names)

    style = info.get("style", None)
    if style is not None:
        if isinstance(style, str):
            raise TypeError(
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


def style_info_cols(
    info: StyleInfo,
    *,
    browser_column_names: ListOrTuple[str],
) -> tuple[int, ...] | None:
    cols = info.get("cols", None)
    if cols is None:
        return None
    if isinstance(cols, (str, int)):
        cols = (cols,)
    if not isinstance(cols, (list, tuple)):
        raise TypeError(
            "`StyleInfo` `cols` value must be a list, tuple, int, or string"
        )

    # cols_tup = tuple(cols)
    if len(cols) == 0:
        return ()

    if isinstance(cols[0], bool):
        if len(cols) != len(browser_column_names):
            raise ValueError(
                f"Style column boolean list must have the same length as the data frame column names. Expected {len(browser_column_names)}, got {len(cols)}"
            )
        return tuple(i for i, col in enumerate(cols) if col)

    if isinstance(cols[0], str):
        ret: list[int] = []
        col_names = set(browser_column_names)
        for col in cols:
            assert isinstance(
                col, str
            ), "All elements of `StyleInfo` `cols` must be of the same type: str, int, or bool."
            if col not in col_names:
                raise ValueError(
                    f"`StyleInfo` `cols` value '{col}' not found in data frame column names"
                )
            ret.append(browser_column_names.index(col))
        return tuple(ret)
    elif isinstance(cols[0], int):
        ret: list[int] = []
        for col in cols:
            assert isinstance(
                col, int
            ), "All elements of `StyleInfo` `cols` must be of the same type: str, int, or bool."
            if col < 0:
                raise ValueError(f"Style column index `{col}` must be non-negative")
            if col >= len(browser_column_names):
                raise ValueError(
                    f"Style column index `{col}` out of range (max: {len(browser_column_names) - 1})"
                )
            ret.append(col)
        return tuple(ret)
    elif isinstance(cols[0], bool):
        if all(isinstance(col, bool) for col in cols):
            return tuple(i for i, val in enumerate(cols) if val)
        raise TypeError(
            "All elements of `StyleInfo` `cols` must be of the same type: str, int, or bool."
        )
    else:
        raise TypeError(
            "All elements of `StyleInfo` `cols` must be of the same type: str, int, or bool."
        )


def style_info_rows(
    info: StyleInfo,
    *,
    nrow: int,
) -> None | tuple[int, ...]:
    rows = info.get("rows", None)
    if rows is None:
        return None
    if isinstance(rows, (bool, int)):
        return (rows,)
    if not isinstance(rows, (list, tuple)):
        raise TypeError("`StyleInfo` `rows` value must be a list, tuple, int or string")

    rows_tup = tuple(rows)
    if len(rows_tup) == 0:
        return rows_tup

    if isinstance(rows_tup[0], bool):
        assert (
            len(rows_tup) == nrow
        ), "Length of `StyleInfo` `rows` must match the number of rows in the data frame when `rows` is a boolean list / tuple."
        if all(isinstance(row, bool) for row in rows_tup):
            # Turn into a tuple of indices
            ret = tuple(i for i, val in enumerate(rows_tup) if val)
            return ret

        raise TypeError(
            "All elements of `StyleInfo` `rows` must be of the same type: bool or int."
        )

    elif isinstance(rows_tup[0], int):
        if all(isinstance(row, int) for row in rows_tup):
            return rows_tup

        raise TypeError(
            "All elements of `StyleInfo` `rows` must be of the same type: bool or int."
        )
    else:
        raise TypeError(
            "`StyleInfo` `rows` value must be a list or tuple containing ints, bools, or str values."
        )


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
    nrow = data.shape[0]
    return [
        style_info_to_browser_style_info(
            info,
            nrow=nrow,
            browser_column_names=browser_column_names,
        )
        for info in style_infos
    ]
