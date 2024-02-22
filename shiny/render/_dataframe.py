from __future__ import annotations

import abc
import json
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Literal,
    Optional,
    Protocol,
    Self,
    Sequence,
    Union,
    cast,
    runtime_checkable,
)

from htmltools import Tag

from .. import ui
from .._docstring import add_example, no_example
from .._utils import wrap_async
from ..reactive import Value as ReactiveValue
from ..reactive import isolate
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
        row_selection_mode: Literal["none", "single", "multiple"] = "none",
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
        self.row_selection_mode = row_selection_mode
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
        row_selection_mode: Union[
            Literal["none"], Literal["single"], Literal["multiple"]
        ] = "none",
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
        self.row_selection_mode = row_selection_mode

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


DataFrameResult = Union[None, "pd.DataFrame", DataGrid, DataTable]


class OnCellUpdateFn(Protocol):
    async def __call__(
        self,
        data: "pd.DataFrame",
        *,
        row_index: int,
        column_id: str,
        value: str,
        prev: str,
    ) -> Any: ...


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

    _row_selection_mode: str | None
    _session: Session | None
    _value: DataFrameResult
    _data: ReactiveValue[pd.DataFrame | None]

    # Reactive!
    # Turn this into a reactive calc value!
    def data_patched(self) -> pd.DataFrame | None:
        """
        Reactive value of the data frame output data.
        """
        data = self._data()
        if data is None:
            return None

        import pandas as pd

        if not isinstance(data, pd.DataFrame):
            raise TypeError(f"Unexpected type for self._data: {type(data)}")
        return data

    def _get_session(self) -> Session:
        if self._session is None:
            raise RuntimeError(
                "The input_selected_rows method can only be used within a reactive context"
            )
        return self._session

    def auto_output_ui(self) -> Tag:
        return ui.output_data_frame(id=self.output_id)

    _on_cell_update_fn: OnCellUpdateFn | None

    def on_cell_update(self, fn: OnCellUpdateFn | None) -> Self:
        self._on_cell_update_fn = fn
        return self

    def _add_message_handlers(self) -> None:
        self._on_cell_update_fn = None

        session = self._session
        if session is None:
            return

        UPDATE_CELL = "dataframeUpdateCell"
        if UPDATE_CELL not in session._message_handlers:

            from typing import TypedDict

            class UpdateDFParams(TypedDict):
                id: str
                rowIndex: int
                columnId: str
                value: str
                prev: str

            async def dataframe_update_cell(*args: UpdateDFParams):
                # TODO-barret; This should be a generic update method that dispatches to the output's on_cell_update method
                if self._on_cell_update_fn is None:
                    raise RuntimeError(
                        "`@render.data_frame` class has not set `on_cell_update` method."
                    )
                with session_context(session):
                    with isolate():
                        data = self.data_patched()
                        if data is None:
                            raise RuntimeError(
                                "`@render.data_frame` has no data to update. Please file an issue on GitHub with a reprex."
                            )
                        for arg in args:
                            row_index = arg["rowIndex"]
                            column_id = arg["columnId"]
                            value = arg["value"]
                            prev = arg["prev"]

                            formatted_value = await self._on_cell_update_fn(
                                data,
                                row_index=row_index,
                                column_id=column_id,
                                value=value,
                                prev=prev,
                            )
                            return formatted_value
                        # if active_session._debug:
                        #     print("Update cell: " + str(arg), flush=True)
                    # if active_session._debug:
                    #     print("Upload init: " + str(file_infos), flush=True)

                    # # TODO: Don't alter message in place?
                    # for fi in file_infos:
                    #     if fi["type"] == "":
                    #         fi["type"] = _utils.guess_mime_type(fi["name"])

                    # job_id = self._file_upload_manager.create_upload_operation(file_infos)
                    # worker_id = ""
                    # return {
                    #     "jobId": job_id,
                    #     "uploadUrl": f"session/{self.id}/upload/{job_id}?w={worker_id}",
                    # }
                    return None

            print("Adding message handler: ", UPDATE_CELL)
            session._message_handlers[UPDATE_CELL] = dataframe_update_cell

    def __init__(self, fn: ValueFn[DataFrameResult]):
        # Must be done before super().__init__ is called
        session = get_current_session()
        self._session = session

        super().__init__(fn)

        self._row_selection_mode = None
        self._data = ReactiveValue(None)

        self._add_message_handlers()

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
                "Please file an issue on GitHub with an example of how to reproduce this error. "
                "We would be curious to know your use case!"
            )

    async def render(self) -> Jsonifiable:
        with isolate():
            self._data.set(None)
        self._row_selection_mode = None

        value = await self.fn()
        if value is None:
            self._data.set(None)
            return None

        if not isinstance(value, AbstractTabularData):
            value = DataGrid(
                cast_to_pandas(
                    value,
                    "@render.data_frame doesn't know how to render objects of type",
                )
            )

        if isinstance(value, (DataGrid, DataTable)):
            self._data.set(value.data)
        else:
            self._data.set(value)
        self._row_selection_mode = value.row_selection_mode

        return value.to_payload()

    async def _send_message(self, handler: str, obj: dict[str, Any]):
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

    def input_selected_rows(self) -> tuple[int] | None:
        """
        Reactive input value of selected rows indicies.

        This method is a wrapper around `input.<id>_selected_rows()`, where `<id>` is
        the `id` of the data frame output. This method returns the selected rows and
        will cause reactive updates as the selected rows change.

        Returns
        -------
        :
            * `None` if the row selection mode is None
            * `tuple[int]`a tuple of integers representing the indices of the selected rows
        """
        return self._get_session().input[f"{self.output_id}_selected_rows"]()

    def data_selected_rows(self) -> pd.DataFrame | None:
        """
        Reactive input value of the selected rows in the data frame output.

        This method is a wrapper around `input.<id>_selected_rows()`, where `<id>` is
        the `id` of the data frame output. This method returns the selected rows and
        will cause reactive updates as the selected rows change.

        Returns
        -------
        :
            * `None` if the row selection mode is None
            * `tuple[int]`a tuple of integers representing the indices of the selected rows
        """
        indicies = self.input_selected_rows()
        if indicies is None:
            return None

        data = self.data_patched()
        if data is None:
            return None

        return data.iloc[list(indicies)]

    async def update_row_selection(
        self, idx: Optional[Sequence[int] | int] = None
    ) -> None:
        if idx is None:
            idx = ()
        elif isinstance(idx, int):
            idx = (idx,)

        mode = self._row_selection_mode
        if mode == "none":
            raise ValueError(
                "You can't update row selections when row_selection_mode is 'none'"
            )

        if mode == "single" and len(idx) > 1:
            raise ValueError(
                "Attempted to set multiple row selection values when row_selection_mode is 'single'"
            )
        await self._send_message("updateRowSelection", {"keys": idx})


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
