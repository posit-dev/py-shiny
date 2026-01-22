"""Tests for shiny/render/_data_frame_utils/_types.py module."""

from shiny.render._data_frame_utils._types import (
    ColumnSort,
    CellPatch,
)


class TestColumnSort:
    """Tests for ColumnSort class."""

    def test_column_sort_exists(self):
        """Test ColumnSort exists."""
        assert ColumnSort is not None


class TestCellPatch:
    """Tests for CellPatch class."""

    def test_cell_patch_exists(self):
        """Test CellPatch exists."""
        assert CellPatch is not None
