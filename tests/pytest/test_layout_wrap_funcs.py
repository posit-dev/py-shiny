"""Tests for shiny.ui._layout module."""

from htmltools import Tag

from shiny.ui._layout import layout_column_wrap


class TestLayoutColumnWrap:
    """Tests for layout_column_wrap function."""

    def test_basic_wrap(self) -> None:
        """Test basic layout_column_wrap creation."""
        result = layout_column_wrap("Item 1", "Item 2", "Item 3")
        assert isinstance(result, Tag)

    def test_wrap_with_width(self) -> None:
        """Test layout_column_wrap with width parameter."""
        result = layout_column_wrap("Item 1", "Item 2", width="200px")
        assert isinstance(result, Tag)

    def test_wrap_with_fixed_width(self) -> None:
        """Test layout_column_wrap with fixed_width parameter."""
        result = layout_column_wrap("Item 1", "Item 2", width="1/2", fixed_width=True)
        assert isinstance(result, Tag)

    def test_wrap_with_heights_equal(self) -> None:
        """Test layout_column_wrap with heights_equal='all'."""
        result = layout_column_wrap("Item 1", "Item 2", heights_equal="all")
        assert isinstance(result, Tag)

    def test_wrap_with_heights_equal_row(self) -> None:
        """Test layout_column_wrap with heights_equal='row'."""
        result = layout_column_wrap("Item 1", "Item 2", heights_equal="row")
        assert isinstance(result, Tag)

    def test_wrap_with_fill(self) -> None:
        """Test layout_column_wrap with fill parameter."""
        result = layout_column_wrap("Item 1", "Item 2", fill=True)
        assert isinstance(result, Tag)

    def test_wrap_with_fillable(self) -> None:
        """Test layout_column_wrap with fillable parameter."""
        result = layout_column_wrap("Item 1", "Item 2", fillable=True)
        assert isinstance(result, Tag)

    def test_wrap_with_gap(self) -> None:
        """Test layout_column_wrap with gap parameter."""
        result = layout_column_wrap("Item 1", "Item 2", gap="1rem")
        assert isinstance(result, Tag)

    def test_wrap_with_height(self) -> None:
        """Test layout_column_wrap with height parameter."""
        result = layout_column_wrap("Item 1", "Item 2", height="400px")
        assert isinstance(result, Tag)

    def test_wrap_with_tag_children(self) -> None:
        """Test layout_column_wrap with Tag children."""
        from htmltools import div

        result = layout_column_wrap(
            div("Box 1"),
            div("Box 2"),
            div("Box 3"),
        )
        assert isinstance(result, Tag)

    def test_wrap_with_class(self) -> None:
        """Test layout_column_wrap with class_ parameter."""
        result = layout_column_wrap("Item", class_="my-custom-class")
        html = str(result)
        assert "my-custom-class" in html

    def test_wrap_with_id(self) -> None:
        """Test layout_column_wrap with id parameter."""
        result = layout_column_wrap("Item", id="my-wrapper")
        html = str(result)
        assert "my-wrapper" in html

    def test_wrap_no_children(self) -> None:
        """Test layout_column_wrap with no children."""
        result = layout_column_wrap()
        assert isinstance(result, Tag)

    def test_wrap_single_child(self) -> None:
        """Test layout_column_wrap with single child."""
        result = layout_column_wrap("Single item")
        assert isinstance(result, Tag)

    def test_wrap_many_children(self) -> None:
        """Test layout_column_wrap with many children."""
        items = [f"Item {i}" for i in range(10)]
        result = layout_column_wrap(*items)
        assert isinstance(result, Tag)
