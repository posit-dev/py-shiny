from __future__ import annotations

import warnings

# TODO-barret; Docs
# TODO-barret; Add examples!
from typing import TYPE_CHECKING, Any, Awaitable, Callable, TypeVar

from htmltools import Tag

from .. import reactive, ui
from .._docstring import add_example
from .._typing_extensions import Self, TypedDict
from ..session._utils import get_current_session, require_active_session
from ._data_frame_utils import (
    AbstractTabularData,
    BrowserCellSelection,
    CellPatch,
    CellSelection,
    CellValue,
    DataGrid,
    DataTable,
    PatchesFn,
    PatchFn,
    SelectionMode,
    as_browser_cell_selection,
    assert_patches_shape,
    cast_to_pandas,
    cell_patch_to_jsonifiable,
)

# as_selection_location_js,
from .renderer import Jsonifiable, Renderer, ValueFn

if TYPE_CHECKING:
    import pandas as pd

    from ..session._utils import Session

    DataFrameT = TypeVar("DataFrameT", bound=pd.DataFrame)
    # TODO-future; Pandas, Polars, api compat, etc.; Today, we only support Pandas


from ._data_frame_utils._datagridtable import DataFrameResult


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
    `<data_frame_renderer>.data_selected()` or
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
    # _data: reactive.Value[pd.DataFrame | None]

    _patch_fn: PatchFn
    _patches_fn: PatchesFn

    _cell_patch_map: reactive.Value[dict[tuple[int, int], CellPatch]]
    """
    Reactive map of patches to be applied to the data frame.

    The key is defined as `(row_index, column_index)`, and the value is a `CellPatch`.

    This map is used for faster deduplications of patches at each location.
    """
    cell_patches: reactive.Calc_[list[CellPatch]]

    data: reactive.Calc_[pd.DataFrame]
    """
    Reactive value of the data frame's output data.

    This is a quick reference to the original data frame that was returned from the
    app's render function. If it is mutated in place, it **will** modify the original
    data.
    """
    data_patched: reactive.Calc_[pd.DataFrame]
    """
    Reactive value of the data frame's edited output data.

    This is a shallow copy of the original data frame. It is possible that alterations
    to `data_patched` could alter the original `data` data frame. Please be cautious
    when using this value directly.

    See Also
    --------
    * [`pandas.DataFrame.copy` API documentation]h(ttps://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.copy.html)
    """
    selection_mode: reactive.Calc_[SelectionMode]
    """
    Reactive value of the data frame's selection mode.
    """

    input_cell_selection: reactive.Calc_[BrowserCellSelection | None]
    """
    Reactive value of selected information.

    This method is a wrapper around `input.<id>_selected_cells()`, where `<id>` is
    the `id` of the data frame output. This method returns the selected rows and
    will cause reactive updates as the selected rows change.

    Returns
    -------
    :
        * `None` if the selection mode is `None`
        * :class:`~shiny.types.SelectionLocationJS` representing the indices of the
          selected cells.
    """

    data_selected: reactive.Calc_[pd.DataFrame]
    """
    Reactive value that returns the edited data frame subsetted to the selected area.

    Returns
    -------
    :
        * If the row selection mode is `None`, the calculation will throw a silent error
          (`req(False)`)
        * The edited data (`.data_patched()`) at the indices of the selected rows
    """

    def _reset_reactives(self) -> None:
        self._value.set(None)
        self._cell_patch_map.set({})

    def _init_reactives(self) -> None:

        import pandas as pd

        from .. import req

        # Init
        self._value: reactive.Value[DataFrameResult | None] = reactive.Value(None)
        self._cell_patch_map = reactive.Value({})

        @reactive.calc
        def self_cell_patches() -> list[CellPatch]:
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
        def self_selection_mode() -> SelectionMode:
            value = self._value()
            req(value)
            if not isinstance(value, (DataGrid, DataTable)):
                raise TypeError(
                    f"Unsupported type returned from render function: {type(value)}. Expected `DataGrid` or `DataTable`"
                )

            return value.selection_mode

        self.selection_mode = self_selection_mode

        @reactive.calc
        def self_input_cell_selection() -> BrowserCellSelection | None:
            selection_mode: SelectionMode = self.selection_mode()
            if selection_mode == "none":
                return None

            input_val = self._get_session().input[f"{self.output_id}_cell_selection"]()
            if input_val is None:
                return None

            browser_cell_selection = as_browser_cell_selection(input_val)

            return browser_cell_selection

        self.input_cell_selection = self_input_cell_selection

        @reactive.calc
        # TODO-barret; Subset data according to what is viewed in the browser; Apply filtering and sorting as well! https://github.com/posit-dev/py-shiny/issues/1240
        def self_data_selected() -> pd.DataFrame:
            # browser_cell_selection
            bcs = self.input_cell_selection()
            if bcs is None:
                req(False)
                raise RuntimeError("This should never be reached for typing purposes")

            data_selected = self.data_patched()
            if bcs["type"] == "all":
                return data_selected
            elif bcs["type"] == "none":
                # Empty subset
                return data_selected.iloc[[]]
            elif bcs["type"] == "row":
                # Seems to not work with `tuple[int, ...]`,
                # but converting to a list does!
                rows = list(bcs["rows"])
                return data_selected.iloc[rows]
            elif bcs["type"] == "col":
                # Seems to not work with `tuple[int, ...]`,
                # but converting to a list does!
                cols = list(bcs["cols"])
                return data_selected.iloc[:, cols]
            elif bcs["type"] == "region":
                return data_selected.iloc[
                    bcs["rows"][0] : bcs["rows"][1],
                    bcs["cols"][0] : bcs["cols"][1],
                ]
            raise RuntimeError(f"Unhandled selection type: {bcs['type']}")

        self.data_selected = self_data_selected

        @reactive.calc
        def self_data_patched() -> pd.DataFrame:
            # Enable copy-on-write mode for the data;
            # Use `deep=False` to avoid copying the full data; CoW will copy the necessary data when modified
            with pd.option_context("mode.copy_on_write", True):
                data = self.data().copy(deep=False)
                for cell_patch in self.cell_patches():
                    data.iat[  # pyright: ignore[reportUnknownMemberType]
                        cell_patch["row_index"],
                        cell_patch["column_index"],
                    ] = cell_patch["value"]

                return data

        self.data_patched = self_data_patched

    def _get_session(self) -> Session:
        if self._session is None:
            raise RuntimeError(
                "The data frame being used was not initialized within a reactive context / session. Please call `@render.data_frame` where `shiny.session.get_current_context()` returns a non-`None` value."
            )
        return self._session

    def set_patch_fn(self, fn: PatchFn) -> Self:
        self._patch_fn = fn
        return self

    def set_patches_fn(self, fn: PatchesFn) -> Self:
        self._patches_fn = fn
        return self

    def _init_handlers(self) -> None:
        async def patch_fn(
            *,
            patch: CellPatch,
        ) -> str:
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

        # Call user's cell update method to retrieve formatted values
        updated_patches = await self._patches_fn(patches=patches)

        # Check to make sure `updated_infos` is a list of dicts with the correct keys
        bad_patches_format = not isinstance(updated_patches, list)
        if not bad_patches_format:
            for updated_patch in updated_patches:
                if not (
                    # Verify structure
                    isinstance(updated_patch, dict)
                    # Verify types
                    and isinstance(updated_patch["row_index"], int)
                    and isinstance(updated_patch["column_index"], int)
                    and isinstance(updated_patch["value"], CellValue)
                ):
                    bad_patches_format = True
                    break
                # TODO-barret; check type of `value` here?
                # TODO-barret; The `value` should be coerced by pandas to the correct type

        if bad_patches_format:
            raise ValueError(
                f"The return value of {self.output_id}'s `_patches_fn()` "
                f"(typically set by `@{self.output_id}.set_patches_fn`) "
                f"must be a list where each item has a row_index (`int`), column_index (`int`), and value (`{CellValue}`)."
            )

        # Copy to make sure reactive set works
        cell_patch_map = self._cell_patch_map().copy()
        # Add (or overwrite) new cell patches
        for updated_patch in updated_patches:
            cell_patch_map[
                (updated_patch["row_index"], updated_patch["column_index"])
            ] = updated_patch

        # (Reactively) Set new patch map
        self._cell_patch_map.set(cell_patch_map)

        return [
            cell_patch_to_jsonifiable(updated_patch)
            for updated_patch in updated_patches
        ]

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

        # Send info to client
        patch_key = self._set_patches_handler()
        self._value.set(value)
        return {
            "data": value.to_payload(),
            "patchInfo": {
                "key": patch_key,
            },
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
        # self, selection: SelectionLocation | SelectionLocationJS
        self,
        selection: CellSelection | BrowserCellSelection | None,
    ) -> None:
        if selection is None:
            selection = "none"

        with reactive.isolate():
            selection_mode = self.selection_mode()
        if selection_mode == "none":
            warnings.warn(
                "Cell selection cannot be updated when `.selection_mode()` is 'none'. "
                "Please set `selection_mode=` to 'single' or 'multiple' in the return "
                "value of `@render.data_frame` to enable cell selection.",
                stacklevel=2,
            )

            selection = "none"

        browser_cell_selection = as_browser_cell_selection(selection)
        if browser_cell_selection["type"] == "none":
            pass
        elif browser_cell_selection["type"] == "all":
            pass
        elif browser_cell_selection["type"] == "region":
            raise RuntimeError("Region selection is not yet supported")
        elif browser_cell_selection["type"] == "col":
            raise RuntimeError("Column selection is not yet supported")
        elif browser_cell_selection["type"] == "row":
            row_value = browser_cell_selection["rows"]
            if selection_mode == "row" and len(row_value) > 1:
                warnings.warn(
                    "Attempted to set cell selection to more than 1 row when `.selection_mode()` is 'row'. "
                    "Only the first row supplied will be selected.",
                    stacklevel=2,
                )

                browser_cell_selection["rows"] = (row_value[0],)
        else:
            raise ValueError(
                f"Unhandled selection type: {browser_cell_selection['type']}"
            )
        await self._send_message_to_browser(
            "updateCellSelection",
            {"cellSelection": browser_cell_selection},
        )
