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
    Self,
    Sequence,
    TypedDict,
    Union,
    cast,
    runtime_checkable,
)

from htmltools import Tag

from .. import reactive, ui
from .._docstring import add_example, no_example
from ..session._utils import (
    get_current_session,
    require_active_session,
    session_context,
)
from ._dataframe_unsafe import serialize_numpy_dtypes
from .renderer import Jsonifiable, Renderer, ValueFn

if TYPE_CHECKING:
    import pandas as pd

    from ..session._utils import Session


class AbstractTabularData(abc.ABC):
    @abc.abstractmethod
    def to_payload(self) -> Jsonifiable: ...


RowSelectionMode = Literal["none", "single", "multiple"]


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
        A _maximum_ amount of vertical space for the data grid to occupy, in CSS units
        (e.g. `"400px"`) or as a number, which will be interpreted as pixels. The
        default is `fit-content`, which sets the grid's width according to its contents.
        Set this to `100%` to use the maximum available horizontal space.
    height
        A _maximum_ amount of vertical space for the data grid to occupy, in CSS units
        (e.g. `"400px"`) or as a number, which will be interpreted as pixels. If there
        are more rows than can fit in this space, the grid will scroll. Set the height
        to `None` to allow the grid to grow to fit all of the rows (this is not
        recommended for large data sets, as it may crash the browser).
    summary
        If `True` (the default), shows a message like "Viewing rows 1 through 10 of 20"
        below the grid when not all of the rows are being shown. If `False`, the message
        is not displayed. You can also specify a string template to customize the
        message, containing `{start}`, `{end}`, and `{total}` tokens. For example:
        `"Viendo filas {start} a {end} de {total}"`.
    filters
        If `True`, shows a row of filter inputs below the headers, one for each column.
    row_selection_mode
        Use `"none"` to disable row selection, `"single"` to allow a single row to be
        selected at a time, and `"multiple"` to allow multiple rows to be selected by
        clicking on them individually.

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
        height: Union[str, float, None] = "500px",
        summary: Union[bool, str] = True,
        filters: bool = False,
        row_selection_mode: RowSelectionMode = "none",
        editable: bool = False,
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
        self.row_selection_mode: RowSelectionMode = row_selection_mode
        self.editable = editable

    def to_payload(self) -> Jsonifiable:
        res = serialize_pandas_df(self.data)
        res["options"] = dict(
            width=self.width,
            height=self.height,
            summary=self.summary,
            filters=self.filters,
            row_selection_mode=self.row_selection_mode,
            editable=self.editable,
            style="grid",
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
    row_selection_mode
        Use `"none"` to disable row selection, `"single"` to allow a single row to be
        selected at a time, and `"multiple"` to allow multiple rows to be selected by
        clicking on them individually.

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
        row_selection_mode: RowSelectionMode = "none",
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
        self.row_selection_mode: RowSelectionMode = row_selection_mode

    def to_payload(self) -> Jsonifiable:
        res = serialize_pandas_df(self.data)
        res["options"] = dict(
            width=self.width,
            height=self.height,
            summary=self.summary,
            filters=self.filters,
            row_selection_mode=self.row_selection_mode,
            style="table",
        )
        return res


def serialize_pandas_df(df: "pd.DataFrame") -> dict[str, Any]:
    # Currently, we don't make use of the index; drop it so we don't error trying to
    # serialize it or something
    df = df.reset_index(drop=True)

    res = json.loads(
        # {index: [index], columns: [columns], data: [values]}
        df.to_json(None, orient="split")  # pyright: ignore[reportUnknownMemberType]
    )

    res["type_hints"] = serialize_numpy_dtypes(df)

    return res


# TODO-barret; make generic
DataFrameResult = Union[None, "pd.DataFrame", DataGrid, DataTable]


class OnCellUpdateFn(Protocol):
    async def __call__(
        self,
        *,
        row_index: int,
        column_id: str,
        value: str,
        prev: str,
        **kwargs: Any,  # future proofing
    ) -> Any: ...
class OnCellUpdateParams(TypedDict):
    row_index: int
    column_id: str
    value: str
    prev: str


class OnCellsUpdateFn(Protocol):
    async def __call__(
        self,
        *,
        update_infos: list[OnCellUpdateParams],
        **kwargs: Any,  # future proofing
    ) -> Any: ...
@dataclass
class CellPatch:
    row_index: int
    column_id: str
    value: str
    prev: str


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
    be `None` if no rows are selected, or a tuple of integers representing the indices
    of the selected rows. To filter a pandas data frame down to the selected rows, use
    `df.iloc[list(input.<id>_selected_rows())]`.

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

    handle_cell_update: OnCellUpdateFn
    handle_cells_update: OnCellsUpdateFn

    cell_patches: reactive.Value[list[CellPatch]]

    data: reactive.Calc_[pd.DataFrame]
    """
    Reactive value of the data frame's output data.
    """
    data_patched: reactive.Calc_[pd.DataFrame]
    """
    Reactive value of the data frame's edited output data.
    """
    row_selection_mode: reactive.Calc_[RowSelectionMode]
    """
    Reactive value of the data frame's row selection mode.
    """

    input_selected_rows: reactive.Calc_[tuple[int] | None]
    """
    Reactive value of selected rows indicies.

    This method is a wrapper around `input.<id>_selected_rows()`, where `<id>` is
    the `id` of the data frame output. This method returns the selected rows and
    will cause reactive updates as the selected rows change.

    Returns
    -------
    :
        * `None` if the row selection mode is None
        * `tuple[int]`representing the indices of the selected rows
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
        self._value = reactive.Value[DataFrameResult | None](None)

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
        def self_row_selection_mode() -> RowSelectionMode:
            value = self._value()
            req(value)
            if not isinstance(value, (DataGrid, DataTable)):
                raise TypeError(
                    f"Unsupported type returned from render function: {type(value)}. Expected `DataGrid` or `DataTable`"
                )

            return value.row_selection_mode

        self.row_selection_mode = self_row_selection_mode

        @reactive.calc
        def self_input_selected_rows() -> tuple[int] | None:
            mode = self.row_selection_mode()
            if mode == "none":
                return None
            return self._get_session().input[f"{self.output_id}_selected_rows"]()

        self.input_selected_rows = self_input_selected_rows

        @reactive.calc
        def self_data_selected() -> pd.DataFrame:
            indicies = self.input_selected_rows()
            if indicies is None:
                req(False)
                raise RuntimeError("This should never be reached for typing purposes")

            data = self.data_patched()
            return data.iloc[list(indicies)]

        self.data_selected = self_data_selected

        self.cell_patches = reactive.Value[list[CellPatch]]([])

        @reactive.calc
        def self_data_patched() -> pd.DataFrame:
            data = self.data()

            with pd.option_context("mode.copy_on_write", True):
                for cell_patch in self.cell_patches():
                    data.iat[cell_patch.row_index, cell_patch.column_id] = (
                        cell_patch.value
                    )
            return data

        self.data_patched = self_data_patched

    def _get_session(self) -> Session:
        if self._session is None:
            raise RuntimeError(
                "The data frame's session can only be accessed within a reactive context"
            )
        return self._session

    def on_cell_update(self, fn: OnCellUpdateFn) -> Self:
        self.handle_cell_update = fn
        return self

    def on_cells_update(self, fn: OnCellsUpdateFn) -> Self:
        self.handle_cells_update = fn
        return self

    def _init_handlers(self) -> None:
        async def _on_cell_update_default(
            *,
            row_index: int,
            column_id: str,
            value: str,
            prev: str,
            **kwargs: Any,
        ) -> str:
            return value

        async def _on_cells_update_default(
            *,
            update_infos: list[OnCellUpdateParams],
            **kwargs: Any,
        ):
            with reactive.isolate():
                formatted_values: list[Any] = []
                for update_info in update_infos:
                    row_index = update_info["row_index"]
                    column_id = update_info["column_id"]
                    value = update_info["value"]
                    prev = update_info["prev"]

                    formatted_value = await self.handle_cell_update(
                        row_index=row_index,
                        column_id=column_id,
                        value=value,
                        prev=prev,
                    )
                    # TODO-barret; check type here?
                    # TODO-barret; The return value should be coerced by pandas to the correct type
                    formatted_values.append(formatted_value)

                return formatted_values

        self.on_cell_update(_on_cell_update_default)
        self.on_cells_update(_on_cells_update_default)
        # self._add_message_handlers()

    # To be called by session's outputRPC message handler on this data_frame
    # Do not change this method unless you update corresponding code in `/js/dataframe/`!!
    async def _handle_cells_update(self, update_infos: list[OnCellUpdateParams]):
        with session_context(self._get_session()):
            with reactive.isolate():
                # Make new array to trigger reactive update
                patches = [p for p in self.cell_patches()]

                # Call on_cells_update
                formatted_values = await self.handle_cells_update(
                    update_infos=update_infos
                )

                if len(formatted_values) != len(update_infos):
                    raise ValueError(
                        f"The return value of {self.output_id}'s `handle_cells_update()` (typically set by `@{self.output_id}.on_cells_update`) must be a list of the same length as the input list of cell updates. Received {len(formatted_values)} items and expected {len(update_infos)}."
                    )

                # Add new patches
                # TODO-barret-future; Reduce the set to unique patches (by location)?
                for formatted_value, update_info in zip(formatted_values, update_infos):
                    patches.append(
                        CellPatch(
                            row_index=update_info["row_index"],
                            column_id=update_info["column_id"],
                            value=formatted_value,
                            prev=update_info["prev"],
                        )
                    )

                # Set new patches
                self.cell_patches.set(patches)

                return formatted_values

    def auto_output_ui(self) -> Tag:
        return ui.output_data_frame(id=self.output_id)

    def __init__(self, fn: ValueFn[DataFrameResult]):
        # Must be done before super().__init__ is called
        session = get_current_session()
        self._session = session

        super().__init__(fn)

        # Set reactives from calculated properties
        self._init_reactives()
        # Set update functions
        self._init_handlers()

    def _set_output_metadata(self, *, output_id: str) -> None:
        super()._set_output_metadata(output_id=output_id)

        # Verify that the session used when creating the renderer is the same session used
        # when executing the renderer. This is to prevent a user from creating a renderer
        # in one module and setting an output on another.

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

        value = await self.fn()
        if value is None:
            # Quit early
            self._value.set(None)
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
        # TODO-barret; capture data in render method
        # TODO-barret; invalidate data in render method before user fn has been called

        session = self._get_session()
        id = session.ns(self.output_id)

        await session.send_custom_message(
            "receiveMessage",
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
            mode = self.row_selection_mode()
        if mode == "none":
            raise ValueError(
                "You can't update row selections when row_selection_mode is 'none'"
            )

        if mode == "single" and len(idx) > 1:
            raise ValueError(
                "Attempted to set multiple row selection values when row_selection_mode is 'single'"
            )
        await self._send_message_to_browser("updateRowSelection", {"keys": idx})


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
