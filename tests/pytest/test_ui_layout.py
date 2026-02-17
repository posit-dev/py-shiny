"""Tests for shiny/ui/_layout.py"""

from __future__ import annotations

from htmltools import Tag, tags

from shiny.ui._layout import layout_column_wrap


class TestLayoutColumnWrap:
    """Tests for the layout_column_wrap function."""

    def test_basic_layout(self) -> None:
        """Test basic layout_column_wrap creation."""
        result = layout_column_wrap(
            tags.div("Item 1"),
            tags.div("Item 2"),
            tags.div("Item 3"),
        )

        assert isinstance(result, Tag)
        assert result.name == "div"

    def test_with_width_fraction(self) -> None:
        """Test with width as fraction (e.g., 1/3)."""
        result = layout_column_wrap(
            tags.div("Item 1"),
            tags.div("Item 2"),
            width=1 / 3,
        )

        rendered = str(result)
        assert "bslib-grid" in rendered

    def test_with_width_css_unit(self) -> None:
        """Test with width as CSS unit."""
        result = layout_column_wrap(
            tags.div("Item 1"),
            tags.div("Item 2"),
            width="200px",
        )

        assert isinstance(result, Tag)
        rendered = str(result)
        assert "200px" in rendered

    def test_with_fixed_width(self) -> None:
        """Test with fixed_width=True."""
        result = layout_column_wrap(
            tags.div("Item"),
            width="150px",
            fixed_width=True,
        )

        rendered = str(result)
        # Should use auto-fit with minmax
        assert "150px" in rendered

    def test_with_heights_equal_all(self) -> None:
        """Test with heights_equal='all'."""
        result = layout_column_wrap(
            tags.div("Item 1"),
            tags.div("Item 2"),
            heights_equal="all",
        )

        rendered = str(result)
        # Should include grid-auto-rows: 1fr
        assert "1fr" in rendered

    def test_with_heights_equal_row(self) -> None:
        """Test with heights_equal='row'."""
        result = layout_column_wrap(
            tags.div("Item 1"),
            heights_equal="row",
        )

        # Should not include grid-auto-rows: 1fr
        assert isinstance(result, Tag)

    def test_with_fill_true(self) -> None:
        """Test with fill=True."""
        result = layout_column_wrap(
            tags.div("Item"),
            fill=True,
        )

        # Should be a fill item
        assert result.has_class("html-fill-item")

    def test_with_fill_false(self) -> None:
        """Test with fill=False."""
        result = layout_column_wrap(
            tags.div("Item"),
            fill=False,
        )

        # Should not be a fill item
        assert not result.has_class("html-fill-item")

    def test_with_height(self) -> None:
        """Test with height parameter."""
        result = layout_column_wrap(
            tags.div("Item"),
            height="400px",
        )

        rendered = str(result)
        assert "400px" in rendered

    def test_with_gap(self) -> None:
        """Test with gap parameter."""
        result = layout_column_wrap(
            tags.div("Item"),
            gap="10px",
        )

        rendered = str(result)
        assert "10px" in rendered

    def test_with_class(self) -> None:
        """Test with custom class."""
        result = layout_column_wrap(
            tags.div("Item"),
            class_="my-custom-class",
        )

        assert result.has_class("my-custom-class")

    def test_with_min_height(self) -> None:
        """Test with min_height parameter."""
        result = layout_column_wrap(
            tags.div("Item"),
            min_height="100px",
        )

        rendered = str(result)
        assert "100px" in rendered

    def test_with_max_height(self) -> None:
        """Test with max_height parameter."""
        result = layout_column_wrap(
            tags.div("Item"),
            max_height="500px",
        )

        rendered = str(result)
        assert "500px" in rendered

    def test_with_height_mobile(self) -> None:
        """Test with height_mobile parameter."""
        result = layout_column_wrap(
            tags.div("Item"),
            height_mobile="300px",
        )

        rendered = str(result)
        assert "300px" in rendered

    def test_width_none(self) -> None:
        """Test with width=None."""
        result = layout_column_wrap(
            tags.div("Item"),
            width=None,
        )

        # Should not have grid-template-columns set
        assert isinstance(result, Tag)

    def test_fillable_true(self) -> None:
        """Test with fillable=True (default)."""
        result = layout_column_wrap(
            tags.div("Item"),
            fillable=True,
        )

        rendered = str(result)
        # Children should be wrapped in fillable containers
        assert "html-fill-container" in rendered

    def test_fillable_false(self) -> None:
        """Test with fillable=False."""
        result = layout_column_wrap(
            tags.div("Item"),
            fillable=False,
        )

        # Children should not be fillable containers
        assert isinstance(result, Tag)

    def test_multiple_children(self) -> None:
        """Test with multiple children."""
        result = layout_column_wrap(
            tags.div("One"),
            tags.div("Two"),
            tags.div("Three"),
            tags.div("Four"),
        )

        rendered = str(result)
        assert "One" in rendered
        assert "Two" in rendered
        assert "Three" in rendered
        assert "Four" in rendered

    def test_invalid_width_fraction_raises(self) -> None:
        """Test that invalid width fraction raises ValueError."""
        import pytest

        with pytest.raises(ValueError):
            layout_column_wrap(
                tags.div("Item"),
                width=0.3,  # 1/0.3 is not an integer
            )
