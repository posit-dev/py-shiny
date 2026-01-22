"""Tests for shiny/ui/_card.py module."""

from shiny.ui._card import card, card_footer, card_header


class TestCard:
    """Tests for card function."""

    def test_card_is_callable(self):
        """Test card is callable."""
        assert callable(card)

    def test_card_returns_tag(self):
        """Test card returns a Tag."""
        from htmltools import Tag

        result = card("Card content")
        assert isinstance(result, Tag)

    def test_card_with_header_footer(self):
        """Test card with header and footer."""
        from htmltools import Tag

        result = card(
            card_header("Header"),
            "Main content",
            card_footer("Footer"),
        )
        assert isinstance(result, Tag)


class TestCardHeader:
    """Tests for card_header function."""

    def test_card_header_is_callable(self):
        """Test card_header is callable."""
        assert callable(card_header)

    def test_card_header_returns_card_item(self):
        """Test card_header returns a CardItem object."""
        from shiny.ui._card import CardItem

        result = card_header("Header text")
        assert isinstance(result, CardItem)


class TestCardFooter:
    """Tests for card_footer function."""

    def test_card_footer_is_callable(self):
        """Test card_footer is callable."""
        assert callable(card_footer)

    def test_card_footer_returns_card_item(self):
        """Test card_footer returns a CardItem object."""
        from shiny.ui._card import CardItem

        result = card_footer("Footer text")
        assert isinstance(result, CardItem)


class TestCardExported:
    """Tests for card functions export."""

    def test_card_in_ui(self):
        """Test card is in ui module."""
        from shiny import ui

        assert hasattr(ui, "card")

    def test_card_header_in_ui(self):
        """Test card_header is in ui module."""
        from shiny import ui

        assert hasattr(ui, "card_header")

    def test_card_footer_in_ui(self):
        """Test card_footer is in ui module."""
        from shiny import ui

        assert hasattr(ui, "card_footer")
