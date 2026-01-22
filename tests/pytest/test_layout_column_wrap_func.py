"""Tests for shiny.ui._layout module."""

from htmltools import div, tags

from shiny.ui import layout_column_wrap


class TestLayoutColumnWrap:
    """Tests for the layout_column_wrap function."""

    def test_basic_layout(self):
        """Test creating a basic column wrap layout."""
        result = layout_column_wrap(
            div("Item 1"),
            div("Item 2"),
            div("Item 3"),
            width="200px",
        )
        html = str(result)

        assert "Item 1" in html
        assert "Item 2" in html
        assert "Item 3" in html

    def test_layout_with_fixed_width(self):
        """Test layout with fixed width columns."""
        result = layout_column_wrap(
            div("Item 1"),
            div("Item 2"),
            width="300px",
            fixed_width=True,
        )
        html = str(result)

        assert "Item 1" in html

    def test_layout_with_fractional_width(self):
        """Test layout with fractional width (1/3)."""
        result = layout_column_wrap(
            div("Item 1"),
            div("Item 2"),
            div("Item 3"),
            width=1 / 3,
        )
        html = str(result)

        assert "Item 1" in html

    def test_layout_heights_equal_all(self):
        """Test layout with all heights equal."""
        result = layout_column_wrap(
            div("Item 1"),
            div("Item 2"),
            width="200px",
            heights_equal="all",
        )
        html = str(result)

        assert "Item 1" in html

    def test_layout_heights_equal_row(self):
        """Test layout with row heights equal."""
        result = layout_column_wrap(
            div("Item 1"),
            div("Item 2"),
            width="200px",
            heights_equal="row",
        )
        html = str(result)

        assert "Item 1" in html

    def test_layout_with_fill_false(self):
        """Test layout with fill disabled."""
        result = layout_column_wrap(
            div("Item 1"),
            div("Item 2"),
            width="200px",
            fill=False,
        )
        html = str(result)

        assert "Item 1" in html

    def test_layout_with_fillable_false(self):
        """Test layout with fillable disabled."""
        result = layout_column_wrap(
            div("Item 1"),
            div("Item 2"),
            width="200px",
            fillable=False,
        )
        html = str(result)

        assert "Item 1" in html

    def test_layout_with_height(self):
        """Test layout with explicit height."""
        result = layout_column_wrap(
            div("Item 1"),
            div("Item 2"),
            width="200px",
            height="400px",
        )
        html = str(result)

        assert "400px" in html

    def test_layout_with_min_max_height(self):
        """Test layout with min and max height."""
        result = layout_column_wrap(
            div("Item 1"),
            div("Item 2"),
            width="200px",
            min_height="200px",
            max_height="600px",
        )
        html = str(result)

        assert "Item 1" in html

    def test_layout_with_height_mobile(self):
        """Test layout with mobile height."""
        result = layout_column_wrap(
            div("Item 1"),
            div("Item 2"),
            width="200px",
            height_mobile="300px",
        )
        html = str(result)

        assert "Item 1" in html

    def test_layout_with_gap(self):
        """Test layout with custom gap."""
        result = layout_column_wrap(
            div("Item 1"),
            div("Item 2"),
            width="200px",
            gap="20px",
        )
        html = str(result)

        assert "Item 1" in html

    def test_layout_with_class(self):
        """Test layout with custom CSS class."""
        result = layout_column_wrap(
            div("Item 1"),
            div("Item 2"),
            width="200px",
            class_="my-custom-class",
        )
        html = str(result)

        assert "my-custom-class" in html

    def test_layout_with_width_none(self):
        """Test layout with width=None for manual CSS control."""
        result = layout_column_wrap(
            div("Item 1"),
            div("Item 2"),
            width=None,
        )
        html = str(result)

        assert "Item 1" in html

    def test_layout_empty(self):
        """Test layout with no children."""
        result = layout_column_wrap(width="200px")
        html = str(result)

        # Should still render container
        assert html is not None

    def test_layout_with_tag_children(self):
        """Test layout with various tag children."""
        result = layout_column_wrap(
            tags.p("Paragraph 1"),
            tags.p("Paragraph 2"),
            tags.span("Span"),
            width="200px",
        )
        html = str(result)

        assert "Paragraph 1" in html
        assert "Paragraph 2" in html
        assert "Span" in html
