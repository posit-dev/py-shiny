"""Tests for shiny/ui/__init__.py module exports."""

import shiny.ui as ui


class TestUiExports:
    """Tests for ui module exports."""

    def test_ui_has_input_text(self):
        """Test ui has input_text."""
        assert hasattr(ui, "input_text")

    def test_ui_has_output_text(self):
        """Test ui has output_text."""
        assert hasattr(ui, "output_text")

    def test_ui_has_page_fluid(self):
        """Test ui has page_fluid."""
        assert hasattr(ui, "page_fluid")

    def test_ui_has_layout_sidebar(self):
        """Test ui has layout_sidebar."""
        assert hasattr(ui, "layout_sidebar")

    def test_ui_has_card(self):
        """Test ui has card."""
        assert hasattr(ui, "card")


class TestUiAll:
    """Tests for __all__ exports."""

    def test_all_is_tuple(self):
        """Test __all__ is a tuple."""
        assert isinstance(ui.__all__, tuple)

    def test_all_contains_input_text(self):
        """Test __all__ contains input_text."""
        assert "input_text" in ui.__all__

    def test_all_contains_output_text(self):
        """Test __all__ contains output_text."""
        assert "output_text" in ui.__all__

    def test_all_contains_page_fluid(self):
        """Test __all__ contains page_fluid."""
        assert "page_fluid" in ui.__all__

    def test_all_contains_card(self):
        """Test __all__ contains card."""
        assert "card" in ui.__all__
