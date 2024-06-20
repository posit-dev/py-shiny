from abc import ABC
from functools import singledispatch
from typing import TYPE_CHECKING, Any, Literal, Union

from typing_extensions import NotRequired, TypedDict

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
    ...


@singledispatch
def subset_frame(data, rows=None, col=None): ...


# pandas DataFrame methods called
# iat
# loc
# copy
# shape
