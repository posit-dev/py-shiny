"""Tests for shiny.ui._card module."""

from htmltools import Tag, div

from shiny.ui._card import (
    CardItem,
    card,
    card_body,
    card_footer,
    card_header,
)


class TestCard:
    """Tests for card function."""

    def test_card_basic(self) -> None:
        """Test basic card creation."""
        result = card()
        assert isinstance(result, Tag)

    def test_card_with_content(self) -> None:
        """Test card with content."""
        result = card("Card content")
        html = str(result)
        assert "Card content" in html

    def test_card_with_multiple_children(self) -> None:
        """Test card with multiple children."""
        result = card("First", "Second", "Third")
        html = str(result)
        assert "First" in html
        assert "Second" in html
        assert "Third" in html

    def test_card_with_div_content(self) -> None:
        """Test card with div content."""
        result = card(div("Inner content"))
        html = str(result)
        assert "Inner content" in html

    def test_card_has_card_class(self) -> None:
        """Test card has card class."""
        result = card()
        html = str(result)
        assert "card" in html

    def test_card_with_full_screen(self) -> None:
        """Test card with full_screen parameter."""
        result = card(full_screen=True)
        html = str(result)
        assert "card" in html

    def test_card_with_height(self) -> None:
        """Test card with height parameter."""
        result = card(height="400px")
        html = str(result)
        assert "card" in html

    def test_card_with_fill(self) -> None:
        """Test card with fill parameter."""
        result = card(fill=True)
        html = str(result)
        assert "card" in html

    def test_card_with_class(self) -> None:
        """Test card with class_ parameter."""
        result = card(class_="my-custom-class")
        html = str(result)
        assert "my-custom-class" in html


class TestCardHeader:
    """Tests for card_header function."""

    def test_card_header_basic(self) -> None:
        """Test basic card_header creation."""
        result = card_header("Header text")
        assert isinstance(result, CardItem)

    def test_card_header_with_content(self) -> None:
        """Test card_header with content."""
        result = card_header("My Header")
        resolved = result.resolve()
        html = str(resolved)
        assert "My Header" in html

    def test_card_header_has_header_class(self) -> None:
        """Test card_header has card-header class."""
        result = card_header("Header")
        resolved = result.resolve()
        html = str(resolved)
        assert "card-header" in html


class TestCardBody:
    """Tests for card_body function."""

    def test_card_body_basic(self) -> None:
        """Test basic card_body creation."""
        result = card_body()
        assert isinstance(result, CardItem)

    def test_card_body_with_content(self) -> None:
        """Test card_body with content."""
        result = card_body("Body content")
        resolved = result.resolve()
        html = str(resolved)
        assert "Body content" in html

    def test_card_body_has_body_class(self) -> None:
        """Test card_body has card-body class."""
        result = card_body("Content")
        resolved = result.resolve()
        html = str(resolved)
        assert "card-body" in html

    def test_card_body_with_multiple_children(self) -> None:
        """Test card_body with multiple children."""
        result = card_body("First", "Second")
        resolved = result.resolve()
        html = str(resolved)
        assert "First" in html
        assert "Second" in html

    def test_card_body_with_class(self) -> None:
        """Test card_body with class_ parameter."""
        result = card_body("Content", class_="custom-class")
        resolved = result.resolve()
        html = str(resolved)
        assert "custom-class" in html

    def test_card_body_with_fill(self) -> None:
        """Test card_body with fill parameter."""
        result = card_body("Content", fill=True)
        assert isinstance(result, CardItem)


class TestCardFooter:
    """Tests for card_footer function."""

    def test_card_footer_basic(self) -> None:
        """Test basic card_footer creation."""
        result = card_footer("Footer text")
        assert isinstance(result, CardItem)

    def test_card_footer_with_content(self) -> None:
        """Test card_footer with content."""
        result = card_footer("My Footer")
        resolved = result.resolve()
        html = str(resolved)
        assert "My Footer" in html

    def test_card_footer_has_footer_class(self) -> None:
        """Test card_footer has card-footer class."""
        result = card_footer("Footer")
        resolved = result.resolve()
        html = str(resolved)
        assert "card-footer" in html


class TestCardComposition:
    """Tests for composing card components."""

    def test_card_with_header_and_body(self) -> None:
        """Test card with header and body."""
        result = card(
            card_header("Title"),
            card_body("Content"),
        )
        html = str(result)
        assert "Title" in html
        assert "Content" in html

    def test_card_with_all_components(self) -> None:
        """Test card with header, body, and footer."""
        result = card(
            card_header("Title"),
            card_body("Content"),
            card_footer("Footer"),
        )
        html = str(result)
        assert "Title" in html
        assert "Content" in html
        assert "Footer" in html
