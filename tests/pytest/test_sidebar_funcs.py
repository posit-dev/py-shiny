"""Tests for shiny.ui._sidebar module."""

from shiny.ui._card import CardItem
from shiny.ui._sidebar import layout_sidebar, sidebar


class TestSidebar:
    """Tests for sidebar function."""

    def test_sidebar_basic(self) -> None:
        """Test basic sidebar creation."""
        result = sidebar("Sidebar content")
        assert result is not None

    def test_sidebar_with_content(self) -> None:
        """Test sidebar with content."""
        result = sidebar("My sidebar content")
        assert result is not None

    def test_sidebar_with_id(self) -> None:
        """Test sidebar with id parameter."""
        result = sidebar("Content", id="my_sidebar")
        assert result is not None

    def test_sidebar_with_title(self) -> None:
        """Test sidebar with title parameter."""
        result = sidebar("Content", title="Sidebar Title")
        assert result is not None

    def test_sidebar_with_width(self) -> None:
        """Test sidebar with width parameter."""
        result = sidebar("Content", width="300px")
        assert result is not None

    def test_sidebar_position_left(self) -> None:
        """Test sidebar with position='left'."""
        result = sidebar("Content", position="left")
        assert result is not None

    def test_sidebar_position_right(self) -> None:
        """Test sidebar with position='right'."""
        result = sidebar("Content", position="right")
        assert result is not None

    def test_sidebar_open_desktop(self) -> None:
        """Test sidebar with open='desktop'."""
        result = sidebar("Content", open="desktop")
        assert result is not None

    def test_sidebar_open_always(self) -> None:
        """Test sidebar with open='always'."""
        result = sidebar("Content", open="always")
        assert result is not None

    def test_sidebar_open_closed(self) -> None:
        """Test sidebar with open='closed'."""
        result = sidebar("Content", open="closed")
        assert result is not None

    def test_sidebar_open_open(self) -> None:
        """Test sidebar with open='open'."""
        result = sidebar("Content", open="open")
        assert result is not None


class TestLayoutSidebar:
    """Tests for layout_sidebar function."""

    def test_layout_sidebar_basic(self) -> None:
        """Test basic layout_sidebar creation."""
        result = layout_sidebar(
            sidebar("Sidebar"),
            "Main content",
        )
        assert isinstance(result, CardItem)

    def test_layout_sidebar_with_content(self) -> None:
        """Test layout_sidebar with content."""
        result = layout_sidebar(
            sidebar("Sidebar content"),
            "Main area",
        )
        resolved = result.resolve()
        html = str(resolved)
        assert "Main area" in html

    def test_layout_sidebar_fillable(self) -> None:
        """Test layout_sidebar with fillable parameter."""
        result = layout_sidebar(
            sidebar("Sidebar"),
            "Content",
            fillable=True,
        )
        assert isinstance(result, CardItem)

    def test_layout_sidebar_fill(self) -> None:
        """Test layout_sidebar with fill parameter."""
        result = layout_sidebar(
            sidebar("Sidebar"),
            "Content",
            fill=True,
        )
        assert isinstance(result, CardItem)
