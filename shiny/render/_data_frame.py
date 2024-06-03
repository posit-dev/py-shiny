from __future__ import annotations

import warnings

# TODO-barret; Should `.input_cell_selection()` ever return None? Is that value even helpful? Empty lists would be much more user friendly.
# * For next release: Agreed to remove `None` type.
# * For this release: Immediately make PR to remove `.input_` from `.input_cell_selection()`
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
from .._typing_extensions import Annotated, TypedDict
from .._utils import wrap_async
from ..session._utils import require_active_session, session_context
from ..types import ListOrTuple
from ._data_frame_utils import (
    AbstractTabularData,
    BrowserCellSelection,
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
from ._data_frame_utils._unsafe import serialize_numpy_dtype

# as_selection_location_js,
from .renderer import Jsonifiable, Renderer, ValueFn

if TYPE_CHECKING:
    import pandas as pd

    from ..session import Session

    DataFrameT = TypeVar("DataFrameT", bound=pd.DataFrame)
    # TODO-barret-render.data_frame; Pandas, Polars, api compat, etc.; Today, we only support Pandas


from ._data_frame_utils._datagridtable import DataFrameResult


class ColumnSort(TypedDict):
    col: int
    desc: bool


class ColumnFilterStr(TypedDict):
    col: int
    value: str


class ColumnFilterNumber(TypedDict):
    col: int
    value: (
        tuple[int | float, int | float]
        | tuple[int | float, None]
        | tuple[None, int | float]
        | Annotated[list[int | float | None], 2]
    )


ColumnFilter = Union[ColumnFilterStr, ColumnFilterNumber]


class DataViewInfo(TypedDict):
    sort: tuple[ColumnSort, ...]
    filter: tuple[ColumnFilter, ...]

    rows: tuple[int, ...]  # sorted and filtered row number
    selected_rows: tuple[int, ...]  # selected and sorted and filtered row number
    # selected_columns: tuple[int, ...]  # selected and sorted and filtered row number


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
    `<data_frame_renderer>.cell_selection()` method, where `<data_frame_renderer>`
    is the `@render.data_frame` function name that corresponds with the `id=` used in
    :func:`~shiny.ui.outout_data_frame`. Internally,
    `<data_frame_renderer>.cell_selection()` retrieves the selected cell
    information from session's `input.<data_frame_renderer>_cell_selection()` value and
    upgrades it for consistent subsetting.

    To filter your pandas data frame (`df`) down to the selected rows, you can use:

    * `df.iloc[list(input.<data_frame_renderer>_cell_selection()["rows"])]`
    * `df.iloc[list(<data_frame_renderer>.cell_selection()["rows"])]`
    * `df.iloc[list(<data_frame_renderer>.data_view_info()["selected_rows"])]`
    * `<data_frame_renderer>.data_view(selected=True)`

    Editing cells
    -------------
    When a returned `DataTable` or `DataGrid` object has `editable=True`, app users will
    be able to edit the cells in the table. After a cell has been edited, the edited
    value will be sent to the server for processing. The handling methods are set via
    `@<data_frame_renderer>.set_patch_fn` or `@<data_frame_renderer>.set_patches_fn`
    decorators. By default, both decorators will return a string value.

    To access the data viewed by the user, use `<data_frame_renderer>.data_view()`. This
    method will sort, filter, and apply any patches to the data frame as viewed by the
    user within the browser. This is a shallow copy of the original data frame. It is
    possible that alterations to `data_view` could alter the original `data` data frame.

    To access the original data, use `<data_frame_renderer>.data()`. This is a quick
    reference to the original data frame (converted to a `pandas.DataFrame`) that was
    returned from the app's render function. If it is mutated in place, it **will**
    modify the original data.

    Note... if the data frame renderer is re-rendered due to reactivity, then (currently)
    the user's edits, sorting, and filtering will be lost. We hope to improve upon this
    in the future.

    Tip
    ---
    This decorator should be applied **before** the ``@output`` decorator (if that
    decorator is used). Also, the name of the decorated function (or
    ``@output(id=...)``) should match the ``id`` of a :func:`~shiny.ui.output_data_frame`
    container (see :func:`~shiny.ui.output_data_frame` for example usage).

    See Also
    --------
    * :func:`~shiny.ui.output_data_frame`
    * :class:`~shiny.render.DataGrid` and :class:`~shiny.render.DataTable` are the
      objects you can return from the rendering function to specify options.
    """

    _value: reactive.Value[DataFrameResult | None]
    """
    Reactive value of the data frame's rendered object.
    """
    _type_hints: reactive.Value[dict[str, str] | None]
    """
    Reactive value of the data frame's type hints for each column.

    This is enhanced with `"html"` type for rendering HTML content in the data frame.
    """

    _patch_fn: PatchFn
    """
    User-defined function to update a single cell in the data frame.

    Defaults to return the value as is.
    """
    _patches_fn: PatchesFn
    """
    User-defined function to update all cells in a batch actions.

    It gives the user opportunity to return less, the same, or even more patches than
    originally requested by the browser.

    Defaults to calling `._patch_fn()` on each input patch and returning the input
    patches with updated values.
    """

    _cell_patch_map: reactive.Value[dict[tuple[int, int], CellPatchProcessed]]
    """
    Reactive dictionary of patches to be applied to the data frame.

    This map is used for faster deduplications of patches at each location given the row
    and column indices.

    The key is defined as `(row_index, column_index)`.
    """
    cell_patches: reactive.Calc_[list[CellPatchProcessed]]
    """
    Reactive value of the data frame's edits provided by the user.
    """

    data: reactive.Calc_[pd.DataFrame]
    """
    Reactive value of the data frame's output data.

    This is a quick reference to the original data frame that was returned from the
    app's render function. If it is mutated in place, it **will** modify the original
    data.

    Even if the rendered data value was not `pd.DataFrame`, this method currently
    returns the converted `pd.DataFrame`.
    """
    _data_view_all: reactive.Calc_[pd.DataFrame]
    """
    Reactive value of the full (sorted and filtered) data.
    """
    _data_view_selected: reactive.Calc_[pd.DataFrame]
    """
    Reactive value of the selected rows of the (sorted and filtered) data.
    """

    @add_example(ex_dir="../api-examples/data_frame_data_view")
    def data_view(self, *, selected: bool = False) -> pd.DataFrame:
        """
        Reactive function that retrieves the data how it is viewed within the browser.

        This function will sort, filter, and apply any patches to the data frame as
        viewed by the user within the browser.

        This is a shallow copy of the original data frame. It is possible that
        alterations to `data_view` could alter the original `data` data frame. Please be
        cautious when using this value directly.

        Parameters
        ----------
        selected
            If `True`, subset the viewed data to the selected area. Defaults to `False`.

        Returns
        -------
        :
            A view of the data frame as seen in the browser. Even if the rendered data
            value was not `pd.DataFrame`, this method currently returns the converted
            `pd.DataFrame`.

        See Also
        --------
        * [`pandas.DataFrame.copy` API documentation]h(ttps://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.copy.html)
        """
        # Return reactive calculations so that they can be cached for other calculations
        if selected:
            return self._data_view_selected()
        else:
            return self._data_view_all()

    # TODO-barret-render.data_frame; Allow for DataTable and DataGrid to accept SelectionModes
    selection_modes: reactive.Calc_[SelectionModes]
    """
    Reactive value of the data frame's possible selection modes.
    """

    cell_selection: reactive.Calc_[CellSelection]
    """
    Reactive value of selected cell information.

    This method is a wrapper around `input.<id>_cell_selection()`, where `<id>` is
    the `id` of the data frame output. This method returns the selected rows and
    will cause reactive updates as the selected rows change.

    The value has been enhanced from it's vanilla form to include the missing `cols` key
    (or `rows` key) as a tuple of integers representing all column (or row) numbers.
    This allows for consistent usage within code when subsetting your data. These
    missing keys are not sent over the wire as they are independent of the selection.

    Returns
    -------
    :
        :class:`~shiny.render.CellSelection` representing the indices of the selected
        cells. If no cells are currently selected, `None` is returned.
    """

    data_view_rows: reactive.Calc_[tuple[int, ...]]
    """
    Reactive value of the data frame's user view row numbers.

    This value is a wrapper around `input.<id>_data_view_rows()`, where `<id>` is the
    `id` of the data frame output.

    Returns
    -------
    :
        The row numbers of the data frame that are currently being viewed in the browser
        after sorting and filtering has been applied.
    """
    _data_patched: reactive.Calc_[pd.DataFrame]
    """
    Reactive value of the data frame's patched data.

    Returns
    -------
    :
        The data frame with all the user's edit patches applied to it.
    """

    sort: reactive.Calc_[tuple[ColumnSort, ...]]
    """
    Reactive value of the data frame's column sorting information.

    Returns
    -------
    :
        An array of `col`umn number and _is `desc`ending_ information.
    """

    filter: reactive.Calc_[tuple[ColumnFilter, ...]]
    """
    Reactive value of the data frame's column filters.

    Returns
    -------
    :
        An array of `col`umn number and `value` information.
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
        def self_cell_selection() -> CellSelection:
            browser_cell_selection = cast(
                BrowserCellSelection,
                self._get_session().input[f"{self.output_id}_cell_selection"](),
            )

            cell_selection = as_cell_selection(
                browser_cell_selection,
                selection_modes=self.selection_modes(),
                data=self.data(),
                data_view_rows=self.data_view_rows(),
                data_view_cols=tuple(range(self.data().shape[1])),
            )

            return cell_selection

        self.cell_selection = self_cell_selection

        @reactive.calc
        def self_sort() -> tuple[ColumnSort, ...]:
            column_sort = self._get_session().input[f"{self.output_id}_column_sort"]()
            return tuple(column_sort)

        self.sort = self_sort

        @reactive.calc
        def self_filter() -> tuple[ColumnFilter, ...]:
            column_filter = self._get_session().input[
                f"{self.output_id}_column_filter"
            ]()
            return tuple(column_filter)

        self.filter = self_filter

        @reactive.calc
        def self_data_view_rows() -> tuple[int, ...]:
            data_view_rows = self._get_session().input[
                f"{self.output_id}_data_view_rows"
            ]()
            return tuple(data_view_rows)

        self.data_view_rows = self_data_view_rows

        # @reactive.calc
        # def self__data_selected() -> pd.DataFrame:
        #     # browser_cell_selection
        #     bcs = self.cell_selection()
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

        # Apply filtering and sorting
        # https://github.com/posit-dev/py-shiny/issues/1240
        def _subset_data_view(selected: bool) -> pd.DataFrame:
            """
            Helper method to subset data according to what is viewed in the browser;

            Applies filtering and sorting to the patched data. If `selected=True`, only
            the user selected rows are returned.


            Note Future rect selection changes
            ----------------------------------
            In the future, the selected rows may need to be **after** filtering
            and sorting are applied. This would allow for rectangular selections to be
            applied to the filtered and sorted data given min/max row info.

            Where as, currently, the selected rows are applied to the original data
            before filtering and sorting are applied. Serializing the rect selection
            would require tuple info of all cells selected.
            """

            # Enable copy-on-write mode for the data;
            # Use `deep=False` to avoid copying the full data; CoW will copy the necessary data when modified
            with pd.option_context("mode.copy_on_write", True):
                # Get patched data
                data = self._data_patched().copy(deep=False)

                if selected:
                    rows = self.cell_selection()["rows"]
                else:
                    rows = self.data_view_rows()

                # Turn into list for pandas compatibility
                rows = list(rows)
                return data.iloc[rows]

        # Helper reactives so that internal calculations can be cached for use in other calculations
        @reactive.calc
        def self__data_view() -> pd.DataFrame:
            return _subset_data_view(selected=False)

        @reactive.calc
        def self__data_view_selected() -> pd.DataFrame:
            return _subset_data_view(selected=True)

        self._data_view_all = self__data_view
        self._data_view_selected = self__data_view_selected

    def _get_session(self) -> Session:
        if self._session is None:
            raise RuntimeError(
                "The data frame being used was not initialized within a reactive context / session. Please call `@render.data_frame` where `shiny.session.get_current_context()` returns a non-`None` value."
            )
        return self._session

    @add_example(ex_dir="../api-examples/data_frame_data_view")
    def set_patch_fn(self, fn: PatchFn | PatchFnSync) -> None:
        """
        Decorator to set the function that updates a single cell in the data frame.

        The default patch function returns the value as is.

        Parameters
        ----------
        fn
            A function that accepts a kwarg `patch` and returns the processed
            `patch.value` for the cell.
        """
        self._patch_fn = wrap_async(  # pyright: ignore[reportGeneralTypeIssues,reportAttributeAccessIssue]
            fn
        )
        # Do not return self here as it is typically used as a decorator (which would return `self`)
        # By returning `self` in express mode, it is attempted to be registered twice. That is bad.
        # So for now, we will not return `self` here.
        # from .._typing_extensions import Self
        # return self

    @add_example(ex_dir="../api-examples/data_frame_set_patches")
    def set_patches_fn(self, fn: PatchesFn | PatchesFnSync) -> None:
        """
        Decorator to set the function that updates a batch of cells in the data frame.

        The default patches function calls the async `._patch_fn()` on each input patch
        and returns the updated patch values.

        There are no checks made on the quantity of patches returned. The user can
        return more, less, or the same number of patches as the input patches. This
        allows for the app author to own more control over which columns are updated and
        how they are updated.
        """
        self._patches_fn = wrap_async(  # pyright: ignore[reportGeneralTypeIssues,reportAttributeAccessIssue]
            fn
        )
        # Do not return self here as it is typically used as a decorator (which would return `self`)
        # By returning `self` in express mode, it is attempted to be registered twice. That is bad.
        # So for now, we will not return `self` here.
        # from .._typing_extensions import Self
        # return self

    def _init_patch_fns(self) -> None:
        """
        Initialize `._patch_fn()` and `._patches_fn()`.
        """

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
        """
        Set the client patches request handler for the data frame.

        This method should be removed when the rendered result is `None`.
        (... b/c there is no data frame to send requests!)
        """
        session = self._get_session()
        key = session.set_message_handler(
            f"data_frame_patches_{self.output_id}",
            handler,
        )
        return key

    def _reset_patches_handler(self) -> str:
        """
        Resets the client patches request handler for the data frame.
        """
        return self._set_patches_handler_impl(None)

    def _set_patches_handler(self) -> str:
        """
        Set the client patches handler for the data frame.

        This method **must be** called as late as possible as it depends on the ID of the output.
        """
        return self._set_patches_handler_impl(self._patches_handler)

    # Do not change this method name unless you update corresponding code in `/js/dataframe/`!!
    async def _patches_handler(self, patches: list[CellPatch]) -> Jsonifiable:
        """
        Accepts edit patches requests from the client and returns the processed patches.

        Parameters
        ----------
        patches
            A list of patches to apply to the data frame.

        Returns
        -------
        :
            A list of processed patches to apply to the data frame. The number of
            processed patches can be different from the number of input patches.
        """
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
                    # # Do not check the value type here. It should be validated by
                    # # `._set_cell_patch_map_value()` later with more type hint context
                    # and isinstance(updated_patch["value"], CellValue)
                ):
                    raise ValueError(
                        f"The return value of {self.output_id}'s `_patches_fn()` "
                        f"(typically set by `@{self.output_id}.set_patches_fn`) "
                        f"must be a list where each item has a row_index (`int`), column_index (`int`), and value (`TagChild`)."
                    )

        # Add (or overwrite) new cell patches by setting each patch into the cell patch map
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
        return processed_patches

    def _set_cell_patch_map_value(
        self,
        value: CellValue,
        *,
        row_index: int,
        column_index: int,
    ) -> CellPatchProcessed:
        """
        Set the value within the cell patch map.

        Parameters
        ----------
        value
            The new value to set the cell to.
        row_index
            The row index of the cell to update.
        column_index
            The column index of the cell to update.
        """
        assert isinstance(
            row_index, int
        ), f"Expected `row_index` to be an `int`, got {type(row_index)}"
        assert isinstance(
            column_index, int
        ), f"Expected `column_index` to be an `int`, got {type(column_index)}"

        # TODO-barret-render.data_frame; Check for cell type and compare against self._type_hints
        # TODO-barret-render.data_frame; The `value` should be coerced by pandas to the correct type
        # TODO-barret; See https://pandas.pydata.org/pandas-docs/stable/user_guide/basics.html#object-conversion

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

    # TODO-barret-render.data_frame; Add `update_cell_value()` method
    # def _update_cell_value(
    #     self, value: CellValue, *, row_index: int, column_index: int
    # ) -> CellPatchProcessed:
    #     """
    #     Update the value of a cell in the data frame.
    #
    #     Parameters
    #     ----------
    #     value
    #         The new value to set the cell to.
    #     row_index
    #         The row index of the cell to update.
    #     column_index
    #         The column index of the cell to update.
    #     """
    #     cell_patch_processed = self._set_cell_patch_map_value(
    #         value, row_index=row_index, column_index=column_index
    #     )
    #     # TODO-barret-render.data_frame; Send message to client to update cell value
    #     return cell_patch_processed

    def auto_output_ui(self) -> Tag:
        return ui.output_data_frame(id=self.output_id)

    def __init__(self, fn: ValueFn[DataFrameResult]):
        super().__init__(fn)

        # Set reactives from calculated properties
        self._init_reactives()
        # Set update functions
        self._init_patch_fns()

    def _set_output_metadata(self, *, output_id: str) -> None:
        super()._set_output_metadata(output_id=output_id)

        # Verify that the session used (during `__init__`) when creating the renderer is
        # the same session used when executing the renderer. This is to prevent a user
        # from creating a renderer in one module and registering it on an output with a
        # different session.

        active_session = require_active_session()
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
        # self, selection: SelectionLocation | CellSelection
        self,
        selection: CellSelection | Literal["all"] | None | BrowserCellSelection,
    ) -> None:
        """
        Update the cell selection in the data frame.

        Currently only single (`"type": "row"`) or multiple (`"type": "rows"`) row
        selection is supported.

        If the current data frame selection mode is `"none"` and a non-none selection is
        provided, a warning will be raised and no rows will be selected. If cells are
        supposes to be selected, the selection mode returned from the render function
        must (currently) be set to `"row"` or `"rows"`.

        Parameters
        ----------
        selection
            The cell selection to apply to the data frame. This can be a `CellSelection`
            object, `"all"` to select all cells (if possible), or `None` to clear the
            selection.
        """
        with reactive.isolate():
            selection_modes = self.selection_modes()
            data = self.data()
            data_view_rows = self.data_view_rows()
            data_view_cols = tuple(range(data.shape[1]))

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
            data_view_rows=data_view_rows,
            data_view_cols=data_view_cols,
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

    @add_example(ex_dir="../api-examples/data_frame_update_sort")
    async def update_sort(
        self,
        sort: ListOrTuple[ColumnSort | int] | int | ColumnSort | None,
    ) -> None:
        """
        Update the column sorting in the data frame.

        The sort will be applied in reverse order so that the first value has the highest
        precedence. This mean _ties_ will go to the second sort column (and so on).

        Parameters
        ----------
        sort
            A list of column sorting information. If `None`, sorting will be removed. `int` values will be upgraded to `{"col": int, "desc": <DESC>}` where `<DESC>` is `True` if the column is number like and `False` otherwise.
        """
        if sort is None:
            sort = ()
        elif isinstance(sort, int):
            sort = (sort,)
        elif isinstance(sort, (list, tuple)):
            ...
        else:
            raise TypeError(
                f"Expected `sort` to be a `list`, `tuple`, `int`, or `None`. Received `{type(sort)}`"
            )

        vals: list[ColumnSort] = []
        if len(sort) > 0:
            with reactive.isolate():
                data = self.data()
            ncol = len(data.columns)

            for val in sort:
                val_dict: ColumnSort
                if isinstance(val, int):
                    col: pd.Series[Any] = data.iloc[:, val]
                    desc = serialize_numpy_dtype(col)["type"] == "numeric"
                    val_dict = {"col": val, "desc": desc}
                val_dict: ColumnSort = (
                    val if isinstance(val, dict) else {"col": val, "desc": True}
                )
                assert isinstance(val_dict, dict)
                assert isinstance(val_dict["col"], int)
                assert 0 <= val_dict["col"] < ncol
                assert isinstance(val_dict["desc"], bool)
                vals.append(val_dict)

        await self._send_message_to_browser(
            "updateColumnSort",
            {"sort": vals},
        )

    @add_example(ex_dir="../api-examples/data_frame_update_filter")
    async def update_filter(
        self,
        filter: ListOrTuple[ColumnFilter] | None,
    ) -> None:
        """
        Update the column filtering in the data frame.

        Parameters
        ----------
        filter
            A list of column filtering information. If `None`, filtering will be removed.
        """

        assert filter is None or isinstance(filter, (list, tuple))

        if filter is None:
            filter = []
        else:
            with reactive.isolate():
                data = self.data()
            ncol = len(data.columns)

            for column_filter, i in zip(filter, range(len(filter))):
                assert isinstance(column_filter, dict)
                assert isinstance(column_filter["col"], int)
                assert 0 <= column_filter["col"] < ncol
                if isinstance(column_filter["value"], str):
                    ...
                elif isinstance(column_filter["value"], (list, tuple)):
                    assert len(column_filter["value"]) == 2
                    if (
                        column_filter["value"][0] is None
                        and column_filter["value"][1] is None
                    ):
                        raise TypeError(
                            "Expected `filter[{i}]['value']` to be a `str` or a `list`/`tuple` of type `int` or `None`. Received `None` for both values."
                        )
                    assert isinstance(
                        column_filter["value"][0], (int, float, type(None))
                    )
                    assert isinstance(
                        column_filter["value"][1], (int, float, type(None))
                    )
                else:
                    raise TypeError(
                        f"Expected `filter[{i}]['value']` to be a `str` or a `list`/`tuple` of type `int` or `None`. Received `{type(column_filter['value'])}`"
                    )

        await self._send_message_to_browser(
            "updateColumnFilter",
            {"filter": filter},
        )

    def input_cell_selection(self) -> CellSelection | None:
        """
        [Deprecated] Reactive value of selected cell information.

        Please use `~shiny.render.data_frame`'s `.cell_selection()` method instead.
        """

        from .._deprecated import warn_deprecated

        warn_deprecated(
            "`@render.data_frame`'s `.input_cell_selection()` method is deprecated. Please use `.cell_selection()` instead."
        )

        cell_selection = self.cell_selection()
        if cell_selection["type"] == "none":
            return None

        return self.cell_selection()
