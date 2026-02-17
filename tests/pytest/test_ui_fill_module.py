"""Tests for shiny/ui/fill/_fill.py module."""

from shiny.ui.fill._fill import (
    as_fill_item,
    as_fillable_container,
    remove_all_fill,
)


class TestAsFillItem:
    """Tests for as_fill_item function."""

    def test_as_fill_item_is_callable(self):
        """Test as_fill_item is callable."""
        assert callable(as_fill_item)


class TestAsFillableContainer:
    """Tests for as_fillable_container function."""

    def test_as_fillable_container_is_callable(self):
        """Test as_fillable_container is callable."""
        assert callable(as_fillable_container)


class TestRemoveAllFill:
    """Tests for remove_all_fill function."""

    def test_remove_all_fill_is_callable(self):
        """Test remove_all_fill is callable."""
        assert callable(remove_all_fill)
