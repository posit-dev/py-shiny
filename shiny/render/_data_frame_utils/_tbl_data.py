from __future__ import annotations

from typing import Any, List, Tuple, TypedDict, cast

import narwhals.stable.v1 as nw
import orjson

from ..._typing_extensions import TypeIs
from ...session import Session, require_active_session
from ...types import Jsonifiable, JsonifiableDict
from ._html import as_cell_html, ui_must_be_processed
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
    RowsList,
)

__all__ = (
    "is_into_data_frame",
    "as_data_frame",
    "data_frame_to_native",
    "apply_frame_patches",
    "serialize_dtype",
    "serialize_frame",
    "subset_frame",
    "get_frame_cell",
    "frame_shape",
    "copy_frame",
    "frame_column_names",
)

########################################################################################
# Narwhals
#
# This module contains functions for working with data frames. It is a wrapper
# around the Narwhals library, which provides a unified interface for working with
# data frames (e.g. Pandas and Polars).
#
# The functions in this module are used to:
# * convert data frames to and from the Narwhals format,
# * apply patches to data frames,
# * serialize data frames to JSON,
# * subset data frames,
# * and get information about data frames (e.g. shape, column names).
#
# The functions in this module are used by the Shiny framework to work with data frames.
#
# For more information on the Narwhals library, see:
# * Intro https://narwhals-dev.github.io/narwhals/basics/dataframe/
# * `nw.DataFrame`: https://narwhals-dev.github.io/narwhals/api-reference/dataframe/
# * `nw.typing.IntoDataFrameT`: https://narwhals-dev.github.io/narwhals/api-reference/typing/#intodataframet
#
########################################################################################


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
            compatible_data = compatible_to_pandas(data)
            return nw.from_native(compatible_data, eager_only=True)
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
            "A `.to_pandas()` was found on your data object and will be called. "
            "To remove this warning, please call `.to_pandas()` on your data "
            "and use the pandas result in your returned value. "
            "In the future, this will raise an error.",
            stacklevel=3,
        )
        return data.to_pandas()

    raise TypeError(f"Unsupported data type: {type(data)}")


# TODO-future; Replace with `nw.is_into_data_frame(x)`?
def is_into_data_frame(
    data: IntoDataFrameT | object,
) -> TypeIs[IntoDataFrameT]:
    nw_df = nw.from_native(data, strict=False, eager_only=True)
    if isinstance(nw_df, nw.DataFrame):
        return True
    return False


# apply_frame_patches --------------------------------------------------------------------
def apply_frame_patches(
    nw_data: DataFrame[IntoDataFrameT],
    patches: List[CellPatch],
) -> DataFrame[IntoDataFrameT]:
    # data = data.clone()

    if len(patches) == 0:
        return nw_data

    # Apply the patches

    # TODO-future-barret; Might be faster to _always_ store the patches as a
    #     `cell_patches_by_column` object. Then iff they need the patches would we
    #     deconstruct them into a flattened list. Where as this conversion is being
    #     performed on every serialization of the data frame payload

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
    #
    # In; patches: List[Dict[row_index: int, column_index: int, value: Any]]
    # Out; cell_patches_by_column: Dict[column_name: str, List[Dict[row_index: int, value: Any]]]
    #
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


# serialize_dtype ----------------------------------------------------------------------
def serialize_dtype(col: nw.Series) -> FrameDtype:

    from ._html import series_contains_htmltoolslike

    dtype: DType = col.dtype

    if isinstance(dtype, nw.String):
        type_ = "string"

    elif dtype.is_numeric():
        type_ = "numeric"

    elif isinstance(dtype, (nw.Categorical, nw.Enum)):
        categories = col.cat.get_categories().to_list()
        return {"type": "categorical", "categories": categories}
    elif isinstance(dtype, nw.Boolean):
        type_ = "boolean"
    elif isinstance(dtype, nw.Date):
        type_ = "date"
    elif isinstance(dtype, nw.Datetime):
        type_ = "datetime"
    elif isinstance(dtype, nw.Duration):
        type_ = "duration"
    elif isinstance(dtype, nw.Object):
        type_ = "object"
        if series_contains_htmltoolslike(col):
            type_ = "html"
    elif isinstance(dtype, (nw.Struct, nw.List, nw.Array)):
        type_ = "object"
    else:
        type_ = "unknown"
        if series_contains_htmltoolslike(col):
            type_ = "html"

    return {"type": type_}


# serialize_frame ----------------------------------------------------------------------
def serialize_frame(into_data: IntoDataFrame) -> FrameJson:

    data = as_data_frame(into_data)

    type_hints = [serialize_dtype(data[col_name]) for col_name in data.columns]

    # TODO-future-barret; Swich serialization to "by column", rather than "by row"
    # * This would allow for a single column to be serialized in a single operation
    #   * This would allow for each column to capture the `"html"` type hint properly
    #     for object and unknown columns. Currently, there is no way to determine which
    #     cells are HTML-like during orjson serialization.
    # * Even better, would be to move `orjson` serialization to the websocket
    #   serialization.
    #   * No need to serialize to JSON, then unserialize, then serialize again when
    #     sending it to the client!
    #   * The only serialization would occur during "send to browser"
    #   * This approach would lose the ability to upgrade the column type hints to "html"
    data_rows = data.rows(named=False)

    session: Session | None = None

    def default_orjson_serializer(val: Any) -> Jsonifiable:
        nonlocal session
        if ui_must_be_processed(val):
            if session is None:
                session = require_active_session(None)
            return cast(JsonifiableDict, dict(as_cell_html(val, session=session)))

        # All other values are serialized as strings
        return str(val)

    data_val = orjson.loads(
        orjson.dumps(
            data_rows,
            default=default_orjson_serializer,
            # option=(orjson.OPT_NAIVE_UTC),
        )
    )

    return {
        "columns": data.columns,
        "data": data_val,
        "typeHints": type_hints,
    }


# subset_frame -------------------------------------------------------------------------
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


# # get_frame_cell -----------------------------------------------------------------------
def get_frame_cell(data: DataFrame[Any], row: int, col: int) -> Any:
    return data.item(row, col)


# shape --------------------------------------------------------------------------------
def frame_shape(data: IntoDataFrame) -> Tuple[int, int]:
    nw_data = as_data_frame(data)
    return nw_data.shape


def column_is_numeric(nw_data: DataFrame[Any], column_index: int) -> bool:
    series_dtype: DType = nw_data[:, column_index].dtype
    return series_dtype.is_numeric()


# copy_frame ---------------------------------------------------------------------------
def copy_frame(nw_data: DataFrameT) -> DataFrameT:
    return nw_data.clone()


# column_names -------------------------------------------------------------------------
def frame_column_names(into_data: IntoDataFrame) -> List[str]:
    return as_data_frame(into_data).columns


class ScatterValues(TypedDict):
    row_indexes: list[int]
    values: list[CellValue]
