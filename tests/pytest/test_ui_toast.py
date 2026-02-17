"""Tests for shiny/ui/_toast.py module."""

from shiny.ui._toast import (
    show_toast,
)


class TestShowToast:
    """Tests for show_toast function."""

    def test_show_toast_is_callable(self):
        """Test show_toast is callable."""
        assert callable(show_toast)


class TestToastExported:
    """Tests for toast functions export."""

    def test_show_toast_in_ui(self):
        """Test show_toast is in ui module."""
        from shiny import ui

        assert hasattr(ui, "show_toast")
