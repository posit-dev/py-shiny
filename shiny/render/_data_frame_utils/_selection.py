from __future__ import annotations

# TODO-barret; Docs
# TODO-barret; Add examples!
import warnings
from typing import Literal, Sequence, Union

from ..._deprecated import warn_deprecated
from ..._typing_extensions import NotRequired, TypedDict

# RowSelectionMode = Literal["none", "row", "rows"]
RowSelectionMode = Literal["row", "rows"]
# ColSelectionMode = Literal["col", "cols"]
# RegionSelectionMode = Literal["region"]
# CellSelectionMode = Literal["cell"]

SelectionMode = Union[
    RowSelectionMode,
    # ColumnSelectionMode,
    # RegionSelectionMode,
    # CellSelectionMode,
    Literal["none"],
]

# Types
SelectionModes = tuple[SelectionMode, ...]
"""
Tuple of possible modes for selecting cells in a DataGrid or DataTable.

- `"none"`: No cells can be selected.
- `"row"`: Only a single row can be selected.
- `"rows"`: Multiple rows can be selected.
"""
# - `"col"`: Only a single column can be selected.
# - `"cols"`: Multiple columns can be selected.
# - `"region"`: A single rectangular region can be selected.
# - `"cell"`: Only a single cell can be selected.


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
    rows: int | Sequence[int]
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


# Proposal, remove BrowserCellSelectionAll and BrowserCellSelectionNone as they can be represented by an empty Row/Col/Region
# Update: Maybe only remove `All` as `None` has a different meaning in that nothing should be selected. Whereas `All` means everything can could be represented as a row, column, or region with appropriate values.


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


class BrowserCellSelectionCell(TypedDict):
    type: Literal["cell"]
    rows: tuple[int]
    cols: tuple[int]


# For receiving selection info from JS:
BrowserCellSelection = Union[
    BrowserCellSelectionRow,
    BrowserCellSelectionCol,
    BrowserCellSelectionCell,
    BrowserCellSelectionRegion,
    BrowserCellSelectionNone,
    # BrowserCellSelectionAll,
]
"""
A single selection set sent to/from the browser.

- `"none"`: No cells are selected
- `"row"`: A set of selected rows
"""
# - `"all"`: All cells are selected
# - `"col"`: A set of selected columns
# - `"region"`: A single rectangular region that is selected
# - `"cell"`: A single cell that is selected

# ####################


def to_tuple_or_none(x: int | Sequence[int] | None) -> tuple[int, ...] | None:
    if x is None:
        return None
    if isinstance(x, int):
        return (x,)

    assert isinstance(x, Sequence)
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
    selectionModes: SelectionModes,
) -> BrowserCellSelection:

    if x == "none" or x is None or "none" in selectionModes:
        return {"type": "none"}

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
            if not ("row" in selectionModes or "rows" in selectionModes):
                raise ValueError(
                    "Current selection modes do not support row based selection. "
                    f"Current selection modes: {', '.join(selectionModes)}"
                )
            assert row_value is not None
            return {"type": "row", "rows": row_value}
        if x["type"] == "col":
            raise ValueError(
                "Column based cell selections are not currently supported."
            )
            if not ("col" in selectionModes or "cols" in selectionModes):
                raise ValueError(
                    "Current selection modes do not support col based selection. "
                    f"Current selection modes: {', '.join(selectionModes)}"
                )
            assert col_value is not None
            return {"type": "col", "cols": col_value}
        if x["type"] == "cell":
            raise ValueError("Cell based cell selections are not currently supported.")
            if "cell" not in selectionModes:
                raise ValueError(
                    "Current selection modes do not support cell based selection. "
                    f"Current selection modes: {', '.join(selectionModes)}"
                )
            assert row_value is not None
            assert col_value is not None
            assert len(x["rows"]) == 1
            assert len(x["cols"]) == 1
            return {"type": "cell", "rows": row_value, "cols": col_value}
        if x["type"] == "region":
            raise ValueError(
                "Region based cell selections are not currently supported."
            )
            if "region" not in selectionModes:
                raise ValueError(
                    "Current selection modes do not support cell based selection. "
                    f"Current selection modes: {', '.join(selectionModes)}"
                )
            assert row_value is not None
            assert col_value is not None
            assert len(x["rows"]) == 2
            assert len(x["cols"]) == 2
            assert x["rows"][0] <= x["rows"][1]
            assert x["cols"][0] <= x["cols"][1]
            return {"type": "region", "rows": row_value, "cols": col_value}
        raise ValueError(f"Unhandled BrowserCellSelection['type']: {x['type']}")

    # Not a BrowserCellSelection, convert as if a CellSelection!
    if row_value is None:
        if col_value is None:
            # None!
            return as_browser_cell_selection("none", selectionModes)
        else:
            # Col!
            return as_browser_cell_selection(
                {"type": "col", "cols": col_value}, selectionModes
            )
    else:
        # row_value is not None
        if col_value is None:
            # Row!
            return as_browser_cell_selection(
                {"type": "row", "rows": row_value},
                selectionModes,
            )
        else:
            # row_value is not None
            # col_value is not None

            if len(row_value) == 1 and len(col_value) == 1:
                # Cell!
                return as_browser_cell_selection(
                    {"type": "cell", "rows": row_value, "cols": col_value},
                    selectionModes,
                )
            else:
                # Region!
                assert len(row_value) == 2
                assert len(col_value) == 2
                return as_browser_cell_selection(
                    {"type": "region", "rows": row_value, "cols": col_value},
                    selectionModes,
                )


RowSelectionModeDeprecated = Literal["single", "multiple", "none", "deprecated"]


def as_selection_modes(
    selection_modes: SelectionMode | Sequence[SelectionMode],
    *,
    name: str,
    editable: bool,
    row_selection_mode: RowSelectionModeDeprecated = "deprecated",
) -> SelectionModes:
    # If a user supplied `row_selection_mode`, use the value but warn against it
    if row_selection_mode != "deprecated":

        warn_deprecated(
            f"`{name}(row_selection_mode=)` has been superseded by `{name}(selection_modes=)`."
            f' Please use `{name}(mode="{row_selection_mode}_row")` instead.'
        )

        if row_selection_mode == "none":
            selection_modes = ("none",)
        elif row_selection_mode == "single":
            selection_modes = ("row",)
        elif row_selection_mode == "multiple":
            selection_modes = ("rows",)
        else:
            raise ValueError("Unknown row_selection_mode: {row_selection_mode}")

    # Upgrade to tuple
    if isinstance(selection_modes, str):
        selection_modes_tuple = (selection_modes,)
    else:
        assert isinstance(selection_modes, Sequence)
        selection_modes_tuple = tuple(selection_modes)

    # Disable selection_mode if `editable=True``
    if editable and "none" not in selection_modes_tuple:
        warnings.warn(
            '`editable` can not currently be `True` while `selection_mode` != `"none"`. '
            'Setting `selection_mode=("none",)`',
            stacklevel=3,
        )
        selection_modes_tuple = ("none",)

    # Trim values
    if "none" in selection_modes_tuple:
        return ("none",)
    if "row" in selection_modes_tuple and "rows" in selection_modes_tuple:
        selection_modes_tuple = tuple(
            mode for mode in selection_modes_tuple if mode != "row"
        )
    # if "col" in selection_modes_tuple and "cols" in selection_modes_tuple:
    #     selection_modes_tuple = tuple(
    #         mode for mode in selection_modes_tuple if mode != "col"
    #     )

    return selection_modes_tuple
