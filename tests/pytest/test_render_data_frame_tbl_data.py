from datetime import datetime

import pandas as pd
import polars as pl
import pytest

from shiny.render._data_frame_utils._tbl_data import serialize_dtype, serialize_frame
from shiny.ui import HTML, h1

DATA = {
    "num": [1, 2, 3],
    "chr": ["a", "b", "c"],
    "cat": ["a", "a", "c"],
    "dt": [datetime.now()] * 3,
    "struct": [{"x": 1}, {"x": 2}, {"x": 3}],
}

params_frames = [
    pytest.param(pd.DataFrame, id="pandas"),
    pytest.param(pl.DataFrame, id="polars"),
]


@pytest.fixture(params=params_frames, scope="function")
def df(request) -> pd.DataFrame:
    return request.param(DATA)


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
        (pd.Series([datetime.now()], dtype="datetime64[ns]"), "unknown"),
        (pd.Series(["a"], dtype="category"), "categorical"),
        (pd.Series([{"x": 1}]), "unknown"),
        (pd.Series([h1("yo")]), "html"),
        (pd.Series([HTML("yo")]), "html"),
    ],
)
def test_serialize_dtype(ser, res_type):
    assert serialize_dtype(ser)["type"] == res_type
