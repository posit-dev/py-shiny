"""Tests for shiny/ui/_progress.py module."""

from shiny.ui._progress import Progress


class TestProgress:
    """Tests for Progress class."""

    def test_progress_is_class(self):
        """Test Progress is a class."""
        assert isinstance(Progress, type)


class TestProgressExported:
    """Tests for Progress export."""

    def test_progress_in_ui(self):
        """Test Progress is in ui module."""
        from shiny import ui

        assert hasattr(ui, "Progress")
