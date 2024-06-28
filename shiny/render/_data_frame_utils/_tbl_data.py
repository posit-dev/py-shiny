from __future__ import annotations

from abc import ABC
from functools import singledispatch
from typing import TYPE_CHECKING, Any, Optional, Union

from typing_extensions import TypeAlias, TypedDict

from ._databackend import AbstractBackend

if TYPE_CHECKING:
    import pandas as pd
    import polars as pl

    from ._unsafe import DataFrameDtype

    PdDataFrame = pd.DataFrame
    PlDataFrame = pl.DataFrame
    PdSeries = pd.Series[Any]
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


@singledispatch
def serialize_dtype(col: SeriesLike) -> DataFrameDtype:
    raise TypeError(f"Unsupported type: {type(col)}")


# TODO: we can't import DataFrameDtype at runtime, due to circular dependency. So
# we import it during type checking. But this means we have to explicitly register
# the dispatch type below.


@serialize_dtype.register(PdSeries)
def _(col: PdSeries) -> DataFrameDtype:
    from ._unsafe import serialize_numpy_dtype

    return serialize_numpy_dtype(col)


@serialize_dtype.register(PlSeries)
def _(col: PlSeries) -> DataFrameDtype:
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
def serialize_frame(data: DataFrameLike) -> _FrameJson:
    raise TypeError(f"Unsupported type: {type(data)}")


@serialize_frame.register
def _(data: PdDataFrame) -> _FrameJson:
    from ._datagridtable import serialize_pandas_df

    return serialize_pandas_df(data)


@serialize_frame.register
def _(data: PlDataFrame) -> _FrameJson:
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
# TODO: this should replace use of iloc

_RowsList: TypeAlias = Optional[list[int]]
_ColsList: TypeAlias = Optional[list[str]]


@singledispatch
def subset_frame(
    data: DataFrameLike, rows: _RowsList = None, cols: _ColsList = None
) -> DataFrameLike:
    """Return a subsetted DataFrame, based on row positions and column names.

    Note that when None is passed, all rows or columns get included.
    """
    # Note that this type signature assumes column names are strings things.
    # This is always true in Polars, but not in Pandas (e.g. a column name could be an
    # int, or even a tuple of ints)
    raise TypeError(f"Unsupported type: {type(data)}")


@subset_frame.register
def _(data: PdDataFrame, rows: _RowsList = None, cols: _ColsList = None) -> PdDataFrame:
    # iloc requires integer positions, so we convert column name strings to ints, or
    # the slice default.
    if cols is not None:
        indx_cols = data.columns.get_indexer_for(cols)
    else:
        indx_cols = slice(None)

    indx_rows = rows if rows is not None else slice(None)

    return data.iloc[indx_rows, indx_cols]


@subset_frame.register
def _(data: PlDataFrame, rows: _RowsList = None, cols: _ColsList = None) -> PlDataFrame:
    indx_cols = cols if cols is not None else slice(None)
    indx_rows = rows if rows is not None else slice(None)
    return data[indx_rows, indx_cols]


# get_frame_cell -----------------------------------------------------------------------


@singledispatch
def get_frame_cell(data: DataFrameLike, row: int, col: int) -> Any:
    raise TypeError(f"Unsupported type: {type(data)}")


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
    raise TypeError(f"Unsupported type: {type(data)}")


@copy_frame.register
def _(data: PdDataFrame) -> PdDataFrame:
    return data.copy()


@copy_frame.register
def _(data: PlDataFrame) -> PlDataFrame:
    return data.clone()
