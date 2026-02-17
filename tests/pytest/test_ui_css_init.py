"""Tests for shiny/ui/css/__init__.py - CSS module exports."""

from shiny.ui import css


class TestCssExports:
    """Tests for CSS module exports."""

    def test_cssunit_exported(self):
        """Test CssUnit is exported."""
        assert hasattr(css, "CssUnit")

    def test_as_css_unit_exported(self):
        """Test as_css_unit is exported."""
        assert hasattr(css, "as_css_unit")
        assert callable(css.as_css_unit)

    def test_as_css_padding_exported(self):
        """Test as_css_padding is exported."""
        assert hasattr(css, "as_css_padding")
        assert callable(css.as_css_padding)


class TestCssAll:
    """Tests for __all__ exports."""

    def test_all_is_tuple(self):
        """Test __all__ is a tuple."""
        assert isinstance(css.__all__, tuple)

    def test_all_contains_cssunit(self):
        """Test __all__ contains CssUnit."""
        assert "CssUnit" in css.__all__

    def test_all_contains_as_css_unit(self):
        """Test __all__ contains as_css_unit."""
        assert "as_css_unit" in css.__all__

    def test_all_contains_as_css_padding(self):
        """Test __all__ contains as_css_padding."""
        assert "as_css_padding" in css.__all__
