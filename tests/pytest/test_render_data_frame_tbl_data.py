from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Union

import narwhals.stable.v1 as nw
import pandas as pd
import polars as pl
import polars.testing as pl_testing
import pytest
from typing_extensions import TypeAlias

from shiny.render._data_frame_utils._tbl_data import (
    copy_frame,
    frame_shape,
    get_frame_cell,
    serialize_dtype,
    serialize_frame,
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
    pytest.param(
        lambda d: nw.from_native(pl.DataFrame(d), eager_only=True), id="narwhals"
    ),
]

DataFrameLike: TypeAlias = Union[pd.DataFrame, pl.DataFrame]
# SeriesLike: TypeAlias = Union[
#     pd.Series[Any],
#     pl.Series,
# ]


@pytest.fixture(params=params_frames, scope="function")
def df(request: pytest.FixtureRequest) -> DataFrameLike:
    return request.param(DATA)


@pytest.fixture(params=params_frames, scope="function")
def small_df(request: pytest.FixtureRequest) -> DataFrameLike:
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
    src: pd.DataFrame | pl.DataFrame,
    target_dict: dict,
    use_index: bool = False,
):
    src = nw.to_native(src, strict=False)
    target = nw.to_native(src, strict=False).__class__(target_dict)

    assert_frame_equal(src, target, use_index)


# TODO: explicitly pass dtype= when doing Series construction
@pytest.mark.parametrize(
    "ser, res_type",
    [  # pyright: ignore[reportUnknownArgumentType] # We are explicitly setting some values to `unkown`
        # polars ----
        (pl.Series([1]), "numeric"),
        (pl.Series([1.1]), "numeric"),
        (pl.Series(["a"]), "string"),
        (pl.Series([datetime.now()]), "unknown"),
        (pl.Series(["a"], dtype=pl.Categorical), "categorical"),
        (pl.Series([{"x": 1}]), "unknown"),
        (pl.Series([h1("yo")]), "html"),
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
def test_serialize_dtype(
    ser: Union[
        "pd.Series[Any]",
        pl.Series,
    ],
    res_type: str,
):
    if isinstance(ser, pl.Series):
        assert (
            serialize_dtype(nw.from_native(ser, eager_only=True, allow_series=True))[
                "type"
            ]
            == res_type
        )
    assert serialize_dtype(ser)["type"] == res_type


def test_serialize_frame(df: DataFrameLike):
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


def test_subset_frame(df: DataFrameLike):
    # TODO: this assumes subset_frame doesn't reset index
    res = subset_frame(df, rows=[1], cols=["chr", "num"])
    dst = {"chr": ["b"], "num": [2]}

    assert_frame_equal2(res, dst)


def test_get_frame_cell(df: DataFrameLike):
    assert get_frame_cell(df, 1, 1) == "b"


def test_copy_frame(df: DataFrameLike):
    new_df = copy_frame(df)

    assert new_df is not df


def test_subset_frame_rows_single(small_df: DataFrameLike):
    res = subset_frame(small_df, rows=[1])

    assert_frame_equal2(
        res,
        {"x": [2], "y": [4]},
    )


def test_subset_frame_cols_single(small_df: DataFrameLike):
    # TODO: include test of polars
    res = subset_frame(small_df, cols=["y"])

    assert_frame_equal2(
        res,
        {"y": [3, 4]},
    )


def test_shape(small_df: DataFrameLike):
    assert frame_shape(small_df) == (2, 2)
