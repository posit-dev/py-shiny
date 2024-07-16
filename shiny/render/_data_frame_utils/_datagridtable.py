from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Generic, Literal, Union

from ..._docstring import add_example
from ._selection import (
    RowSelectionModeDeprecated,
    SelectionModeInput,
    SelectionModes,
    as_selection_modes,
)
from ._styles import StyleFn, StyleInfo, as_browser_style_infos, as_style_infos
from ._tbl_data import as_data_frame_like, serialize_frame
from ._types import DataFrameLikeT, FrameJson

if TYPE_CHECKING:

    DataFrameResult = Union[
        None,
        DataFrameLikeT,
        "DataGrid[DataFrameLikeT]",
        "DataTable[DataFrameLikeT]",
    ]

else:
    # The parent class of `data_frame` needs something to hold onto
    # To avoid loading pandas, we use `object` as a placeholder
    DataFrameResult = Union[None, object]


class AbstractTabularData(abc.ABC):
    @abc.abstractmethod
    def to_payload(self) -> FrameJson: ...


@add_example(ex_dir="../../api-examples/data_frame_grid_table")
@add_example(ex_dir="../../api-examples/data_frame_styles")
class DataGrid(AbstractTabularData, Generic[DataFrameLikeT]):
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
    editable
        If `True`, allows the user to edit the cells in the grid. When a cell is edited,
        the new value is sent to the server for processing. The server can then return
        a new value for the cell, which will be displayed in the grid.
    selection_mode
        Single string or a `set`/`list`/`tuple` of string values to define possible ways
        to select data within the data frame.

        Supported values:
        * Use `"none"` to disable any cell selections or editing.
        * Use `"row"` to allow a single row to be selected at a time.
        * Use `"rows"` to allow multiple rows to be selected by clicking on them
        individually.

        Resolution rules:
        * If `"none"` is supplied, all other values will be ignored.
        * If both `"row"` and `"rows"` are supplied, `"row"` will be dropped (supporting `"rows"`).
    styles
        A style info object, a list of style info objects, or a function that receives
        the (possibly updated) data frame and returns a list of style info objects. The
        style info objects can be used to apply CSS styles to the data frame. If
        `styles=None`, no styling will be applied.

        Style info object key/value description:
        * `location`: This value is required and currently only supports `"body"`.
        * `rows`: The row numbers to which the style should be applied. If `None`, the
            style will be applied to all rows.
        * `cols`: The column numbers to which the style should be applied. If `None`,
            the style will be applied to all columns.
        * `style`: A dictionary of CSS properties and values to apply to the selected
            rows and columns. The keys must be _camelCased_ CSS property names to work
            properly with react.js (e.g. `backgroundColor` instead of
            `background-color`).
        * `class`: A string of CSS class names to apply to the selected rows and columns.

        If both `style` and `class` are missing or `None`, nothing will be applied. If
        both `rows` and `cols` are missing or `None`, the style will be applied to the
        complete data frame.
    row_selection_mode
        Deprecated. Please use `selection_mode=` instead.

    Returns
    -------
    :
        An object suitable for being returned from a `@render.data_frame`-decorated
        output function.

    See Also
    --------
    * :func:`~shiny.ui.output_data_frame` - The UI placeholder for a data frame output.
    * :class:`~shiny.render.data_frame` - The `render` method for data frames.
    * :class:`~shiny.render.DataTable` - A more _tabular_ view of the data.
    """

    data: DataFrameLikeT
    width: str | float | None
    height: str | float | None
    summary: bool | str
    filters: bool
    editable: bool
    selection_modes: SelectionModes
    styles: list[StyleInfo] | StyleFn[DataFrameLikeT]

    def __init__(
        self,
        data: DataFrameLikeT,
        *,
        width: str | float | None = "fit-content",
        height: str | float | None = None,
        summary: bool | str = True,
        filters: bool = False,
        editable: bool = False,
        selection_mode: SelectionModeInput = "none",
        styles: StyleInfo | list[StyleInfo] | StyleFn[DataFrameLikeT] | None = None,
        row_selection_mode: RowSelectionModeDeprecated = "deprecated",
    ):

        self.data = as_data_frame_like(data)

        self.width = width
        self.height = height
        self.summary = summary
        self.filters = filters
        self.editable = bool(editable)
        self.selection_modes = as_selection_modes(
            selection_mode,
            name="DataGrid",
            row_selection_mode=row_selection_mode,
        )
        self.styles = as_style_infos(styles)

    def to_payload(self) -> FrameJson:
        res: FrameJson = {
            **serialize_frame(self.data),
            "options": {
                "width": self.width,
                "height": self.height,
                "summary": self.summary,
                "filters": self.filters,
                "editable": self.editable,
                "style": "grid",
                "fill": self.height is None,
                "styles": as_browser_style_infos(
                    self.styles,
                    data=self.data,
                ),
            },
        }
        return res


@add_example(ex_dir="../../api-examples/data_frame_grid_table")
@add_example(ex_dir="../../api-examples/data_frame_styles")
class DataTable(AbstractTabularData, Generic[DataFrameLikeT]):
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
    editable
        If `True`, allows the user to edit the cells in the grid. When a cell is edited,
        the new value is sent to the server for processing. The server can then return
        a new value for the cell, which will be displayed in the grid.
    selection_mode
        Single string or a `set`/`list`/`tuple` of string values to define possible ways
        to select data within the data frame.

        Supported values:
        * Use `"none"` to disable any cell selections or editing.
        * Use `"row"` to allow a single row to be selected at a time.
        * Use `"rows"` to allow multiple rows to be selected by clicking on them
        individually.

        Resolution rules:
        * If `"none"` is supplied, all other values will be ignored.
        * If both `"row"` and `"rows"` are supplied, `"row"` will be dropped (supporting `"rows"`).
    styles
        A style info object, a list of style info objects, or a function that receives
        the (possibly updated) data frame and returns a list of style info objects. The
        style info objects can be used to apply CSS styles to the data frame. If
        `styles=None`, no styling will be applied.

        Style info object key/value description:
        * `location`: This value is required and currently only supports `"body"`.
        * `rows`: The row numbers to which the style should be applied. If `None`, the
            style will be applied to all rows.
        * `cols`: The column numbers to which the style should be applied. If `None`,
            the style will be applied to all columns.
        * `style`: A dictionary of CSS properties and values to apply to the selected
            rows and columns. The keys must be _camelCased_ CSS property names to work
            properly with react.js (e.g. `backgroundColor` instead of
            `background-color`).
        * `class`: A string of CSS class names to apply to the selected rows and columns.

        If both `style` and `class` are missing or `None`, nothing will be applied. If
        both `rows` and `cols` are missing or `None`, the style will be applied to the
        complete data frame.
    row_selection_mode
        Deprecated. Please use `mode={row_selection_mode}_row` instead.

    Returns
    -------
    :
        An object suitable for being returned from a `@render.data_frame`-decorated
        output function.

    See Also
    --------
    * :func:`~shiny.ui.output_data_frame` - The UI placeholder for a data frame output.
    * :class:`~shiny.render.data_frame` - The `render` method for data frames.
    * :class:`~shiny.render.DataTable` - A more _grid_ view of the data.
    """

    data: DataFrameLikeT
    width: str | float | None
    height: str | float | None
    summary: bool | str
    filters: bool
    editable: bool
    selection_modes: SelectionModes
    styles: list[StyleInfo] | StyleFn[DataFrameLikeT]

    def __init__(
        self,
        data: DataFrameLikeT,
        *,
        width: str | float | None = "fit-content",
        height: str | float | None = "500px",
        summary: bool | str = True,
        filters: bool = False,
        editable: bool = False,
        selection_mode: SelectionModeInput = "none",
        styles: StyleInfo | list[StyleInfo] | StyleFn[DataFrameLikeT] | None = None,
        row_selection_mode: Literal["deprecated"] = "deprecated",
    ):
        self.data = as_data_frame_like(data)

        self.width = width
        self.height = height
        self.summary = summary
        self.filters = filters
        self.editable = bool(editable)
        self.selection_modes = as_selection_modes(
            selection_mode,
            name="DataTable",
            row_selection_mode=row_selection_mode,
        )
        self.styles = as_style_infos(styles)

    def to_payload(self) -> FrameJson:
        res: FrameJson = {
            **serialize_frame(self.data),
            "options": {
                "width": self.width,
                "height": self.height,
                "summary": self.summary,
                "filters": self.filters,
                "editable": self.editable,
                "style": "table",
                "styles": as_browser_style_infos(
                    self.styles,
                    data=self.data,
                ),
            },
        }
        return res
