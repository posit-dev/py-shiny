from __future__ import annotations

import json
import typing
from dataclasses import asdict, dataclass
from typing import (
    Any,
    Awaitable,
    Callable,
    Literal,
    Optional,
    Tuple,
    Union,
    cast,
    overload,
)

from .. import _utils
from .._typing_extensions import Protocol, runtime_checkable
from ..render import RenderFunction, RenderFunctionAsync


# ======================================================================================
# RenderDataGrid
# ======================================================================================
# It would be nice to specify the return type of RenderPlotFunc to be something like:
#   Union[pandas.DataFrame, <protocol with .to_pandas()>]
# However, if we did that, we'd have to import pandas at load time, which adds
# a nontrivial amount of overhead. So for now, we're just using `object`.
@dataclass
class DataGridOptions:
    style: Union[Literal["table"], Literal["grid"]] = "table"
    summary: Union[bool, str] = True
    row_selection_mode: Union[
        Literal["none"], Literal["single"], Literal["multi"], Literal["multi-set"]
    ] = "none"


DataGridResult = Union[None, object, Tuple[object, DataGridOptions]]

RenderDataGridFunc = Callable[[], object]
RenderDataGridFuncAsync = Callable[[], Awaitable[object]]


@runtime_checkable
class PandasCompatible(Protocol):
    # Signature doesn't matter, runtime_checkable won't look at it anyway
    def to_pandas(self) -> object:
        ...


class RenderDataGrid(RenderFunction[DataGridResult, object]):
    def __init__(
        self,
        fn: RenderDataGridFunc,
        *,
        index: bool = False,
        width: Optional[str] = None,
        height: Optional[str] = None,
    ) -> None:
        super().__init__(fn)
        self._index = index
        self._width = width
        self._height = height
        # The Render*Async subclass will pass in an async function, but it tells the
        # static type checker that it's synchronous. wrap_async() is smart -- if is
        # passed an async function, it will not change it.
        self._fn: RenderDataGridFuncAsync = _utils.wrap_async(fn)

    def __call__(self) -> object:
        return _utils.run_coro_sync(self._run())

    async def _run(self) -> object:
        x = await self._fn()

        if x is None:
            return None

        options: DataGridOptions
        if isinstance(x, Tuple):
            options = cast(DataGridOptions, x[1])
            x = cast(object, x[0])
        else:
            options = DataGridOptions()

        import pandas as pd

        if not isinstance(x, pd.DataFrame):
            if not isinstance(x, PandasCompatible):
                raise TypeError(
                    "@render.table doesn't know how to render objects of type "
                    f"'{str(type(x))}'. Return either a pandas.DataFrame, or an object "
                    "that has a .to_pandas() method."
                )
            x = x.to_pandas()

        df = cast(pd.DataFrame, x)

        res: dict[str, Any] = json.loads(
            # {index: [index], columns: [columns], data: [values]}
            df.to_json(None, orient="split")  # pyright: ignore[reportUnknownMemberType]
        )

        res["options"] = asdict(options)
        res["width"] = self._width
        res["height"] = self._height

        return res


class RenderDataGridAsync(RenderDataGrid, RenderFunctionAsync[DataGridResult, object]):
    def __init__(
        self,
        fn: RenderDataGridFuncAsync,
        *,
        index: bool = False,
        width: Optional[str] = None,
        height: Optional[str] = None,
    ) -> None:
        if not _utils.is_async_callable(fn):
            raise TypeError(self.__class__.__name__ + " requires an async function")
        super().__init__(
            typing.cast(RenderDataGridFunc, fn),
            index=index,
            width=width,
            height=height,
        )

    async def __call__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
    ) -> object:
        return await self._run()


@overload
def data_grid(fn: RenderDataGridFunc | RenderDataGridFuncAsync) -> RenderDataGrid:
    ...


@overload
def data_grid(
    *,
    index: bool = False,
    width: Optional[str] = None,
    height: Optional[str] = None,
) -> Callable[[RenderDataGridFunc | RenderDataGridFuncAsync], RenderDataGrid]:
    ...


# TODO: Use more specific types for render.data_grid
def data_grid(
    fn: Optional[RenderDataGridFunc | RenderDataGridFuncAsync] = None,
    *,
    index: bool = False,
    width: Optional[str] = None,
    height: Optional[str] = None,
) -> (
    RenderDataGrid
    | Callable[[RenderDataGridFunc | RenderDataGridFuncAsync], RenderDataGrid]
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
    ~shiny.ui.output_data_grid
    """

    def wrapper(fn: RenderDataGridFunc | RenderDataGridFuncAsync) -> RenderDataGrid:
        if _utils.is_async_callable(fn):
            return RenderDataGridAsync(
                fn,
                index=index,
                width=width,
                height=height,
            )
        else:
            return RenderDataGrid(
                fn,
                index=index,
                width=width,
                height=height,
            )

    if fn is None:
        return wrapper
    else:
        return wrapper(fn)
