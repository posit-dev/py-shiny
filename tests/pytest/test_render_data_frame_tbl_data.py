# TODO: Barret: ts code to stringify objects?

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Union, cast

import htmltools
import narwhals.stable.v1 as nw
import numpy as np
import pandas as pd
import polars as pl
import polars.testing as pl_testing
import pytest

from shiny._namespaces import Root
from shiny.module import ResolvedId
from shiny.render._data_frame_utils._html import maybe_as_cell_html
from shiny.render._data_frame_utils._tbl_data import (
    apply_frame_patches,
    as_col_indexes,
    as_data_frame,
    serialize_dtype,
    serialize_frame,
    subset_frame,
)
from shiny.render._data_frame_utils._types import CellPatch, IntoDataFrame
from shiny.session import Session, session_context
from shiny.session._session import RenderedDeps
from shiny.ui import HTML, TagChild, TagList, h1, span


class _MockSession:
    ns: ResolvedId = Root

    # Simplified version of `AppSession._process_ui()`
    def _process_ui(self, ui: TagChild) -> RenderedDeps:
        res = TagList(ui).render()
        deps: list[dict[str, Any]] = []
        for dep in res["dependencies"]:
            # self.app._register_web_dependency(dep)
            dep_dict = dep.as_dict()
            deps.append(dep_dict)

        return {"deps": deps, "html": res["html"]}


test_session = cast(Session, _MockSession())


class C:
    x: int

    def __init__(self, x: int):
        self.x = x

    def __str__(self):
        return f"<{self.__class__.__name__} object>"


@dataclass
class D:
    y: int


html_dep = htmltools.HTMLDependency("test-dep", version="1", head="head-content")
ex_html_dep_dict = html_dep.as_dict()


DATA = {
    "num": [1, 2],
    "chr": ["a", "b"],
    "cat": ["a", "a"],
    "bool": [True, False],
    "dt": [datetime(2000, 1, 2)] * 2,
    "duration": [timedelta(weeks=1), timedelta(days=7)],
    "html": [span("span content", html_dep)] * 2,
    "html_str": [HTML("<strong>bolded</strong>")] * 2,
    "struct": [{"x": 1}, {"x": 2}],
    "arr": [[1, 2], [3, 4]],
    "object": [C(1), D(2)],
}

# Polars.Series is not always a TagNode (as it has a `__repr_html__` method)
# So we need to check if it is a TagNode to determine if it is an `"html"` or `"unknown"` type
polars_series_col_type = (
    "html" if htmltools.is_tag_node(pl.Series([[1, 2], [3, 4]])) else "unknown"
)


def pandas_dict_to_narwhals(d: dict[str, Any]) -> nw.DataFrame[pd.DataFrame]:
    return nw.from_native(pd.DataFrame(d), eager_only=True)


def polars_dict_to_narwhals(d: dict[str, Any]) -> nw.DataFrame[pl.DataFrame]:
    return nw.from_native(pl.DataFrame(d), eager_only=True)


def series_to_narwhals(ser: pd.Series[Any] | pl.Series) -> nw.Series:
    return nw.from_native(ser, series_only=True, strict=True)


params_frames = [
    pytest.param(pd.DataFrame, id="pandas"),
    pytest.param(pl.DataFrame, id="polars"),
    pytest.param(pandas_dict_to_narwhals, id="narwhals-pandas"),
    pytest.param(polars_dict_to_narwhals, id="narwhals-polars"),
]


@pytest.fixture(params=params_frames, scope="function")
def df_f(request: pytest.FixtureRequest) -> IntoDataFrame:
    return request.param(DATA)


@pytest.fixture(params=params_frames, scope="function")
def small_df_f(request: pytest.FixtureRequest) -> IntoDataFrame:
    return request.param({"x": [1, 2], "y": [3, 4]})


def assert_frame_equal(
    src: pd.DataFrame | pl.DataFrame,
    target: pd.DataFrame | pl.DataFrame,
    use_index: bool = False,
):
    if isinstance(src, pd.DataFrame):
        assert isinstance(target, pd.DataFrame)
        if use_index:
            pd.testing.assert_frame_equal(src, target)
        else:
            pd.testing.assert_frame_equal(
                src.reset_index(drop=True),
                target.reset_index(drop=True),
            )
    elif isinstance(src, pl.DataFrame):
        assert isinstance(target, pl.DataFrame)
        pl_testing.assert_frame_equal(src, target)
    else:
        raise NotImplementedError(f"Unsupported data type: {type(src)}")


def assert_frame_equal2(
    src: IntoDataFrame,
    target_dict: dict[str, Any],
    use_index: bool = False,
):
    src_native = nw.to_native(src, strict=False)
    target_native = nw.to_native(src, strict=False).__class__(target_dict)

    assert_frame_equal(src_native, target_native, use_index)


@pytest.mark.parametrize(
    "ser, res_type",
    [  # pyright: ignore[reportUnknownArgumentType] # We are explicitly setting some values to `unkown`
        # polars ----
        (pl.Series([1]), "numeric"),
        (pl.Series([1.1]), "numeric"),
        (pl.Series(["a"]), "string"),
        (pl.Series([True, False]), "boolean"),
        (pl.Series([datetime.now()]), "datetime"),
        (pl.Series([timedelta(weeks=1)]), "duration"),
        (
            pl.Series(["a", "b", "b", "c"], dtype=pl.Categorical),
            ("categorical", ["a", "b", "c"]),
        ),
        (
            pl.Series(
                ["Panda", "Polar", "Brown", "Brown", "Polar"],
                dtype=pl.Enum(["Polar", "Panda", "Brown"]),
            ),
            ("categorical", ["Polar", "Panda", "Brown"]),
        ),
        (pl.Series([{"x": 1}]), "object"),
        (pl.Series([h1("yo")]), "html"),
        (pl.Series([HTML("yo")]), "html"),
        # pandas ----
        (pd.Series([1]), "numeric"),
        (pd.Series([1.1]), "numeric"),
        (pd.Series(["a"]), "string"),
        (pd.Series([True, False]), "boolean"),
        (pd.Series([datetime.now()]), "datetime"),
        (pd.Series([timedelta(weeks=1)]), "duration"),
        (
            pd.Series(["a", "b", "b", "c"], dtype="category"),
            ("categorical", ["a", "b", "c"]),
        ),
        (
            pd.Series(
                pd.Categorical(
                    ["Panda", "Polar", "Brown", "Brown", "Polar"],
                    categories=["Polar", "Panda", "Brown"],
                )
            ),
            ("categorical", ["Polar", "Panda", "Brown"]),
        ),
        (
            pd.Series(
                pd.CategoricalIndex(
                    ["Panda", "Polar", "Brown", "Brown", "Polar"],
                )
            ),
            ("categorical", ["Brown", "Panda", "Polar"]),
        ),
        (
            pd.Series(
                pd.CategoricalIndex(
                    ["Panda", "Polar", "Brown", "Brown", "Polar"],
                    categories=["Polar", "Panda", "Brown"],
                )
            ),
            ("categorical", ["Polar", "Panda", "Brown"]),
        ),
        (pd.Series([{"x": 1}]), "object"),
        (pd.Series([h1("yo")]), "html"),
        (pd.Series([HTML("yo")]), "html"),
    ],
)
def test_serialize_dtype(
    ser: Union[
        "pd.Series[Any]",
        pl.Series,
    ],
    res_type: str | tuple[str, list[str]],
):
    nw_ser = series_to_narwhals(ser)
    dtype_info = serialize_dtype(nw_ser)
    ex_type = res_type if isinstance(res_type, str) else res_type[0]
    assert dtype_info["type"] == ex_type
    if dtype_info["type"] == "categorical":
        assert isinstance(res_type, tuple)
        assert dtype_info["categories"] == res_type[1]


def test_serialize_frame(df_f: IntoDataFrame):

    # if not isinstance(df_f, pl.DataFrame):
    #     pytest.skip()

    df_nw = as_data_frame(df_f)

    is_polars_backed = isinstance(
        nw.to_native(nw.from_native(df_f, eager_only=True)), pl.DataFrame
    )

    with session_context(test_session):
        res = serialize_frame(df_nw)
    assert res == {
        "columns": [
            "num",
            "chr",
            "cat",
            "bool",
            "dt",
            "duration",
            "html",
            "html_str",
            "struct",
            "arr",
            "object",
        ],
        "data": [
            [
                1,
                "a",
                "a",
                True,
                "2000-01-02T00:00:00" if is_polars_backed else "2000-01-02 00:00:00",
                "7 days, 0:00:00" if is_polars_backed else "7 days 00:00:00",
                {
                    "isShinyHtml": True,
                    "obj": {"deps": [], "html": "<span>span content</span>"},
                },
                {
                    "isShinyHtml": True,
                    "obj": {"deps": [], "html": "<strong>bolded</strong>"},
                },
                {"x": 1},
                [1, 2],
                "<C object>",
            ],
            [
                2,
                "b",
                "a",
                False,
                "2000-01-02T00:00:00" if is_polars_backed else "2000-01-02 00:00:00",
                "7 days, 0:00:00" if is_polars_backed else "7 days 00:00:00",
                {
                    "isShinyHtml": True,
                    "obj": {"deps": [], "html": "<span>span content</span>"},
                },
                {
                    "isShinyHtml": True,
                    "obj": {"deps": [], "html": "<strong>bolded</strong>"},
                },
                {"x": 2},
                [3, 4],
                {"y": 2},
            ],
        ],
        "typeHints": [
            {"type": "numeric"},
            {"type": "string"},
            {"type": "string"},
            {"type": "boolean"},
            {"type": "datetime"},
            {"type": "duration"},
            {"type": "html"},
            {"type": "html"},
            {"type": "object"},
            {"type": "object"},
            {"type": "object"},
        ],
        "htmlDeps": [ex_html_dep_dict],
    }


def test_serialize_frame_numeric_column_names():
    # Regression test: numeric column names (e.g. `0`, `1`) previously raised in
    # serialize_frame because `data[col_name]` was interpreted as positional/row
    # access on the narwhals frame instead of column access.
    df = pd.DataFrame([["a", 1], ["b", 2], ["c", 3]], columns=[0, 1])

    with session_context(test_session):
        res = serialize_frame(as_data_frame(df))

    assert res["columns"] == [0, 1]
    assert [hint["type"] for hint in res["typeHints"]] == ["string", "numeric"]
    assert res["data"] == [["a", 1], ["b", 2], ["c", 3]]


def test_apply_frame_patches_numeric_column_names():
    # Regression test: patching a cell of a frame with numeric column names previously
    # raised in apply_frame_patches because `nw_data[column_name]` was interpreted as
    # positional/row access, returning a frame (which has no `.scatter()` method).
    df = as_data_frame(
        pd.DataFrame([["a", "x"], ["b", "y"], ["c", "z"]], columns=[0, 1])
    )

    # Patch two different columns so the patches are grouped by column name
    patches: list[CellPatch] = [
        {"row_index": 0, "column_index": 0, "value": "A"},
        {"row_index": 2, "column_index": 1, "value": "Z"},
    ]

    res = apply_frame_patches(df, patches)

    assert res.columns == [0, 1]
    assert res.rows(named=False) == [("A", "x"), ("b", "y"), ("c", "Z")]
    # The original frame is cloned, not patched in place
    assert df.rows(named=False) == [("a", "x"), ("b", "y"), ("c", "z")]


@pytest.mark.parametrize("constructor", [pd.DataFrame, pl.DataFrame])
def test_apply_frame_patches_empty_column_name(constructor: Any):
    # Patches are keyed by column index all the way through, so a column whose name is
    # `""` is patched like any other. https://github.com/posit-dev/py-shiny/issues/1844
    df = as_data_frame(constructor({"": ["a", "b"], "num": [1, 2]}))

    patches: list[CellPatch] = [
        {"row_index": 1, "column_index": 0, "value": "B"},
        {"row_index": 0, "column_index": 1, "value": 10},
    ]

    res = apply_frame_patches(df, patches)

    assert res.columns == ["", "num"]
    assert res.rows(named=False) == [("a", 10), ("B", 2)]


def test_apply_frame_patches_non_string_values():
    # `CellValue` allows non-string scalars so that `@<data_frame>.set_patch_fn` can
    # coerce the browser's string to the column's type. Writing a `str` into these
    # columns raises `pandas.errors.LossySetitemError`, so the scalar types must work.
    df = as_data_frame(
        pd.DataFrame({"num": [1, 2], "dbl": [1.5, 2.5], "bool": [True, False]})
    )

    patches: list[CellPatch] = [
        {"row_index": 0, "column_index": 0, "value": 30},
        {"row_index": 1, "column_index": 1, "value": 3.5},
        {"row_index": 0, "column_index": 2, "value": False},
    ]

    res = apply_frame_patches(df, patches)

    assert res.rows(named=False) == [(30, 1.5, False), (2, 3.5, False)]


def test_maybe_as_cell_html_passes_scalars_through():
    # `CellPatchProcessed["value"]` is `JsonifiableScalar | CellHtml`, so every
    # `CellValue` must land in one of those two shapes: scalars unchanged (`str`
    # included), HTML-like content upgraded to a `CellHtml` dict.
    for scalar in ("a", 1, 1.5, True, None):
        assert maybe_as_cell_html(scalar, session=test_session) is scalar

    res = maybe_as_cell_html(HTML("<b>bold</b>"), session=test_session)

    assert res["isShinyHtml"] is True
    assert res["obj"]["html"] == "<b>bold</b>"


@pytest.mark.parametrize("empty_col_index", [0, 1, 2])
def test_serialize_frame_empty_column_name(empty_col_index: int):
    # Empty column names must be sent to the client as-is (`""`) in first,
    # middle, and last position. The client is responsible for giving such a
    # column a usable TanStack Table id.
    # https://github.com/posit-dev/py-shiny/issues/1844
    names = ["a", "b", "c"]
    names[empty_col_index] = ""
    df = pd.DataFrame({names[0]: [1, 2], names[1]: [3, 4], names[2]: [5, 6]})

    with session_context(test_session):
        res = serialize_frame(as_data_frame(df))

    assert res["columns"] == names
    assert res["data"] == [[1, 3, 5], [2, 4, 6]]


def test_subset_frame(df_f: IntoDataFrame):
    # TODO: this assumes subset_frame doesn't reset index
    res = subset_frame(as_data_frame(df_f), rows=[1], cols=["chr", "num"])
    dst = {"chr": ["b"], "num": [2]}

    assert_frame_equal2(res, dst)


def test_subset_frame_numeric_column_names():
    # `cols` entries are positions when `int`, so they must not be handed to narwhals as
    # column names: with non-string column names narwhals reads the name as a position,
    # selecting the wrong column or raising `IndexError` when it is out of bounds.
    df = as_data_frame(pd.DataFrame([["a", 1], ["b", 2]], columns=[10, 20]))

    res = subset_frame(df, cols=[0])

    assert res.columns == [10]
    assert res.rows(named=False) == [("a",), ("b",)]

    res = subset_frame(df, rows=[1], cols=[1])

    assert res.columns == [20]
    assert res.rows(named=False) == [(2,)]


def test_as_col_indexes_resolves_names_and_positions():
    df = as_data_frame(pd.DataFrame({"chr": ["a"], "": ["b"], "num": [1]}))

    # Names resolve to positions, including the empty name
    assert as_col_indexes(df, ["chr", "", "num"]) == [0, 1, 2]
    # Ints are already positions and pass straight through
    assert as_col_indexes(df, [2, 0]) == [2, 0]
    # Mixed input is fine
    assert as_col_indexes(df, ["num", 0]) == [2, 0]
    assert as_col_indexes(df, []) == []


def test_as_col_indexes_unknown_name_raises():
    df = as_data_frame(pd.DataFrame({"chr": ["a"], "num": [1]}))

    with pytest.raises(ValueError, match="Column name 'nope' not found"):
        as_col_indexes(df, ["nope"])


def test_as_col_indexes_int_is_always_a_position():
    # An `int` cannot be told apart from a pandas integer label, so it is documented and
    # tested as a position. The only input that tells the two readings apart is an int
    # that is also a label: on this frame `5` is the label of position 0, so reading it
    # as a label would give `[0]` while reading it as a position is out of range.
    df = as_data_frame(pd.DataFrame([["a", 1]], columns=[5, 3]))

    with pytest.raises(ValueError, match="Column position 5 is out of range"):
        as_col_indexes(df, [5])

    # Position 1 is the column labelled `3`, not the label `1` (which does not exist)
    assert as_col_indexes(df, [1]) == [1]
    assert subset_frame(df, cols=[1]).columns == [3]


def test_as_col_indexes_numpy_int_is_a_position():
    # `np.int64` is not an `int`, but it is what `np.where()` and friends hand back, so
    # it has to follow the same rule rather than falling through to the name lookup: on
    # this frame the label `5` would resolve to position 0 by equality.
    df = as_data_frame(pd.DataFrame([["a", 1]], columns=[5, 3]))

    assert as_col_indexes(df, [np.int64(1)]) == [1]
    with pytest.raises(ValueError, match="Column position 5 is out of range"):
        as_col_indexes(df, [np.int64(5)])


def test_as_col_indexes_out_of_range_position_raises():
    df = as_data_frame(pd.DataFrame({"chr": ["a"], "num": [1]}))

    # Negative positions are rejected rather than wrapping around to the last column
    with pytest.raises(ValueError, match="Column position -1 must be greater than"):
        as_col_indexes(df, [-1])

    # Out of range is rejected here rather than escaping as a narwhals `IndexError`
    with pytest.raises(ValueError, match="Column position 99 is out of range"):
        as_col_indexes(df, [99])


def test_as_col_indexes_bool_raises():
    # `bool` is a subclass of `int`, so `[True, False]` would otherwise read as
    # positions `[1, 0]`. `StyleInfo`'s `cols` accepts a bool mask; this does not.
    df = as_data_frame(pd.DataFrame({"chr": ["a"], "num": [1]}))

    with pytest.raises(TypeError, match="not a `bool`"):
        as_col_indexes(df, [True, False])


def test_subset_frame_rows_single(small_df_f: IntoDataFrame):
    res = subset_frame(as_data_frame(small_df_f), rows=[1])

    assert_frame_equal2(
        res,
        {"x": [2], "y": [4]},
    )


def test_subset_frame_cols_single(small_df_f: IntoDataFrame):
    # TODO: include test of polars
    res = subset_frame(as_data_frame(small_df_f), cols=["y"])

    assert_frame_equal2(
        res,
        {"y": [3, 4]},
    )


def test_dtype_coverage():
    from pathlib import Path

    from narwhals.stable.v1 import dtypes as nw_dtypes

    # Copy from https://github.com/narwhals-dev/narwhals/blob/2c9e2e7a308ebb30c6f672e27c1da2086ebbecbc/utils/check_api_reference.py#L144-L146
    dtype_names = [
        i
        for i in cast(str, nw_dtypes.__dir__())  # pyright: ignore
        if i[0].isupper() and not i.isupper() and i[0] != "_"
    ]

    with open(
        Path(__file__).parent.parent.parent  # Repo root
        / "shiny"
        / "render"
        / "_data_frame_utils"
        / "_tbl_data.py"
    ) as f:
        tbl_data_lines = f.readlines()

    tbl_data_lines = [line for line in tbl_data_lines if "nw." in line]

    errs: list[str] = []

    for dtype_name in dtype_names:

        # Skip known types or imports that are not dtypes
        if dtype_name.endswith("Type"):
            # "DType",
            # "NestedType",
            # "NumericType",
            # "TemporalType",
            continue
        if dtype_name in (
            # narwhals
            "Unknown",
            # typing import
            "Literal",
        ):
            continue

        dtype_cls = getattr(nw_dtypes, dtype_name)
        if not issubclass(dtype_cls, nw_dtypes.DType):
            continue

        if dtype_cls.is_numeric():
            continue

        if f"nw.{dtype_name}" in "".join(tbl_data_lines):
            continue

        errs.append(f"Missing: {dtype_name}")

    assert not errs, "Missing narwhals dtype implementations:\n" + "\n".join(errs)
