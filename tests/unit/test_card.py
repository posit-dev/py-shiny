"""Unit tests for shiny.ui._card module."""

from __future__ import annotations

from htmltools import Tag, tags

from shiny.ui import card, card_body, card_footer, card_header


class TestCard:
    """Tests for card function."""

    def test_basic_card(self) -> None:
        """Test basic card with content."""
        result = card("Card content")

        assert isinstance(result, Tag)
        html = str(result)
        assert "card" in html
        assert "Card content" in html

    def test_card_returns_tag(self) -> None:
        """Test that card returns a Tag."""
        result = card("Content")
        assert isinstance(result, Tag)

    def test_card_with_id(self) -> None:
        """Test card with id parameter."""
        result = card("Content", id="my_card")
        html = str(result)

        assert "my_card" in html

    def test_card_full_screen(self) -> None:
        """Test card with full_screen enabled."""
        result = card("Content", full_screen=True)
        html = str(result)

        assert "full-screen" in html.lower()

    def test_card_height(self) -> None:
        """Test card with height parameter."""
        result = card("Content", height="300px")
        html = str(result)

        assert "300px" in html

    def test_card_max_height(self) -> None:
        """Test card with max_height parameter."""
        result = card("Content", max_height="500px")
        html = str(result)

        assert "500px" in html

    def test_card_min_height(self) -> None:
        """Test card with min_height parameter."""
        result = card("Content", min_height="200px")
        html = str(result)

        assert "200px" in html

    def test_card_fill_true(self) -> None:
        """Test card with fill=True (default)."""
        result = card("Content", fill=True)
        html = str(result)

        # Should have fill-related classes
        assert "card" in html

    def test_card_fill_false(self) -> None:
        """Test card with fill=False."""
        result = card("Content", fill=False)
        html = str(result)

        assert "card" in html

    def test_card_with_class(self) -> None:
        """Test card with custom class."""
        result = card("Content", class_="custom-card")
        html = str(result)

        assert "custom-card" in html

    def test_card_multiple_content(self) -> None:
        """Test card with multiple content children."""
        result = card(
            tags.p("First paragraph"),
            tags.p("Second paragraph"),
        )
        html = str(result)

        assert "First paragraph" in html
        assert "Second paragraph" in html

    def test_card_html_content(self) -> None:
        """Test card with HTML content."""
        result = card(
            tags.strong("Bold text"),
            tags.em("Italic text"),
        )
        html = str(result)

        assert "<strong>Bold text</strong>" in html
        assert "<em>Italic text</em>" in html


class TestCardHeader:
    """Tests for card_header function."""

    def test_basic_card_header(self) -> None:
        """Test basic card_header."""
        result = card_header("Header text")
        html = str(result.resolve())

        assert "card-header" in html
        assert "Header text" in html

    def test_card_header_container(self) -> None:
        """Test card_header container classes."""
        result = card_header("Header", container=tags.h3)
        html = str(result.resolve())

        assert "card-header" in html

    def test_card_header_with_class(self) -> None:
        """Test card_header with custom class."""
        result = card_header("Header", class_="custom-header")
        html = str(result.resolve())

        assert "custom-header" in html

    def test_card_in_card(self) -> None:
        """Test card_header used in a card."""
        result = card(
            card_header("My Header"),
            "Card body content",
        )
        html = str(result)

        assert "card-header" in html
        assert "My Header" in html


class TestCardFooter:
    """Tests for card_footer function."""

    def test_basic_card_footer(self) -> None:
        """Test basic card_footer."""
        result = card_footer("Footer text")
        html = str(result.resolve())

        assert "card-footer" in html
        assert "Footer text" in html

    def test_card_footer_with_class(self) -> None:
        """Test card_footer with custom class."""
        result = card_footer("Footer", class_="custom-footer")
        html = str(result.resolve())

        assert "custom-footer" in html

    def test_card_footer_in_card(self) -> None:
        """Test card_footer used in a card."""
        result = card(
            "Card body content",
            card_footer("My Footer"),
        )
        html = str(result)

        assert "card-footer" in html
        assert "My Footer" in html


class TestCardBody:
    """Tests for card_body function."""

    def test_basic_card_body(self) -> None:
        """Test basic card_body."""
        result = card_body("Body content")
        html = str(result.resolve())

        assert "card-body" in html
        assert "Body content" in html

    def test_card_body_fillable_true(self) -> None:
        """Test card_body with fillable=True (default)."""
        result = card_body("Content", fillable=True)
        html = str(result.resolve())

        assert "card-body" in html

    def test_card_body_fillable_false(self) -> None:
        """Test card_body with fillable=False."""
        result = card_body("Content", fillable=False)
        html = str(result.resolve())

        assert "card-body" in html

    def test_card_body_height(self) -> None:
        """Test card_body with height parameter."""
        result = card_body("Content", height="200px")
        html = str(result.resolve())

        assert "200px" in html

    def test_card_body_min_height(self) -> None:
        """Test card_body with min_height parameter."""
        result = card_body("Content", min_height="100px")
        html = str(result.resolve())

        assert "100px" in html

    def test_card_body_max_height(self) -> None:
        """Test card_body with max_height parameter."""
        result = card_body("Content", max_height="400px")
        html = str(result.resolve())

        assert "400px" in html

    def test_card_body_padding(self) -> None:
        """Test card_body with padding parameter."""
        result = card_body("Content", padding="20px")
        html = str(result.resolve())

        assert "20px" in html

    def test_card_body_gap(self) -> None:
        """Test card_body with gap parameter."""
        result = card_body("Content", gap="10px")
        html = str(result.resolve())

        assert "10px" in html

    def test_card_body_fill_true(self) -> None:
        """Test card_body with fill=True (default)."""
        result = card_body("Content", fill=True)
        html = str(result.resolve())

        assert "card-body" in html

    def test_card_body_fill_false(self) -> None:
        """Test card_body with fill=False."""
        result = card_body("Content", fill=False)
        html = str(result.resolve())

        assert "card-body" in html

    def test_card_body_with_class(self) -> None:
        """Test card_body with custom class."""
        result = card_body("Content", class_="custom-body")
        html = str(result.resolve())

        assert "custom-body" in html

    def test_card_body_in_card(self) -> None:
        """Test card_body used in a card."""
        result = card(
            card_header("Header"),
            card_body("Body content"),
            card_footer("Footer"),
        )
        html = str(result)

        assert "card-body" in html
        assert "Body content" in html


class TestCardWithAllParts:
    """Tests for card with header, body, and footer."""

    def test_complete_card(self) -> None:
        """Test card with header, body, and footer."""
        result = card(
            card_header("Card Title"),
            card_body("Main content goes here"),
            card_footer("Footer text"),
        )
        html = str(result)

        assert "card-header" in html
        assert "card-body" in html
        assert "card-footer" in html
        assert "Card Title" in html
        assert "Main content goes here" in html
        assert "Footer text" in html

    def test_card_multiple_body_sections(self) -> None:
        """Test card with multiple body sections."""
        result = card(
            card_header("Title"),
            card_body("Body 1"),
            card_body("Body 2"),
            card_footer("Footer"),
        )
        html = str(result)

        assert "Body 1" in html
        assert "Body 2" in html
