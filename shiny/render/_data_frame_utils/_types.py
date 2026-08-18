from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Dict,
    Literal,
    Optional,
    Protocol,
    Tuple,
    Union,
    cast,
    runtime_checkable,
)

import narwhals.stable.v1 as nw
from htmltools import TagNode
from narwhals.stable.v1.dtypes import DType as DType
from narwhals.stable.v1.typing import DataFrameT as DataFrameT
from narwhals.stable.v1.typing import IntoDataFrame as IntoDataFrame
from narwhals.stable.v1.typing import IntoDataFrameT as IntoDataFrameT
from narwhals.stable.v1.typing import IntoExpr as IntoExpr

from ..._typing_extensions import Annotated, NotRequired, Required, TypedDict
from ...types import Jsonifiable, JsonifiableDict, ListOrTuple

if TYPE_CHECKING:
    import pandas as pd

    from ...session._utils import RenderedDeps

__all__ = (
    "IntoExpr",
    "DataFrame",
    "DataFrameT",
    "DType",
    "IntoDataFrame",
    "IntoDataFrameT",
    "PandasCompatible",
    "CellHtml",
    "ColumnSort",
    "ColumnFilterStr",
    "ColumnFilterNumber",
    "ColumnFilter",
    "DataViewInfo",
    "FrameRenderPatchInfo",
    "FrameRenderSelectionModes",
    "FrameRender",
    "frame_render_to_jsonifiable",
    "FrameJsonOptions",
    "FrameJson",
    "RowsList",
    "ColsList",
    "ColIndexes",
    "FrameDtypeSubset",
    "FrameDtypeCategories",
    "FrameDtype",
    "StyleInfoBody",
    "StyleInfo",
    "BrowserStyleInfoBody",
    "BrowserStyleInfo",
    "CellValue",
    "CellPatch",
    "CellPatchProcessed",
)


# ---------------------------------------------------------------------

DataFrame = nw.DataFrame
Series = nw.Series

# ---------------------------------------------------------------------


@runtime_checkable
class PandasCompatible(Protocol):
    # Signature doesn't matter, runtime_checkable won't look at it anyway
    def to_pandas(self) -> pd.DataFrame: ...


class CellHtml(TypedDict):
    isShinyHtml: bool
    obj: RenderedDeps


# ---------------------------------------------------------------------


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


# ---------------------------------------------------------------------


class FrameRenderPatchInfo(TypedDict):
    key: str


class FrameRenderSelectionModes(TypedDict):
    row: Literal["single", "multiple", "none"]
    col: Literal["single", "multiple", "none"]
    rect: Literal["cell", "region", "none"]


class FrameRender(TypedDict):
    payload: FrameJson
    patchInfo: FrameRenderPatchInfo
    selectionModes: FrameRenderSelectionModes


def frame_render_to_jsonifiable(frame_render: FrameRender) -> JsonifiableDict:
    return cast(JsonifiableDict, dict(frame_render))


# ---------------------------------------------------------------------


class FrameJsonOptions(TypedDict):
    width: NotRequired[str | float | None]
    height: NotRequired[str | float | None]
    summary: NotRequired[bool | str]
    filters: NotRequired[bool]
    editable: NotRequired[bool]
    style: NotRequired[str]
    fill: NotRequired[bool]
    styles: NotRequired[list[BrowserStyleInfo]]


class FrameJson(TypedDict):
    columns: Required[list[str]]  # column names
    # index: Required[list[Any]]  # pandas index values
    data: Required[list[list[Jsonifiable]]]  # each entry is a row of len(columns)
    typeHints: Required[
        list[FrameDtype]
    ]  # each entry is a hint for the type of the column
    options: NotRequired[FrameJsonOptions]
    htmlDeps: NotRequired[list[JsonifiableDict]]


RowsList = Optional[ListOrTuple[int]]

ColsList = Optional[ListOrTuple[Union[str, int]]]
"""
Columns as a caller may supply them: either column names or column positions.

Resolve to :data:`ColIndexes` with `as_col_indexes()` before doing any work, as column
names are not dependable identifiers (they may be empty, and pandas allows names that
are not strings).
"""

ColIndexes = ListOrTuple[int]
"""
Columns as the internals address them: positions only, never names.
"""


# ---------------------------------------------------------------------


class FrameDtypeSubset(TypedDict):
    type: Literal[
        "string",
        "numeric",
        "boolean",
        "date",
        "datetime",
        "time",
        "duration",
        "object",
        "unknown",
        "html",
        "binary",
    ]


class FrameDtypeCategories(TypedDict):
    type: Literal["categorical"]
    categories: list[str]


FrameDtype = Union[
    FrameDtypeSubset,
    FrameDtypeCategories,
]


# ---------------------------------------------------------------------

# great_tables's StyleInfo
# @dataclass(frozen=True)
# class StyleInfo:
#     locname: str
#     locnum: int
#     grpname: str | None = None
#     colname: str | None = None
#     rownum: int | None = None
#     colnum: int | None = None
#     styles: list[CellStyle] = field(default_factory=list)


# https://typing.readthedocs.io/en/latest/spec/typeddict.html#alternative-syntax
# Use alternative syntax for TypedDict to avoid key error with `class`:
StyleInfoBody = TypedDict(
    "StyleInfoBody",
    {
        "location": NotRequired[Literal["body"]],
        "rows": NotRequired[Union[int, ListOrTuple[int], ListOrTuple[bool], None]],
        "cols": NotRequired[
            Union[str, int, ListOrTuple[str], ListOrTuple[int], ListOrTuple[bool], None]
        ],
        "style": NotRequired[Union[Dict[str, Jsonifiable], None]],
        "class": NotRequired[Union[str, None]],
    },
)
StyleInfo = StyleInfoBody


BrowserStyleInfoBody = TypedDict(
    "BrowserStyleInfoBody",
    {
        "location": Required[Literal["body"]],
        "rows": Required[Union[Tuple[int, ...], None]],
        "cols": Required[Union[Tuple[int, ...], None]],
        "style": Required[Union[Dict[str, Jsonifiable], None]],
        "class": Required[Union[str, None]],
    },
)
BrowserStyleInfo = BrowserStyleInfoBody


# Cell patches ----------------------------------------------------------

# CellValue = str | TagList | Tag | HTML
#
# A cell's value is either HTML-like content (`TagNode`, which includes `str`) or a
# non-string scalar. The scalars are limited to the JSON-native types, as patch values
# are sent back to the browser with `json.dumps()`; e.g. a `datetime` would serialize
# the data frame fine but raise when the patch is sent to the client.
#
# Non-string scalars matter when patching a non-string column: the browser always sends
# the edited value as a `str`, and writing that `str` into (say) a numeric column can
# fail (pandas raises `LossySetitemError`), so `@<data_frame>.set_patch_fn` is expected
# to coerce the value to the column's type before it is applied.
#
# `Jsonifiable`'s containers (list, tuple, dict) are deliberately excluded: a cell holds
# a single value, not a collection.
JsonifiableScalar = Union[str, int, float, bool, None]
CellValue = Union[TagNode, JsonifiableScalar]


class CellPatch(TypedDict):
    row_index: int
    column_index: int
    value: CellValue


class CellPatchProcessed(TypedDict):
    row_index: int
    column_index: int
    # HTML-like values are upgraded to `CellHtml`; the scalars in `CellValue` are passed
    # through as-is to be sent to the client.
    value: JsonifiableScalar | CellHtml
    # prev_value: CellValue


def cell_patch_processed_to_jsonifiable(
    cell_patch_processed: CellPatchProcessed,
) -> JsonifiableDict:
    return cast(JsonifiableDict, dict(cell_patch_processed))
