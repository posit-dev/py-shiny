"""Tests for shiny.ui._layout_columns module."""

from htmltools import Tag, div

from shiny.ui._layout_columns import layout_columns


class TestLayoutColumns:
    """Tests for layout_columns function."""

    def test_layout_columns_basic(self) -> None:
        """Test basic layout_columns creation."""
        result = layout_columns("Column 1", "Column 2")
        assert isinstance(result, Tag)

    def test_layout_columns_with_content(self) -> None:
        """Test layout_columns with content."""
        result = layout_columns("First", "Second")
        html = str(result)
        assert "First" in html
        assert "Second" in html

    def test_layout_columns_with_div(self) -> None:
        """Test layout_columns with div content."""
        result = layout_columns(div("Col 1"), div("Col 2"))
        html = str(result)
        assert "Col 1" in html
        assert "Col 2" in html

    def test_layout_columns_with_col_widths(self) -> None:
        """Test layout_columns with col_widths parameter."""
        result = layout_columns("A", "B", col_widths=(6, 6))
        html = str(result)
        assert "A" in html
        assert "B" in html

    def test_layout_columns_with_row_heights(self) -> None:
        """Test layout_columns with row_heights parameter."""
        result = layout_columns("A", "B", row_heights="200px")
        html = str(result)
        assert "A" in html

    def test_layout_columns_has_grid_class(self) -> None:
        """Test layout_columns has grid class."""
        result = layout_columns("A", "B")
        html = str(result)
        assert "grid" in html
        assert "bslib-grid" in html

    def test_layout_columns_with_fill(self) -> None:
        """Test layout_columns with fill parameter."""
        result = layout_columns("A", "B", fill=True)
        html = str(result)
        assert "A" in html

    def test_layout_columns_with_fillable(self) -> None:
        """Test layout_columns with fillable parameter."""
        result = layout_columns("A", "B", fillable=True)
        html = str(result)
        assert "A" in html

    def test_layout_columns_with_gap(self) -> None:
        """Test layout_columns with gap parameter."""
        result = layout_columns("A", "B", gap="20px")
        html = str(result)
        assert "A" in html

    def test_layout_columns_with_heights_equal(self) -> None:
        """Test layout_columns with heights_equal parameter."""
        result = layout_columns("A", "B", heights_equal="row")
        html = str(result)
        assert "A" in html

    def test_layout_columns_single_column(self) -> None:
        """Test layout_columns with single column."""
        result = layout_columns("Only column")
        html = str(result)
        assert "Only column" in html

    def test_layout_columns_three_columns(self) -> None:
        """Test layout_columns with three columns."""
        result = layout_columns("A", "B", "C")
        html = str(result)
        assert "A" in html
        assert "B" in html
        assert "C" in html
