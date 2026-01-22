"""Tests for shiny.ui._layout_columns module."""

from htmltools import div, tags

from shiny.ui import layout_columns


class TestLayoutColumns:
    """Tests for the layout_columns function."""

    def test_basic_layout(self):
        """Test creating a basic column layout."""
        result = layout_columns(
            div("Column 1"),
            div("Column 2"),
            div("Column 3"),
        )
        html = str(result)

        assert "Column 1" in html
        assert "Column 2" in html
        assert "Column 3" in html
        assert "bslib-grid" in html

    def test_layout_with_col_widths_list(self):
        """Test layout with column widths as list."""
        result = layout_columns(
            div("Item 1"),
            div("Item 2"),
            div("Item 3"),
            col_widths=[4, 4, 4],
        )
        html = str(result)

        assert "Item 1" in html

    def test_layout_with_col_widths_tuple(self):
        """Test layout with column widths as tuple."""
        result = layout_columns(
            div("Item 1"),
            div("Item 2"),
            col_widths=(6, 6),
        )
        html = str(result)

        assert "Item 1" in html

    def test_layout_with_col_widths_dict(self):
        """Test layout with breakpoint-specific column widths."""
        result = layout_columns(
            div("Item 1"),
            div("Item 2"),
            col_widths={"sm": (6, 6), "lg": (4, 8)},
        )
        html = str(result)

        assert "Item 1" in html

    def test_layout_with_negative_col_widths(self):
        """Test layout with negative column widths (empty columns)."""
        result = layout_columns(
            div("Item 1"),
            div("Item 2"),
            col_widths=(-2, 4, 4, -2),
        )
        html = str(result)

        assert "Item 1" in html

    def test_layout_with_row_heights_list(self):
        """Test layout with row heights as list."""
        result = layout_columns(
            div("Item 1"),
            div("Item 2"),
            div("Item 3"),
            div("Item 4"),
            col_widths=(6, 6),
            row_heights=[1, 2],
        )
        html = str(result)

        assert "Item 1" in html

    def test_layout_with_row_heights_string(self):
        """Test layout with row heights as string."""
        result = layout_columns(
            div("Item 1"),
            div("Item 2"),
            row_heights="200px",
        )
        html = str(result)

        assert "Item 1" in html

    def test_layout_with_fill_false(self):
        """Test layout with fill disabled."""
        result = layout_columns(
            div("Item 1"),
            div("Item 2"),
            fill=False,
        )
        html = str(result)

        assert "Item 1" in html

    def test_layout_with_fillable_false(self):
        """Test layout with fillable disabled."""
        result = layout_columns(
            div("Item 1"),
            div("Item 2"),
            fillable=False,
        )
        html = str(result)

        assert "Item 1" in html

    def test_layout_with_gap(self):
        """Test layout with custom gap."""
        result = layout_columns(
            div("Item 1"),
            div("Item 2"),
            gap="20px",
        )
        html = str(result)

        assert "Item 1" in html

    def test_layout_with_height(self):
        """Test layout with explicit height."""
        result = layout_columns(
            div("Item 1"),
            div("Item 2"),
            height="400px",
        )
        html = str(result)

        assert "400px" in html

    def test_layout_with_min_max_height(self):
        """Test layout with min and max height."""
        result = layout_columns(
            div("Item 1"),
            div("Item 2"),
            min_height="200px",
            max_height="600px",
        )
        html = str(result)

        assert "Item 1" in html

    def test_layout_with_class(self):
        """Test layout with custom CSS class."""
        result = layout_columns(
            div("Item 1"),
            div("Item 2"),
            class_="my-custom-class",
        )
        html = str(result)

        assert "my-custom-class" in html

    def test_layout_empty(self):
        """Test layout with no children."""
        result = layout_columns()
        html = str(result)

        # Should still render container
        assert "bslib-layout-columns" in html

    def test_layout_with_tag_children(self):
        """Test layout with various tag children."""
        result = layout_columns(
            tags.p("Paragraph 1"),
            tags.span("Span"),
            tags.div("Div"),
        )
        html = str(result)

        assert "Paragraph 1" in html
        assert "Span" in html
        assert "Div" in html

    def test_layout_with_single_col_width(self):
        """Test layout with single column width value."""
        result = layout_columns(
            div("Item 1"),
            div("Item 2"),
            div("Item 3"),
            col_widths=4,
        )
        html = str(result)

        assert "Item 1" in html
