"""Tests for shiny/ui/_page.py module."""

from shiny.ui._page import (
    page_auto,
    page_bootstrap,
    page_fillable,
    page_fixed,
    page_fluid,
    page_navbar,
    page_sidebar,
)


class TestPageFluid:
    """Tests for page_fluid function."""

    def test_page_fluid_is_callable(self):
        """Test page_fluid is callable."""
        assert callable(page_fluid)

    def test_page_fluid_returns_tag(self):
        """Test page_fluid returns a Tag."""
        from htmltools import Tag

        result = page_fluid("Content")
        assert isinstance(result, Tag)


class TestPageFixed:
    """Tests for page_fixed function."""

    def test_page_fixed_is_callable(self):
        """Test page_fixed is callable."""
        assert callable(page_fixed)


class TestPageFillable:
    """Tests for page_fillable function."""

    def test_page_fillable_is_callable(self):
        """Test page_fillable is callable."""
        assert callable(page_fillable)


class TestPageSidebar:
    """Tests for page_sidebar function."""

    def test_page_sidebar_is_callable(self):
        """Test page_sidebar is callable."""
        assert callable(page_sidebar)


class TestPageBootstrap:
    """Tests for page_bootstrap function."""

    def test_page_bootstrap_is_callable(self):
        """Test page_bootstrap is callable."""
        assert callable(page_bootstrap)


class TestPageAuto:
    """Tests for page_auto function."""

    def test_page_auto_is_callable(self):
        """Test page_auto is callable."""
        assert callable(page_auto)


class TestPageNavbar:
    """Tests for page_navbar function."""

    def test_page_navbar_is_callable(self):
        """Test page_navbar is callable."""
        assert callable(page_navbar)


class TestPageExported:
    """Tests for page functions export."""

    def test_page_fluid_in_ui(self):
        """Test page_fluid is in ui module."""
        from shiny import ui

        assert hasattr(ui, "page_fluid")

    def test_page_navbar_in_ui(self):
        """Test page_navbar is in ui module."""
        from shiny import ui

        assert hasattr(ui, "page_navbar")
