from __future__ import annotations

from typing import (
    Dict,
    List,
    Literal,
    Optional,
    Protocol,
    Tuple,
    Union,
    cast,
    runtime_checkable,
)

from ..._typing_extensions import Annotated, NotRequired, Required, TypedDict
from ...types import Jsonifiable, JsonifiableDict, ListOrTuple

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


RowsList = Optional[List[int]]
ColsList = Optional[List[str]]


# ---------------------------------------------------------------------


class FrameDtypeSubset(TypedDict):
    type: Literal["numeric", "string", "html", "datetime", "timedelta", "unknown"]


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
        "location": Required[Literal["body"]],
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

# ---------------------------------------------------------------------


# TODO-future; Replace this class with `htmltools.ReprHtml` when it is publically available. Even better... there should be a "is tag-like" method in htmltools that determines if the object could be enhanced by rendering
@runtime_checkable
class ReprHtml(Protocol):
    """
    Objects with a `_repr_html_()` method.
    """

    def _repr_html_(self) -> str: ...
