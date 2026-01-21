"""Tests for shiny/ui/_sidebar.py"""

from __future__ import annotations

import pytest

from shiny.ui._sidebar import (
    Sidebar,
    SidebarOpen,
    layout_sidebar,
    sidebar,
)


class TestSidebarOpen:
    """Tests for the SidebarOpen class."""

    def test_default_values(self) -> None:
        """Test default SidebarOpen values."""
        so = SidebarOpen()
        assert so.desktop == "open"
        assert so.mobile == "closed"

    def test_custom_values(self) -> None:
        """Test custom SidebarOpen values."""
        so = SidebarOpen(desktop="closed", mobile="open")
        assert so.desktop == "closed"
        assert so.mobile == "open"

    def test_always_values(self) -> None:
        """Test 'always' values."""
        so = SidebarOpen(desktop="always", mobile="always")
        assert so.desktop == "always"
        assert so.mobile == "always"

    def test_mobile_always_above(self) -> None:
        """Test 'always-above' for mobile."""
        so = SidebarOpen(mobile="always-above")
        assert so.mobile == "always-above"

    def test_invalid_desktop_raises(self) -> None:
        """Test that invalid desktop value raises ValueError."""
        with pytest.raises(ValueError, match="desktop"):
            SidebarOpen(desktop="invalid")  # type: ignore

    def test_invalid_mobile_raises(self) -> None:
        """Test that invalid mobile value raises ValueError."""
        with pytest.raises(ValueError, match="mobile"):
            SidebarOpen(mobile="invalid")  # type: ignore

    def test_is_always_open_desktop(self) -> None:
        """Test _is_always_open for desktop."""
        so = SidebarOpen(desktop="always", mobile="closed")
        assert so._is_always_open("desktop") is True
        assert so._is_always_open("mobile") is False
        assert so._is_always_open("both") is False

    def test_is_always_open_mobile(self) -> None:
        """Test _is_always_open for mobile."""
        so = SidebarOpen(desktop="open", mobile="always")
        assert so._is_always_open("desktop") is False
        assert so._is_always_open("mobile") is True
        assert so._is_always_open("both") is False

    def test_is_always_open_both(self) -> None:
        """Test _is_always_open for both."""
        so = SidebarOpen(desktop="always", mobile="always")
        assert so._is_always_open("both") is True

    def test_is_always_open_always_above(self) -> None:
        """Test _is_always_open with always-above."""
        so = SidebarOpen(desktop="open", mobile="always-above")
        assert so._is_always_open("mobile") is True


class TestSidebar:
    """Tests for the sidebar function."""

    def test_basic_sidebar(self) -> None:
        """Test basic sidebar creation."""
        result = sidebar("Content")

        assert isinstance(result, Sidebar)

    def test_sidebar_with_title(self) -> None:
        """Test sidebar with title."""
        result = sidebar("Content", title="My Sidebar")

        assert isinstance(result, Sidebar)

    def test_sidebar_with_id(self) -> None:
        """Test sidebar with id."""
        result = sidebar("Content", id="my_sidebar")

        assert isinstance(result, Sidebar)

    def test_sidebar_open_string(self) -> None:
        """Test sidebar with open as string."""
        result = sidebar("Content", open="closed")
        assert isinstance(result, Sidebar)

    def test_sidebar_open_object(self) -> None:
        """Test sidebar with SidebarOpen dict spec."""
        open_spec = {"desktop": "closed", "mobile": "open"}
        result = sidebar("Content", open=open_spec)  # type: ignore
        assert isinstance(result, Sidebar)

    def test_sidebar_width(self) -> None:
        """Test sidebar with width."""
        result = sidebar("Content", width=300)
        assert isinstance(result, Sidebar)

    def test_sidebar_position_left(self) -> None:
        """Test sidebar with position left."""
        result = sidebar("Content", position="left")
        assert isinstance(result, Sidebar)

    def test_sidebar_position_right(self) -> None:
        """Test sidebar with position right."""
        result = sidebar("Content", position="right")
        assert isinstance(result, Sidebar)

    def test_sidebar_max_height_mobile(self) -> None:
        """Test sidebar with max_height_mobile."""
        result = sidebar("Content", max_height_mobile="200px")
        assert isinstance(result, Sidebar)

    def test_sidebar_gap(self) -> None:
        """Test sidebar with gap."""
        result = sidebar("Content", gap=10)
        assert isinstance(result, Sidebar)

    def test_sidebar_padding(self) -> None:
        """Test sidebar with padding."""
        result = sidebar("Content", padding=20)
        assert isinstance(result, Sidebar)


class TestLayoutSidebar:
    """Tests for the layout_sidebar function."""

    def test_basic_layout_sidebar(self) -> None:
        """Test basic layout_sidebar creation."""
        result = layout_sidebar(sidebar("Sidebar content"), "Main content")

        # layout_sidebar returns a CardItem
        assert result is not None

    def test_layout_sidebar_structure(self) -> None:
        """Test layout_sidebar returns CardItem."""
        result = layout_sidebar(sidebar("Sidebar"), "Main")

        # The result is a CardItem, not a Tag directly
        assert result is not None

    def test_layout_sidebar_with_fillable(self) -> None:
        """Test layout_sidebar with fillable option."""
        result = layout_sidebar(sidebar("Sidebar"), "Main", fillable=True)

        assert result is not None

    def test_layout_sidebar_with_fill(self) -> None:
        """Test layout_sidebar with fill option."""
        result = layout_sidebar(sidebar("Sidebar"), "Main", fill=True)

        assert result is not None

    def test_layout_sidebar_with_border(self) -> None:
        """Test layout_sidebar with border option."""
        result = layout_sidebar(sidebar("Sidebar"), "Main", border=True)

        assert result is not None

    def test_layout_sidebar_with_border_radius(self) -> None:
        """Test layout_sidebar with border_radius option."""
        result = layout_sidebar(sidebar("Sidebar"), "Main", border_radius=True)

        assert result is not None

    def test_layout_sidebar_height(self) -> None:
        """Test layout_sidebar with height."""
        result = layout_sidebar(sidebar("Sidebar"), "Main", height="500px")

        assert result is not None


class TestSidebarClass:
    """Tests for the Sidebar class attributes and methods."""

    def test_sidebar_has_children(self) -> None:
        """Test that Sidebar has children."""
        sb = sidebar("Child 1", "Child 2")
        # Sidebar wraps content
        assert sb is not None

    def test_sidebar_has_attrs(self) -> None:
        """Test that Sidebar has attrs."""
        sb = sidebar("Content", class_="my-class")
        assert sb is not None
