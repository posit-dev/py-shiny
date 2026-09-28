"""Tests for `shiny.plotutils.near_points()`."""

from __future__ import annotations

import pandas as pd
import pytest

from shiny.plotutils import near_points
from shiny.types import CoordInfo


@pytest.fixture
def coordinfo() -> CoordInfo:
    """A click at the origin of a plot whose data and image coordinates match."""
    return {
        "x": 0.0,
        "y": 0.0,
        "coords_css": {"x": 0.0, "y": 0.0},
        "coords_img": {"x": 0.0, "y": 0.0},
        "img_css_ratio": {"x": 1.0, "y": 1.0},
        "mapping": {"x": "x", "y": "y"},
        "domain": {"left": 0.0, "right": 10.0, "bottom": 0.0, "top": 10.0},
        "range": {"left": 0.0, "right": 10.0, "bottom": 0.0, "top": 10.0},
        "log": {"x": None, "y": None},
    }


@pytest.fixture
def df() -> pd.DataFrame:
    return pd.DataFrame({"x": [0.0, 3.0, 10.0], "y": [0.0, 4.0, 10.0]})


class TestNearPointsAddDist:
    def test_adds_the_documented_dist_column(
        self, df: pd.DataFrame, coordinfo: CoordInfo
    ):
        # Act
        res = near_points(df, coordinfo, add_dist=True, all_rows=True)

        # Assert: the column is the `dist_` the documentation promises, in the
        # same trailing-underscore style as `selected_`.
        assert "dist_" in res.columns
        assert "dist" not in res.columns
        assert res["dist_"].tolist() == pytest.approx([0.0, 5.0, 14.1421356])

    def test_adds_dist_column_without_a_pointer_event(self, df: pd.DataFrame):
        # Act
        res = near_points(df, None, add_dist=True, all_rows=True)

        # Assert
        assert "dist_" in res.columns
        assert "dist" not in res.columns
        assert res["dist_"].isna().all()

    def test_no_dist_column_when_add_dist_is_false(
        self, df: pd.DataFrame, coordinfo: CoordInfo
    ):
        # Act
        res = near_points(df, coordinfo, all_rows=True)

        # Assert
        assert "dist_" not in res.columns
        assert "dist" not in res.columns
