"""Tests for shiny/ui/fill/__init__.py - Fill module exports."""

from shiny.ui import fill


class TestFillExports:
    """Tests for fill module exports."""

    def test_as_fillable_container_exported(self):
        """Test as_fillable_container is exported."""
        assert hasattr(fill, "as_fillable_container")
        assert callable(fill.as_fillable_container)

    def test_as_fill_item_exported(self):
        """Test as_fill_item is exported."""
        assert hasattr(fill, "as_fill_item")
        assert callable(fill.as_fill_item)

    def test_remove_all_fill_exported(self):
        """Test remove_all_fill is exported."""
        assert hasattr(fill, "remove_all_fill")
        assert callable(fill.remove_all_fill)


class TestFillAll:
    """Tests for __all__ exports."""

    def test_all_is_tuple(self):
        """Test __all__ is a tuple."""
        assert isinstance(fill.__all__, tuple)

    def test_all_contains_as_fillable_container(self):
        """Test __all__ contains as_fillable_container."""
        assert "as_fillable_container" in fill.__all__

    def test_all_contains_as_fill_item(self):
        """Test __all__ contains as_fill_item."""
        assert "as_fill_item" in fill.__all__

    def test_all_contains_remove_all_fill(self):
        """Test __all__ contains remove_all_fill."""
        assert "remove_all_fill" in fill.__all__
