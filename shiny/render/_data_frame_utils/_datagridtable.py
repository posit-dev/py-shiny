# TODO-future-barret; Maybe use a `._options()` method to return a `JsonifiableDict` within the DataGrid/DataTable classes?
# TODO-future-barret; Really feals as if we should have a base class that does most of this for us

from __future__ import annotations

import abc
from typing import Generic, Literal

from ..._docstring import add_example
from ._selection import (
    RowSelectionModeDeprecated,
    SelectionModeInput,
    SelectionModes,
    as_selection_modes,
)
from ._styles import StyleFn, StyleInfo, as_browser_style_infos, as_style_infos
from ._tbl_data import assert_data_is_not_none, serialize_frame
from ._types import FrameJson, IntoDataFrameT


class AbstractTabularData(abc.ABC):
    @abc.abstractmethod
    def to_payload(self) -> FrameJson: ...


@add_example(ex_dir="../../api-examples/data_frame_grid_table")
@add_example(ex_dir="../../api-examples/data_frame_styles")
class DataGrid(AbstractTabularData, Generic[IntoDataFrameT]):
    """
    Holds the data and options for a :class:`~shiny.render.data_frame` output, for a
    spreadsheet-like view.

    This class is used to wrap the returned data frame from a `@render.data_frame`
    render function. It allows you to specify options for the data grid, such as the
    width and height of the grid, whether to show a summary message, whether to show
    filter inputs, whether the cells are editable, and how the cells are selected.

    While there are currently no execution or parameter differences between `DataGrid`
    and `DataTable` other than CSS styling in the browser, the two classes are kept
    separate to allow for future extensibility.

    Parameters
    ----------
    data
        A [pandas](https://pandas.pydata.org/), [polars](https://pola.rs/), or
        eager [`narwhals`](https://narwhals-dev.github.io/narwhals/) compatible `DataFrame`
        object.
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
        * `location`: This value `"body"` and is not required.
        * `rows`: The row numbers to which the style should be applied. If `None`, the
            style will be applied to all rows.
        * `cols`: The column numbers to which the style should be applied. If `None`,
            the style will be applied to all columns.
        * `style`: A dictionary of CSS properties and values to apply to the selected
            rows and columns. Traditional _kebab-cased_ CSS property names (e.g.
            `background-color`) will work in addition to _camelCased_ CSS property names
            (e.g. `backgroundColor`).
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

    data: IntoDataFrameT
    width: str | float | None
    height: str | float | None
    summary: bool | str
    filters: bool
    editable: bool
    selection_modes: SelectionModes
    styles: list[StyleInfo] | StyleFn[IntoDataFrameT]

    def __init__(
        self,
        data: IntoDataFrameT,
        *,
        width: str | float | None = "fit-content",
        height: str | float | None = None,
        summary: bool | str = True,
        filters: bool = False,
        editable: bool = False,
        selection_mode: SelectionModeInput = "none",
        styles: StyleInfo | list[StyleInfo] | StyleFn[IntoDataFrameT] | None = None,
        row_selection_mode: RowSelectionModeDeprecated = "deprecated",
    ):
        assert_data_is_not_none(data)
        self.data = data

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
        """
        Converts the `DataGrid` object to a payload dictionary.

        Returns
        -------
        :
            The payload dictionary representing the `DataGrid` object.
        """
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
                    into_data=self.data,
                ),
            },
        }
        return res


@add_example(ex_dir="../../api-examples/data_frame_grid_table")
@add_example(ex_dir="../../api-examples/data_frame_styles")
class DataTable(AbstractTabularData, Generic[IntoDataFrameT]):
    """
    Holds the data and options for a :class:`~shiny.render.data_frame` output, for a
    spreadsheet-like view.

    This class is used to wrap the returned data frame from a `@render.data_frame`
    render function. It allows you to specify options for the data table, such as the
    width and height of the table, whether to show a summary message, whether to show
    filter inputs, whether the cells are editable, and how the cells are selected.

    While there are currently no execution or parameter differences between `DataGrid`
    and `DataTable` other than CSS styling in the browser, the two classes are kept
    separate to allow for future extensibility.

    Parameters
    ----------
    data
        A [pandas](https://pandas.pydata.org/), [polars](https://pola.rs/), or
        eager [`narwhals`](https://narwhals-dev.github.io/narwhals/) compatible `DataFrame`
        object.
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
        * `location`: This value `"body"` and is not required.
        * `rows`: The row numbers to which the style should be applied. If `None`, the
            style will be applied to all rows.
        * `cols`: The column numbers to which the style should be applied. If `None`,
            the style will be applied to all columns.
        * `style`: A dictionary of CSS properties and values to apply to the selected
            rows and columns. Traditional _kebab-cased_ CSS property names (e.g.
            `background-color`) will work in addition to _camelCased_ CSS property names
            (e.g. `backgroundColor`).
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

    data: IntoDataFrameT
    width: str | float | None
    height: str | float | None
    summary: bool | str
    filters: bool
    editable: bool
    selection_modes: SelectionModes
    styles: list[StyleInfo] | StyleFn[IntoDataFrameT]

    def __init__(
        self,
        data: IntoDataFrameT,
        *,
        width: str | float | None = "fit-content",
        height: str | float | None = "500px",
        summary: bool | str = True,
        filters: bool = False,
        editable: bool = False,
        selection_mode: SelectionModeInput = "none",
        styles: StyleInfo | list[StyleInfo] | StyleFn[IntoDataFrameT] | None = None,
        row_selection_mode: Literal["deprecated"] = "deprecated",
    ):
        assert_data_is_not_none(data)

        self.data = data

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
        """
        Converts the `DataTable` object to a payload dictionary.

        Returns
        -------
        :
            The payload dictionary representing the `DataTable` object.
        """
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
                    into_data=self.data,
                ),
            },
        }
        return res
