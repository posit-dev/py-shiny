"""Tests for shiny/ui/_valuebox.py module."""

from shiny.ui._valuebox import value_box


class TestValueBox:
    """Tests for value_box function."""

    def test_value_box_is_callable(self):
        """Test value_box is callable."""
        assert callable(value_box)

    def test_value_box_returns_tag(self):
        """Test value_box returns a Tag."""
        from htmltools import Tag

        result = value_box("Title", "100", showcase="🎉")
        assert isinstance(result, Tag)

    def test_value_box_with_showcase_icon(self):
        """Test value_box with showcase as icon."""
        from htmltools import Tag

        icon = Tag("i", class_="fa fa-dollar")
        result = value_box("Revenue", "$1,000", showcase=icon)
        assert isinstance(result, Tag)


class TestValueBoxExported:
    """Tests for value_box functions export."""

    def test_value_box_in_ui(self):
        """Test value_box is in ui module."""
        from shiny import ui

        assert hasattr(ui, "value_box")

    def test_showcase_layout_in_ui(self):
        """Test showcase_left_center is in ui module."""
        from shiny import ui

        assert hasattr(ui, "showcase_left_center")
