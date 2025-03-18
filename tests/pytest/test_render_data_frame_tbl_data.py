# TODO: Barret: ts code to stringify objects?

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Union, cast

import htmltools
import narwhals.stable.v1 as nw
import pandas as pd
import polars as pl
import polars.testing as pl_testing
import pytest

from shiny._namespaces import Root
from shiny.module import ResolvedId
from shiny.render._data_frame_utils._tbl_data import (
    as_data_frame,
    serialize_dtype,
    serialize_frame,
    subset_frame,
)
from shiny.render._data_frame_utils._types import IntoDataFrame
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


def test_subset_frame(df_f: IntoDataFrame):
    # TODO: this assumes subset_frame doesn't reset index
    res = subset_frame(as_data_frame(df_f), rows=[1], cols=["chr", "num"])
    dst = {"chr": ["b"], "num": [2]}

    assert_frame_equal2(res, dst)


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
