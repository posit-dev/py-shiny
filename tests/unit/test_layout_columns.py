"""Tests for shiny/ui/_layout_columns.py"""

from htmltools import Tag, div

from shiny.ui import layout_columns


class TestLayoutColumns:
    """Tests for the layout_columns function."""

    def test_basic_layout_columns(self):
        """Test basic layout columns creation."""
        result = layout_columns("Item 1", "Item 2", "Item 3")
        html = str(result)
        assert "Item 1" in html
        assert "Item 2" in html
        assert "Item 3" in html

    def test_layout_columns_returns_tag(self):
        """Test layout_columns returns a Tag."""
        result = layout_columns("Content")
        assert isinstance(result, Tag)

    def test_layout_columns_with_col_widths_list(self):
        """Test layout columns with explicit column widths."""
        result = layout_columns("A", "B", "C", col_widths=[4, 4, 4])
        html = str(result)
        assert "A" in html
        assert "B" in html
        assert "C" in html

    def test_layout_columns_with_col_widths_unequal(self):
        """Test layout columns with unequal column widths."""
        result = layout_columns("Narrow", "Wide", col_widths=[3, 9])
        html = str(result)
        assert "Narrow" in html
        assert "Wide" in html

    def test_layout_columns_with_fill_true(self):
        """Test layout columns with fill enabled."""
        result = layout_columns("Content", fill=True)
        html = str(result)
        assert "Content" in html

    def test_layout_columns_with_fill_false(self):
        """Test layout columns with fill disabled."""
        result = layout_columns("Content", fill=False)
        html = str(result)
        assert "Content" in html

    def test_layout_columns_with_fillable_true(self):
        """Test layout columns with fillable enabled."""
        result = layout_columns("Content", fillable=True)
        html = str(result)
        assert "Content" in html

    def test_layout_columns_with_fillable_false(self):
        """Test layout columns with fillable disabled."""
        result = layout_columns("Content", fillable=False)
        html = str(result)
        assert "Content" in html

    def test_layout_columns_with_gap(self):
        """Test layout columns with gap."""
        result = layout_columns("A", "B", gap="20px")
        html = str(result)
        assert "A" in html
        assert "B" in html

    def test_layout_columns_with_class(self):
        """Test layout columns with custom class."""
        result = layout_columns("Content", class_="my-custom-class")
        html = str(result)
        assert "my-custom-class" in html

    def test_layout_columns_with_height(self):
        """Test layout columns with height."""
        result = layout_columns("Content", height="500px")
        html = str(result)
        assert "Content" in html

    def test_layout_columns_with_min_height(self):
        """Test layout columns with min height."""
        result = layout_columns("Content", min_height="200px")
        html = str(result)
        assert "Content" in html

    def test_layout_columns_with_max_height(self):
        """Test layout columns with max height."""
        result = layout_columns("Content", max_height="800px")
        html = str(result)
        assert "Content" in html

    def test_layout_columns_with_kwargs(self):
        """Test layout columns with additional attributes."""
        result = layout_columns("Content", id="my-layout", data_custom="value")
        html = str(result)
        assert 'id="my-layout"' in html
        assert 'data-custom="value"' in html

    def test_layout_columns_with_row_heights(self):
        """Test layout columns with row heights."""
        result = layout_columns("Row 1", "Row 2", row_heights=[1, 2])
        html = str(result)
        assert "Row 1" in html
        assert "Row 2" in html

    def test_layout_columns_with_row_heights_string(self):
        """Test layout columns with row heights as string."""
        result = layout_columns("Content", row_heights="auto")
        html = str(result)
        assert "Content" in html

    def test_layout_columns_with_negative_col_widths(self):
        """Test layout columns with negative widths (empty columns)."""
        result = layout_columns("Content", col_widths=[-2, 8, -2])
        html = str(result)
        assert "Content" in html

    def test_layout_columns_with_tag_children(self):
        """Test layout columns with Tag children."""
        result = layout_columns(
            div("First", id="div1"),
            div("Second", id="div2"),
        )
        html = str(result)
        assert 'id="div1"' in html
        assert 'id="div2"' in html

    def test_layout_columns_empty(self):
        """Test layout columns with no children."""
        result = layout_columns()
        assert isinstance(result, Tag)

    def test_layout_columns_with_breakpoint_col_widths(self):
        """Test layout columns with breakpoint-specific column widths."""
        result = layout_columns(
            "A", "B", "C", col_widths={"sm": [6, 6, 12], "lg": [4, 4, 4]}
        )
        html = str(result)
        assert "A" in html
        assert "B" in html
        assert "C" in html
