"""Tests for shiny/ui/_layout.py module."""

from shiny.ui._layout import layout_column_wrap
from shiny.ui._layout_columns import layout_columns
from shiny.ui._sidebar import layout_sidebar


class TestLayoutSidebar:
    """Tests for layout_sidebar function."""

    def test_layout_sidebar_is_callable(self):
        """Test layout_sidebar is callable."""
        assert callable(layout_sidebar)

    def test_layout_sidebar_returns_card_item(self):
        """Test layout_sidebar returns a CardItem object."""
        from shiny import ui
        from shiny.ui._card import CardItem

        sidebar = ui.sidebar("Sidebar content")
        result = layout_sidebar(sidebar, "Main content")
        assert isinstance(result, CardItem)


class TestLayoutColumnWrap:
    """Tests for layout_column_wrap function."""

    def test_layout_column_wrap_is_callable(self):
        """Test layout_column_wrap is callable."""
        assert callable(layout_column_wrap)

    def test_layout_column_wrap_returns_tag(self):
        """Test layout_column_wrap returns a Tag."""
        from htmltools import Tag

        result = layout_column_wrap("Content 1", "Content 2", "Content 3")
        assert isinstance(result, Tag)

    def test_layout_column_wrap_with_width(self):
        """Test layout_column_wrap with width parameter."""
        from htmltools import Tag

        result = layout_column_wrap("Content 1", "Content 2", width=1 / 2)
        assert isinstance(result, Tag)


class TestLayoutColumns:
    """Tests for layout_columns function."""

    def test_layout_columns_is_callable(self):
        """Test layout_columns is callable."""
        assert callable(layout_columns)

    def test_layout_columns_returns_tag(self):
        """Test layout_columns returns a Tag."""
        from htmltools import Tag

        result = layout_columns("Content 1", "Content 2")
        assert isinstance(result, Tag)


class TestLayoutExported:
    """Tests for layout functions export."""

    def test_layout_sidebar_in_ui(self):
        """Test layout_sidebar is in ui module."""
        from shiny import ui

        assert hasattr(ui, "layout_sidebar")

    def test_layout_column_wrap_in_ui(self):
        """Test layout_column_wrap is in ui module."""
        from shiny import ui

        assert hasattr(ui, "layout_column_wrap")

    def test_layout_columns_in_ui(self):
        """Test layout_columns is in ui module."""
        from shiny import ui

        assert hasattr(ui, "layout_columns")
