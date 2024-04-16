from __future__ import annotations

# TODO-barret-render.data_frame; Docs
# TODO-barret-render.data_frame; Add examples of selection!
import warnings
from typing import TYPE_CHECKING, List, Literal, Set, Tuple, Union, cast

from ..._deprecated import warn_deprecated
from ..._typing_extensions import NotRequired, TypedDict
from ...types import MISSING, MISSING_TYPE, Jsonifiable

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
                "Region based cell selections are not currently supported."
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
    List[SelectionMode],
    Tuple[SelectionMode, ...],
    Set[SelectionMode],
    # Support the upgraded selection modes
    SelectionModes,
]
"""
Input types for selection modes in a DataGrid or DataTable.
"""


# row_idx = 0
# col_idx = 9
# min_row = 0
# max_row = 3
# min_col = 0
# max_col = 3

# # Select single cell
# x = {"rows": row_idx, "cols": col_idx}
# x = {"rows": [row_idx], "cols": [col_idx]}
# # select single region
# x = {"rows": [min_row, max_row], "cols": [max_col, min_col]}
# # No multi-region selection!

# # select single row; all columns
# x = {"rows": row_idx}
# x = {"rows": row_idx, "cols": None}
# x = {"rows": [row_idx]}
# x = {"rows": [row_idx], "cols": None}
# # select multiple rows; all columns
# x = {"rows": [row_idx, row_idx + 3, row_idx + 5]}
# x = {"rows": [row_idx, row_idx + 3, row_idx + 5], "cols": None}

# # (same for cols)
# # select single col; all rows
# x = {"cols": col_idx}
# x = {"cols": col_idx, "rows": None}
# x = {"cols": [col_idx]}
# x = {"cols": [col_idx], "rows": None}
# # select multiple cols; all rows
# x = {"cols": [col_idx, col_idx + 3, col_idx + 5]}
# x = {"cols": [col_idx, col_idx + 3, col_idx + 5], "rows": None}


####################
# Cell Selection: For users to type in python
####################


# Should only contain a single selection area
class CellSelectionCell(TypedDict):
    rows: int
    cols: int


class CellSelectionRegion(TypedDict):
    rows: int | tuple[int, int]
    cols: int | tuple[int, int]


class CellSelectionRow(TypedDict):
    rows: int | tuple[int, ...]
    cols: NotRequired[None]


class CellSelectionCol(TypedDict):
    rows: NotRequired[None]
    cols: int | tuple[int, ...]


# class CellSelectionNone(TypedDict):
#     rows: None
#     cols: None


# class CellSelectionAll(TypedDict):
#     rows: True
#     cols: True


# For users to type in python
CellSelectionDict = CellSelectionRow
Union[
    CellSelectionCell,
    CellSelectionRegion,
    CellSelectionRow,
    CellSelectionCol,
    # CellSelectionNone,
    # CellSelectionAll,
]

# More user friendly Selection type:
CellSelection = Union[
    CellSelectionDict,
    Literal["all", "none"],
]
"""
A single selection area to be defined in update cell selection method.
"""

# ####################
# # BrowserCellSelection: For receiving selection info from JS
# ####################

# Should only contain a single selection area

# # Do not include `BrowserCellSelectionAll` as it should be represented by a row, column, or region with appropriate values.
# class BrowserCellSelectionAll(TypedDict):
#     type: Literal["all"]


class BrowserCellSelectionNone(TypedDict):
    type: Literal["none"]


class BrowserCellSelectionRow(TypedDict):
    type: Literal["row"]
    rows: tuple[int, ...]


class BrowserCellSelectionCol(TypedDict):
    type: Literal["col"]
    cols: tuple[int, ...]


class BrowserCellSelectionRegion(TypedDict):
    type: Literal["region"]
    rows: tuple[int, int]
    cols: tuple[int, int]


# class BrowserCellSelectionCell(TypedDict):
#     type: Literal["cell"]
#     rows: tuple[int]
#     cols: tuple[int]


# For receiving selection info from JS:
BrowserCellSelection = Union[
    BrowserCellSelectionRow,
    BrowserCellSelectionCol,
    # BrowserCellSelectionCell,
    BrowserCellSelectionRegion,
    BrowserCellSelectionNone,
]
"""
A single selection set sent to/from the browser.

- `"none"`: No cells are selected
- `"row"`: A set of selected rows
- `"col"`: A set of selected columns
- `"region"`: A single rectangular region that is selected
- `"cell"`: A single cell that is selected
"""

# ####################


def to_tuple_or_none(
    x: int | list[int] | tuple[int, ...] | None
) -> tuple[int, ...] | None:
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


# def as_cell_selection(
#     x: BrowserCellSelection | None,
# ) -> CellSelection:
#     if x is None:
#         return "none"
#     assert isinstance(x, dict)
#     assert "type" in x
#     # if x["type"] == "all":
#     #     return "all"
#     if x["type"] == "none":
#         return "none"

#     if x["type"] == "col":
#         assert "cols" in x
#         assert isinstance(x["cols"], Sequence)
#         # Check for no cols selected
#         if len(x["cols"]) == 0:
#             return "none"

#         for col in x["cols"]:
#             assert isinstance(col, int)
#         return {"cols": x["cols"]}

#     if x["type"] == "row":
#         assert "rows" in x
#         assert isinstance(x["rows"], Sequence)
#         # Check for no rows selected
#         if len(x["rows"]) == 0:
#             return "none"
#         for row in x["rows"]:
#             assert isinstance(row, int)
#         return {"rows": x["rows"]}

#     if x["type"] == "region":
#         assert "rows" in x and "cols" in x
#         assert isinstance(x["rows"], Sequence) and len(x["rows"]) == 2
#         assert isinstance(x["cols"], Sequence) and len(x["cols"]) == 2
#         assert isinstance(x["rows"][0], int) and isinstance(x["rows"][1], int)
#         assert isinstance(x["cols"][0], int) and isinstance(x["cols"][1], int)
#         return {
#             "rows": x["rows"],
#             "cols": x["cols"],
#         }

#     raise ValueError(f"Unhandled BrowserCellSelection['type']: {x['type']}")


def as_browser_cell_selection(
    x: CellSelection | BrowserCellSelection | None,
    *,
    selection_modes: SelectionModes,
    data: pd.DataFrame | MISSING_TYPE = MISSING,
) -> BrowserCellSelection:

    if x == "none" or x is None or selection_modes._is_none():
        return {"type": "none"}

    if x == "all":
        if isinstance(data, MISSING_TYPE):
            raise ValueError(
                "Cannot use `all` selection mode without providing `data`."
            )
        row_len, col_len = data.shape
        # Look at the selection modes to determine what to do
        if selection_modes._has_rect():
            if selection_modes.rect == "region":
                return {
                    "type": "region",
                    "rows": (0, row_len - 1),
                    "cols": (0, col_len - 1),
                }
        if selection_modes._has_row():

            if selection_modes.row == "multiple":
                return {"type": "row", "rows": tuple(range(row_len))}
        if selection_modes._has_col():
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

    if "type" in x:
        # Looks like a BrowserCellSelection, verify and return
        # if x["type"] == "all":
        #     return x
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
        if x["type"] == "region":
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
            return {"type": "region", "rows": row_value, "cols": col_value}

        raise ValueError(f"Unhandled BrowserCellSelection['type']: {x['type']}")

    # Not a BrowserCellSelection, convert as if a CellSelection!
    if row_value is None:
        if col_value is None:
            # None!
            return as_browser_cell_selection("none", selection_modes=selection_modes)
        else:
            # Col!
            return as_browser_cell_selection(
                {"type": "col", "cols": col_value}, selection_modes=selection_modes
            )
    else:
        # row_value is not None
        if col_value is None:
            # Row!
            return as_browser_cell_selection(
                {"type": "row", "rows": row_value},
                selection_modes=selection_modes,
            )
        else:
            # row_value is not None
            # col_value is not None

            # if len(row_value) == 1 and len(col_value) == 1:
            #     # Cell!
            #     return as_browser_cell_selection(
            #         {"type": "cell", "rows": row_value, "cols": col_value},
            #         selection_modes=selection_modes,
            #     )
            # else:
            # Region!
            assert len(row_value) == 2
            assert len(col_value) == 2
            return as_browser_cell_selection(
                {"type": "region", "rows": row_value, "cols": col_value},
                selection_modes=selection_modes,
            )


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
