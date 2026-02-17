"""Tests for shiny/experimental/ui/_deprecated.py module."""

from shiny.experimental.ui._deprecated import card


class TestCardDeprecation:
    """Tests for card deprecation."""

    def test_card_is_callable(self):
        """Test card is callable."""
        assert callable(card)


class TestCardExported:
    """Tests for card export."""

    def test_card_in_experimental_ui(self):
        """Test card is in experimental.ui module."""
        from shiny.experimental import ui

        assert hasattr(ui, "card")
