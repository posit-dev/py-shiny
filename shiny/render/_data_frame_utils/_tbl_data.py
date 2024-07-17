# Note - barret 2024-07-08; When we adopt `narwhals` support, we should remove the singledispatch and instead always use `narwhals`. In addition, we should return the native type of a native type was originally provided. (Or maintain the narwhals object, if a narwhals object was provided.)

from __future__ import annotations

from functools import singledispatch
from typing import Any, List, Tuple, cast

from htmltools import TagNode

from ..._typing_extensions import TypeIs
from ...session import require_active_session
from ._html import maybe_as_cell_html

# from ...types import Jsonifiable
from ._types import (
    CellPatch,
    ColsList,
    DataFrameLike,
    DataFrameLikeT,
    FrameDtype,
    FrameJson,
    ListSeriesLike,
    PandasCompatible,
    PdDataFrame,
    PdSeries,
    PlDataFrame,
    PlSeries,
    RowsList,
    SeriesLike,
)

__all__ = (
    "is_data_frame_like",
    # "as_data_frame_like",
    "frame_columns",
    "apply_frame_patches",
    "serialize_dtype",
    "serialize_frame",
    "subset_frame",
    "get_frame_cell",
    "frame_shape",
    "copy_frame",
    "frame_column_names",
)

# as_frame -----------------------------------------------------------------------------


def as_data_frame_like(
    data: DataFrameLikeT,
) -> DataFrameLikeT:
    if is_data_frame_like(data):
        return data

    # Legacy support for non-Pandas/Polars data frames that were previously supported
    # and converted to pandas
    if isinstance(data, PandasCompatible):
        from ..._deprecated import warn_deprecated

        warn_deprecated(
            "Returned data frame data values that are not Pandas or Polars `DataFrame`s are currently not supported. "
            "A `.to_pandas()` was found on your object and will be called. "
            "To remove this warning, please call `.to_pandas()` on your data "
            "and use the pandas result in your returned value. "
            "In the future, this will raise an error."
        )
        return data.to_pandas()

    raise TypeError(f"Unsupported type: {type(data)}")


# @singledispatch
# def is_data_frame_like(
#     data: object,
# ) -> bool:
#     return False


# @is_data_frame_like.register
# def _(data: PdDataFrame) -> bool:
#     return True


# @is_data_frame_like.register
# def _(data: PlDataFrame) -> bool:
#     return True


def is_data_frame_like(
    data: DataFrameLikeT | object,
) -> TypeIs[DataFrameLikeT]:
    if isinstance(data, (PdDataFrame, PlDataFrame)):
        return True

    return False


# frame_columns ------------------------------------------------------------------------


@singledispatch
def frame_columns(data: DataFrameLike) -> ListSeriesLike:
    raise TypeError(f"Unsupported type: {type(data)}")


@frame_columns.register
def _(data: PdDataFrame) -> ListSeriesLike:
    ret = [cast(PlSeries, data[col]) for col in data.columns]
    return ret


@frame_columns.register
def _(data: PlDataFrame) -> ListSeriesLike:
    return data.get_columns()


# apply_frame_patches --------------------------------------------------------------------


def apply_frame_patches__typed(
    data: DataFrameLikeT, patches: List[CellPatch]
) -> DataFrameLikeT:
    return cast(DataFrameLikeT, apply_frame_patches(data, patches))


@singledispatch
def apply_frame_patches(
    data: DataFrameLike,
    patches: List[CellPatch],
) -> DataFrameLike:
    raise TypeError(f"Unsupported type: {type(data)}")


@apply_frame_patches.register
def _(data: PdDataFrame, patches: List[CellPatch]) -> PdDataFrame:
    import pandas as pd

    # Enable copy-on-write mode for the data;
    # Use `deep=False` to avoid copying the full data; CoW will copy the necessary data when modified
    with pd.option_context("mode.copy_on_write", True):
        # Apply patches!
        data = data.copy(deep=False)
        for cell_patch in patches:
            data.iat[  # pyright: ignore[reportUnknownMemberType]
                cell_patch["row_index"],
                cell_patch["column_index"],
            ] = cell_patch["value"]

        return data


@apply_frame_patches.register
def _(data: PlDataFrame, patches: List[CellPatch]) -> PlDataFrame:
    data = data.clone()
    for cell_patch in patches:
        data[cell_patch["row_index"], cell_patch["column_index"]] = cell_patch["value"]

    return data


# serialize_dtype ----------------------------------------------------------------------


@singledispatch
def serialize_dtype(col: SeriesLike) -> FrameDtype:
    raise TypeError(f"Unsupported type: {type(col)}")


# TODO: we can't import DataFrameDtype at runtime, due to circular dependency. So
# we import it during type checking. But this means we have to explicitly register
# the dispatch type below.


@serialize_dtype.register
def _(col: PdSeries) -> FrameDtype:
    from ._pandas import serialize_pd_dtype

    return serialize_pd_dtype(col)


@serialize_dtype.register
def _(col: PlSeries) -> FrameDtype:
    import polars as pl

    from ._html import col_contains_shiny_html

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
        if col_contains_shiny_html(col):
            type_ = "html"

    return {"type": type_}


# serialize_frame ----------------------------------------------------------------------


@singledispatch
def serialize_frame(data: DataFrameLike) -> FrameJson:
    raise TypeError(f"Unsupported type: {type(data)}")


@serialize_frame.register
def _(data: PdDataFrame) -> FrameJson:
    from ._pandas import serialize_frame_pd

    return serialize_frame_pd(data)


@serialize_frame.register
def _(data: PlDataFrame) -> FrameJson:
    import json

    type_hints = list(map(serialize_dtype, data))
    data_by_row = list(map(list, data.rows()))

    # Shiny tag support
    type_hints_type = [type_hint["type"] for type_hint in type_hints]
    if "html" in type_hints_type:
        session = require_active_session(None)

        def wrap_shiny_html_with_session(x: TagNode):
            return maybe_as_cell_html(x, session=session)

        html_columns = [i for i, x in enumerate(type_hints_type) if x == "html"]

        for html_column in html_columns:
            for row in data_by_row:
                row[html_column] = wrap_shiny_html_with_session(row[html_column])

    data_val = json.loads(json.dumps(data_by_row, default=str))

    return {
        # "index": list(range(len(data))),
        "columns": data.columns,
        "data": data_val,
        "typeHints": type_hints,
    }


# subset_frame -------------------------------------------------------------------------
def subset_frame__typed(
    data: DataFrameLikeT, *, rows: RowsList = None, cols: ColsList = None
) -> DataFrameLikeT:
    return cast(DataFrameLikeT, subset_frame(data, rows=rows, cols=cols))


@singledispatch
def subset_frame(
    data: DataFrameLike, *, rows: RowsList = None, cols: ColsList = None
) -> DataFrameLike:
    """Return a subsetted DataFrame, based on row positions and column names.

    Note that when None is passed, all rows or columns get included.
    """
    # Note that this type signature assumes column names are strings things.
    # This is always true in Polars, but not in Pandas (e.g. a column name could be an
    # int, or even a tuple of ints)
    raise TypeError(f"Unsupported type: {type(data)}")


@subset_frame.register
def _(
    data: PdDataFrame,
    *,
    rows: RowsList = None,
    cols: ColsList = None,
) -> PdDataFrame:
    # Enable copy-on-write mode for the data;
    # Use `deep=False` to avoid copying the full data; CoW will copy the necessary data when modified
    import pandas as pd

    with pd.option_context("mode.copy_on_write", True):
        # iloc requires integer positions, so we convert column name strings to ints, or
        # the slice default.
        indx_cols = (  # pyright: ignore[reportUnknownVariableType]
            slice(None)
            if cols is None
            else [
                (
                    # Send in an array of size 1 and retrieve the first element
                    data.columns.get_indexer_for(  # pyright: ignore[reportUnknownMemberType]
                        [col]
                    )[
                        0
                    ]
                    if isinstance(col, str)
                    else col
                )
                for col in cols
            ]
        )

        # Force list when using a non-None value for pandas compatibility
        indx_rows = list(rows) if rows is not None else slice(None)

        return data.iloc[indx_rows, indx_cols]


@subset_frame.register
def _(
    data: PlDataFrame,
    *,
    rows: RowsList = None,
    cols: ColsList = None,
) -> PlDataFrame:
    indx_cols = (
        [col if isinstance(col, str) else data.columns[col] for col in cols]
        if cols is not None
        else slice(None)
    )
    indx_rows = rows if rows is not None else slice(None)
    return data[indx_rows, indx_cols]


# get_frame_cell -----------------------------------------------------------------------


@singledispatch
def get_frame_cell(data: DataFrameLike, row: int, col: int) -> Any:
    raise TypeError(f"Unsupported type: {type(data)}")


@get_frame_cell.register
def _(data: PdDataFrame, row: int, col: int) -> Any:
    return (
        data.iat[  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
            row, col
        ]
    )


@get_frame_cell.register
def _(data: PlDataFrame, row: int, col: int) -> Any:
    return data[row, col]


# shape --------------------------------------------------------------------------------


@singledispatch
def frame_shape(data: DataFrameLike) -> Tuple[int, ...]:
    raise TypeError(f"Unsupported type: {type(data)}")


@frame_shape.register
def _(data: PdDataFrame) -> Tuple[int, ...]:
    return data.shape


@frame_shape.register
def _(data: PlDataFrame) -> Tuple[int, ...]:
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


# column_names -------------------------------------------------------------------------
@singledispatch
def frame_column_names(data: DataFrameLike) -> List[str]:
    raise TypeError(f"Unsupported type: {type(data)}")


@frame_column_names.register
def _(data: PdDataFrame) -> List[str]:
    return data.columns.to_list()


@frame_column_names.register
def _(data: PlDataFrame) -> List[str]:
    return data.columns
