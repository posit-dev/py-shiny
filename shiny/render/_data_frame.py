from __future__ import annotations

import warnings

# TODO-barret-render.data_frame; Docs
# TODO-barret-render.data_frame; Add examples!
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Dict,
    Literal,
    TypeVar,
    Union,
    cast,
)

from htmltools import Tag

from .. import reactive, ui
from .._docstring import add_example
from .._typing_extensions import Self, TypedDict
from .._utils import wrap_async
from ..session._utils import (
    get_current_session,
    require_active_session,
    session_context,
)
from ._data_frame_utils import (
    AbstractTabularData,
    CellPatch,
    CellPatchProcessed,
    CellSelection,
    CellValue,
    DataGrid,
    DataTable,
    PatchesFn,
    PatchesFnSync,
    PatchFn,
    PatchFnSync,
    SelectionModes,
    as_cell_selection,
    assert_patches_shape,
    cast_to_pandas,
    cell_patch_processed_to_jsonifiable,
    wrap_shiny_html,
)

# as_selection_location_js,
from .renderer import Jsonifiable, Renderer, ValueFn

if TYPE_CHECKING:
    import pandas as pd

    from ..session._utils import Session

    DataFrameT = TypeVar("DataFrameT", bound=pd.DataFrame)
    # TODO-barret-render.data_frame; Pandas, Polars, api compat, etc.; Today, we only support Pandas


from ._data_frame_utils._datagridtable import DataFrameResult


class SelectedIndices(TypedDict):
    rows: tuple[int] | None
    columns: tuple[int] | None


class ColumnSort(TypedDict):
    id: str
    desc: bool


class ColumnFilterStr(TypedDict):
    id: str
    value: str


class ColumnFilterNumber(TypedDict):
    id: str
    value: tuple[float, float]


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
    `<data_frame_renderer>.input_cell_selection()` method, where `<data_frame_renderer>`
    is the render function name that corresponds with the `id=` used in
    :func:`~shiny.ui.outout_data_frame`. Internally, this method retrieves the selected
    cell information from session's `input.<id>_cell_selection()` value. The value
    returned will be `None` if the row selection mode is `"none"`, or a tuple of
    integers representing the indices of the selected rows. If no rows have been
    selected (while in a non-`"none"` row selection mode), an empty tuple will be
    returned. To filter a pandas data frame down to the selected rows, use
    `<data_frame_renderer>.data_view()` or
    `df.iloc[list(input.<id>_cell_selection()["rows"])]`.

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
    _type_hints: reactive.Value[dict[str, str] | None]
    # _data: reactive.Value[pd.DataFrame | None]

    _patch_fn: PatchFn
    _patches_fn: PatchesFn

    _cell_patch_map: reactive.Value[dict[tuple[int, int], CellPatchProcessed]]
    """
    Reactive map of patches to be applied to the data frame.

    The key is defined as `(row_index, column_index)`, and the value is a `CellPatch`.

    This map is used for faster deduplications of patches at each location.
    """
    cell_patches: reactive.Calc_[list[CellPatchProcessed]]

    data: reactive.Calc_[pd.DataFrame]
    """
    Reactive value of the data frame's output data.

    This is a quick reference to the original data frame that was returned from the
    app's render function. If it is mutated in place, it **will** modify the original
    data.
    """
    _data_view: reactive.Calc_[pd.DataFrame]
    _data_view_selected: reactive.Calc_[pd.DataFrame]

    def data_view(self, *, selected: bool = False) -> pd.DataFrame:
        """
        Reactive function to retrieve the data how it is viewed within the browser.

        This function will sort, filter, and apply any patches to the data frame as viewed
        by the user within the browser.

        This is a shallow copy of the original data frame. It is possible that alterations
        to `data_view` could alter the original `data` data frame. Please be cautious
        when using this value directly.

        Parameters
        ----------
        selected
            If `True`, subset the viewed data to the selected area. Defaults to `False`.

        See Also
        --------
        * [`pandas.DataFrame.copy` API documentation]h(ttps://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.copy.html)
        """
        # Return reactive calculations so that they can be cached for other calculations
        if selected:
            return self._data_view_selected()
        else:
            return self._data_view()

    # data_patched: reactive.Calc_[pd.DataFrame]
    # """
    # Reactive value of the data frame's edited output data.

    # This is a shallow copy of the original data frame. It is possible that alterations
    # to `data_patched` could alter the original `data` data frame. Please be cautious
    # when using this value directly.

    # See Also
    # --------
    # * [`pandas.DataFrame.copy` API documentation]h(ttps://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.copy.html)
    # """

    # TODO-barret-Q; Should this be the original? Or the updated version
    selection_modes: reactive.Calc_[SelectionModes]
    """
    Reactive value of the data frame's possible selection modes.
    """

    input_cell_selection: reactive.Calc_[CellSelection | None]
    """
    Reactive value of selected information.

    This method is a wrapper around `input.<id>_selected_cells()`, where `<id>` is
    the `id` of the data frame output. This method returns the selected rows and
    will cause reactive updates as the selected rows change.

    Returns
    -------
    :
        * `None` if the selection mode is `"none"`
        * :class:`~shiny.types.BrowserCellSelection` representing the indices of the
          selected cells.
    """

    def _reset_reactives(self) -> None:
        self._value.set(None)
        self._cell_patch_map.set({})
        self._type_hints.set(None)

    def _init_reactives(self) -> None:

        import pandas as pd

        from .. import req

        # Init
        self._value: reactive.Value[DataFrameResult | None] = reactive.Value(None)
        self._type_hints: reactive.Value[dict[str, str] | None] = reactive.Value(None)
        self._cell_patch_map = reactive.Value({})

        @reactive.calc
        def self_cell_patches() -> list[CellPatchProcessed]:
            return list(self._cell_patch_map().values())

        self.cell_patches = self_cell_patches

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
        def self_selection_modes() -> SelectionModes:
            value = self._value()
            req(value)
            if not isinstance(value, (DataGrid, DataTable)):
                raise TypeError(
                    f"Unsupported type returned from render function: {type(value)}. Expected `DataGrid` or `DataTable`"
                )

            return value.selection_modes

        self.selection_modes = self_selection_modes

        @reactive.calc
        def self_input_cell_selection() -> CellSelection | None:
            browser_cell_selection_input = self._get_session().input[
                f"{self.output_id}_cell_selection"
            ]()

            browser_cell_selection = as_cell_selection(
                browser_cell_selection_input,
                selection_modes=self.selection_modes(),
            )
            if browser_cell_selection["type"] == "none":
                return None

            return browser_cell_selection

        self.input_cell_selection = self_input_cell_selection

        # Array of sorted column information
        # TODO-barret-render.data_frame; Expose and update column sorting
        # Do not expose until update methods are provided
        @reactive.calc
        def self__input_column_sort() -> list[ColumnSort]:
            column_sort = self._get_session().input[f"{self.output_id}_column_sort"]()
            return column_sort

        self._input_column_sort = self__input_column_sort

        # Array of column filters applied by user
        # TODO-barret-render.data_frame; Expose and update column filters
        # Do not expose until update methods are provided
        @reactive.calc
        def self__input_column_filter() -> list[ColumnFilterStr | ColumnFilterNumber]:
            column_filter = self._get_session().input[
                f"{self.output_id}_column_filter"
            ]()
            return column_filter

        self._input_column_filter = self__input_column_filter

        @reactive.calc
        def self__input_data_view_indicies() -> list[int]:
            data_view_indicies = self._get_session().input[
                f"{self.output_id}_data_view_indicies"
            ]()
            return data_view_indicies

        self._input_data_view_indicies = self__input_data_view_indicies

        # @reactive.calc
        # def self__data_selected() -> pd.DataFrame:
        #     # browser_cell_selection
        #     bcs = self.input_cell_selection()
        #     if bcs is None:
        #         req(False)
        #         raise RuntimeError("This should never be reached for typing purposes")
        #     data_selected = self.data_view(selected=False)
        #     if bcs["type"] == "none":
        #         # Empty subset
        #         return data_selected.iloc[[]]
        #     elif bcs["type"] == "row":
        #         # Seems to not work with `tuple[int, ...]`,
        #         # but converting to a list does!
        #         rows = list(bcs["rows"])
        #         return data_selected.iloc[rows]
        #     elif bcs["type"] == "col":
        #         # Seems to not work with `tuple[int, ...]`,
        #         # but converting to a list does!
        #         cols = list(bcs["cols"])
        #         return data_selected.iloc[:, cols]
        #     elif bcs["type"] == "rect":
        #         return data_selected.iloc[
        #             bcs["rows"][0] : bcs["rows"][1],
        #             bcs["cols"][0] : bcs["cols"][1],
        #         ]
        #     raise RuntimeError(f"Unhandled selection type: {bcs['type']}")
        # # self._data_selected = self__data_selected

        @reactive.calc
        def self__data_patched() -> pd.DataFrame:
            # Enable copy-on-write mode for the data;
            # Use `deep=False` to avoid copying the full data; CoW will copy the necessary data when modified
            with pd.option_context("mode.copy_on_write", True):
                # Apply patches!
                data = self.data().copy(deep=False)
                for cell_patch in self.cell_patches():
                    data.iat[  # pyright: ignore[reportUnknownMemberType]
                        cell_patch["row_index"],
                        cell_patch["column_index"],
                    ] = cell_patch["value"]

                return data

        self._data_patched = self__data_patched

        # Helper method to subset data according to what is viewed in the browser;
        # Apply filtering and sorting
        # https://github.com/posit-dev/py-shiny/issues/1240
        def _subset_data_view(selected: bool) -> pd.DataFrame:
            # Enable copy-on-write mode for the data;
            # Use `deep=False` to avoid copying the full data; CoW will copy the necessary data when modified
            with pd.option_context("mode.copy_on_write", True):
                # Get patched data
                data = self._data_patched().copy(deep=False)

                # Turn into list for pandas compatibility
                data_view_indicies = list(self._input_data_view_indicies())

                # Possibly subset the indicies to selected rows
                if selected:
                    cell_selection = self.input_cell_selection()
                    if cell_selection is not None and cell_selection["type"] == "row":
                        # Use a `set` for faster lookups
                        selected_row_indicies_set = set(cell_selection["rows"])

                        # Subset the data view indicies to only include the selected rows
                        data_view_indicies = [
                            index
                            for index in data_view_indicies
                            if index in selected_row_indicies_set
                        ]

                return data.iloc[data_view_indicies]

        # Helper reactives so that internal calculations can be cached for use in other calculations
        @reactive.calc
        def self__data_view() -> pd.DataFrame:
            return _subset_data_view(selected=False)

        @reactive.calc
        def self__data_view_selected() -> pd.DataFrame:
            return _subset_data_view(selected=True)

        self._data_view = self__data_view
        self._data_view_selected = self__data_view_selected

    def _get_session(self) -> Session:
        if self._session is None:
            raise RuntimeError(
                "The data frame being used was not initialized within a reactive context / session. Please call `@render.data_frame` where `shiny.session.get_current_context()` returns a non-`None` value."
            )
        return self._session

    def set_patch_fn(self, fn: PatchFn | PatchFnSync) -> Self:
        self._patch_fn = wrap_async(  # pyright: ignore[reportGeneralTypeIssues,reportAttributeAccessIssue]
            fn
        )
        return self

    def set_patches_fn(self, fn: PatchesFn | PatchesFnSync) -> Self:
        self._patches_fn = wrap_async(  # pyright: ignore[reportGeneralTypeIssues,reportAttributeAccessIssue]
            fn
        )
        return self

    def _init_handlers(self) -> None:
        async def patch_fn(
            *,
            patch: CellPatch,
        ) -> CellValue:
            return patch["value"]

        async def patches_fn(
            *,
            patches: list[CellPatch],
        ):
            ret_patches: list[CellPatch] = []
            for patch in patches:

                new_patch = patch.copy()
                new_patch["value"] = await self._patch_fn(patch=patch)
                ret_patches.append(new_patch)

            return ret_patches

        self.set_patch_fn(patch_fn)
        self.set_patches_fn(patches_fn)

    def _set_patches_handler_impl(
        self,
        handler: Callable[..., Awaitable[Jsonifiable]] | None,
    ) -> str:
        session = self._get_session()
        key = session.set_message_handler(
            f"data_frame_patches_{self.output_id}",
            handler,
        )
        return key

    def _reset_patches_handler(self) -> str:
        return self._set_patches_handler_impl(None)

    def _set_patches_handler(self) -> str:
        """
        Set the client patches handler for the data frame.

        This method **must be** called as late as possible as it depends on the ID of the output.
        """
        return self._set_patches_handler_impl(self._patches_handler)

    # Do not change this method name unless you update corresponding code in `/js/dataframe/`!!
    async def _patches_handler(self, patches: list[CellPatch]) -> Jsonifiable:
        assert_patches_shape(patches)

        with session_context(self._get_session()):
            # Call user's cell update method to retrieve formatted values
            patches = await self._patches_fn(patches=patches)

        # Check to make sure `updated_infos` is a list of dicts with the correct keys
        bad_patches_format = not isinstance(patches, list)
        if not bad_patches_format:
            for patch in patches:
                if not (
                    # Verify structure
                    isinstance(patch, dict)
                    # Verify types
                    and isinstance(patch["row_index"], int)
                    and isinstance(patch["column_index"], int)
                    # TODO-barret-render.data_frame; Check for cell type and compare against self._type_hints
                    # and isinstance(updated_patch["value"], CellValue)
                ):
                    raise ValueError(
                        f"The return value of {self.output_id}'s `_patches_fn()` "
                        f"(typically set by `@{self.output_id}.set_patches_fn`) "
                        f"must be a list where each item has a row_index (`int`), column_index (`int`), and value (`TagChild`)."
                    )

        # Add (or overwrite) new cell patches
        processed_patches: list[Jsonifiable] = []
        for patch in patches:
            processed_patch = self._set_cell_patch_map_value(
                value=patch["value"],
                row_index=patch["row_index"],
                column_index=patch["column_index"],
            )
            processed_patches.append(
                cell_patch_processed_to_jsonifiable(processed_patch)
            )

        # Return the processed patches to the client
        print("processed_patches", processed_patches)
        return processed_patches

    def _set_cell_patch_map_value(
        self, value: CellValue, *, row_index: int, column_index: int
    ) -> CellPatchProcessed:
        """
        Set the value within the cell patch map.

        Parameters
        ----------
        value :
            The new value to set the cell to.
        row_index :
            The row index of the cell to update.
        column_index :
            The column index of the cell to update.
        """
        assert isinstance(
            row_index, int
        ), f"Expected `row_index` to be an `int`, got {type(row_index)}"
        assert isinstance(
            column_index, int
        ), f"Expected `column_index` to be an `int`, got {type(column_index)}"

        # TODO-barret-render.data_frame; check type of `value` here?
        # TODO-barret-render.data_frame; The `value` should be coerced by pandas to the correct type

        cell_patch_processed: CellPatchProcessed = {
            "row_index": row_index,
            "column_index": column_index,
            "value": wrap_shiny_html(value, session=self._get_session()),
        }
        # Use copy to set the new value
        cell_patch_map = self._cell_patch_map().copy()
        cell_patch_map[(row_index, column_index)] = cell_patch_processed
        self._cell_patch_map.set(cell_patch_map)

        return cell_patch_processed

    def _update_cell_value(
        self, value: CellValue, *, row_index: int, column_index: int
    ) -> CellPatchProcessed:
        """
        Update the value of a cell in the data frame.

        Parameters
        ----------
        value :
            The new value to set the cell to.
        row_index :
            The row index of the cell to update.
        column_index :
            The column index of the cell to update.
        """
        cell_patch_processed = self._set_cell_patch_map_value(
            value, row_index=row_index, column_index=column_index
        )

        # TODO-barret-render.data_frame; Send message to client to update cell value

        return cell_patch_processed

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
        self._reset_reactives()
        self._reset_patches_handler()

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

        # Set patches url handler for client
        patch_key = self._set_patches_handler()
        self._value.set(value)

        # Use session context so `to_payload()` gets the correct session
        with session_context(self._get_session()):
            payload = value.to_payload()

            type_hints = cast(
                Union[Dict[str, str], None],
                payload.get("typeHints", None),
            )
            self._type_hints.set(type_hints)

            return {
                "payload": payload,
                "patchInfo": {
                    "key": patch_key,
                },
                "selectionModes": self.selection_modes().as_dict(),
            }

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

    async def update_cell_selection(
        # self, selection: SelectionLocation | BrowserCellSelection
        self,
        selection: CellSelection | Literal["all"] | None,
    ) -> None:
        with reactive.isolate():
            selection_modes = self.selection_modes()
            data = self.data()

        if selection_modes._is_none():
            warnings.warn(
                'Cell selection cannot be updated when `.selection_mode=` contains "none". '
                'Please set `selection_mode=` to contain a non-`"none"` value '
                "(e.g. 'row' or 'rows') in the return value of "
                "`@render.data_frame` to enable cell selection.",
                stacklevel=2,
            )

            selection = None

        cell_selection = as_cell_selection(
            selection,
            selection_modes=selection_modes,
            data=data,
        )

        if cell_selection["type"] == "none":
            pass
        elif cell_selection["type"] == "rect":
            raise RuntimeError("Rectangle region selection is not yet supported")
        elif cell_selection["type"] == "col":
            raise RuntimeError("Column selection is not yet supported")
        elif cell_selection["type"] == "row":
            row_value = cell_selection["rows"]
            if selection_modes.row == "single" and len(row_value) > 1:
                warnings.warn(
                    "Attempted to set cell selection to more than 1 row when `.selection_modes()` contains 'row'. "
                    "Only the first row supplied will be selected.",
                    stacklevel=2,
                )

                cell_selection["rows"] = (row_value[0],)
        else:
            raise ValueError(f"Unhandled selection type: {cell_selection['type']}")
        await self._send_message_to_browser(
            "updateCellSelection",
            {"cellSelection": cell_selection},
        )
