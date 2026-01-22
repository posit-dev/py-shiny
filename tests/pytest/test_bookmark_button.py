"""Tests for shiny/bookmark/_button.py module."""

from shiny.bookmark._button import input_bookmark_button


class TestInputBookmarkButton:
    """Tests for input_bookmark_button function."""

    def test_input_bookmark_button_is_callable(self):
        """Test input_bookmark_button is callable."""
        assert callable(input_bookmark_button)


class TestInputBookmarkButtonInAll:
    """Tests for input_bookmark_button in module __all__."""

    def test_input_bookmark_button_exported(self):
        """Test input_bookmark_button is exported from bookmark module."""
        from shiny import bookmark

        assert hasattr(bookmark, "input_bookmark_button")
