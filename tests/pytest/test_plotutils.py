"""Tests for shiny/plotutils.py"""

from __future__ import annotations

import pytest

# These tests require pandas, so skip if not available
pd = pytest.importorskip("pandas")

from shiny.plotutils import brushed_points, near_points
from shiny.types import BrushInfo, CoordInfo


class TestBrushedPoints:
    """Tests for the brushed_points function."""

    def test_basic_brush_selection(self) -> None:
        """Test basic brush point selection."""
        df = pd.DataFrame(
            {
                "x": [1.0, 2.0, 3.0, 4.0, 5.0],
                "y": [1.0, 2.0, 3.0, 4.0, 5.0],
            }
        )

        brush: BrushInfo = {
            "xmin": 1.5,
            "xmax": 3.5,
            "ymin": 1.5,
            "ymax": 3.5,
            "direction": "xy",
            "mapping": {"x": "x", "y": "y"},
            "coords_css": {"xmin": 0, "xmax": 100, "ymin": 0, "ymax": 100},
            "coords_img": {"xmin": 0, "xmax": 100, "ymin": 0, "ymax": 100},
            "img_css_ratio": {"x": 1.0, "y": 1.0},
            "log": {"x": None, "y": None},
            "range": {"left": 0, "right": 100, "bottom": 0, "top": 100},
            "domain": {"left": 0, "right": 10, "bottom": 0, "top": 10},
        }

        result = brushed_points(df, brush, xvar="x", yvar="y")

        # Should select points where 1.5 <= x <= 3.5 and 1.5 <= y <= 3.5
        assert len(result) == 2  # Points (2,2) and (3,3)

    def test_brush_none_returns_empty(self) -> None:
        """Test that None brush returns empty dataframe."""
        df = pd.DataFrame(
            {
                "x": [1.0, 2.0, 3.0],
                "y": [1.0, 2.0, 3.0],
            }
        )

        result = brushed_points(df, None, xvar="x", yvar="y")
        assert len(result) == 0

    def test_brush_none_with_all_rows(self) -> None:
        """Test that None brush with all_rows adds selected_ column."""
        df = pd.DataFrame(
            {
                "x": [1.0, 2.0, 3.0],
                "y": [1.0, 2.0, 3.0],
            }
        )

        result = brushed_points(df, None, xvar="x", yvar="y", all_rows=True)
        assert len(result) == 3
        assert "selected_" in result.columns
        assert result["selected_"].sum() == 0  # None selected

    def test_brush_with_all_rows(self) -> None:
        """Test brush with all_rows=True returns all rows with selection column."""
        df = pd.DataFrame(
            {
                "x": [1.0, 2.0, 3.0, 4.0, 5.0],
                "y": [1.0, 2.0, 3.0, 4.0, 5.0],
            }
        )

        brush: BrushInfo = {
            "xmin": 1.5,
            "xmax": 3.5,
            "ymin": 1.5,
            "ymax": 3.5,
            "direction": "xy",
            "mapping": {"x": "x", "y": "y"},
            "coords_css": {"xmin": 0, "xmax": 100, "ymin": 0, "ymax": 100},
            "coords_img": {"xmin": 0, "xmax": 100, "ymin": 0, "ymax": 100},
            "img_css_ratio": {"x": 1.0, "y": 1.0},
            "log": {"x": None, "y": None},
            "range": {"left": 0, "right": 100, "bottom": 0, "top": 100},
            "domain": {"left": 0, "right": 10, "bottom": 0, "top": 10},
        }

        result = brushed_points(df, brush, xvar="x", yvar="y", all_rows=True)

        assert len(result) == 5
        assert "selected_" in result.columns
        assert result["selected_"].sum() == 2  # 2 points selected

    def test_brush_x_direction_only(self) -> None:
        """Test brush in x direction only."""
        df = pd.DataFrame(
            {
                "x": [1.0, 2.0, 3.0, 4.0, 5.0],
                "y": [1.0, 2.0, 3.0, 4.0, 5.0],
            }
        )

        brush: BrushInfo = {
            "xmin": 2.5,
            "xmax": 4.5,
            "ymin": 0,
            "ymax": 10,
            "direction": "x",  # x only
            "mapping": {"x": "x"},
            "coords_css": {"xmin": 0, "xmax": 100, "ymin": 0, "ymax": 100},
            "coords_img": {"xmin": 0, "xmax": 100, "ymin": 0, "ymax": 100},
            "img_css_ratio": {"x": 1.0, "y": 1.0},
            "log": {"x": None, "y": None},
            "range": {"left": 0, "right": 100, "bottom": 0, "top": 100},
            "domain": {"left": 0, "right": 10, "bottom": 0, "top": 10},
        }

        result = brushed_points(df, brush, xvar="x")

        # Should select points where 2.5 <= x <= 4.5
        assert len(result) == 2  # Points at x=3 and x=4

    def test_brush_missing_xvar_raises(self) -> None:
        """Test that missing xvar raises ValueError."""
        df = pd.DataFrame(
            {
                "x": [1.0, 2.0, 3.0],
                "y": [1.0, 2.0, 3.0],
            }
        )

        brush: BrushInfo = {
            "xmin": 1.5,
            "xmax": 2.5,
            "ymin": 1.5,
            "ymax": 2.5,
            "direction": "xy",
            "mapping": {},  # No mapping
            "coords_css": {"xmin": 0, "xmax": 100, "ymin": 0, "ymax": 100},
            "coords_img": {"xmin": 0, "xmax": 100, "ymin": 0, "ymax": 100},
            "img_css_ratio": {"x": 1.0, "y": 1.0},
            "log": {"x": None, "y": None},
            "range": {"left": 0, "right": 100, "bottom": 0, "top": 100},
            "domain": {"left": 0, "right": 10, "bottom": 0, "top": 10},
        }

        with pytest.raises(ValueError, match="not able to automatically infer `xvar`"):
            brushed_points(df, brush)

    def test_brush_xvar_not_in_dataframe_raises(self) -> None:
        """Test that xvar not in dataframe raises ValueError."""
        df = pd.DataFrame(
            {
                "a": [1.0, 2.0, 3.0],
                "b": [1.0, 2.0, 3.0],
            }
        )

        brush: BrushInfo = {
            "xmin": 1.5,
            "xmax": 2.5,
            "ymin": 1.5,
            "ymax": 2.5,
            "direction": "xy",
            "mapping": {"x": "x", "y": "y"},
            "coords_css": {"xmin": 0, "xmax": 100, "ymin": 0, "ymax": 100},
            "coords_img": {"xmin": 0, "xmax": 100, "ymin": 0, "ymax": 100},
            "img_css_ratio": {"x": 1.0, "y": 1.0},
            "log": {"x": None, "y": None},
            "range": {"left": 0, "right": 100, "bottom": 0, "top": 100},
            "domain": {"left": 0, "right": 10, "bottom": 0, "top": 10},
        }

        with pytest.raises(ValueError, match="not in dataframe"):
            brushed_points(df, brush, xvar="x", yvar="y")


class TestNearPoints:
    """Tests for the near_points function."""

    def test_basic_near_points(self) -> None:
        """Test basic near points selection."""
        df = pd.DataFrame(
            {
                "x": [1.0, 2.0, 3.0, 4.0, 5.0],
                "y": [1.0, 2.0, 3.0, 4.0, 5.0],
            }
        )

        coordinfo: CoordInfo = {
            "x": 2.0,
            "y": 2.0,
            "coords_css": {"x": 50, "y": 50},
            "coords_img": {"x": 50, "y": 50},
            "img_css_ratio": {"x": 1.0, "y": 1.0},
            "mapping": {"x": "x", "y": "y"},
            "log": {"x": None, "y": None},
            "range": {"left": 0, "right": 100, "bottom": 0, "top": 100},
            "domain": {"left": 0, "right": 10, "bottom": 0, "top": 10},
        }

        result = near_points(df, coordinfo, xvar="x", yvar="y", threshold=50)

        # Should find the nearest point(s) within threshold
        assert len(result) >= 1

    def test_near_points_none_returns_empty(self) -> None:
        """Test that None coordinfo returns empty dataframe."""
        df = pd.DataFrame(
            {
                "x": [1.0, 2.0, 3.0],
                "y": [1.0, 2.0, 3.0],
            }
        )

        result = near_points(df, None, xvar="x", yvar="y")
        assert len(result) == 0

    def test_near_points_with_all_rows(self) -> None:
        """Test near_points with all_rows=True."""
        df = pd.DataFrame(
            {
                "x": [1.0, 2.0, 3.0],
                "y": [1.0, 2.0, 3.0],
            }
        )

        result = near_points(df, None, xvar="x", yvar="y", all_rows=True)
        assert len(result) == 3
        assert "selected_" in result.columns

    def test_near_points_with_add_dist(self) -> None:
        """Test near_points with add_dist=True."""
        df = pd.DataFrame(
            {
                "x": [1.0, 2.0, 3.0],
                "y": [1.0, 2.0, 3.0],
            }
        )

        coordinfo: CoordInfo = {
            "x": 2.0,
            "y": 2.0,
            "coords_css": {"x": 50, "y": 50},
            "coords_img": {"x": 50, "y": 50},
            "img_css_ratio": {"x": 1.0, "y": 1.0},
            "mapping": {"x": "x", "y": "y"},
            "log": {"x": None, "y": None},
            "range": {"left": 0, "right": 100, "bottom": 0, "top": 100},
            "domain": {"left": 0, "right": 10, "bottom": 0, "top": 10},
        }

        result = near_points(
            df, coordinfo, xvar="x", yvar="y", threshold=100, add_dist=True
        )

        if len(result) > 0:
            assert "dist" in result.columns

    def test_near_points_with_max_points(self) -> None:
        """Test near_points with max_points limit."""
        df = pd.DataFrame(
            {
                "x": [1.0, 1.1, 1.2, 2.0, 3.0],
                "y": [1.0, 1.1, 1.2, 2.0, 3.0],
            }
        )

        coordinfo: CoordInfo = {
            "x": 1.0,
            "y": 1.0,
            "coords_css": {"x": 10, "y": 90},  # Near (1,1)
            "coords_img": {"x": 10, "y": 90},
            "img_css_ratio": {"x": 1.0, "y": 1.0},
            "mapping": {"x": "x", "y": "y"},
            "log": {"x": None, "y": None},
            "range": {"left": 0, "right": 100, "bottom": 0, "top": 100},
            "domain": {"left": 0, "right": 5, "bottom": 0, "top": 5},
        }

        result = near_points(
            df, coordinfo, xvar="x", yvar="y", threshold=100, max_points=2
        )

        # Should return at most 2 points
        assert len(result) <= 2


class TestPlotutilsExports:
    """Test that the module exports are correct."""

    def test_exports_available(self) -> None:
        """Test that exported functions are available."""
        from shiny.plotutils import brushed_points, near_points

        assert callable(brushed_points)
        assert callable(near_points)
