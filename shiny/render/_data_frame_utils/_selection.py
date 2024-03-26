from __future__ import annotations

# TODO-barret; Docs
# TODO-barret; Add examples!
import warnings
from typing import (
    Literal,
    NotRequired,
    Sequence,
    TypedDict,
    TypeGuard,
    Union,
)

from ..._deprecated import warn_deprecated

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

LocationRange = tuple[int, int]


# class SelectionLocation_(TypedDict):
#     rows: LocationRange | Literal["all"]
#     cols: LocationRange | Literal["all"]

row_idx = 0
col_idx = 9
min_row = 0
max_row = 3
min_col = 0
max_col = 3


# Select single cell
x = {"rows": row_idx, "cols": col_idx}
x = {"rows": [row_idx], "cols": [col_idx]}
# select single region
x = {"rows": [min_row, max_row], "cols": [max_col, min_col]}
# No multi-region selection!

# select single row; all columns
x = {"rows": row_idx}
x = {"rows": row_idx, "cols": None}
x = {"rows": [row_idx]}
x = {"rows": [row_idx], "cols": None}
# select multiple rows; all columns
x = {"rows": [row_idx, row_idx + 3, row_idx + 5]}
x = {"rows": [row_idx, row_idx + 3, row_idx + 5], "cols": None}

# (same for cols)
# select single col; all rows
x = {"cols": col_idx}
x = {"cols": col_idx, "rows": None}
x = {"cols": [col_idx]}
x = {"cols": [col_idx], "rows": None}
# select multiple cols; all rows
x = {"cols": [col_idx, col_idx + 3, col_idx + 5]}
x = {"cols": [col_idx, col_idx + 3, col_idx + 5], "rows": None}


class CellSelectionCell(TypedDict):
    rows: int
    cols: int


class CellSelectionRegion(TypedDict):
    rows: int | Sequence[int]
    cols: int | Sequence[int]


class CellSelectionRow(TypedDict):
    rows: int | Sequence[int]
    cols: NotRequired[None]


class CellSelectionCol(TypedDict):
    rows: NotRequired[None]
    cols: int | tuple[int, ...]


class CellSelectionNone(TypedDict):
    rows: None
    cols: None


# class CellSelectionCore(TypedDict):
#     rows: Sequence[int] | None
#     cols: Sequence[int] | None
# CellSelectionBase = Union[
#     # SelectionLocationDict,
#     CellSelectionCore,
#     Literal["all", "none"],
# ]


# class CellSelectionAll(TypedDict):
#     rows: True
#     cols: True


# For users to type in python
CellSelectionDict = Union[
    CellSelectionCell,
    CellSelectionRegion,
    CellSelectionRow,
    CellSelectionCol,
    CellSelectionNone,
    # CellSelectionAll,
]

# @@@@@@@@@@@@@@


# class SelectionLocationRegion(TypedDict):
#     rows: LocationRange
#     cols: LocationRange


# class SelectionLocationRow(TypedDict):
#     rows: tuple[int, ...]
#     cols: Literal["all"]


# class SelectionLocationCol(TypedDict):
#     rows: Literal["all"]
#     cols: LocationRange


# class SelectionLocationAll(TypedDict):
#     rows: Literal["all"]
#     cols: Literal["all"]


# SelectionLocationDict = Union[
#     SelectionLocationRegion,
#     SelectionLocationRow,
#     SelectionLocationCol,
#     SelectionLocationAll,
# ]

# More user friendly Selection type:
CellSelection = Union[
    # SelectionLocationDict,
    CellSelectionDict,
    Literal["all", "none"],
]


class BrowserCellSelectionAll(TypedDict):
    type: Literal["all"]


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


# For receiving selection info from JS:
BrowserCellSelection = Union[
    BrowserCellSelectionRegion,
    BrowserCellSelectionRow,
    BrowserCellSelectionCol,
    BrowserCellSelectionAll,
    BrowserCellSelectionNone,
]


def assert_rows(x: BrowserCellSelection):
    assert "rows" in x
    assert isinstance(x["rows"], tuple) and len(x["rows"]) == 2
    assert isinstance(x["rows"][0], int)
    assert isinstance(x["rows"][1], int)


def assert_cols(x: BrowserCellSelection):
    assert "cols" in x
    assert isinstance(x["cols"], tuple) and len(x["cols"]) == 2
    assert isinstance(x["cols"][0], int)
    assert isinstance(x["cols"][1], int)


def is_location_range(r: LocationRange) -> TypeGuard[LocationRange]:
    return (
        isinstance(r, tuple)
        and len(r) == 2
        and isinstance(r[0], int)
        and isinstance(r[1], int)
    )


def is_sequence_2(r: Sequence[int]) -> TypeGuard[LocationRange]:
    return (
        isinstance(r, tuple)
        and len(r) == 2
        and isinstance(r[0], int)
        and isinstance(r[1], int)
    )


# def as_cell_selection(
#     x: SelectionLocationJS | CellSelectionDict,
# ) -> SelectionLocationJS:
#     if x == "all":
#         return "all"
#     if x == "none":
#         return "none"

#     assert isinstance(x, dict)

#     # Seems like a SelectionLocationJS, verify shape...
#     if "type" in x:
#         if x["type"] == "all":
#             return x

#         if x["type"] == "row":
#             assert_rows(x)
#             return x
#         if x["type"] == "col":
#             assert_cols(x)
#             return x
#         if x["type"] == "region":
#             assert_rows(x)
#             assert_cols(x)
#             return x
#         raise ValueError(f"Unknown SelectionLocationJS[\"type\"]: {x['type']}")

#     # Seems like a SelectionLocation, verify and convert...
#     if "rows" not in x:
#         raise ValueError("SelectionLocation must have 'rows' key")
#     if "cols" not in x:
#         raise ValueError("SelectionLocation must have 'cols' key")

#     # All
#     if x["rows"] == "all" and x["cols"] == "all":
#         return {"type": "all"}

#     # Cols
#     if x["rows"] == "all":
#         assert x["cols"] != "all"
#         if is_location_range(x["cols"]):
#             return {"type": "col", "cols": x["cols"]}
#         else:
#             raise ValueError("SelectionLocation['cols'] must be a tuple[int, int]")

#     # Rows
#     if x["cols"] == "all":
#         assert x["rows"] != "all"
#         if is_location_range(x["rows"]):
#             return {"type": "row", "rows": x["rows"]}
#         else:
#             raise ValueError("SelectionLocation['rows'] must be a tuple[int, int]")


#     # Region
#     if is_location_range(x["rows"]) and is_location_range(x["cols"]):
#         return {"type": "region", "rows": x["rows"], "cols": x["cols"]}
#     else:
#         raise ValueError(
#             "SelectionLocation['rows'] and ['cols'] must be a tuple[int, int]"
#         )


def to_list_or_none(x: int | Sequence[int] | None) -> Sequence[int] | None:
    if x is None:
        return None
    if isinstance(x, int):
        return [x]

    assert isinstance(x, Sequence)
    if len(x) == 0:
        return None
    for i in x:
        assert isinstance(i, int)
    return x


def as_cell_selection(
    x: BrowserCellSelection,
) -> CellSelection:
    assert isinstance(x, dict)
    assert "type" in x
    if x["type"] == "all":
        return "all"
    if x["type"] == "none":
        return "none"

    if x["type"] == "col":
        assert "cols" in x
        assert isinstance(x["cols"], Sequence)
        # Check for no cols selected
        if len(x["cols"]) == 0:
            return "none"

        for col in x["cols"]:
            assert isinstance(col, int)
        return {"cols": x["cols"]}

    if x["type"] == "row":
        assert "rows" in x
        assert isinstance(x["rows"], Sequence)
        # Check for no rows selected
        if len(x["rows"]) == 0:
            return "none"
        for row in x["rows"]:
            assert isinstance(row, int)
        return {"rows": x["rows"]}

    if x["type"] == "region":
        assert "rows" in x and "cols" in x
        assert isinstance(x["rows"], Sequence) and len(x["rows"]) == 2
        assert isinstance(x["cols"], Sequence) and len(x["cols"]) == 2
        assert isinstance(x["rows"][0], int) and isinstance(x["rows"][1], int)
        assert isinstance(x["cols"][0], int) and isinstance(x["cols"][1], int)
        return {
            "rows": x["rows"],
            "cols": x["cols"],
        }

    raise ValueError(f"Unhandled BrowserCellSelection['type']: {x['type']}")


def as_browser_cell_selection(
    x: CellSelection | BrowserCellSelection,
) -> BrowserCellSelection:

    if x == "all":
        return {"type": "all"}
    if x == "none":
        return {"type": "none"}

    # Can't handle lists of dictionaries right now
    assert isinstance(x, dict)

    if "type" in x:
        # Looks like a BrowserCellSelection, verify and return
        if x["type"] == "all":
            return x
        if x["type"] == "none":
            return x
        if x["type"] == "row":
            assert "rows" in x
            assert isinstance(x["rows"], Sequence)
            return x
        if x["type"] == "col":
            assert "cols" in x
            assert isinstance(x["cols"], Sequence)
            return x
        if x["type"] == "region":
            assert "rows" in x
            assert "cols" in x
            assert isinstance(x["rows"], Sequence)
            assert isinstance(x["cols"], Sequence)
            return x
        raise ValueError(f"Unhandled BrowserCellSelection['type']: {x['type']}")

    # Not a BrowserCellSelection, convert as if a CellSelection!
    row_value = to_list_or_none(x.get("rows", None))
    col_value = to_list_or_none(x.get("cols", None))

    if row_value is None:
        if col_value is None:
            # None!
            return {"type": "none"}
        else:
            # Col!
            assert isinstance(col_value, Sequence)
            if len(col_value) == 0:
                # Nothing selected
                return {"type": "none"}
            return {"type": "col", "cols": tuple(col_value)}
    else:
        # row_value is not None
        if col_value is None:
            # Row!
            assert isinstance(row_value, Sequence)
            if len(row_value) == 0:
                # Nothing selected
                return {"type": "none"}

            return {"type": "row", "rows": tuple(row_value)}
        else:
            # Region!
            assert isinstance(row_value, Sequence)
            assert isinstance(col_value, Sequence)
            assert len(row_value) == 2
            assert len(col_value) == 2
            return {
                "type": "region",
                "rows": (row_value[0], row_value[1]),
                "cols": (col_value[0], col_value[1]),
            }


RowSelectionModeDeprecated = Literal["single", "multiple", "none", "deprecated"]


def as_selection_mode(
    selection_mode: SelectionMode,
    *,
    name: str,
    editable: bool,
    row_selection_mode: RowSelectionModeDeprecated = "deprecated",
) -> SelectionMode:
    if row_selection_mode == "deprecated":
        # Disable selection_mode if `editable=True``
        if editable:
            warnings.warn(
                '`editable` can not be `True` while `selection_mode` != `"none"`. '
                'Setting `selection_mode="none"`',
                stacklevel=2,
            )
            return "none"

        return selection_mode

    warn_deprecated(
        f"`{name}(row_selection_mode=)` has been superseded by `{name}(selection_mode=)`."
        f' Please use `{name}(mode="{row_selection_mode}_row")` instead.'
    )

    if row_selection_mode == "none":
        return as_selection_mode("none", name=name, editable=editable)
    elif row_selection_mode == "single":
        return as_selection_mode("row", name=name, editable=editable)
    elif row_selection_mode == "multiple":
        return as_selection_mode("rows", name=name, editable=editable)
    else:
        raise ValueError("Unknown row_selection_mode: {row_selection_mode}")
