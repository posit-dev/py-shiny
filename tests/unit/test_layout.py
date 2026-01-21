"""Unit tests for shiny.ui._layout module."""

from __future__ import annotations

from htmltools import Tag, tags

from shiny.ui import layout_column_wrap


class TestLayoutColumnWrap:
    """Tests for layout_column_wrap function."""

    def test_basic_layout_column_wrap(self) -> None:
        """Test basic layout_column_wrap creation."""
        result = layout_column_wrap(
            tags.div("Item 1"),
            tags.div("Item 2"),
            width="200px",
        )
        assert isinstance(result, Tag)

    def test_layout_column_wrap_returns_tag(self) -> None:
        """Test that layout_column_wrap returns a Tag."""
        result = layout_column_wrap(
            tags.div("Item 1"),
            width="200px",
        )
        assert isinstance(result, Tag)

    def test_layout_column_wrap_html(self) -> None:
        """Test layout_column_wrap HTML output."""
        result = layout_column_wrap(
            tags.div("Item 1"),
            tags.div("Item 2"),
            width="200px",
        )
        html = str(result)
        assert "Item 1" in html
        assert "Item 2" in html

    def test_layout_column_wrap_fixed_width_false(self) -> None:
        """Test layout_column_wrap with fixed_width=False."""
        result = layout_column_wrap(
            tags.div("Item 1"),
            width="200px",
            fixed_width=False,
        )
        html = str(result)
        assert "Item 1" in html

    def test_layout_column_wrap_fixed_width_true(self) -> None:
        """Test layout_column_wrap with fixed_width=True."""
        result = layout_column_wrap(
            tags.div("Item 1"),
            width="200px",
            fixed_width=True,
        )
        html = str(result)
        assert "Item 1" in html

    def test_layout_column_wrap_heights_equal_all(self) -> None:
        """Test layout_column_wrap with heights_equal='all'."""
        result = layout_column_wrap(
            tags.div("Item 1"),
            tags.div("Item 2"),
            width="200px",
            heights_equal="all",
        )
        html = str(result)
        assert "Item 1" in html

    def test_layout_column_wrap_heights_equal_row(self) -> None:
        """Test layout_column_wrap with heights_equal='row'."""
        result = layout_column_wrap(
            tags.div("Item 1"),
            tags.div("Item 2"),
            width="200px",
            heights_equal="row",
        )
        html = str(result)
        assert "Item 1" in html

    def test_layout_column_wrap_fill_true(self) -> None:
        """Test layout_column_wrap with fill=True."""
        result = layout_column_wrap(
            tags.div("Item 1"),
            width="200px",
            fill=True,
        )
        html = str(result)
        assert "Item 1" in html

    def test_layout_column_wrap_fill_false(self) -> None:
        """Test layout_column_wrap with fill=False."""
        result = layout_column_wrap(
            tags.div("Item 1"),
            width="200px",
            fill=False,
        )
        html = str(result)
        assert "Item 1" in html

    def test_layout_column_wrap_fillable_true(self) -> None:
        """Test layout_column_wrap with fillable=True."""
        result = layout_column_wrap(
            tags.div("Item 1"),
            width="200px",
            fillable=True,
        )
        html = str(result)
        assert "Item 1" in html

    def test_layout_column_wrap_fillable_false(self) -> None:
        """Test layout_column_wrap with fillable=False."""
        result = layout_column_wrap(
            tags.div("Item 1"),
            width="200px",
            fillable=False,
        )
        html = str(result)
        assert "Item 1" in html

    def test_layout_column_wrap_height(self) -> None:
        """Test layout_column_wrap with height."""
        result = layout_column_wrap(
            tags.div("Item 1"),
            width="200px",
            height="400px",
        )
        html = str(result)
        assert "400px" in html

    def test_layout_column_wrap_min_height(self) -> None:
        """Test layout_column_wrap with min_height."""
        result = layout_column_wrap(
            tags.div("Item 1"),
            width="200px",
            min_height="200px",
        )
        html = str(result)
        assert "200px" in html

    def test_layout_column_wrap_max_height(self) -> None:
        """Test layout_column_wrap with max_height."""
        result = layout_column_wrap(
            tags.div("Item 1"),
            width="200px",
            max_height="600px",
        )
        html = str(result)
        assert "600px" in html

    def test_layout_column_wrap_gap(self) -> None:
        """Test layout_column_wrap with gap."""
        result = layout_column_wrap(
            tags.div("Item 1"),
            tags.div("Item 2"),
            width="200px",
            gap="20px",
        )
        html = str(result)
        assert "20px" in html

    def test_layout_column_wrap_class(self) -> None:
        """Test layout_column_wrap with custom class."""
        result = layout_column_wrap(
            tags.div("Item 1"),
            width="200px",
            class_="custom-layout",
        )
        html = str(result)
        assert "custom-layout" in html

    def test_layout_column_wrap_width_fraction(self) -> None:
        """Test layout_column_wrap with width as fraction."""
        result = layout_column_wrap(
            tags.div("Item 1"),
            tags.div("Item 2"),
            tags.div("Item 3"),
            width=1 / 3,
        )
        html = str(result)
        assert "Item 1" in html

    def test_layout_column_wrap_width_none(self) -> None:
        """Test layout_column_wrap with width=None."""
        result = layout_column_wrap(
            tags.div("Item 1"),
            width=None,
        )
        html = str(result)
        assert "Item 1" in html

    def test_layout_column_wrap_many_items(self) -> None:
        """Test layout_column_wrap with many items."""
        result = layout_column_wrap(
            *[tags.div(f"Item {i}") for i in range(6)],
            width="150px",
        )
        html = str(result)
        assert "Item 0" in html
        assert "Item 5" in html

    def test_layout_column_wrap_height_mobile(self) -> None:
        """Test layout_column_wrap with height_mobile."""
        result = layout_column_wrap(
            tags.div("Item 1"),
            width="200px",
            height_mobile="300px",
        )
        html = str(result)
        assert "300px" in html
