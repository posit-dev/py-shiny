"""Tests for shiny/ui/_insert.py module."""

from shiny.ui._insert import insert_ui, remove_ui


class TestInsertUi:
    """Tests for insert_ui function."""

    def test_insert_ui_is_callable(self):
        """Test insert_ui is callable."""
        assert callable(insert_ui)


class TestRemoveUi:
    """Tests for remove_ui function."""

    def test_remove_ui_is_callable(self):
        """Test remove_ui is callable."""
        assert callable(remove_ui)


class TestInsertExported:
    """Tests for insert functions export."""

    def test_insert_ui_in_ui(self):
        """Test insert_ui is in ui module."""
        from shiny import ui

        assert hasattr(ui, "insert_ui")

    def test_remove_ui_in_ui(self):
        """Test remove_ui is in ui module."""
        from shiny import ui

        assert hasattr(ui, "remove_ui")
