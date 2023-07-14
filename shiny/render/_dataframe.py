from __future__ import annotations

import abc
import json
from typing import TYPE_CHECKING, Any, Literal, Protocol, Union, cast, runtime_checkable

from .._docstring import add_example
from . import RendererMeta, renderer_gen

if TYPE_CHECKING:
    import pandas as pd


class AbstractTabularData(abc.ABC):
    @abc.abstractmethod
    def to_payload(self) -> object:
        ...


class DataGrid(AbstractTabularData):
    """
    Holds the data and options for a ``shiny.render.data_frame`` output, for a
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
    :func:`~shiny.ui.output_data_frame`
    :func:`~shiny.render.data_frame`
    :class:`~shiny.render.DataTable`
    """

    def __init__(
        self,
        data: object,
        *,
        width: str | float | None = "fit-content",
        height: Union[str, float, None] = "500px",
        summary: Union[bool, str] = True,
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
        self.row_selection_mode = row_selection_mode

    def to_payload(self) -> object:
        res: dict[str, Any] = json.loads(
            # {index: [index], columns: [columns], data: [values]}
            self.data.to_json(  # pyright: ignore[reportUnknownMemberType]
                None, orient="split"
            )
        )
        res["options"] = dict(
            width=self.width,
            height=self.height,
            summary=self.summary,
            row_selection_mode=self.row_selection_mode,
            style="grid",
        )
        return res


class DataTable(AbstractTabularData):
    """
    Holds the data and options for a ``shiny.render.data_frame`` output, for a
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
    :func:`~shiny.ui.output_data_frame`
    :func:`~shiny.render.data_frame`
    :class:`~shiny.render.DataGrid`
    """

    def __init__(
        self,
        data: object,
        *,
        width: Union[str, float, None] = "fit-content",
        height: Union[str, float, None] = "500px",
        summary: Union[bool, str] = True,
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
        self.row_selection_mode = row_selection_mode

    def to_payload(self) -> object:
        res: dict[str, Any] = json.loads(
            # {index: [index], columns: [columns], data: [values]}
            self.data.to_json(  # pyright: ignore[reportUnknownMemberType]
                None, orient="split"
            )
        )
        res["options"] = dict(
            width=self.width,
            height=self.height,
            summary=self.summary,
            row_selection_mode=self.row_selection_mode,
            style="table",
        )
        return res


DataFrameResult = Union[None, "pd.DataFrame", DataGrid, DataTable]


# TODO-barret; Port `__name__` and `__docs__` of `value_fn`
@add_example()
@renderer_gen
def data_frame(
    meta: RendererMeta,
    x: DataFrameResult,
) -> object | None:
    """
    Reactively render a Pandas data frame object (or similar) as a basic HTML table.

    Returns
    -------
    :
        A decorator for a function that returns either a pandas :class:`DataFrame`
        object, pandas :class:`Styler` object, or any object that has a `.to_pandas()`
        method (e.g., a Polars data frame or Arrow table).

    Tip
    ----
    This decorator should be applied **before** the ``@output`` decorator. Also, the
    name of the decorated function (or ``@output(id=...)``) should match the ``id`` of a
    :func:`~shiny.ui.output_data_frame` container (see
    :func:`~shiny.ui.output_data_frame` for example usage).

    See Also
    --------
    :class:`~shiny.render.DataGrid`
    :class:`~shiny.render.DataTable`
    :func:`~shiny.ui.output_data_frame`
    """
    if x is None:
        return None

    if not isinstance(x, AbstractTabularData):
        x = DataGrid(
            cast_to_pandas(
                x, "@render.data_frame doesn't know how to render objects of type"
            )
        )
    return x.to_payload()


@runtime_checkable
class PandasCompatible(Protocol):
    # Signature doesn't matter, runtime_checkable won't look at it anyway
    def to_pandas(self) -> object:
        ...


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
