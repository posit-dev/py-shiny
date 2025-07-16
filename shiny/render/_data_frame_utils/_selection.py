from __future__ import annotations

# TODO-barret-render.data_frame; Docs
# TODO-barret-render.data_frame; Add examples of selection!
import warnings
from typing import Any, Literal, Set, Union, cast

from ..._deprecated import warn_deprecated
from ..._typing_extensions import TypedDict
from ...types import ListOrTuple
from ._types import DataFrame, FrameRenderSelectionModes

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

    def as_dict(self) -> FrameRenderSelectionModes:
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
# # BrowserCellSelection: For receiving selection info from JS
# ####################

# Should only contain a single selection area

# Do not include `BrowserCellSelectionAll` as it should be represented by a row, column, or region with appropriate values.
# # class BrowserCellSelectionAll(TypedDict):
# #    type: Literal["all"]


class BrowserCellSelectionNone(TypedDict):
    type: Literal["none"]


class BrowserCellSelectionRow(TypedDict):
    type: Literal["row"]
    rows: ListOrTuple[int]


class BrowserCellSelectionCol(TypedDict):
    type: Literal["col"]
    cols: ListOrTuple[int]


class BrowserCellSelectionRect(TypedDict):
    type: Literal["rect"]
    # All rows and cols values! (Not min/max values!)
    # This is required as row selection is applied after sort/filter is applied. This
    # rearranges the rows into a non-sequential order, requiring all row numbers.
    rows: ListOrTuple[int]
    cols: ListOrTuple[int]


# For receiving selection info from JS:
BrowserCellSelection = Union[
    BrowserCellSelectionRow,
    BrowserCellSelectionCol,
    BrowserCellSelectionRect,
    BrowserCellSelectionNone,
]
"""
A single data frame selection set sent to/from the browser.

This object will be converted to `CellSelection` when being sent to (or received from)
the browser.

`type` values:

- `"none"`: No cells are selected. `rows` and `cols` will be missing.
- `"row"`: A set of selected `rows` numbers. `cols` will be missing.
- `"col"`: A set of selected `cols` numbers. `rows` will be missing.
- `"rect"`: A single rectangular region that is selected. `rows` and `cols` will be the
  row and column numbers for the selected region.
"""


class CellSelection(TypedDict):
    """
    A single data frame selection enhanced with missing keys.

    This object will always contain `rows` and `cols` keys to make it more user friendly.

    * If a cell selection is being sent to the browser, unnecessary keys will be dropped.
    * If a cell selection is being received from the browser, missing `rows` and `cols`
      keys will be added to contain all possible values. E.g. when `type="row"`, `cols`
      will be set to all column numbers for the data. These _extra_ values are not sent
      across as an input as they are not needed for the browser to render the selection.

    `type` values:

    - `"none"`: No cells are selected. `rows` and `cols` will be empty tuples.
    - `"row"`: A set of selected `rows` numbers. `cols` will be all column numbers for the data.
    - `"col"`: A set of selected `cols` numbers. `rows` will be all row numbers for the data.
    - `"rect"`: A single rectangular region that is selected. `rows` and `cols` will be
      the row and column numbers for the selected region.
    """

    type: Literal["none", "row", "col", "rect"]
    rows: ListOrTuple[int]
    cols: ListOrTuple[int]


# ####################


def as_browser_cell_selection(
    x: BrowserCellSelection | CellSelection | Literal["all"] | None,
    *,
    selection_modes: SelectionModes,
    nw_data: DataFrame[Any],
) -> BrowserCellSelection:

    if x is None or selection_modes._is_none():
        return {"type": "none"}

    if x == "all":
        row_len, col_len = nw_data.shape
        # Look at the selection modes to determine what to do
        if selection_modes._has_rect():
            if selection_modes.rect == "cell":
                warnings.warn(
                    "Cannot select all cells with `cell` selection mode. Selecting the first cell",
                    stacklevel=3,
                )
                return {"type": "rect", "rows": (0,), "cols": (0,)}
            if selection_modes.rect == "region":
                return {
                    "type": "rect",
                    "rows": tuple(range(row_len)),
                    "cols": tuple(range(col_len)),
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

    def to_int_tuple_or_none(
        arr: int | ListOrTuple[int] | None, *, name: str
    ) -> tuple[int, ...] | None:
        if arr is None:
            return None
        if not isinstance(arr, (list, tuple)):
            arr = (arr,)

        for item in arr:
            if not isinstance(item, int):
                raise TypeError(
                    f"Expected cell selection's `{name}` to be an int. Received {type(item)}"
                )
        return tuple(arr)

    rows = to_int_tuple_or_none(x.get("rows", None), name="rows")
    cols = to_int_tuple_or_none(x.get("cols", None), name="cols")

    assert "type" in x, "`type` field is required in CellSelection"

    if x["type"] == "none":
        return {"type": "none"}

    if x["type"] == "row":
        if not selection_modes._has_row():
            raise ValueError(
                "Current selection modes do not support row based selection. "
                f"Current selection modes: {selection_modes}"
            )
        assert rows is not None
        return {"type": "row", "rows": rows}
    if x["type"] == "col":
        assert cols is not None
        return {"type": "col", "cols": cols}
    if x["type"] == "rect":
        if not selection_modes._has_rect():
            raise ValueError(
                "Current selection modes do not support cell based selection. "
                f"Current selection modes: {selection_modes}"
            )
        assert rows is not None
        assert cols is not None
        assert len(rows) > 0
        assert len(cols) > 0
        return {"type": "rect", "rows": rows, "cols": cols}

    raise ValueError(f"Unhandled CellSelection['type']: {x['type']}")


def as_cell_selection(
    x: CellSelection | Literal["all"] | None | BrowserCellSelection,
    *,
    selection_modes: SelectionModes,
    nw_data: DataFrame[Any],
    data_view_rows: ListOrTuple[int],
    data_view_cols: ListOrTuple[int],
) -> CellSelection:
    """
    Converts the selection to `BrowserCellSelection` type and then adds missing
    `rows` and `cols` to represent all reasonable values for consistent user interactions.
    """
    browser_cell_selection = as_browser_cell_selection(
        x,
        selection_modes=selection_modes,
        nw_data=nw_data,
    )
    ret: CellSelection | None = None
    if browser_cell_selection["type"] == "none":
        ret = {
            "type": "none",
            "rows": (),
            "cols": (),
        }
    elif browser_cell_selection["type"] == "row":

        ret = {
            "type": "row",
            "rows": browser_cell_selection["rows"],
            "cols": tuple(data_view_cols),
        }
    elif browser_cell_selection["type"] == "col":
        ret = {
            "type": "col",
            "rows": tuple(data_view_rows),
            "cols": browser_cell_selection["cols"],
        }
    elif browser_cell_selection["type"] == "rect":
        ret = {
            "type": "rect",
            "rows": browser_cell_selection["rows"],
            "cols": browser_cell_selection["cols"],
        }
    else:
        raise ValueError(
            f"Unhandled BrowserCellSelection['type']: {browser_cell_selection['type']}"
        )

    # Make sure the rows are within the data
    nrow, ncol = nw_data.shape
    ret["rows"] = tuple(row for row in ret["rows"] if row < nrow)
    ret["cols"] = tuple(col for col in ret["cols"] if col < ncol)

    return ret


RowSelectionModeDeprecated = Literal["single", "multiple", "none", "deprecated"]


def as_selection_modes(
    selection_mode: SelectionModeInput,
    *,
    name: str,
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

    return SelectionModes(selection_mode_set=selection_mode_set)
