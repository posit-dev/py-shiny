from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Union

import narwhals.stable.v1 as nw
import pandas as pd
import polars as pl
import polars.testing as pl_testing
import pytest

from shiny.render._data_frame_utils._tbl_data import (
    as_data_frame,
    copy_frame,
    frame_shape,
    serialize_dtype,
    serialize_frame,
    subset_frame,
)
from shiny.render._data_frame_utils._types import IntoDataFrame, SeriesLike
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


def polars_dict_to_narwhals(d: dict[str, Any]) -> nw.DataFrame[pl.DataFrame]:
    return nw.from_native(pl.DataFrame(d), eager_only=True)


def series_to_narwhals(ser: SeriesLike) -> nw.Series:
    return nw.from_native(ser, series_only=True, strict=True)


params_frames = [
    pytest.param(pd.DataFrame, id="pandas"),
    pytest.param(pl.DataFrame, id="polars"),
    pytest.param(polars_dict_to_narwhals, id="narwhals"),
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


# TODO: explicitly pass dtype= when doing Series construction
@pytest.mark.parametrize(
    "ser, res_type",
    [  # pyright: ignore[reportUnknownArgumentType] # We are explicitly setting some values to `unkown`
        # polars ----
        (pl.Series([1]), "numeric"),
        (pl.Series([1.1]), "numeric"),
        (pl.Series(["a"]), "string"),
        (pl.Series([datetime.now()]), "datetime"),
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
        # (pd.Series([pd.Timedelta(days=1)]), "timedelta"),
        (pd.Series(["a"], dtype="category"), "categorical"),
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
    res_type: str,
):
    nw_ser = series_to_narwhals(ser)
    assert serialize_dtype(nw_ser)["type"] == res_type


def test_serialize_frame(df_f: IntoDataFrame):
    # if not isinstance(df_f, pl.DataFrame):
    #     pytest.skip()

    df_nw = as_data_frame(df_f)

    # # TODO: pandas converts datetime entries to int, but Polars
    # # preserves the datetime object.
    # if isinstance(df_f, pl.DataFrame):
    #     pytest.xfail()

    res = serialize_frame(df_nw)
    assert res == {
        "columns": ["num", "chr", "cat", "dt", "struct", "arr", "object"],
        # "index": [0, 1],
        "data": [
            [1, "a", "a", "2000-01-02T00:00:00", {"x": 1}, [1, 2], "<C object>"],
            [2, "b", "a", "2000-01-02T00:00:00", {"x": 2}, [3, 4], {"y": 2}],
        ],
        "typeHints": [
            {"type": "numeric"},
            {"type": "string"},
            {"type": "string"},
            {"type": "datetime"},
            {"type": "object" if (isinstance(df_f, pd.DataFrame)) else "unknown"},
            {"type": "object" if (isinstance(df_f, pd.DataFrame)) else "unknown"},
            {"type": "object"},
        ],
    }


def test_subset_frame(df_f: IntoDataFrame):
    # TODO: this assumes subset_frame doesn't reset index
    res = subset_frame(as_data_frame(df_f), rows=[1], cols=["chr", "num"])
    dst = {"chr": ["b"], "num": [2]}

    assert_frame_equal2(res, dst)


# def test_get_frame_cell(df_f: IntoDataFrameT):
#     assert get_frame_cell(df_f, 1, 1) == "b"


def test_copy_frame(df_f: IntoDataFrame):
    new_df = copy_frame(as_data_frame(df_f))

    assert new_df is not df_f


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


def test_shape(small_df_f: IntoDataFrame):
    assert frame_shape(small_df_f) == (2, 2)
