"""Tests for shiny.ui._bootstrap module."""

from htmltools import Tag, TagList

from shiny.ui._bootstrap import (
    column,
    panel_title,
    row,
)


class TestRow:
    """Tests for row function."""

    def test_row_basic(self) -> None:
        """Test basic row creation."""
        result = row("content")
        assert isinstance(result, Tag)
        assert result.name == "div"

    def test_row_has_class(self) -> None:
        """Test row has row class."""
        result = row("content")
        html = str(result)
        assert "row" in html

    def test_row_multiple_children(self) -> None:
        """Test row with multiple children."""
        result = row("child1", "child2", "child3")
        assert isinstance(result, Tag)


class TestColumn:
    """Tests for column function."""

    def test_column_basic(self) -> None:
        """Test basic column creation."""
        result = column(6, "content")
        assert isinstance(result, Tag)
        assert result.name == "div"

    def test_column_has_class(self) -> None:
        """Test column has col class."""
        result = column(6, "content")
        html = str(result)
        assert "col" in html

    def test_column_width_in_class(self) -> None:
        """Test column width is in class name."""
        result = column(6, "content")
        html = str(result)
        assert "col-sm-6" in html

    def test_column_offset(self) -> None:
        """Test column with offset."""
        result = column(6, "content", offset=3)
        html = str(result)
        assert "offset" in html

    def test_column_width_12(self) -> None:
        """Test full-width column."""
        result = column(12, "content")
        html = str(result)
        assert "col-sm-12" in html

    def test_column_multiple_children(self) -> None:
        """Test column with multiple children."""
        result = column(6, "child1", "child2")
        assert isinstance(result, Tag)


class TestPanelTitle:
    """Tests for panel_title function."""

    def test_panel_title_basic(self) -> None:
        """Test basic panel_title creation."""
        result = panel_title("My Title")
        assert isinstance(result, TagList)

    def test_panel_title_has_title(self) -> None:
        """Test panel_title contains title text."""
        result = panel_title("Test Title")
        html = str(result)
        assert "Test Title" in html

    def test_panel_title_h2_tag(self) -> None:
        """Test panel_title uses h2 tag."""
        result = panel_title("Title")
        html = str(result)
        assert "<h2" in html

    def test_panel_title_with_window_title(self) -> None:
        """Test panel_title with window_title parameter."""
        result = panel_title("Visible Title", window_title="Window Title")
        # Should contain the visible title
        html = str(result)
        assert "Visible Title" in html


class TestRowColumnIntegration:
    """Integration tests for row and column."""

    def test_row_with_columns(self) -> None:
        """Test row containing columns."""
        result = row(
            column(6, "Left"),
            column(6, "Right"),
        )
        assert isinstance(result, Tag)
        html = str(result)
        assert "row" in html
        assert "col-sm-6" in html

    def test_nested_rows(self) -> None:
        """Test nested rows."""
        result = row(
            column(
                12,
                row(
                    column(6, "Nested"),
                ),
            ),
        )
        assert isinstance(result, Tag)
