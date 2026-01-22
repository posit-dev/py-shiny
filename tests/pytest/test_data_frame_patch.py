"""Tests for shiny/render/_data_frame_utils/_patch.py module."""

from shiny.render._data_frame_utils._patch import (
    CellPatch,
    CellValue,
)


class TestCellPatch:
    """Tests for CellPatch class."""

    def test_cell_patch_is_class(self):
        """Test CellPatch is a class."""
        assert isinstance(CellPatch, type)


class TestCellValue:
    """Tests for CellValue type."""

    def test_cell_value_exists(self):
        """Test CellValue exists."""
        assert CellValue is not None
