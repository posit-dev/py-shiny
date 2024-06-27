from dataclasses import dataclass
from datetime import datetime

import pandas as pd
import polars as pl
import polars.testing
import pytest
from typing_extensions import TypeAlias

from shiny.render._data_frame_utils._tbl_data import (
    copy_frame,
    get_frame_cell,
    serialize_dtype,
    serialize_frame,
    shape,
    subset_frame,
)
from shiny.ui import HTML, h1


class C:
    x: int

    def __init__(self, x: int):
        self.x = x

    def __str__(self):
        return f"<{self.__class__.__name__} object>"


@dataclass
class D:
    y: int


DATA = {
    "num": [1, 2],
    "chr": ["a", "b"],
    "cat": ["a", "a"],
    "dt": [datetime(2000, 1, 2)] * 2,
    # TODO: mock session in tests (needed for registering dependencies)
    # "html": [htmltools.span("span content")] * 2,
    # "html_str": [htmltools.HTML("<strong>bolded</strong>")] * 2,
    # TODO: ts code to stringify objects
    "struct": [{"x": 1}, {"x": 2}],
    "arr": [[1, 2], [3, 4]],
    "object": [C(1), D(2)],
}

params_frames = [
    pytest.param(pd.DataFrame, id="pandas"),
    pytest.param(pl.DataFrame, id="polars"),
]

DataFrameLike: TypeAlias = "pd.DataFrame | pl.DataFrame"


@pytest.fixture(params=params_frames, scope="function")
def df(request) -> DataFrameLike:
    return request.param(DATA)


@pytest.fixture(params=params_frames, scope="function")
def small_df(request) -> DataFrameLike:
    return request.param({"x": [1, 2], "y": [3, 4]})


def assert_frame_equal(src, target, use_index=False):
    if isinstance(src, pd.DataFrame):
        if use_index:
            pd.testing.assert_frame_equal(src, target)
        else:
            pd.testing.assert_frame_equal(
                src.reset_index(drop=True),
                target.reset_index(drop=True),
            )
    elif isinstance(src, pl.DataFrame):
        pl.testing.assert_frame_equal(src, target)
    else:
        raise NotImplementedError(f"Unsupported data type: {type(src)}")


# TODO: explicitly pass dtype= when doing Series construction
@pytest.mark.parametrize(
    "ser, res_type",
    [
        # polars ----
        (pl.Series([1]), "numeric"),
        (pl.Series([1.1]), "numeric"),
        (pl.Series(["a"]), "string"),
        (pl.Series([datetime.now()]), "unknown"),
        (pl.Series(["a"], dtype=pl.Categorical), "categorical"),
        (pl.Series([{"x": 1}]), "unknown"),
        pytest.param(pl.Series([h1("yo")]), "html", marks=pytest.mark.xfail),
        pytest.param(pl.Series([HTML("yo")]), "html", marks=pytest.mark.xfail),
        # pandas ----
        (pd.Series([1]), "numeric"),
        (pd.Series([1.1]), "numeric"),
        (pd.Series(["a"], dtype="object"), "string"),
        (pd.Series(["a"], dtype="string"), "string"),
        (pd.Series([datetime.now()], dtype="datetime64[ns]"), "datetime"),
        (pd.Series([pd.Timedelta(days=1)]), "timedelta"),
        (pd.Series(["a"], dtype="category"), "categorical"),
        (pd.Series([{"x": 1}]), "unknown"),
        (pd.Series([h1("yo")]), "html"),
        (pd.Series([HTML("yo")]), "html"),
    ],
)
def test_serialize_dtype(ser, res_type):
    assert serialize_dtype(ser)["type"] == res_type


def test_serialize_frame(df):
    # TODO: pandas converts datetime entries to int, but Polars
    # preserves the datetime object.
    if isinstance(df, pl.DataFrame):
        pytest.xfail()

    res = serialize_frame(df)
    assert res == {
        "columns": ["num", "chr", "cat", "dt", "struct", "arr", "object"],
        "index": [0, 1],
        "data": [
            [1, "a", "a", "2000-01-02T00:00:00.000", {"x": 1}, [1, 2], "<C object>"],
            [2, "b", "a", "2000-01-02T00:00:00.000", {"x": 2}, [3, 4], "D(y=2)"],
        ],
        "typeHints": [
            {"type": "numeric"},
            {"type": "string"},
            {"type": "string"},
            {"type": "datetime"},
            {"type": "unknown"},
            {"type": "unknown"},
            {"type": "unknown"},
        ],
    }


def test_subset_frame(df):
    # TODO: this assumes subset_frame doesn't reset index
    res = subset_frame(df, [1], ["chr", "num"])
    dst = df.__class__({"chr": ["b"], "num": [2]})

    assert_frame_equal(res, dst)


def test_get_frame_cell(df):
    assert get_frame_cell(df, 1, 1) == "b"


def test_copy_frame(df):
    new_df = copy_frame(df)

    assert new_df is not df


def test_subset_frame_rows_single(small_df):
    res = subset_frame(small_df, [1])

    assert_frame_equal(res, small_df.__class__({"x": [2], "y": [4]}))


def test_subset_frame_cols_single(small_df):
    # TODO: include test of polars
    res = subset_frame(small_df, cols=["y"])

    assert_frame_equal(res, small_df.__class__({"y": [3, 4]}))


def test_shape(small_df):
    assert shape(small_df) == (2, 2)
