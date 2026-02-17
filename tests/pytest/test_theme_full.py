"""Tests for shiny/ui/_theme.py module."""

from shiny.ui._theme import Theme


class TestTheme:
    """Tests for Theme class."""

    def test_theme_class_exists(self):
        """Test Theme class exists."""
        assert Theme is not None

    def test_theme_is_callable(self):
        """Test Theme can be instantiated."""
        # Theme should be instantiable
        theme = Theme()
        assert theme is not None

    def test_theme_has_methods(self):
        """Test Theme has expected methods."""
        theme = Theme()
        # Check for common methods
        assert hasattr(theme, "name")


class TestThemeExported:
    """Tests for theme classes export."""

    def test_theme_in_ui(self):
        """Test Theme is in ui module."""
        from shiny import ui

        assert hasattr(ui, "Theme")
