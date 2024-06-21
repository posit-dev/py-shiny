from __future__ import annotations

from abc import ABC
from functools import singledispatch
from typing import TYPE_CHECKING, Any, Literal, Optional, Union

from typing_extensions import NotRequired, TypeAlias, TypedDict

from ._databackend import AbstractBackend

if TYPE_CHECKING:
    import pandas as pd
    import polars as pl

    PdDataFrame = pd.DataFrame
    PlDataFrame = pl.DataFrame
    PdSeries = pd.Series
    PlSeries = pl.Series

    SeriesLike = Union[PdSeries, PlSeries]
    DataFrameLike = Union[PdDataFrame, PlDataFrame]

else:

    class PdDataFrame(AbstractBackend):
        _backends = [("pandas", "DataFrame")]

    class PlDataFrame(AbstractBackend):
        _backends = [("polars", "DataFrame")]

    class PdSeries(AbstractBackend):
        _backends = [("pandas", "Series")]

    class PlSeries(AbstractBackend):
        _backends = [("polars", "Series")]

    class SeriesLike(ABC): ...

    class DataFrameLike(ABC): ...

    SeriesLike.register(PdSeries)
    SeriesLike.register(PlSeries)

    DataFrameLike.register(PdDataFrame)
    DataFrameLike.register(PlDataFrame)


# serialize_dtype ----------------------------------------------------------------------


class _GridDType(TypedDict):
    type: Literal["string", "numeric", "categorical", "html", "unknown"]
    categories: NotRequired[list[str]]


@singledispatch
def serialize_dtype(col: SeriesLike) -> _GridDType:
    raise TypeError(f"Unsupported type: {type(col)}")


@serialize_dtype.register
def _(col: PdSeries) -> _GridDType:
    from ._unsafe import serialize_numpy_dtype

    return serialize_numpy_dtype(col)


@serialize_dtype.register
def _(col: PlSeries) -> _GridDType:
    import polars as pl

    from ._unsafe import col_contains_shiny_html

    if col.dtype.is_(pl.String):
        if col_contains_shiny_html(col):
            type_ = "html"
        else:
            type_ = "string"
    elif col.dtype.is_numeric():
        type_ = "numeric"

    elif col.dtype.is_(pl.Categorical()):
        categories = col.cat.get_categories().to_list()
        return {"type": "categorical", "categories": categories}
    else:
        type_ = "unknown"

    return {"type": type_}


# serialize_frame ----------------------------------------------------------------------


class _FrameJson(TypedDict):
    columns: list[str]  # column names
    index: list[Any]  # pandas index values
    data: list[list[Any]]  # each entry is a row of len(columns)
    typeHints: list[_FrameHintEntry]


class _FrameHintEntry(TypedDict):
    type: "str"


@singledispatch
def serialize_frame(data: DataFrameLike) -> dict[str, Any]:
    raise TypeError(f"Unsupported type: {type(data)}")


@serialize_frame.register
def _(data: PdDataFrame) -> dict[str, Any]:
    from ._datagridtable import serialize_pandas_df

    return serialize_pandas_df(data)


@serialize_frame.register
def _(data: PlDataFrame) -> dict[str, Any]:
    # write_json only does rows (as dictionaries; but we need lists)
    # serialize only does columns
    named_cols = data.to_dict(as_series=False)
    type_hints = list(map(serialize_dtype, data))
    return {
        "columns": list(named_cols),
        "index": list(range(len(data))),
        "data": list(named_cols.values()),
        "typeHints": type_hints,
    }


# subset_frame -------------------------------------------------------------------------

_RowsList: TypeAlias = Optional[list[int]]
_ColsList: TypeAlias = Optional[list[str]]


@singledispatch
def subset_frame(
    data: DataFrameLike, rows: _RowsList = None, cols: _ColsList = None
) -> DataFrameLike:
    # Note that this type signature assumes column names are strings things.
    # This is always true in Polars, but not in Pandas (e.g. a column name could be an
    # int, or even a tuple of ints)
    raise TypeError(f"Unsupported type: {type(col)}")


@subset_frame.register
def _(data: PlDataFrame, rows: _RowsList = None, cols: _ColsList = None) -> PlDataFrame:
    return data[rows, cols]


@subset_frame.register
def _(data: PdDataFrame, rows: _RowsList = None, cols: _ColsList = None) -> PdDataFrame:
    # iloc requires integer positions, so we convert column name strings to ints, or
    # the slice default.
    if cols is not None:
        indx_cols = data.columns.get_indexer_for(cols)
    else:
        indx_cols = slice(None)

    return data.iloc[rows, indx_cols]


# get_frame_cell -----------------------------------------------------------------------


@singledispatch
def get_frame_cell(data: DataFrameLike, row: int, col: int) -> Any:
    raise TypeError(f"Unsupported type: {type(col)}")


@get_frame_cell.register
def _(data: PdDataFrame, row: int, col: int) -> Any:
    return data.iat[row, col]


@get_frame_cell.register
def _(data: PlDataFrame, row: int, col: int) -> Any:
    return data[row, col]


# shape --------------------------------------------------------------------------------


@singledispatch
def shape(data: DataFrameLike) -> tuple[int, ...]:
    return data.shape


# copy_frame ---------------------------------------------------------------------------


@singledispatch
def copy_frame(data: DataFrameLike) -> DataFrameLike:
    raise TypeError(f"Unsupported type: {type(col)}")


@copy_frame.register
def _(data: PdDataFrame) -> PdDataFrame:
    return data.copy()


@copy_frame.register
def _(data: PlDataFrame) -> PlDataFrame:
    return data.clone()
