from __future__ import annotations

import abc
import json
import typing
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Literal,
    Optional,
    Protocol,
    Union,
    cast,
    overload,
    runtime_checkable,
)

from .. import _utils
from .._docstring import add_example
from . import RenderFunction, RenderFunctionAsync
from ._dataframe_unsafe import serialize_numpy_dtypes

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

    def to_payload(self) -> object:
        res = serialize_pandas_df(self.data)
        res["options"] = dict(
            width=self.width,
            height=self.height,
            summary=self.summary,
            filters=self.filters,
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

    def to_payload(self) -> object:
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
    res = json.loads(
        # {index: [index], columns: [columns], data: [values]}
        df.to_json(None, orient="split")  # pyright: ignore[reportUnknownMemberType]
    )

    res["type_hints"] = serialize_numpy_dtypes(df)

    return res


DataFrameResult = Union[None, "pd.DataFrame", DataGrid, DataTable]

RenderDataFrameFunc = Callable[[], DataFrameResult]
RenderDataFrameFuncAsync = Callable[[], Awaitable[DataFrameResult]]


@runtime_checkable
class PandasCompatible(Protocol):
    # Signature doesn't matter, runtime_checkable won't look at it anyway
    def to_pandas(self) -> object:
        ...


class RenderDataFrame(RenderFunction[DataFrameResult, object]):
    def __init__(
        self,
        fn: RenderDataFrameFunc,
    ) -> None:
        super().__init__(fn)
        # The Render*Async subclass will pass in an async function, but it tells the
        # static type checker that it's synchronous. wrap_async() is smart -- if is
        # passed an async function, it will not change it.
        self._fn: RenderDataFrameFuncAsync = _utils.wrap_async(fn)

    def __call__(self) -> object:
        return _utils.run_coro_sync(self._run())

    async def _run(self) -> object:
        x = await self._fn()

        if x is None:
            return None

        if not isinstance(x, AbstractTabularData):
            x = DataGrid(
                cast_to_pandas(
                    x, "@render.data_frame doesn't know how to render objects of type"
                )
            )

        return x.to_payload()


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


class RenderDataFrameAsync(
    RenderDataFrame, RenderFunctionAsync[DataFrameResult, object]
):
    def __init__(
        self,
        fn: RenderDataFrameFuncAsync,
    ) -> None:
        if not _utils.is_async_callable(fn):
            raise TypeError(self.__class__.__name__ + " requires an async function")
        super().__init__(
            typing.cast(RenderDataFrameFunc, fn),
        )

    async def __call__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
    ) -> object:
        return await self._run()


@overload
def data_frame(fn: RenderDataFrameFunc | RenderDataFrameFuncAsync) -> RenderDataFrame:
    ...


@overload
def data_frame() -> (
    Callable[[RenderDataFrameFunc | RenderDataFrameFuncAsync], RenderDataFrame]
):
    ...


@add_example()
def data_frame(
    fn: Optional[RenderDataFrameFunc | RenderDataFrameFuncAsync] = None,
) -> (
    RenderDataFrame
    | Callable[[RenderDataFrameFunc | RenderDataFrameFuncAsync], RenderDataFrame]
):
    """
    Reactively render a Pandas data frame object (or similar) as a basic HTML table.

    Parameters
    ----------
    index
        Whether to print index (row) labels.
    selection


    Returns
    -------
    :
        A decorator for a function that returns any of the following:

        1. A pandas :class:`DataFrame` object.
        2. A pandas :class:`Styler` object.
        3. Any object that has a `.to_pandas()` method (e.g., a Polars data frame or
           Arrow table).

    Tip
    ----
    This decorator should be applied **before** the ``@output`` decorator. Also, the
    name of the decorated function (or ``@output(id=...)``) should match the ``id`` of
    a :func:`~shiny.ui.output_table` container (see :func:`~shiny.ui.output_table` for
    example usage).

    See Also
    --------
    ~shiny.ui.output_data_frame
    """

    def wrapper(fn: RenderDataFrameFunc | RenderDataFrameFuncAsync) -> RenderDataFrame:
        if _utils.is_async_callable(fn):
            return RenderDataFrameAsync(fn)
        else:
            return RenderDataFrame(cast(RenderDataFrameFunc, fn))

    if fn is None:
        return wrapper
    else:
        return wrapper(fn)
