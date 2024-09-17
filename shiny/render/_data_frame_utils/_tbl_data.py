# Note - barret 2024-07-08; When we adopt `narwhals` support, we should remove the singledispatch and instead always use `narwhals`. In addition, we should return the native type of a native type was originally provided. (Or maintain the narwhals object, if a narwhals object was provided.)

from __future__ import annotations

from functools import singledispatch
from typing import Any, List, Tuple, TypedDict

import narwhals.stable.v1 as nw
from htmltools import TagNode

from ..._typing_extensions import TypeIs
from ...session import require_active_session
from ._html import maybe_as_cell_html
from ._types import (
    CellPatch,
    CellValue,
    ColsList,
    DataFrame,
    DataFrameT,
    DType,
    FrameDtype,
    FrameJson,
    IntoDataFrame,
    IntoDataFrameT,
    PandasCompatible,
    PdDataFrame,
    RowsList,
    SeriesLike,
)

__all__ = (
    "is_into_data_frame",
    # "as_data_frame_like",
    "as_data_frame",
    "data_frame_to_native",
    # "frame_columns",
    "apply_frame_patches",
    "serialize_dtype",
    "serialize_frame",
    "subset_frame",
    # "get_frame_cell",
    "frame_shape",
    "copy_frame",
    "frame_column_names",
)


# as_frame -----------------------------------------------------------------------------


def data_frame_to_native(data: DataFrame[IntoDataFrameT]) -> IntoDataFrameT:
    return nw.to_native(data)


def as_data_frame(
    data: IntoDataFrameT | DataFrame[IntoDataFrameT],
) -> DataFrame[IntoDataFrameT]:
    if isinstance(data, DataFrame):
        return data  # pyright: ignore[reportUnknownVariableType]
    try:
        return nw.from_native(data, eager_only=True)
    except TypeError as e:
        try:
            return nw.from_native(compatible_to_pandas(data), eager_only=True)
        except TypeError:
            # Couldn't convert to pandas, so raise the original error
            raise e


def compatible_to_pandas(
    data: IntoDataFrameT,
) -> IntoDataFrameT:
    """
    Convert data to pandas, if possible.

    Should only call this method if Narwhals can not handle the data directly.
    """
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


# TODO-barret; Replace with `nw.is_into_data_frame(x)`?
def is_into_data_frame(
    data: IntoDataFrameT | object,
) -> TypeIs[IntoDataFrameT]:
    nw_df = nw.from_native(data, strict=False, eager_only=True)
    if isinstance(nw_df, nw.DataFrame):
        return True
    return False


# # frame_columns ------------------------------------------------------------------------


# @singledispatch
# def frame_columns(data: IntoDataFrame) -> ListSeriesLike:
#     raise TypeError(f"Unsupported type: {type(data)}")


# @frame_columns.register
# def _(data: PdDataFrame) -> ListSeriesLike:
#     ret = [cast(PlSeries, data[col]) for col in data.columns]
#     return ret


# @frame_columns.register
# def _(data: PlDataFrame) -> ListSeriesLike:
#     return data.get_columns()


# apply_frame_patches --------------------------------------------------------------------


# def apply_frame_patches__typed(
#     data: IntoDataFrameT, patches: List[CellPatch]
# ) -> IntoDataFrameT:
#     return cast(IntoDataFrameT, apply_frame_patches(data, patches))


# @singledispatch
# def apply_frame_patches(
#     data: IntoDataFrame,
#     patches: List[CellPatch],
# ) -> IntoDataFrame:
#     raise TypeError(f"Unsupported type: {type(data)}")


# @apply_frame_patches.register
# def _(data: PdDataFrame, patches: List[CellPatch]) -> PdDataFrame:
#     import pandas as pd

#     # Enable copy-on-write mode for the data;
#     # Use `deep=False` to avoid copying the full data; CoW will copy the necessary data when modified
#     with pd.option_context("mode.copy_on_write", True):
#         # Apply patches!
#         data = data.copy(deep=False)
#         for cell_patch in patches:
#             data.iat[  # pyright: ignore[reportUnknownMemberType]
#                 cell_patch["row_index"],
#                 cell_patch["column_index"],
#             ] = cell_patch["value"]

#         return data


# @apply_frame_patches.register
# def _(data: PlDataFrame, patches: List[CellPatch]) -> PlDataFrame:
#     data = data.clone()
#     for cell_patch in patches:
#         data[cell_patch["row_index"], cell_patch["column_index"]] = cell_patch["value"]

#     return data


# @apply_frame_patches.register(DataFrame)
def apply_frame_patches(
    nw_data: DataFrame[IntoDataFrameT],
    patches: List[CellPatch],
) -> DataFrame[IntoDataFrameT]:
    # data = data.clone()

    if len(patches) == 0:
        return nw_data

    # Us an index to know which row we are updating
    data_with_index = nw_data.with_row_index()

    # Apply the patches

    # If multiple `when` statements are possible, then use this code
    if True:
        # # https://discord.com/channels/1235257048170762310/1235257049626181656/1283415086722977895
        # # Using narwhals >= v1.7.0
        # @nw.narwhalify
        # def func(df):
        #     return df.with_columns(
        #         df['a'].scatter([0, 1], [999, 888]),
        #         df['b'].scatter([0, 1], [777, 555]),
        #     )

        # Group patches by column
        # This allows for a single column to be updated in a single operation (rather than multiple updates to the same column)

        cell_patches_by_column: dict[str, ScatterValues] = {}
        for cell_patch in patches:
            column_name = nw_data.columns[cell_patch["column_index"]]
            if column_name not in cell_patches_by_column:
                cell_patches_by_column[column_name] = {
                    "row_indexes": [],
                    "values": [],
                }

            # Append the row index and value to the column information
            cell_patches_by_column[column_name]["row_indexes"].append(
                cell_patch["row_index"]
            )
            cell_patches_by_column[column_name]["values"].append(cell_patch["value"])

        # Upgrade the Scatter info to new column Series objects
        scatter_columns = [
            nw_data[column_name].scatter(
                scatter_values["row_indexes"], scatter_values["values"]
            )
            for column_name, scatter_values in cell_patches_by_column.items()
        ]
        # Apply patches to the nw data
        return nw_data.with_columns(*scatter_columns)

        # Documentation for nw.when: https://narwhals-dev.github.io/narwhals/api-reference/narwhals/#narwhals.when
        # when_then_otherwise_arr: List[IntoExpr] = []

        for column_name, cell_patches in cell_patches_by_column.items():
            col_expr = nw.when(
                nw.col("index") == cell_patches[0]["row_index"],
            ).then(cell_patches[0]["value"])

            for i, cell_patch in enumerate(cell_patches):
                if i == 0:
                    # Performed above to get typing value
                    continue
                col_expr = col_expr.when(
                    nw.col("index") == cell_patch["row_index"],
                ).then(cell_patch["value"])

            col_expr = col_expr.alias(column_name)
            # when_then_otherwise_arr.append(col_expr)
    else:
        # https://discord.com/channels/1235257048170762310/1235257049626181656/1283078606775517184
        # Very inefficient code that works to update a cell by making a new column for every patch value
        for cell_patch in patches:
            data_with_index = data_with_index.with_columns(
                nw.when(nw.col("index") == cell_patch["row_index"])
                .then(cell_patch["value"])
                .otherwise(nw.col(nw_data.columns[cell_patch["column_index"]]))
            )

    patched_data = data_with_index.drop("index")

    return patched_data


# serialize_dtype ----------------------------------------------------------------------


@singledispatch
def serialize_dtype(col: SeriesLike) -> FrameDtype:
    raise TypeError(f"Unsupported type: {type(col)}")


# TODO: we can't import DataFrameDtype at runtime, due to circular dependency. So
# we import it during type checking. But this means we have to explicitly register
# the dispatch type below.


# @serialize_dtype.register
# def _(col: PdSeries) -> FrameDtype:
#     from ._pandas import serialize_pd_dtype

#     return serialize_pd_dtype(col)


# @serialize_dtype.register
# def _(col: PlSeries) -> FrameDtype:
#     import polars as pl

#     from ._html import col_contains_shiny_html

#     if col.dtype == pl.String():
#         if col_contains_shiny_html(col):
#             type_ = "html"
#         else:
#             type_ = "string"
#     elif col.dtype.is_numeric():
#         type_ = "numeric"

#     elif col.dtype.is_(pl.Categorical()):
#         categories = col.cat.get_categories().to_list()
#         return {"type": "categorical", "categories": categories}
#     else:
#         type_ = "unknown"
#         if col_contains_shiny_html(col):
#             type_ = "html"

#     return {"type": type_}


nw_boolean = nw.Boolean()
nw_categorical = nw.Categorical()
nw_enum = nw.Enum()
nw_string = nw.String()
nw_datetime = nw.Datetime()
nw_duration = nw.Duration()
nw_object = nw.Object()


@serialize_dtype.register
def _(col: nw.Series) -> FrameDtype:

    from ._html import col_contains_shiny_html

    dtype: DType = col.dtype

    if dtype == nw_string:
        if col_contains_shiny_html(col):
            type_ = "html"
        else:
            type_ = "string"
    elif dtype.is_numeric():
        type_ = "numeric"

    elif dtype == nw_categorical:
        categories = col.cat.get_categories().to_list()
        return {"type": "categorical", "categories": categories}
    elif dtype == nw_enum:
        raise NotImplementedError("TODO-barret; enum type not tested")
        cat_col = col.cast(nw.Categorical)
        categories = cat_col.cat.get_categories().to_list()
        return {"type": "categorical", "categories": categories}

    elif dtype == nw_boolean:
        raise NotImplementedError("TODO-barret; boolean type not tested")
        type_ = "boolean"
    elif dtype == nw_duration:
        raise NotImplementedError(
            "TODO-barret; duration type not tested. Look at pandas timedelta"
        )
        type_ = "duration"
    elif dtype == nw_datetime:
        type_ = "datetime"
    elif dtype == nw_object:
        type_ = "object"
        if col_contains_shiny_html(col):
            type_ = "html"

    else:
        type_ = "unknown"
        if col_contains_shiny_html(col):
            type_ = "html"

    return {"type": type_}


# serialize_frame ----------------------------------------------------------------------


# @singledispatch
# def serialize_frame(data: IntoDataFrame) -> FrameJson:
#     raise TypeError(f"Unsupported type: {type(data)}")


# @serialize_frame.register
# def _(data: PdDataFrame) -> FrameJson:
#     from ._pandas import serialize_frame_pd

#     return serialize_frame_pd(data)


# # TODO: test this
# @serialize_frame.register
# def _(data: PlDataFrame) -> FrameJson:
#     import json

#     type_hints = list(map(serialize_dtype, data))
#     data_by_row = list(map(list, data.rows()))

#     # Shiny tag support
#     type_hints_type = [type_hint["type"] for type_hint in type_hints]
#     if "html" in type_hints_type:
#         session = require_active_session(None)

#         def wrap_shiny_html_with_session(x: TagNode):
#             return maybe_as_cell_html(x, session=session)

#         html_columns = [i for i, x in enumerate(type_hints_type) if x == "html"]

#         for html_column in html_columns:
#             for row in data_by_row:
#                 row[html_column] = wrap_shiny_html_with_session(row[html_column])

#     data_val = json.loads(json.dumps(data_by_row, default=str))

#     return {
#         # "index": list(range(len(data))),
#         "columns": data.columns,
#         "data": data_val,
#         "typeHints": type_hints,
#     }

# try:
#     import pandas as pd  # type: ignore # noqa: F401

#     has_pandas = True
# except ImportError:
#     has_pandas = False


# @serialize_frame.register(DataFrame)
def serialize_frame(into_data: IntoDataFrame) -> FrameJson:
    # def _(data: DataFrame[Any]) -> FrameJson:

    data = as_data_frame(into_data)

    type_hints = [serialize_dtype(data[col_name]) for col_name in data.columns]
    type_hints_type = [type_hint["type"] for type_hint in type_hints]

    data_rows = data.rows(named=False)

    # print(data_rows)
    # print(data.rows(named=False))

    # Shiny tag support
    if "html" in type_hints_type:
        session = require_active_session(None)

        def wrap_shiny_html_with_session(x: TagNode):
            return maybe_as_cell_html(x, session=session)

        html_column_positions = [
            i for i, x in enumerate(type_hints_type) if x == "html"
        ]

        new_rows: list[tuple[Any, ...]] = []

        # Wrap the corresponding columns with the cell html object
        for row in data_rows:
            new_row = list(row)
            for html_column_position in html_column_positions:
                new_row[html_column_position] = wrap_shiny_html_with_session(
                    new_row[html_column_position]
                )
            new_rows.append(tuple(new_row))

        data_rows = new_rows

    import orjson

    # TODO-barret; Remove debug! Maybe?
    native_data = nw.to_native(data)
    if isinstance(native_data, PdDataFrame):
        from pandas import Timestamp

        def my_str(x: Any) -> str:
            print("x", x)
            if isinstance(x, Timestamp):
                return x.isoformat()

            return str(x)

    else:

        def my_str(x: Any) -> str:
            return str(x)

    data_val = orjson.loads(
        orjson.dumps(
            data_rows,
            default=my_str,
            # option=(orjson.OPT_NAIVE_UTC),
        )
    )

    # import json
    # data_val = json.loads(json.dumps(data_rows, default=str))

    return {
        "columns": data.columns,
        "data": data_val,
        "typeHints": type_hints,
    }


# subset_frame -------------------------------------------------------------------------
# @singledispatch
def subset_frame(
    data: DataFrameT,
    *,
    rows: RowsList = None,
    cols: ColsList = None,
) -> DataFrameT:
    """Return a subsetted DataFrame, based on row positions and column names.

    Note that when None is passed, all rows or columns get included.
    """

    # Note that this type signature assumes column names are strings things.
    # This is always true in Polars, but not in Pandas (e.g. a column name could be an
    # int, or even a tuple of ints)
    if cols is None:
        if rows is None:
            return data
        else:
            # This feels like it should be `data[rows, :]` but that doesn't work for polars
            # https://github.com/narwhals-dev/narwhals/issues/989
            # Must use `list(rows)` as tuples are not supported
            # https://github.com/narwhals-dev/narwhals/issues/990
            return data[list(rows), data.columns]
    else:
        # `cols` is not None
        col_names = [data.columns[col] if isinstance(col, int) else col for col in cols]
        # If len(cols) == 0, then we should return an empty DataFrame
        # Currently this is broken when backed by pandas.
        # https://github.com/narwhals-dev/narwhals/issues/989
        if len(col_names) == 0:
            # Return a DataFrame with no rows or columns
            # If there are no columns, there are no Series objects to support any rows
            return data[[], []]

        if rows is None:
            return data[:, col_names]
        else:
            # Be sure rows is a list, not a tuple. Tuple
            return data[list(rows), col_names]


# @subset_frame.register
# def _(
#     data: PdDataFrame,
#     *,
#     rows: RowsList = None,
#     cols: ColsList = None,
# ) -> PdDataFrame:
#     # Enable copy-on-write mode for the data;
#     # Use `deep=False` to avoid copying the full data; CoW will copy the necessary data when modified
#     import pandas as pd

#     with pd.option_context("mode.copy_on_write", True):
#         # iloc requires integer positions, so we convert column name strings to ints, or
#         # the slice default.
#         indx_cols = (  # pyright: ignore[reportUnknownVariableType]
#             slice(None)
#             if cols is None
#             else [
#                 (
#                     # Send in an array of size 1 and retrieve the first element
#                     data.columns.get_indexer_for(  # pyright: ignore[reportUnknownMemberType]
#                         [col]
#                     )[
#                         0
#                     ]
#                     if isinstance(col, str)
#                     else col
#                 )
#                 for col in cols
#             ]
#         )

#         # Force list when using a non-None value for pandas compatibility
#         indx_rows = list(rows) if rows is not None else slice(None)

#         return data.iloc[indx_rows, indx_cols]


# @subset_frame.register
# def _(
#     data: PlDataFrame,
#     *,
#     rows: RowsList = None,
#     cols: ColsList = None,
# ) -> PlDataFrame:
#     indx_cols = (
#         [col if isinstance(col, str) else data.columns[col] for col in cols]
#         if cols is not None
#         else slice(None)
#     )
#     indx_rows = rows if rows is not None else slice(None)
#     return data[indx_cols][indx_rows]


# # get_frame_cell -----------------------------------------------------------------------


# @singledispatch
# def get_frame_cell(data: IntoDataFrame, row: int, col: int) -> Any:
#     raise TypeError(f"Unsupported type: {type(data)}")


# @get_frame_cell.register
# def _(data: PdDataFrame, row: int, col: int) -> Any:
#     return (
#         data.iat[  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
#             row, col
#         ]
#     )


# @get_frame_cell.register(DataFrame)
# @get_frame_cell.register
# def _(data: PlDataFrame, row: int, col: int) -> Any:
#     return data.item(row, col)


# shape --------------------------------------------------------------------------------


# @singledispatch
# def frame_shape(data: IntoDataFrame) -> Tuple[int, int]:
#     raise TypeError(f"Unsupported type: {type(data)}")


# # @frame_shape.register
# # def _(data: PdDataFrame) -> Tuple[int, int]:
# #     return data.shape


# # @frame_shape.register
# # def _(data: PlDataFrame) -> Tuple[int, int]:
# #     return data.shape


# @frame_shape.register(DataFrame)
# def _(data: DataFrame[Any]) -> Tuple[int, int]:
#     return data.shape


def frame_shape(data: IntoDataFrame) -> Tuple[int, int]:
    nw_data = as_data_frame(data)
    return nw_data.shape


def column_is_numeric(nw_data: DataFrame[Any], column_index: int) -> bool:
    series_dtype: DType = nw_data[:, column_index].dtype
    return series_dtype.is_numeric()


# copy_frame ---------------------------------------------------------------------------


def copy_frame(nw_data: DataFrameT) -> DataFrameT:
    return nw_data.clone()


# @singledispatch
# def copy_frame(data: IntoDataFrame) -> IntoDataFrame:
#     raise TypeError(f"Unsupported type: {type(data)}")


# @copy_frame.register
# def _(data: PdDataFrame) -> PdDataFrame:
#     return data.copy()


# @copy_frame.register(DataFrame)
# @copy_frame.register
# def _(data: PlDataFrame) -> PlDataFrame:
#     return data.clone()


# column_names -------------------------------------------------------------------------
# @singledispatch
# def frame_column_names(data: IntoDataFrame) -> List[str]:
#     raise TypeError(f"Unsupported type: {type(data)}")


# # @frame_column_names.register
# # def _(data: PdDataFrame) -> List[str]:
# #     return data.columns.to_list()

# # @frame_column_names.register
# # def _(data: PlDataFrame) -> List[str]:
# #     return data.columns


# @frame_column_names.register(DataFrame)
# def _(data: DataFrame[Any]) -> List[str]:
#     return data.columns


def frame_column_names(into_data: IntoDataFrame) -> List[str]:
    return as_data_frame(into_data).columns


class ScatterValues(TypedDict):
    row_indexes: list[int]
    values: list[CellValue]
