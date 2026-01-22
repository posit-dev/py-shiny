"""Tests for shiny/ui/_progress.py module."""

from shiny.ui._progress import (
    Progress,
)


class TestProgressClass:
    """Tests for Progress class."""

    def test_progress_class_exists(self):
        """Test Progress class exists."""
        assert Progress is not None

    def test_progress_is_type(self):
        """Test Progress is a class."""
        assert isinstance(Progress, type)


class TestProgressExported:
    """Tests for progress functions export."""

    def test_progress_in_ui(self):
        """Test Progress is in ui module."""
        from shiny import ui

        assert hasattr(ui, "Progress")
