from __future__ import annotations

import abc
import json
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    Optional,
    Protocol,
    Sequence,
    TypedDict,
    Union,
    cast,
    runtime_checkable,
)

from htmltools import Tag

from .. import reactive, ui
from .._deprecated import ShinyDeprecationWarning
from .._docstring import add_example, no_example
from .._typing_extensions import Self
from ..session._utils import get_current_session, require_active_session
from ._dataframe_unsafe import serialize_numpy_dtypes
from .renderer import Jsonifiable, Renderer, ValueFn, output_dispatch_handler

if TYPE_CHECKING:
    import pandas as pd

    from ..session._utils import Session

# TODO-barret-future; make generic? By currently accepting `object`, it is difficult to capture the generic type of the data.
DataFrameResult = Union[None, "pd.DataFrame", "DataGrid", "DataTable"]


class CellUpdateFn(Protocol):
    async def __call__(
        self,
        *,
        info: CellUpdateInfo,
    ) -> Any: ...


class CellUpdateInfo(TypedDict):
    row_index: int
    column_index: int
    value: str
    prev: str


class CellsUpdateFn(Protocol):
    async def __call__(
        self,
        *,
        infos: list[CellUpdateInfo],
    ) -> list[Any]: ...
@dataclass
class CellPatch:
    row_index: int
    column_index: int
    value: str
    prev: str


class AbstractTabularData(abc.ABC):
    @abc.abstractmethod
    def to_payload(self) -> Jsonifiable: ...


EditMode = Literal["none", "edit"]
RowSelectionMode = Literal["none", "single_row", "multiple_row"]
# ColumnSelectionMode = Literal["single_col", "multiple_col"]
DataFrameMode = Union[
    EditMode,
    RowSelectionMode,
    # ColumnSelectionMode,
    Literal["none"],
]

RowSelectionModeDeprecated = Literal["single", "multiple", "none", "deprecated"]


class SelectedIndices(TypedDict):
    rows: tuple[int] | None
    columns: tuple[int] | None


# # TODO-future; Use `dataframe-api-compat>=0.2.6` to injest dataframes and return standardized dataframe structures
# # TODO-future: Find this type definition: https://github.com/data-apis/dataframe-api-compat/blob/273c0be45962573985b3a420869d0505a3f9f55d/dataframe_api_compat/polars_standard/dataframe_object.py#L22
# # Related: https://data-apis.org/dataframe-api-compat/quick_start/
# # Related: https://github.com/data-apis/dataframe-api-compat
# # Related: `.collect()` is needed. Boo. : https://data-apis.org/dataframe-api-compat/basics/dataframe/#__tabbed_2_2
# from dataframe_api import DataFrame as DataFrameStandard
# class ConsortiumNamespaceDataframe(Protocol):
#     def __dataframe_namespace__(self) -> DataFrameStandard: ...
# class ConsortiumStandardDataframe(Protocol):
#     def __dataframe_consortium_standard__(self,api_version: str) -> DataFrameStandard: ...
# # https://data-apis.org/dataframe-protocol/latest/purpose_and_scope.html#this-dataframe-protocol
# def get_compliant_df(
#     df: ConsortiumNamespaceDataframe | ConsortiumStandardDataframe,
# ) -> DataFrameStandard:
#     """Utility function to support programming against a dataframe API"""
#     if hasattr(df, "__dataframe_namespace__"):
#         # Is already Standard-compliant DataFrame, nothing to do here.
#         pass
#     elif hasattr(df, "__dataframe_consortium_standard__"):
#         # Convert to Standard-compliant DataFrame.
#         df = df.__dataframe_consortium_standard__(api_version="2023.11-beta")
#     else:
#         # Here we can raise an exception if we only want to support compliant dataframes,
#         # or convert to our default choice of dataframe if we want to accept (e.g.) dicts
#         raise TypeError(
#             "Expected Standard-compliant DataFrame, or DataFrame with Standard-compliant implementation"
#         )
#     return df


def as_mode(
    mode: DataFrameMode,
    *,
    name: str,
    row_selection_mode: RowSelectionModeDeprecated,
) -> DataFrameMode:
    if row_selection_mode == "deprecated":
        if mode == "edit":
            print(
                f"`{name}(mode='edit')` is an expirmental feature. If you find any bugs or would like different behavior, please make an issue at https://github.com/posit-dev/py-shiny/issues/new"
            )
        return mode
    ShinyDeprecationWarning(
        "`DataGraid(row_selection_mode=)` has been superseded by `DataGrid(mode=)`."
        ' Please use `DataGrid(mode="{row_selection_mode}_row")` instead.'
    )
    if row_selection_mode == "none":
        return "none"

    mode = cast(RowSelectionMode, f"{row_selection_mode}_row")
    return mode


@add_example(ex_dir="../api-examples/data_frame")
class DataGrid(AbstractTabularData):
    """
    Holds the data and options for a :class:`~shiny.render.data_frame` output, for a
    spreadsheet-like view.

    Parameters
    ----------
    data
        A pandas `DataFrame` object, or any object that has a `.to_pandas()` method
        (e.g., a Polars data frame or Arrow table).
    width
        A _maximum_ amount of horizontal space for the data grid to occupy, in CSS units
        (e.g. `"400px"`) or as a number, which will be interpreted as pixels. The
        default is `fit-content`, which sets the grid's width according to its contents.
        Set this to `100%` to use the maximum available horizontal space.
    height
        A _maximum_ amount of vertical space for the data grid to occupy, in CSS units
        (e.g. `"400px"`) or as a number, which will be interpreted as pixels. If there
        are more rows than can fit in this space, the grid will scroll. Set the height
        to `"auto"` to allow the grid to grow to fit all of the rows (this is not
        recommended for large data sets, as it may crash the browser).
    summary
        If `True` (the default), shows a message like "Viewing rows 1 through 10 of 20"
        below the grid when not all of the rows are being shown. If `False`, the message
        is not displayed. You can also specify a string template to customize the
        message, containing `{start}`, `{end}`, and `{total}` tokens. For example:
        `"Viendo filas {start} a {end} de {total}"`.
    filters
        If `True`, shows a row of filter inputs below the headers, one for each column.
    mode
        Single string to set the mode of the table.

        Supported values:
        * Use `"none"` to disable any cell selections or editing.
        * Use `"single_row"` to allow a single row to be selected at a time.
        * Use `"multiple_row"` to allow multiple rows to be selected by clicking on them individually.
        * Use `"edit"` to allow editing of the cells in the table.
    row_selection_mode
        Deprecated. Please use `mode={row_selection_mode}_row` instead.

    Returns
    -------
    :
        An object suitable for being returned from a `@render.data_frame`-decorated
        output function.

    See Also
    --------
    * :func:`~shiny.ui.output_data_frame`
    * :class:`~shiny.render.data_frame`
    * :class:`~shiny.render.DataTable`
    """

    def __init__(
        self,
        data: object,
        *,
        width: str | float | None = "fit-content",
        height: Union[str, float, None] = None,
        summary: Union[bool, str] = True,
        filters: bool = False,
        mode: DataFrameMode = "none",
        row_selection_mode: RowSelectionModeDeprecated = "deprecated",
    ):
        import pandas as pd

        self.data: pd.DataFrame = cast(
            pd.DataFrame,
            cast_to_pandas(
                data,
                "The DataGrid() constructor didn't expect a 'data' argument of type",
            ),
        )

        self.width = width
        self.height = height
        self.summary = summary
        self.filters = filters
        self.mode: DataFrameMode = as_mode(
            mode, name="DataGrid", row_selection_mode=row_selection_mode
        )

    def to_payload(self) -> Jsonifiable:
        res = serialize_pandas_df(self.data)
        res["options"] = dict(
            width=self.width,
            height=self.height,
            summary=self.summary,
            filters=self.filters,
            mode=self.mode,
            style="grid",
            fill=self.height is None,
        )
        return res


@no_example()
class DataTable(AbstractTabularData):
    """
    Holds the data and options for a :class:`~shiny.render.data_frame` output, for a
    spreadsheet-like view.

    Parameters
    ----------
    data
        A pandas `DataFrame` object, or any object that has a `.to_pandas()` method
        (e.g., a Polars data frame or Arrow table).
    width
        A _maximum_ amount of vertical space for the data table to occupy, in CSS units
        (e.g. `"400px"`) or as a number, which will be interpreted as pixels. The
        default is `fit-content`, which sets the table's width according to its
        contents. Set this to `100%` to use the maximum available horizontal space.
    height
        A _maximum_ amount of vertical space for the data table to occupy, in CSS units
        (e.g. `"400px"`) or as a number, which will be interpreted as pixels. If there
        are more rows than can fit in this space, the table body will scroll. Set the
        height to `None` to allow the table to grow to fit all of the rows (this is not
        recommended for large data sets, as it may crash the browser).
    summary
        If `True` (the default), shows a message like "Viewing rows 1 through 10 of 20"
        below the grid when not all of the rows are being shown. If `False`, the message
        is not displayed. You can also specify a string template to customize the
        message, containing `{start}`, `{end}`, and `{total}` tokens. For example:
        `"Viendo filas {start} a {end} de {total}"`.
    filters
        If `True`, shows a row of filter inputs below the headers, one for each column.
    mode
        Single string to set the mode of the table.

        Supported values:
        * Use `"none"` to disable any cell selections or editing.
        * Use `"single_row"` to allow a single row to be selected at a time.
        * Use `"multiple_row"` to allow multiple rows to be selected by clicking on them individually.
        * Use `"edit"` to allow editing of the cells in the table.
    row_selection_mode
        Deprecated. Please use `mode={row_selection_mode}_row` instead.

    Returns
    -------
    :
        An object suitable for being returned from a `@render.data_frame`-decorated
        output function.

    See Also
    --------
    * :func:`~shiny.ui.output_data_frame`
    * :class:`~shiny.render.data_frame`
    * :class:`~shiny.render.DataGrid`
    """

    def __init__(
        self,
        data: object,
        *,
        width: Union[str, float, None] = "fit-content",
        height: Union[str, float, None] = "500px",
        summary: Union[bool, str] = True,
        filters: bool = False,
        mode: DataFrameMode = "none",
        row_selection_mode: Literal["deprecated"] = "deprecated",
    ):
        import pandas as pd

        self.data: pd.DataFrame = cast(
            pd.DataFrame,
            cast_to_pandas(
                data,
                "The DataTable() constructor didn't expect a 'data' argument of type",
            ),
        )

        self.width = width
        self.height = height
        self.summary = summary
        self.filters = filters
        self.mode: DataFrameMode = as_mode(
            mode, name="DataTable", row_selection_mode=row_selection_mode
        )

    def to_payload(self) -> Jsonifiable:
        res = serialize_pandas_df(self.data)
        res["options"] = dict(
            width=self.width,
            height=self.height,
            summary=self.summary,
            filters=self.filters,
            mode=self.mode,
            style="table",
        )
        return res


def serialize_pandas_df(df: "pd.DataFrame") -> dict[str, Any]:
    columns = df.columns.tolist()
    columns_set = set(columns)
    if len(columns_set) != len(columns):
        raise ValueError(
            "The column names of the pandas DataFrame are not unique."
            " This is not supported by the data_frame renderer."
        )

    # Currently, we don't make use of the index; drop it so we don't error trying to
    # serialize it or something
    df = df.reset_index(drop=True)

    res = json.loads(
        # {index: [index], columns: [columns], data: [values]}
        df.to_json(None, orient="split")  # pyright: ignore[reportUnknownMemberType]
    )

    res["type_hints"] = serialize_numpy_dtypes(df)

    return res


@add_example()
class data_frame(Renderer[DataFrameResult]):
    """
    Decorator for a function that returns a pandas `DataFrame` object (or similar) to
    render as an interactive table or grid. Features fast virtualized scrolling, sorting,
    filtering, and row selection (single or multiple).

    Returns
    -------
    :
        A decorator for a function that returns any of the following:

        1. A :class:`~shiny.render.DataGrid` or :class:`~shiny.render.DataTable` object,
           which can be used to customize the appearance and behavior of the data frame
           output.
        2. A pandas `DataFrame` object. (Equivalent to
           `shiny.render.DataGrid(df)`.)
        3. Any object that has a `.to_pandas()` method (e.g., a Polars data frame or
           Arrow table). (Equivalent to `shiny.render.DataGrid(df.to_pandas())`.)

    Row selection
    -------------
    When using the row selection feature, you can access the selected rows by using the
    `<data_frame_renderer>.input_selected_rows()` method, where `<data_frame_renderer>`
    is the render function name that corresponds with the `id=` used in
    :func:`~shiny.ui.outout_data_frame`. Internally, this method retrieves the selected
    row value from session's `input.<id>_selected_rows()` value. The value returned will
    be `None` if the row selection mode is `"none"`, or a tuple of integers representing
    the indices of the selected rows. If no rows have been selected (while in a non-`"none"`
    row selection mode), an empty tuple will be returned. To filter a pandas data frame
    down to the selected rows, use `df.iloc[list(input.<id>_selected_rows())]`.

    Tip
    ----
    This decorator should be applied **before** the ``@output`` decorator (if that
    decorator is used). Also, the name of the decorated function (or
    ``@output(id=...)``) should match the ``id`` of a :func:`~shiny.ui.output_table`
    container (see :func:`~shiny.ui.output_table` for example usage).

    See Also
    --------
    * :func:`~shiny.ui.output_data_frame`
    * :class:`~shiny.render.DataGrid` and :class:`~shiny.render.DataTable` are the
      objects you can return from the rendering function to specify options.
    """

    _session: Session | None  # Do not use. Use `_get_session()` instead

    _value: reactive.Value[DataFrameResult | None]
    # _data: reactive.Value[pd.DataFrame | None]

    _cell_update_fn: CellUpdateFn
    _cells_update_fn: CellsUpdateFn

    cell_patches: reactive.Value[list[CellPatch]]

    data: reactive.Calc_[pd.DataFrame]
    """
    Reactive value of the data frame's output data.

    This is a quick reference to the original data frame that was returned from the app's render function. If it is mutated in place, it **will** modify the original data.
    """
    data_patched: reactive.Calc_[pd.DataFrame]
    """
    Reactive value of the data frame's edited output data.

    This is a shallow copy of the original data frame. It is possible that alterations to `data_patched` could alter the original `data` data frame. Please be cautious when using this value directly.

    See Also
    --------
    * [`pandas.DataFrame.copy` API documentation]h(ttps://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.copy.html)
    """
    table_mode: reactive.Calc_[DataFrameMode]
    """
    Reactive value of the data frame's row selection mode.
    """

    input_selected: reactive.Calc_[SelectedIndices | None]
    """
    Reactive value of selected rows indices.

    This method is a wrapper around `input.<id>_selected_rows()`, where `<id>` is
    the `id` of the data frame output. This method returns the selected rows and
    will cause reactive updates as the selected rows change.

    Returns
    -------
    :
        * `None` if the row selection mode is None
        * `tuple[int]` representing the indices of the selected rows. If no rowws are selected
    """

    data_selected: reactive.Calc_[pd.DataFrame]
    """
    Reactive value that returns the edited data frame subsetted to the selected area.

    Returns
    -------
    :
        * If the row selection mode is `None`, the calculation will throw a silent error (`req(False)`)
        * The edited data (`.data_patched()`) at the indices of the selected rows
    """

    def _init_reactives(self) -> None:

        import pandas as pd

        from .. import req

        # Init
        self._value: reactive.Value[Union[DataFrameResult, None]] = reactive.Value(None)
        self.cell_patches: reactive.Value[list[CellPatch]] = reactive.Value([])

        @reactive.calc
        def self_data() -> pd.DataFrame:
            value = self._value()
            req(value)

            if not isinstance(value, (DataGrid, DataTable)):
                raise TypeError(
                    f"Unsupported type returned from render function: {type(value)}. Expected `DataGrid` or `DataTable`"
                )

            if not isinstance(value.data, pd.DataFrame):
                raise TypeError(f"Unexpected type for self._data: {type(value.data)}")

            return value.data

        self.data = self_data

        @reactive.calc
        def self_table_mode() -> DataFrameMode:
            value = self._value()
            req(value)
            if not isinstance(value, (DataGrid, DataTable)):
                raise TypeError(
                    f"Unsupported type returned from render function: {type(value)}. Expected `DataGrid` or `DataTable`"
                )

            return value.mode

        self.table_mode = self_table_mode

        @reactive.calc
        def self_input_selected() -> SelectedIndices | None:
            mode = self.table_mode()
            if mode == "none":
                return None
            return {
                "rows": self._get_session().input[f"{self.output_id}_selected_rows"](),
                "columns": None,
            }

        self.input_selected = self_input_selected

        @reactive.calc
        def self_data_selected() -> pd.DataFrame:
            indices = self.input_selected()
            if indices is None:
                req(False)
                raise RuntimeError("This should never be reached for typing purposes")

            data_selected = self.data_patched()
            if indices["rows"] is not None:
                data_selected = data_selected.iloc[list(indices["rows"])]
            if indices["columns"] is not None:
                data_selected = data_selected.iloc[:, list(indices["columns"])]
            return data_selected

        self.data_selected = self_data_selected

        @reactive.calc
        def self_data_patched() -> pd.DataFrame:
            # Enable copy-on-write mode for the data;
            # Use `deep=False` to avoid copying the full data; CoW will copy the necessary data when modified
            with pd.option_context("mode.copy_on_write", True):
                data = self.data().copy(deep=False)
                for cell_patch in self.cell_patches():
                    data.iat[  # pyright: ignore[reportUnknownMemberType]
                        cell_patch.row_index,
                        cell_patch.column_index,
                    ] = cell_patch.value

                return data

        self.data_patched = self_data_patched

    def _get_session(self) -> Session:
        if self._session is None:
            raise RuntimeError(
                "The data frame's session can only be accessed within a reactive context"
            )
        return self._session

    def set_cell_update_fn(self, fn: CellUpdateFn) -> Self:
        self._cell_update_fn = fn
        return self

    def set_cells_update_fn(self, fn: CellsUpdateFn) -> Self:
        self._cells_update_fn = fn
        return self

    def _init_handlers(self) -> None:
        async def _set_cell_update_default(
            *,
            info: CellUpdateInfo,
            # row_index: int,
            # column_index: int,
            # value: str,
            # prev: str,
            **kwargs: Any,
        ) -> str:
            return info["value"]

        async def _set_cells_update_default(
            *,
            infos: list[CellUpdateInfo],
            **kwargs: Any,
        ):
            with reactive.isolate():
                formatted_values: list[Any] = []
                for update_info in infos:
                    # row_index = update_info["row_index"]
                    # column_index = update_info["column_index"]
                    # value = update_info["value"]
                    # prev = update_info["prev"]

                    formatted_value = await self._cell_update_fn(info=update_info)
                    #     row_index=row_index,
                    #     column_index=column_index,
                    #     value=value,
                    #     prev=prev,
                    # )
                    # TODO-barret; check type here?
                    # TODO-barret; The return value should be coerced by pandas to the correct type
                    formatted_values.append(formatted_value)

                return formatted_values

        self.set_cell_update_fn(_set_cell_update_default)
        self.set_cells_update_fn(_set_cells_update_default)
        # self._add_message_handlers()

    # To be called by session's output_handler message handler on this data_frame instance
    @output_dispatch_handler
    # Do not change this method name unless you update corresponding code in `/js/dataframe/`!!
    async def _handle_cells_update(self, update_infos: list[CellUpdateInfo]):

        # Make new array to trigger reactive update
        patches = self.cell_patches().copy()

        # Call user's cell update method to retrieve formatted values
        updated_raw_values = await self._cells_update_fn(infos=update_infos)

        if (not isinstance(updated_raw_values, list)) or len(updated_raw_values) != len(
            update_infos
        ):
            raise ValueError(
                f"The return value of {self.output_id}'s `handle_cells_update()` "
                f"(typically set by `@{self.output_id}.set_cells_update_fn`) "
                "must be a list of the same length as the input list of cell updates. "
                f"Received {len(updated_raw_values)} items and expected {len(update_infos)}."
            )

        # Add new patches
        for updated_raw_value, update_info in zip(updated_raw_values, update_infos):
            patches.append(
                CellPatch(
                    row_index=update_info["row_index"],
                    column_index=update_info["column_index"],
                    value=updated_raw_value,
                    prev=update_info["prev"],
                )
            )

        # Remove duplicate patches
        patch_map: dict[tuple[int, int], CellPatch] = {}
        for patch in patches:
            patch_map[(patch.row_index, patch.column_index)] = patch
        patches = list(patch_map.values())

        # Set new patches
        self.cell_patches.set(patches)

        return updated_raw_values

    def auto_output_ui(self) -> Tag:
        return ui.output_data_frame(id=self.output_id)

    def __init__(self, fn: ValueFn[DataFrameResult]):
        # MUST be done before super().__init__ is called as `_set_output_metadata` is called in `super().__init__` during auto registration of the output
        session = get_current_session()
        self._session = session

        super().__init__(fn)

        # Set reactives from calculated properties
        self._init_reactives()
        # Set update functions
        self._init_handlers()

    def _set_output_metadata(self, *, output_id: str) -> None:
        super()._set_output_metadata(output_id=output_id)

        # Verify that the session used (during `__init__`) when creating the renderer is
        # the same session used when executing the renderer. This is to prevent a user
        # from creating a renderer in one module and registering it on an output with a
        # different session.

        active_session = require_active_session(None)
        if self._get_session() != active_session:
            raise RuntimeError(
                "The session used when creating the renderer "
                "is not the same session used when executing the renderer. "
                "Please file an issue on "
                "GitHub <https://github.com/posit-dev/py-shiny/issues/new> "
                "with an example of how you are reproducing this error. "
                "We would be curious to know your use case!"
            )

    async def render(self) -> Jsonifiable:
        # Reset value
        self._value.set(None)
        self.cell_patches.set([])

        value = await self.fn()
        if value is None:
            return None

        if not isinstance(value, AbstractTabularData):
            value = DataGrid(
                cast_to_pandas(
                    value,
                    "@render.data_frame doesn't know how to render objects of type",
                )
            )

        self._value.set(value)
        return value.to_payload()

    async def _send_message_to_browser(self, handler: str, obj: dict[str, Any]):

        session = self._get_session()
        id = session.ns(self.output_id)

        await session.send_custom_message(
            "shinyDataFrameMessage",
            {
                "id": id,
                "handler": handler,
                "obj": obj,
            },
        )

    async def update_row_selection(
        self, idx: Optional[Sequence[int] | int] = None
    ) -> None:
        if idx is None:
            idx = ()
        elif isinstance(idx, int):
            idx = (idx,)

        with reactive.isolate():
            mode = self.table_mode()
        if mode == "none":
            raise ValueError(
                "You can't update row selections when row_selection_mode is 'none'"
            )

        if mode == "single_row" and len(idx) > 1:
            raise ValueError(
                "Attempted to set multiple row selection values when row_selection_mode is 'single'"
            )
        await self._send_message_to_browser("updateRowSelection", {"keys": idx})

    def input_selected_rows(self) -> Optional[tuple[int]]:
        """
        When `row_selection_mode` is set to "single" or "multiple" this will return
        a tuple of integers representing the rows selected by a user.
        """

        active_session = require_active_session(None)
        return active_session.input[self.output_id + "_selected_rows"]()


@runtime_checkable
class PandasCompatible(Protocol):
    # Signature doesn't matter, runtime_checkable won't look at it anyway
    def to_pandas(self) -> object: ...


def cast_to_pandas(x: object, error_message_begin: str) -> object:
    import pandas as pd

    if not isinstance(x, pd.DataFrame):
        if not isinstance(x, PandasCompatible):
            raise TypeError(
                error_message_begin
                + f" '{str(type(x))}'. Use either a pandas.DataFrame, or an object"
                " that has a .to_pandas() method."
            )
        return x.to_pandas()
    return x
