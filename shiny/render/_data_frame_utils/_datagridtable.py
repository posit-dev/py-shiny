from __future__ import annotations

# TODO-barret-future; make DataTable and DataGrid generic? By currently accepting `object`, it is difficult to capture the generic type of the data.
import abc
import json
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    Protocol,
    TypeVar,
    Union,
    cast,
    overload,
    runtime_checkable,
)

from htmltools import TagNode

from ..._docstring import add_example, no_example
from ..._typing_extensions import TypedDict
from ...session import Session
from ...session._utils import RenderedDeps, require_active_session
from ...types import Jsonifiable
from ._selection import (
    RowSelectionModeDeprecated,
    SelectionModeInput,
    SelectionModes,
    as_selection_modes,
)
from ._unsafe import is_shiny_html, serialize_numpy_dtypes

if TYPE_CHECKING:
    import pandas as pd

    DataFrameT = TypeVar("DataFrameT", bound=pd.DataFrame)
    # TODO-future; Pandas, Polars, api compat, etc.; Today, we only support Pandas

    DataFrameResult = Union[
        None,
        pd.DataFrame,
        "DataGrid",
        "DataTable",
    ]
else:
    # The parent class of `data_frame` needs something to hold onto
    # To avoid loading pandas, we use `object` as a placeholder
    DataFrameResult = Union[None, object, "DataGrid", "DataTable"]


class AbstractTabularData(abc.ABC):
    @abc.abstractmethod
    def to_payload(self) -> dict[str, Jsonifiable]: ...


def as_editable(
    editable: bool,
    *,
    name: str,
) -> bool:
    editable = bool(editable)
    # if editable:
    #     print(
    #         f"`{name}(editable=true)` is an experimental feature. "
    #         "If you find any bugs or would like different behavior, "
    #         "please make an issue at https://github.com/posit-dev/py-shiny/issues/new"
    #     )
    return editable


@add_example(ex_dir="../../api-examples/data_frame")
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
    row_selection_mode
        Deprecated. Please use `selection_mode=` instead.

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

    data: pd.DataFrame
    width: str | float | None
    height: str | float | None
    summary: bool | str
    filters: bool
    editable: bool
    selection_modes: SelectionModes

    def __init__(
        self,
        data: pd.DataFrame | PandasCompatible,
        *,
        width: str | float | None = "fit-content",
        height: str | float | None = None,
        summary: bool | str = True,
        filters: bool = False,
        editable: bool = False,
        selection_mode: SelectionModeInput = "none",
        row_selection_mode: RowSelectionModeDeprecated = "deprecated",
    ):

        self.data = cast_to_pandas(
            data,
            "The DataGrid() constructor didn't expect a 'data' argument of type",
        )

        self.width = width
        self.height = height
        self.summary = summary
        self.filters = filters
        self.editable = as_editable(editable, name="DataGrid")
        self.selection_modes = as_selection_modes(
            selection_mode,
            name="DataGrid",
            editable=self.editable,
            row_selection_mode=row_selection_mode,
        )

    def to_payload(self) -> dict[str, Jsonifiable]:
        res = serialize_pandas_df(self.data)
        res["options"] = dict(
            width=self.width,
            height=self.height,
            summary=self.summary,
            filters=self.filters,
            editable=self.editable,
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
    row_selection_mode
        Deprecated. Please use `mode={row_selection_mode}_row` instead.

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

    data: pd.DataFrame
    width: str | float | None
    height: str | float | None
    summary: bool | str
    filters: bool
    selection_modes: SelectionModes

    def __init__(
        self,
        data: pd.DataFrame | PandasCompatible,
        *,
        width: str | float | None = "fit-content",
        height: str | float | None = "500px",
        summary: bool | str = True,
        filters: bool = False,
        editable: bool = False,
        selection_mode: SelectionModeInput = "none",
        row_selection_mode: Literal["deprecated"] = "deprecated",
    ):

        self.data = cast_to_pandas(
            data,
            "The DataTable() constructor didn't expect a 'data' argument of type",
        )

        self.width = width
        self.height = height
        self.summary = summary
        self.filters = filters
        self.editable = as_editable(editable, name="DataTable")
        self.selection_modes = as_selection_modes(
            selection_mode,
            name="DataTable",
            editable=self.editable,
            row_selection_mode=row_selection_mode,
        )

    def to_payload(self) -> dict[str, Jsonifiable]:
        res = serialize_pandas_df(self.data)
        res["options"] = dict(
            width=self.width,
            height=self.height,
            summary=self.summary,
            filters=self.filters,
            editable=self.editable,
            style="table",
        )
        return res


def serialize_pandas_df(df: "pd.DataFrame") -> dict[str, Any]:

    columns = df.columns.tolist()
    columns_set = set(columns)
    if len(columns_set) != len(columns):
        raise ValueError(
            "The column names of the pandas DataFrame are not unique."
            " This is not supported by the data_frame renderer."
        )

    # Currently, we don't make use of the index; drop it so we don't error trying to
    # serialize it or something
    df = df.reset_index(drop=True)

    # # Can we keep the original column information?
    # # Maybe we need to inspect the original columns for any "unknown" column type. See if it contains any HTML or Tag objects
    # for col in columns:
    #     if df[col].dtype.name == "unknown":
    #         print(df[col].to_list())
    #         raise ValueError(
    #             "The pandas DataFrame contains columns of type 'object'."
    #             " This is not supported by the data_frame renderer."
    #         )

    type_hints = serialize_numpy_dtypes(df)

    # Auto opt-in for html columns
    html_columns = [
        i for i, type_hint in enumerate(type_hints) if type_hint["type"] == "html"
    ]

    if len(html_columns) > 0:
        # Enable copy-on-write mode for the data;
        # Use `deep=False` to avoid copying the full data; CoW will copy the necessary data when modified
        import pandas as pd

        with pd.option_context("mode.copy_on_write", True):
            df = df.copy(deep=False)
            session = require_active_session(None)

            def wrap_shiny_html_with_session(x: TagNode):
                return wrap_shiny_html(x, session=session)

            for html_column in html_columns:
                # _upgrade_ all the HTML columns to `CellHtml` json objects
                df[df.columns[html_column]] = df[
                    df.columns[html_column]
                ].apply(  # pyright: ignore[reportUnknownMemberType]
                    wrap_shiny_html_with_session
                )

    res = json.loads(
        # {index: [index], columns: [columns], data: [values]}
        df.to_json(None, orient="split")  # pyright: ignore[reportUnknownMemberType]
    )

    res["typeHints"] = type_hints

    # print(json.dumps(res, indent=4))
    return res


@runtime_checkable
class PandasCompatible(Protocol):
    # Signature doesn't matter, runtime_checkable won't look at it anyway
    def to_pandas(self) -> pd.DataFrame: ...


@overload
def cast_to_pandas(x: DataFrameT, error_message_begin: str) -> DataFrameT: ...


@overload
def cast_to_pandas(x: PandasCompatible, error_message_begin: str) -> pd.DataFrame: ...


def cast_to_pandas(
    x: DataFrameT | PandasCompatible, error_message_begin: str
) -> DataFrameT | pd.DataFrame:
    import pandas as pd

    if isinstance(x, pd.DataFrame):
        return x

    if isinstance(x, PandasCompatible):
        return x.to_pandas()

    raise TypeError(
        error_message_begin
        + f" '{str(type(x))}'. Use either a pandas.DataFrame, or an object"
        " that has a .to_pandas() method."
    )


class CellHtml(TypedDict):
    isShinyHtml: bool
    obj: RenderedDeps


@overload
def wrap_shiny_html(  # pyright: ignore[reportOverlappingOverload]
    x: TagNode, *, session: Session
) -> CellHtml: ...
@overload
def wrap_shiny_html(x: Jsonifiable, *, session: Session) -> Jsonifiable: ...
def wrap_shiny_html(
    x: Jsonifiable | TagNode, *, session: Session
) -> Jsonifiable | CellHtml:
    if is_shiny_html(x):
        return {"isShinyHtml": True, "obj": session._process_ui(x)}
    return cast(Jsonifiable, x)
