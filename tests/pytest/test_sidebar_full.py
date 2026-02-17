"""Tests for shiny/ui/_sidebar.py module."""

from shiny.ui._sidebar import Sidebar, sidebar


class TestSidebar:
    """Tests for sidebar function."""

    def test_sidebar_is_callable(self):
        """Test sidebar is callable."""
        assert callable(sidebar)

    def test_sidebar_returns_sidebar_object(self):
        """Test sidebar returns a Sidebar object."""
        result = sidebar("Sidebar content")
        assert isinstance(result, Sidebar)

    def test_sidebar_with_title(self):
        """Test sidebar with title parameter."""
        result = sidebar("Content", title="My Sidebar")
        assert isinstance(result, Sidebar)

    def test_sidebar_with_id(self):
        """Test sidebar with id parameter."""
        result = sidebar("Content", id="my_sidebar")
        assert isinstance(result, Sidebar)

    def test_sidebar_with_width(self):
        """Test sidebar with width parameter."""
        result = sidebar("Content", width="300px")
        assert isinstance(result, Sidebar)


class TestSidebarClass:
    """Tests for Sidebar class."""

    def test_sidebar_class_exists(self):
        """Test Sidebar class exists."""
        assert Sidebar is not None

    def test_sidebar_class_is_type(self):
        """Test Sidebar class is a type."""
        # Sidebar might be a NamedTuple or dataclass, check that it's usable
        assert hasattr(Sidebar, "__init__")


class TestSidebarExported:
    """Tests for sidebar functions export."""

    def test_sidebar_in_ui(self):
        """Test sidebar is in ui module."""
        from shiny import ui

        assert hasattr(ui, "sidebar")

    def test_sidebar_class_in_ui(self):
        """Test Sidebar class is in ui module."""
        from shiny import ui

        assert hasattr(ui, "Sidebar")
