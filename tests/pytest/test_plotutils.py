"""Tests for `shiny.plotutils`."""

from __future__ import annotations

import pandas as pd

from shiny.plotutils import brushed_points, to_float
from shiny.types import BrushInfo


def _brushinfo(xmin: float, xmax: float, ymin: float, ymax: float) -> BrushInfo:
    return {
        "xmin": xmin,
        "xmax": xmax,
        "ymin": ymin,
        "ymax": ymax,
        "coords_css": {"x": xmin, "y": ymin},
        "coords_img": {"x": xmin, "y": ymin},
        "img_css_ratio": {"x": 1.0, "y": 1.0},
        "mapping": {"x": "xval", "y": "yval"},
        "domain": {"left": 0.0, "right": 100.0, "bottom": 0.0, "top": 100.0},
        "range": {"left": 0.0, "right": 100.0, "bottom": 0.0, "top": 100.0},
        "log": {"x": None, "y": None},
        "direction": "xy",
    }  # type: ignore[return-value]


def test_to_float_handles_non_string_categorical():
    vals = pd.Series(pd.Categorical([10, 20, 10]))

    assert to_float(vals).tolist() == [1, 2, 1]


def test_to_float_handles_a_bare_categorical():
    # `pd.Categorical` is one of the types `DataFrameColumn` accepts, and it
    # reaches the categorical branch without being wrapped in a Series. The
    # ignore is for the stub's bare `Categorical`, which no concrete
    # `Categorical[T]` is assignable to.
    vals = pd.Categorical([10, 20, 10])

    assert to_float(vals).tolist() == [1, 2, 1]  # type: ignore[bad-argument-type]


def test_brushed_points_with_non_string_categorical_column():
    df = pd.DataFrame(
        {
            "xval": pd.Categorical([10, 20, 30]),
            "yval": [1.0, 2.0, 3.0],
            "label": ["a", "b", "c"],
        }
    )

    # Categorical codes are 1-based here, so category `20` sits at x == 2.
    res = brushed_points(df, _brushinfo(1.5, 2.5, 0.0, 100.0))

    assert res["label"].tolist() == ["b"]


def test_to_float_string_categorical_is_unchanged():
    vals = pd.Series(pd.Categorical(["b", "a", "b"], categories=["b", "a"]))

    assert to_float(vals).tolist() == [1, 2, 1]
