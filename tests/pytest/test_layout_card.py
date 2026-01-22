"""Tests for layout and card UI components."""

from shiny.ui import (
    card,
    card_header,
    card_footer,
    layout_column_wrap,
    layout_columns,
)


class TestCard:
    """Tests for the card function."""

    def test_basic_card(self):
        """Test creating a basic card."""
        c = card("Card content")
        html = str(c)

        assert "card" in html
        assert "Card content" in html

    def test_card_with_header_footer(self):
        """Test card with header and footer."""
        c = card(
            card_header("Header"),
            "Body content",
            card_footer("Footer"),
        )
        html = str(c)

        assert "Header" in html
        assert "Body content" in html
        assert "Footer" in html
        assert "card-header" in html
        assert "card-footer" in html

    def test_card_with_height(self):
        """Test card with explicit height."""
        c = card("Content", height="300px")
        html = str(c)

        assert "300px" in html

    def test_card_full_screen(self):
        """Test card with full_screen option."""
        c = card("Content", full_screen=True)
        html = str(c)

        assert "bslib-full-screen" in html

    def test_card_with_id(self):
        """Test card with id for Shiny input."""
        c = card("Content", id="my_card")
        html = str(c)

        assert 'id="my_card"' in html

    def test_card_not_fillable(self):
        """Test card with fill=False."""
        c = card("Content", fill=False)
        html = str(c)
        # Should still have card class but different fill behavior
        assert "card" in html


class TestCardHeaderInCard:
    """Tests for card_header within a card context."""

    def test_card_with_header(self):
        """Test card header within a card."""
        c = card(card_header("My Header"), "Body content")
        html = str(c)

        assert "card-header" in html
        assert "My Header" in html

    def test_card_header_with_class(self):
        """Test card header with custom class within a card."""
        c = card(card_header("Header", class_="bg-primary"), "Content")
        html = str(c)

        assert "bg-primary" in html


class TestCardFooterInCard:
    """Tests for card_footer within a card context."""

    def test_card_with_footer(self):
        """Test card footer within a card."""
        c = card("Body content", card_footer("My Footer"))
        html = str(c)

        assert "card-footer" in html
        assert "My Footer" in html


class TestLayoutColumnWrap:
    """Tests for the layout_column_wrap function."""

    def test_basic_layout_column_wrap(self):
        """Test creating a basic column wrap layout."""
        layout = layout_column_wrap(
            card("Card 1"), card("Card 2"), card("Card 3"), width="200px"
        )
        html = str(layout)

        assert "Card 1" in html
        assert "Card 2" in html
        assert "Card 3" in html
        assert "grid" in html.lower() or "bslib-grid" in html

    def test_layout_column_wrap_with_fraction(self):
        """Test column wrap with fractional width (3 columns)."""
        layout = layout_column_wrap(card("A"), card("B"), card("C"), width=1 / 3)
        html = str(layout)

        assert "A" in html

    def test_layout_column_wrap_fixed_width(self):
        """Test column wrap with fixed width."""
        layout = layout_column_wrap(
            card("A"), card("B"), width="150px", fixed_width=True
        )
        html = str(layout)

        assert "A" in html

    def test_layout_column_wrap_with_gap(self):
        """Test column wrap with custom gap."""
        layout = layout_column_wrap(card("A"), card("B"), width="200px", gap="20px")
        html = str(layout)

        assert "20px" in html


class TestLayoutColumns:
    """Tests for the layout_columns function."""

    def test_basic_layout_columns(self):
        """Test creating a basic column layout."""
        layout = layout_columns(
            card("Column 1"),
            card("Column 2"),
        )
        html = str(layout)

        assert "Column 1" in html
        assert "Column 2" in html

    def test_layout_columns_with_widths(self):
        """Test column layout with explicit widths."""
        layout = layout_columns(card("Left"), card("Right"), col_widths=[4, 8])
        html = str(layout)

        assert "Left" in html
        assert "Right" in html

    def test_layout_columns_with_gap(self):
        """Test column layout with gap."""
        layout = layout_columns(card("A"), card("B"), gap="15px")
        html = str(layout)

        assert "A" in html
        assert "15px" in html
