from __future__ import annotations

import abc
import json
from typing import TYPE_CHECKING, Any, Literal, Protocol, Union, cast, runtime_checkable

from htmltools import Tag

from .. import ui
from .._docstring import add_example, no_example
from ._dataframe_unsafe import serialize_numpy_dtypes
from .renderer import Jsonifiable, Renderer

if TYPE_CHECKING:
    import pandas as pd


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
        height: Union[str, float, None] = None,
        summary: Union[bool, str] = True,
        filters: bool = False,
        row_selection_mode: Literal["none", "single", "multiple"] = "none",
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

    def to_payload(self) -> Jsonifiable:
        res = serialize_pandas_df(self.data)
        res["options"] = dict(
            width=self.width,
            height=self.height,
            summary=self.summary,
            filters=self.filters,
            row_selection_mode=self.row_selection_mode,
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
    `input.<id>_selected_rows()` function, where `<id>` is the `id` of the
    :func:`~shiny.ui.output_data_frame`. The value returned will be `None` if no rows
    are selected, or a tuple of integers representing the indices of the selected rows.
    To filter a pandas data frame down to the selected rows, use
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

    # `<data_frame_renderer>.input_selected_rows()` method, where `<data_frame_renderer>` is the render function name that corresponds with the `id=` used in :func:`~shiny.ui.outout_data_frame`. Internally, this method retrieves the selected row value from session's `input.<id>_selected_rows()` value. The value returned will be `None` if no rows

    def auto_output_ui(self) -> Tag:
        return ui.output_data_frame(id=self.output_id)

    async def transform(self, value: DataFrameResult) -> Jsonifiable:
        if not isinstance(value, AbstractTabularData):
            value = DataGrid(
                cast_to_pandas(
                    value,
                    "@render.data_frame doesn't know how to render objects of type",
                )
            )
        return value.to_payload()

    # def input_selected_rows(self) -> Optional[tuple[int]]:
    #     """
    #     When `row_selection_mode` is set to "single" or "multiple" this will return
    #     a tuple of integers representing the rows selected by a user.
    #     """

    #     active_session = require_active_session(None)
    #     return active_session.input[self.output_id + "_selected_rows"]()


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
