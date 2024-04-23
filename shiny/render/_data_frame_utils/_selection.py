from __future__ import annotations

# TODO-barret-render.data_frame; Docs
# TODO-barret-render.data_frame; Add examples of selection!
import warnings
from typing import TYPE_CHECKING, Literal, Set, Union, cast

from ..._deprecated import warn_deprecated
from ..._typing_extensions import Annotated, TypedDict
from ...types import MISSING, MISSING_TYPE, Jsonifiable, ListOrTuple

if TYPE_CHECKING:
    import pandas as pd

NoneSelectionMode = Literal["none"]
RowSelectionMode = Literal["row", "rows"]
ColSelectionMode = Literal["col", "cols"]
RectSelectionMode = Literal["cell", "region"]

SelectionMode = Union[
    RowSelectionMode,
    ColSelectionMode,
    RectSelectionMode,
    NoneSelectionMode,
]
none_set: set[NoneSelectionMode] = {"none"}
row_set: set[RowSelectionMode] = {"row", "rows"}
col_set: set[ColSelectionMode] = {"col", "cols"}
rect_set: set[RectSelectionMode] = {"cell", "region"}
complete_selection_mode_set: set[SelectionMode] = (
    none_set | row_set | col_set | rect_set
)


# Types
class SelectionModes:

    row: Literal["none", "single", "multiple"]
    col: Literal["none", "single", "multiple"]
    rect: Literal["none", "cell", "region"]

    def as_dict(self) -> dict[str, Jsonifiable]:
        return {
            "row": self.row,
            "col": self.col,
            "rect": self.rect,
        }

    def __init__(self, *, selection_mode_set: set[SelectionMode]):
        self.row = "none"
        self.col = "none"
        self.rect = "none"

        if not selection_mode_set.issubset(complete_selection_mode_set):
            bad_modes = selection_mode_set - complete_selection_mode_set
            # TODO-test; Test that this error is raised
            raise ValueError(
                f"Unknown selection modes: {', '.join(bad_modes)}. "
                f"Valid selection modes: {', '.join(complete_selection_mode_set)}"
            )

        if len(selection_mode_set) == 0:
            selection_mode_set = {"none"}
        elif "none" in selection_mode_set and len(selection_mode_set) > 1:
            extra_set = selection_mode_set - none_set
            # TODO-test; Test that this error is raised
            raise ValueError(
                "Cannot have other selection modes included with `none`. "
                f"Extra selection modes: {', '.join(extra_set)}"
            )

        if "row" in selection_mode_set and "rows" in selection_mode_set:
            raise ValueError("Cannot have both `row` and `rows` in selection modes.")

        if "col" in selection_mode_set and "cols" in selection_mode_set:
            raise ValueError("Cannot have both `col` and `cols` in selection modes.")

        if "cell" in selection_mode_set and "region" in selection_mode_set:
            raise ValueError("Cannot have both `cell` and `region` in selection modes.")

        if "row" in selection_mode_set:
            self.row = "single"
        elif "rows" in selection_mode_set:
            self.row = "multiple"

        if "col" in selection_mode_set:
            raise RuntimeError(
                "Column based cell selections are not currently supported."
            )
            self.col = "single"
        elif "cols" in selection_mode_set:
            raise RuntimeError(
                "Column based cell selections are not currently supported."
            )
            self.col = "multiple"

        if "cell" in selection_mode_set:
            raise RuntimeError(
                "Cell based cell selections are not currently supported."
            )
            self.rect = "cell"
        elif "region" in selection_mode_set:
            raise RuntimeError(
                "Region based cell selections are not currently supported."
            )
            self.rect = "region"

    def _is_none(self) -> bool:
        """
        Check if all selection modes are set to `"none"`.
        """
        return (self.row == "none") and (self.col == "none") and (self.rect == "none")

    def _has_row(self) -> bool:
        """
        Check if `.row` does not equal `"none"`.
        """
        return self.row != "none"

    def _has_col(self) -> bool:
        """
        Check if `.col` does not equal `"none"`.
        """
        return self.col != "none"

    def _has_rect(self) -> bool:
        """
        Check if `.rect` does not equal `"none"`.
        """
        return self.rect != "none"


SelectionModeInput = Union[
    # String
    SelectionMode,
    # Sequence of strings
    ListOrTuple[SelectionMode],
    # Set[SelectionMode],
    # Support the upgraded selection modes
    SelectionModes,
]
"""
Input types for selection modes in a DataGrid or DataTable.
"""


# ####################
# # CellSelection: For receiving selection info from JS
# ####################

# Should only contain a single selection area

# # Do not include `CellSelectionAll` as it should be represented by a row, column, or region with appropriate values.
# class CellSelectionAll(TypedDict):
#     type: Literal["all"]


class CellSelectionNone(TypedDict):
    type: Literal["none"]


class CellSelectionRow(TypedDict):
    type: Literal["row"]
    rows: ListOrTuple[int]


class CellSelectionCol(TypedDict):
    type: Literal["col"]
    cols: ListOrTuple[int]


class CellSelectionRect(TypedDict):
    type: Literal["rect"]
    # Attempt to type the list of size 2, but it is not type enforced
    rows: tuple[int, int] | Annotated[list[int], 2]
    cols: tuple[int, int] | Annotated[list[int], 2]


# For receiving selection info from JS:
CellSelection = Union[
    CellSelectionRow,
    CellSelectionCol,
    CellSelectionRect,
    CellSelectionNone,
]
"""
A single selection set sent to/from the browser.

- `"none"`: No cells are selected
- `"row"`: A set of selected rows
- `"col"`: A set of selected columns
- `"rect"`: A single rectangular region that is selected
"""

# ####################


def to_tuple_or_none(x: int | ListOrTuple[int] | None) -> tuple[int, ...] | None:
    if x is None:
        return None
    if isinstance(x, int):
        return (x,)

    assert isinstance(x, (list, tuple))
    x = tuple(x)
    # if len(x) == 0:
    #     return None
    for i in x:
        assert isinstance(i, int)
    return x


def as_cell_selection(
    x: CellSelection | Literal["all"] | None,
    *,
    selection_modes: SelectionModes,
    data: pd.DataFrame | MISSING_TYPE = MISSING,
) -> CellSelection:

    if x is None or selection_modes._is_none():
        return {"type": "none"}

    if x == "all":
        if isinstance(data, MISSING_TYPE):
            raise ValueError(
                "Cannot use `all` selection mode without providing `data`."
            )
        row_len, col_len = data.shape
        # Look at the selection modes to determine what to do
        if selection_modes._has_rect():
            if selection_modes.rect == "cell":
                warnings.warn(
                    "Cannot select all cells with `cell` selection mode. Selecting the first cell",
                    stacklevel=3,
                )
                return {"type": "rect", "rows": (0, 0), "cols": (0, 0)}
            if selection_modes.rect == "region":
                return {
                    "type": "rect",
                    "rows": (0, row_len - 1),
                    "cols": (0, col_len - 1),
                }
        if selection_modes._has_row():
            if selection_modes.row == "single":
                warnings.warn(
                    "Cannot select all rows with `row` selection mode. Selecting the first row",
                    stacklevel=3,
                )
                return {"type": "row", "rows": (0,)}
            if selection_modes.row == "multiple":
                return {"type": "row", "rows": tuple(range(row_len))}
        if selection_modes._has_col():
            if selection_modes.col == "single":
                warnings.warn(
                    "Cannot select all columns with `col` selection mode. Selecting the first column",
                    stacklevel=3,
                )
                return {"type": "col", "cols": (0,)}
            if selection_modes.col == "multiple":
                return {"type": "col", "cols": tuple(range(col_len))}
        raise ValueError(
            "Current selection modes do not support cell based selection. "
            f"Current selection modes: {selection_modes}"
        )

    # Can't handle lists of dictionaries right now
    assert isinstance(x, dict)

    row_value = to_tuple_or_none(x.get("rows", None))
    col_value = to_tuple_or_none(x.get("cols", None))

    assert "type" in x, "`type` field is required in CellSelection"

    if x["type"] == "none":
        return x

    if x["type"] == "row":
        if not selection_modes._has_row():
            raise ValueError(
                "Current selection modes do not support row based selection. "
                f"Current selection modes: {selection_modes}"
            )
        assert row_value is not None
        return {"type": "row", "rows": row_value}
    if x["type"] == "col":
        assert col_value is not None
        return {"type": "col", "cols": col_value}
    # if x["type"] == "cell":
    #     if not selection_modes._has_rect():
    #         raise ValueError(
    #             "Current selection modes do not support cell based selection. "
    #             f"Current selection modes: {selection_modes}"
    #         )
    #     assert row_value is not None
    #     assert col_value is not None
    #     assert len(row_value) == 1
    #     assert len(col_value) == 1
    #     return {"type": "cell", "rows": row_value, "cols": col_value}
    if x["type"] == "rect":
        if not selection_modes._has_rect():
            raise ValueError(
                "Current selection modes do not support cell based selection. "
                f"Current selection modes: {selection_modes}"
            )
        assert row_value is not None
        assert col_value is not None
        assert len(row_value) == 2
        assert len(col_value) == 2
        assert row_value[0] <= row_value[1]
        assert col_value[0] <= col_value[1]
        return {"type": "rect", "rows": row_value, "cols": col_value}

    raise ValueError(f"Unhandled CellSelection['type']: {x['type']}")


RowSelectionModeDeprecated = Literal["single", "multiple", "none", "deprecated"]


def as_selection_modes(
    selection_mode: SelectionModeInput,
    *,
    name: str,
    editable: bool,
    row_selection_mode: RowSelectionModeDeprecated = "deprecated",
) -> SelectionModes:
    # TODO-barret; Test that as _selection_modes can take and return a SelectionModes object
    if isinstance(selection_mode, SelectionModes):
        return selection_mode

    selection_mode_val = selection_mode

    # If a user supplied `row_selection_mode`, use the value but warn against it
    if row_selection_mode != "deprecated":

        if row_selection_mode == "none":
            selection_mode_val = "none"
        elif row_selection_mode == "single":
            selection_mode_val = "row"
        elif row_selection_mode == "multiple":
            selection_mode_val = "rows"
        else:
            raise ValueError(f"Unknown row_selection_mode: {row_selection_mode}")

        warn_deprecated(
            f"`{name}(row_selection_mode=)` has been superseded by `{name}(selection_mode=)`."
            f' Please use `{name}(selection_mode="{selection_mode_val}")` instead.'
        )
    if not isinstance(selection_mode_val, tuple):
        selection_mode_val = (selection_mode_val,)

    selection_mode_set = cast(Set[SelectionMode], set(selection_mode_val))

    # TODO-barret-render.data_frame; Fix user cell edit/select interaction model to make this work!
    # Disable selection_mode if `editable=True``
    if editable and not selection_mode_set.issubset(none_set):
        warnings.warn(
            '`editable` can not currently be `True` while `selection_mode` != `"none"`. '
            'Setting `selection_mode=("none",)`',
            stacklevel=3,
        )
        return SelectionModes(selection_mode_set={"none"})

    return SelectionModes(selection_mode_set=selection_mode_set)
