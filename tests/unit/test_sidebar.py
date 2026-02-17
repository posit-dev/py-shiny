"""Unit tests for shiny.ui._sidebar module."""

from __future__ import annotations

import pytest
from htmltools import tags

from shiny.ui import layout_sidebar, sidebar
from shiny.ui._sidebar import Sidebar, SidebarOpen


class TestSidebarOpen:
    """Tests for SidebarOpen class."""

    def test_default_values(self) -> None:
        """Test SidebarOpen default values."""
        so = SidebarOpen()
        assert so.desktop == "open"
        assert so.mobile == "closed"

    def test_custom_values(self) -> None:
        """Test SidebarOpen with custom values."""
        so = SidebarOpen(desktop="closed", mobile="open")
        assert so.desktop == "closed"
        assert so.mobile == "open"

    def test_always_values(self) -> None:
        """Test SidebarOpen with always values."""
        so = SidebarOpen(desktop="always", mobile="always")
        assert so.desktop == "always"
        assert so.mobile == "always"

    def test_always_above_mobile(self) -> None:
        """Test SidebarOpen with always-above for mobile."""
        so = SidebarOpen(desktop="open", mobile="always-above")
        assert so.mobile == "always-above"

    def test_invalid_desktop_value(self) -> None:
        """Test SidebarOpen with invalid desktop value."""
        with pytest.raises(ValueError):
            SidebarOpen(desktop="invalid")  # type: ignore

    def test_invalid_mobile_value(self) -> None:
        """Test SidebarOpen with invalid mobile value."""
        with pytest.raises(ValueError):
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

    def test_from_string_open(self) -> None:
        """Test _from_string with 'open'."""
        so = SidebarOpen._from_string("open")
        assert so.desktop == "open"
        assert so.mobile == "open"

    def test_from_string_closed(self) -> None:
        """Test _from_string with 'closed'."""
        so = SidebarOpen._from_string("closed")
        assert so.desktop == "closed"
        assert so.mobile == "closed"

    def test_from_string_always(self) -> None:
        """Test _from_string with 'always'."""
        so = SidebarOpen._from_string("always")
        assert so.desktop == "always"
        assert so.mobile == "always"

    def test_from_string_desktop(self) -> None:
        """Test _from_string with 'desktop'."""
        so = SidebarOpen._from_string("desktop")
        assert so.desktop == "open"
        assert so.mobile == "closed"

    def test_from_string_invalid(self) -> None:
        """Test _from_string with invalid value."""
        with pytest.raises(ValueError):
            SidebarOpen._from_string("invalid")


class TestSidebar:
    """Tests for sidebar function."""

    def test_basic_sidebar(self) -> None:
        """Test basic sidebar creation."""
        sb = sidebar("Content")
        assert isinstance(sb, Sidebar)

    def test_sidebar_with_id(self) -> None:
        """Test sidebar with id."""
        sb = sidebar("Content", id="my_sidebar")
        assert sb.id == "my_sidebar"

    def test_sidebar_with_title(self) -> None:
        """Test sidebar with title."""
        sb = sidebar("Content", title="My Sidebar")
        assert sb.title is not None

    def test_sidebar_with_width(self) -> None:
        """Test sidebar with custom width."""
        sb = sidebar("Content", width="300px")
        assert sb.width == "300px"

    def test_sidebar_with_position_left(self) -> None:
        """Test sidebar with left position."""
        sb = sidebar("Content", position="left")
        assert sb.position == "left"

    def test_sidebar_with_position_right(self) -> None:
        """Test sidebar with right position."""
        sb = sidebar("Content", position="right")
        assert sb.position == "right"

    def test_sidebar_open_string(self) -> None:
        """Test sidebar with open as string."""
        sb = sidebar("Content", open="open")
        assert sb.open().desktop == "open"

    def test_sidebar_open_closed(self) -> None:
        """Test sidebar with open='closed'."""
        sb = sidebar("Content", open="closed")
        assert sb.open().desktop == "closed"
        assert sb.open().mobile == "closed"

    def test_sidebar_open_always(self) -> None:
        """Test sidebar with open='always'."""
        sb = sidebar("Content", open="always")
        assert sb.open().desktop == "always"
        assert sb.open().mobile == "always"

    def test_sidebar_open_dict(self) -> None:
        """Test sidebar with open as dict."""
        sb = sidebar("Content", open={"desktop": "open", "mobile": "closed"})
        assert sb.open().desktop == "open"
        assert sb.open().mobile == "closed"

    def test_sidebar_colors(self) -> None:
        """Test sidebar with colors."""
        sb = sidebar("Content", bg="white", fg="black")
        assert sb.color["bg"] == "white"
        assert sb.color["fg"] == "black"

    def test_sidebar_class(self) -> None:
        """Test sidebar with custom class."""
        sb = sidebar("Content", class_="custom-sidebar")
        assert sb.class_ == "custom-sidebar"

    def test_sidebar_gap(self) -> None:
        """Test sidebar with gap."""
        sb = sidebar("Content", gap="10px")
        assert sb.gap == "10px"

    def test_sidebar_padding(self) -> None:
        """Test sidebar with padding."""
        sb = sidebar("Content", padding="20px")
        assert sb.padding == "20px"

    def test_sidebar_fillable(self) -> None:
        """Test sidebar with fillable."""
        sb = sidebar("Content", fillable=True)
        assert sb.fillable is True


class TestLayoutSidebar:
    """Tests for layout_sidebar function."""

    def test_basic_layout_sidebar(self) -> None:
        """Test basic layout_sidebar creation."""
        sb = sidebar("Sidebar content")
        result = layout_sidebar(sb, "Main content")
        # layout_sidebar returns a CardItem which needs to be resolved
        html = str(result.resolve())
        assert "sidebar" in html.lower()

    def test_layout_sidebar_html(self) -> None:
        """Test layout_sidebar HTML output."""
        sb = sidebar("Sidebar content")
        result = layout_sidebar(sb, "Main content")
        html = str(result.resolve())
        assert "sidebar" in html.lower()
        assert "Main content" in html

    def test_layout_sidebar_with_fillable(self) -> None:
        """Test layout_sidebar with fillable."""
        sb = sidebar("Sidebar")
        result = layout_sidebar(sb, "Main", fillable=True)
        html = str(result.resolve())
        assert "sidebar" in html.lower()

    def test_layout_sidebar_with_fill(self) -> None:
        """Test layout_sidebar with fill."""
        sb = sidebar("Sidebar")
        result = layout_sidebar(sb, "Main", fill=True)
        html = str(result.resolve())
        assert "sidebar" in html.lower()

    def test_layout_sidebar_with_gap(self) -> None:
        """Test layout_sidebar with gap."""
        sb = sidebar("Sidebar")
        result = layout_sidebar(sb, "Main", gap="20px")
        html = str(result.resolve())
        assert "20px" in html

    def test_layout_sidebar_with_padding(self) -> None:
        """Test layout_sidebar with padding."""
        sb = sidebar("Sidebar")
        result = layout_sidebar(sb, "Main", padding="15px")
        html = str(result.resolve())
        assert "15px" in html

    def test_layout_sidebar_with_height(self) -> None:
        """Test layout_sidebar with height."""
        sb = sidebar("Sidebar")
        result = layout_sidebar(sb, "Main", height="500px")
        html = str(result.resolve())
        assert "500px" in html

    def test_layout_sidebar_multiple_content(self) -> None:
        """Test layout_sidebar with multiple content items."""
        sb = sidebar("Sidebar")
        result = layout_sidebar(
            sb,
            tags.p("First paragraph"),
            tags.p("Second paragraph"),
        )
        html = str(result.resolve())
        assert "First paragraph" in html
        assert "Second paragraph" in html
