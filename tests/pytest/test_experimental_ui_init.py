"""Tests for shiny/experimental/ui/__init__.py module."""

import shiny.experimental.ui as exp_ui


class TestExperimentalUiExports:
    """Tests for experimental ui module exports."""

    def test_experimental_ui_has_card(self):
        """Test experimental ui has card_image."""
        assert hasattr(exp_ui, "card_image")

    def test_experimental_ui_card_image_callable(self):
        """Test experimental ui card_image is callable."""
        assert callable(exp_ui.card_image)


class TestExperimentalUiAll:
    """Tests for __all__ exports."""

    def test_all_is_tuple(self):
        """Test __all__ is a tuple."""
        assert isinstance(exp_ui.__all__, tuple)

    def test_all_contains_card_image(self):
        """Test __all__ contains card_image."""
        assert "card_image" in exp_ui.__all__
