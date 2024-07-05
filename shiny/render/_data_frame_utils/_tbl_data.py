from __future__ import annotations

# TODO-barret; Add fixture for all data frame tests to test pandas and polars
# TODO-barret; Go through all functions and make sure no `.shape` or `.columns` are used being used directly. There should be no direct usage of any custom data frame type.
from functools import singledispatch
from typing import Any, cast

# from ...types import Jsonifiable
from ._types import (
    CellPatchProcessed,
    ColsList,
    DataFrameLike,
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
    "as_data_frame_like",
    "serialize_dtype",
    "serialize_frame",
    "subset_frame",
    "frame_columns",
    "get_frame_cell",
    "frame_shape",
    "copy_frame",
    "frame_column_names",
)

# as_frame -----------------------------------------------------------------------------


@singledispatch
def is_data_frame_like(
    data: DataFrameLike | PandasCompatible,
) -> bool:
    return False


@is_data_frame_like.register
def _(data: PdDataFrame | PlDataFrame) -> bool:
    return True


@singledispatch
def as_data_frame_like(
    data: DataFrameLike | PandasCompatible,
    error_message_begin: str = "Unsupported type:",
) -> DataFrameLike:
    raise TypeError(
        f"{error_message_begin} {str(type(data))}\n"
        "Please use either a `pandas.DataFrame`, a `polars.DataFrame`, "
        "or an object that has a `.to_pandas()` method."
    )


@as_data_frame_like.register
def _(
    data: PdDataFrame | PlDataFrame, error_message_begin: str = "ignored"
) -> DataFrameLike:
    return data


@as_data_frame_like.register
def _(data: PandasCompatible, error_message_begin: str = "ignored") -> DataFrameLike:
    return data.to_pandas()


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


# # get_frame_column ---------------------------------------------------------------------


# @singledispatch
# def get_frame_column(data: DataFrameLike, col: int | str) -> SeriesLike:
#     raise TypeError(f"Unsupported type: {type(data)}")


# @get_frame_column.register
# def _(data: PdDataFrame, col: int | str) -> PdSeries:

#     col_idx: (  # pyright: ignore[reportUnknownVariableType]
#         int
#     ) = data.columns.get_indexer_for(  # pyright: ignore[reportUnknownMemberType]
#         [col]
#     )[  # pyright: ignore[] # placeholder value for Black
#         0
#     ]
#     return cast(PdSeries, data.iloc[col_idx])


# @get_frame_column.register
# def _(data: PlDataFrame, col: int | str) -> PlSeries:
#     return data[col]


# apply_frame_patches --------------------------------------------------------------------


@singledispatch
def apply_frame_patches(
    data: DataFrameLike, patches: list[CellPatchProcessed]
) -> DataFrameLike:
    raise TypeError(f"Unsupported type: {type(data)}")


@apply_frame_patches.register
def _(data: PdDataFrame, patches: list[CellPatchProcessed]) -> PdDataFrame:
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
def _(data: PlDataFrame, patches: list[CellPatchProcessed]) -> PlDataFrame:
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


@serialize_dtype.register(PdSeries)
def _(col: PdSeries) -> FrameDtype:
    from ._pandas import serialize_pd_dtype

    return serialize_pd_dtype(col)


@serialize_dtype.register(PlSeries)
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
    # write_json only does rows (as dictionaries; but we need lists)
    # serialize only does columns
    named_cols = data.to_dict(as_series=False)
    type_hints = list(map(serialize_dtype, data))
    return {
        "columns": list(named_cols),
        # "index": list(range(len(data))),
        "data": list(named_cols.values()),
        "typeHints": type_hints,
    }


# subset_frame -------------------------------------------------------------------------
# TODO: this should replace use of iloc


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
    data: PdDataFrame, *, rows: RowsList = None, cols: ColsList = None
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
            else data.columns.get_indexer_for(  # pyright: ignore[reportUnknownMemberType]
                cols
            )
        )

        # Force list when using a non-None value for pandas compatibility
        indx_rows = list(rows) if rows is not None else slice(None)

        return data.iloc[indx_rows, indx_cols]


@subset_frame.register
def _(
    data: PlDataFrame, *, rows: RowsList = None, cols: ColsList = None
) -> PlDataFrame:
    indx_cols = cols if cols is not None else slice(None)
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
def frame_shape(data: DataFrameLike) -> tuple[int, ...]:
    raise TypeError(f"Unsupported type: {type(data)}")


@frame_shape.register
def _(data: PdDataFrame) -> tuple[int, ...]:
    return data.shape


@frame_shape.register
def _(data: PlDataFrame) -> tuple[int, ...]:
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
def frame_column_names(data: DataFrameLike) -> list[str]:
    raise TypeError(f"Unsupported type: {type(data)}")


@frame_column_names.register
def _(data: PdDataFrame) -> list[str]:
    return data.columns.to_list()


@frame_column_names.register
def _(data: PlDataFrame) -> list[str]:
    return data.columns
