"""Tests for page UI components."""

from shiny.ui import (
    nav_panel,
    page_bootstrap,
    page_fillable,
    page_fixed,
    page_fluid,
    page_navbar,
    page_sidebar,
    sidebar,
)


class TestPageFluid:
    """Tests for the page_fluid function."""

    def test_basic_page_fluid(self):
        """Test creating a basic fluid page."""
        page = page_fluid("Hello World")
        html = str(page)

        assert "Hello World" in html
        assert "container-fluid" in html

    def test_page_fluid_with_title(self):
        """Test fluid page with title."""
        page = page_fluid("Content", title="My Page")
        html = str(page)

        assert "Content" in html


class TestPageFixed:
    """Tests for the page_fixed function."""

    def test_basic_page_fixed(self):
        """Test creating a basic fixed page."""
        page = page_fixed("Hello World")
        html = str(page)

        assert "Hello World" in html
        assert "container" in html


class TestPageFillable:
    """Tests for the page_fillable function."""

    def test_basic_page_fillable(self):
        """Test creating a basic fillable page."""
        page = page_fillable("Fillable content")
        html = str(page)

        assert "Fillable content" in html
        assert "html-fill-container" in html


class TestPageBootstrap:
    """Tests for the page_bootstrap function."""

    def test_basic_page_bootstrap(self):
        """Test creating a basic bootstrap page."""
        page = page_bootstrap("Content")
        html = str(page)

        assert "Content" in html


class TestPageSidebar:
    """Tests for the page_sidebar function."""

    def test_basic_page_sidebar(self):
        """Test creating a basic sidebar page."""
        sb = sidebar("Sidebar content")
        page = page_sidebar(sb, "Main content")
        html = str(page)

        assert "Sidebar content" in html
        assert "Main content" in html


class TestPageNavbar:
    """Tests for the page_navbar function."""

    def test_basic_page_navbar(self):
        """Test creating a basic navbar page."""
        page = page_navbar(
            nav_panel("Tab 1", "Tab 1 content"),
            nav_panel("Tab 2", "Tab 2 content"),
            title="My App",
        )
        html = str(page)

        assert "Tab 1" in html
        assert "Tab 2" in html
        assert "My App" in html

    def test_page_navbar_inverse(self):
        """Test navbar page with inverse styling."""
        page = page_navbar(nav_panel("Tab", "Content"), title="App", inverse=True)
        html = str(page)

        assert "App" in html
