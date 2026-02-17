from htmltools import Tag, tags

from shiny.ui._card import CardItem, card, card_footer, card_header


class TestCard:
    """Tests for the card function."""

    def test_card_basic(self):
        """Test basic card creation."""
        result = card("Card content")

        assert isinstance(result, Tag)
        result_str = str(result)
        assert "card" in result_str
        assert "Card content" in result_str

    def test_card_multiple_content(self):
        """Test card with multiple content elements."""
        result = card(
            "First item",
            tags.p("Second item"),
            tags.div("Third item"),
        )

        result_str = str(result)
        assert "First item" in result_str
        assert "Second item" in result_str
        assert "Third item" in result_str

    def test_card_with_full_screen(self):
        """Test card with full_screen enabled."""
        result = card("Content", full_screen=True)

        result_str = str(result)
        assert "data-full-screen" in result_str

    def test_card_without_full_screen(self):
        """Test card without full_screen (default)."""
        result = card("Content", full_screen=False)

        result_str = str(result)
        # full-screen should not be enabled
        assert 'data-full-screen="false"' not in result_str

    def test_card_with_height(self):
        """Test card with specified height."""
        result = card("Content", height="300px")

        result_str = str(result)
        assert "300px" in result_str

    def test_card_with_max_height(self):
        """Test card with max_height specified."""
        result = card("Content", max_height="500px")

        result_str = str(result)
        assert "500px" in result_str

    def test_card_with_min_height(self):
        """Test card with min_height specified."""
        result = card("Content", min_height="200px")

        result_str = str(result)
        assert "200px" in result_str

    def test_card_fill_true(self):
        """Test card with fill enabled (default)."""
        result = card("Content", fill=True)

        # Card should be a fill item when fill=True
        result_str = str(result)
        assert "card" in result_str

    def test_card_fill_false(self):
        """Test card with fill disabled."""
        result = card("Content", fill=False)

        result_str = str(result)
        assert "card" in result_str

    def test_card_with_custom_class(self):
        """Test card with custom CSS class."""
        result = card("Content", class_="my-custom-card")

        result_str = str(result)
        assert "my-custom-card" in result_str

    def test_card_with_id(self):
        """Test card with explicit id."""
        result = card("Content", id="my_card")

        assert result.attrs.get("id") == "my_card"

    def test_card_with_kwargs(self):
        """Test card with additional HTML attributes."""
        result = card("Content", data_custom="value")

        result_str = str(result)
        assert "data-custom" in result_str

    def test_card_has_bslib_class(self):
        """Test that card has bslib-card class."""
        result = card("Content")

        result_str = str(result)
        assert "bslib-card" in result_str

    def test_card_height_css_unit(self):
        """Test card height with different CSS units."""
        # Test with percentage
        result = card("Content", height="50%")
        assert "50%" in str(result)

        # Test with em
        result = card("Content", height="20em")
        assert "20em" in str(result)


class TestCardHeader:
    """Tests for the card_header function."""

    def test_card_header_basic(self):
        """Test basic card header."""
        result = card_header("Header Text")

        assert isinstance(result, CardItem)
        result_str = str(result.resolve())
        assert "card-header" in result_str
        assert "Header Text" in result_str

    def test_card_header_with_html(self):
        """Test card header with HTML content."""
        result = card_header(tags.strong("Bold Header"))

        result_str = str(result.resolve())
        assert "Bold Header" in result_str
        assert "strong" in result_str

    def test_card_header_multiple_content(self):
        """Test card header with multiple content items."""
        result = card_header(
            tags.span("Icon"),
            "Title",
            tags.span("Badge"),
        )

        result_str = str(result.resolve())
        assert "Icon" in result_str
        assert "Title" in result_str
        assert "Badge" in result_str


class TestCardFooter:
    """Tests for the card_footer function."""

    def test_card_footer_basic(self):
        """Test basic card footer."""
        result = card_footer("Footer Text")

        assert isinstance(result, CardItem)
        result_str = str(result.resolve())
        assert "card-footer" in result_str
        assert "Footer Text" in result_str

    def test_card_footer_with_html(self):
        """Test card footer with HTML content."""
        result = card_footer(
            tags.button("Cancel", class_="btn"),
            tags.button("Save", class_="btn btn-primary"),
        )

        result_str = str(result.resolve())
        assert "Cancel" in result_str
        assert "Save" in result_str

    def test_card_footer_with_class(self):
        """Test card footer with custom class."""
        result = card_footer("Footer", class_="text-muted")

        result_str = str(result.resolve())
        assert "text-muted" in result_str


class TestCardComposition:
    """Tests for composing cards with headers and footers."""

    def test_card_with_header_and_footer(self):
        """Test card with both header and footer."""
        result = card(
            card_header("My Header"),
            "Body content",
            card_footer("My Footer"),
        )

        result_str = str(result)
        assert "My Header" in result_str
        assert "Body content" in result_str
        assert "My Footer" in result_str
        assert "card-header" in result_str
        assert "card-footer" in result_str

    def test_card_with_header_only(self):
        """Test card with header only."""
        result = card(
            card_header("Header"),
            "Content",
        )

        result_str = str(result)
        assert "Header" in result_str
        assert "card-header" in result_str

    def test_card_with_footer_only(self):
        """Test card with footer only."""
        result = card(
            "Content",
            card_footer("Footer"),
        )

        result_str = str(result)
        assert "Footer" in result_str
        assert "card-footer" in result_str
