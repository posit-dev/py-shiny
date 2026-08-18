from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, TypedDict, cast

import narwhals.stable.v1 as nw
import orjson

from ...session import Session, require_active_session
from ...types import Jsonifiable, JsonifiableDict, ListOrTuple
from ._html import as_cell_html, ui_must_be_processed
from ._types import (
    CellHtml,
    CellPatch,
    CellValue,
    ColIndexes,
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
    "as_col_indexes",
    "as_data_frame",
    "data_frame_to_native",
    "apply_frame_patches",
    "serialize_dtype",
    "serialize_frame",
    "subset_frame",
)

if TYPE_CHECKING:
    import pandas as pd

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


def assert_data_is_not_none(data: IntoDataFrame) -> None:
    if data is None:  # pyright: ignore[reportUnnecessaryComparison]
        raise TypeError("`data` cannot be `None`")


def data_frame_to_native(data: DataFrame[IntoDataFrameT]) -> IntoDataFrameT:
    return nw.to_native(data)


def as_data_frame(
    data: IntoDataFrameT | DataFrame[IntoDataFrameT],
) -> DataFrame[IntoDataFrameT]:
    assert_data_is_not_none(data)

    if isinstance(data, DataFrame):
        return data  # pyright: ignore[reportUnknownVariableType]
    try:
        return nw.from_native(data, eager_only=True)
    except TypeError as e:
        try:
            compatible_data = compatible_to_pandas(data)
            ret: DataFrame[pd.DataFrame] = nw.from_native(
                compatible_data, eager_only=True
            )
            # Cast internal data as `IntoDataFrameT` type.
            # A warning has already been given to the user, so this is tolerable.
            return cast(DataFrame[IntoDataFrameT], ret)
        except TypeError:
            # Couldn't convert to pandas, so raise the original error
            raise e


def compatible_to_pandas(
    data: IntoDataFrame,
) -> pd.DataFrame:
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
        # pyright: ignore[reportReturnType]

    raise TypeError(f"Unsupported data type: {type(data)}")


# apply_frame_patches --------------------------------------------------------------------
def apply_frame_patches(
    nw_data: DataFrame[IntoDataFrameT],
    patches: List[CellPatch],
) -> DataFrame[IntoDataFrameT]:

    if len(patches) == 0:
        return nw_data

    # Apply the patches

    # Copy the data to make sure the original data is not modified in place.
    # If https://github.com/narwhals-dev/narwhals/issues/1154 is resolved, this
    # should be able to be removed.
    nw_data = nw_data.clone()

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
    # Out; cell_patches_by_column: Dict[column_index: int, List[Dict[row_index: int, value: Any]]]
    #
    # Patches arrive from the browser keyed by column *index*, and the column is read
    # back out positionally, so the column name never enters the lookup. Names are not
    # dependable keys: they may be empty or, in pandas, not even strings.
    cell_patches_by_column: dict[int, ScatterValues] = {}
    for cell_patch in patches:
        column_index = cell_patch["column_index"]
        if column_index not in cell_patches_by_column:
            cell_patches_by_column[column_index] = {
                "row_indexes": [],
                "values": [],
            }

        # Append the row index and value to the column information
        cell_patches_by_column[column_index]["row_indexes"].append(
            cell_patch["row_index"]
        )
        cell_patches_by_column[column_index]["values"].append(cell_patch["value"])

    # Upgrade the Scatter info to new column Series objects.
    # `nw_data[:, i]` selects positionally; the resulting Series keeps the column's
    # name, which is what `with_columns()` below matches on.
    scatter_columns = [
        nw_data[:, column_index].scatter(
            scatter_values["row_indexes"], scatter_values["values"]
        )
        for column_index, scatter_values in cell_patches_by_column.items()
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
    elif hasattr(nw, "Time") and isinstance(
        dtype,
        # https://github.com/narwhals-dev/narwhals/pull/2113
        nw.Time,  # pyright: ignore[reportUnknownMemberType,reportAttributeAccessIssue]
    ):
        type_ = "time"
    elif hasattr(nw, "Binary") and isinstance(
        dtype,
        # https://github.com/narwhals-dev/narwhals/pull/2243
        nw.Binary,  # pyright: ignore[reportUnknownMemberType,reportAttributeAccessIssue]
    ):
        type_ = "binary"
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

RenderedDependency = dict[str, Jsonifiable]


def serialize_frame(into_data: IntoDataFrame) -> FrameJson:

    data = as_data_frame(into_data)

    type_hints = [
        serialize_dtype(data.get_column(col_name)) for col_name in data.columns
    ]

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
    html_deps: list[RenderedDependency] = []

    # Collect all html deps and dedupe them. Send the html separately from its deps
    # Otherwise, serialize as `str()`
    def default_orjson_serializer(val: Any) -> Jsonifiable:
        nonlocal session
        if ui_must_be_processed(val):
            if session is None:
                session = require_active_session(None)

            processed_ui = session._process_ui(val)
            deps = processed_ui["deps"]
            if len(deps) > 0:
                html_deps.extend(deps)
            # Remove the deps from the rendered html as we'll send them separately
            # Maintain expected structure so that the JS will attempt to add all
            #   dependencies for patched cells in the same manner
            processed_ui["deps"] = []
            cell_html_obj: CellHtml = as_cell_html(processed_ui)
            return cast(JsonifiableDict, cell_html_obj)

        # All other values are serialized as strings
        return str(val)

    data_val = orjson.loads(
        orjson.dumps(
            data_rows,
            default=default_orjson_serializer,
            # option=(orjson.OPT_NAIVE_UTC),
        )
    )

    deduped_html_deps = (
        _resolve_processed_dependencies(html_deps) if len(html_deps) > 1 else html_deps
    )

    return {
        "columns": data.columns,
        "data": data_val,
        "typeHints": type_hints,
        "htmlDeps": deduped_html_deps,
    }


# as_col_indexes -----------------------------------------------------------------------
def as_col_indexes(data: DataFrame[Any], cols: ListOrTuple[str | int]) -> ColIndexes:
    """Resolve caller-supplied columns to column positions.

    This is the single place where a column name is turned into a column position.
    Everything downstream addresses columns by position only (:data:`ColIndexes`),
    because names are not dependable identifiers: they may be empty, and pandas allows
    names that are not strings.

    Parameters
    ----------
    data
        The data frame the columns belong to.
    cols
        Column names (`str`) or column positions (`int`).

        An `int` is **always** read as a position, never as a label. The two cannot be
        told apart otherwise, and narwhals reads a list of ints in the column slot
        positionally, so a pandas frame whose labels are ints (e.g. `{5: ..., 3: ...}`)
        must be addressed by position.

    Raises
    ------
    ValueError
        If a name is not a column of `data`.
    """
    col_indexes: list[int] = []
    for col in cols:
        if isinstance(col, int):
            col_indexes.append(col)
            continue
        try:
            col_indexes.append(data.columns.index(col))
        except ValueError:
            raise ValueError(
                f"Column name {col!r} not found in the data frame. "
                "To select a column by position, pass an `int`."
            ) from None
    return col_indexes


# subset_frame -------------------------------------------------------------------------
def subset_frame(
    data: DataFrameT,
    *,
    rows: RowsList = None,
    cols: ColsList = None,
) -> DataFrameT:
    """Return a subsetted DataFrame, based on row positions and column names or positions.

    Note that when None is passed, all rows or columns get included.

    Known narwhals behavior: on polars, selecting columns positionally renames a column
    whose name is `""` to `"column_0"`. Selecting rows only is unaffected.
    """
    # The nested if-else structure is used to navigate around narwhals' typing system and lack of `:` operator outside of `[`, `]`.

    # Note: pyright resolves `DataFrame.__getitem__` to the overload returning `Self`
    # (i.e. `DataFrameT`), but pyrefly resolves `Self` to the type variable's bound
    # (`DataFrame[Any]`), hence the pyrefly ignores on the subsetted returns.
    if cols is None:
        if rows is None:
            return data
        else:
            return data[rows, :]  # pyrefly: ignore[bad-return]
    else:
        # `cols` is not None. Resolve names to positions once, here, so that the
        # subsetting below only ever deals with positions.
        col_indexes = as_col_indexes(data, cols)

        # Return a DataFrame with no rows or columns
        # If there are no columns, there are no Series objects to support any rows
        if len(col_indexes) == 0:
            return data[[], []]  # pyrefly: ignore[bad-return]

        if rows is None:
            return data[:, col_indexes]  # pyrefly: ignore[bad-return]
        else:
            return data[rows, col_indexes]  # pyrefly: ignore[bad-return]


class ScatterValues(TypedDict):
    row_indexes: list[int]
    values: list[CellValue]


# Direct copy of htmltools._core._resolve_dependencies
# Need new method as we need to access dep values via `dep[NAME]` rather than `dep.NAME`
def _resolve_processed_dependencies(
    deps: list[RenderedDependency],
) -> list[RenderedDependency]:
    map: dict[str, RenderedDependency] = {}
    for dep in deps:
        dep_name = str(dep["name"])
        if dep_name not in map:
            map[dep_name] = dep
        else:
            dep_version = str(dep["version"])
            cur_dep_version = str(map[dep_name]["version"])
            if dep_version > cur_dep_version:
                map[dep_name] = dep

    return list(map.values())
