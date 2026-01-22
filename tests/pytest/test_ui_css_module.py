"""Tests for shiny/ui/css/_css_unit.py module."""

from shiny.ui.css._css_unit import (
    as_css_unit,
    as_css_padding,
    CssUnit,
)


class TestCssUnit:
    """Tests for CSS unit type."""

    def test_css_unit_exists(self):
        """Test CssUnit type exists."""
        assert CssUnit is not None


class TestAsCssUnit:
    """Tests for as_css_unit function."""

    def test_as_css_unit_is_callable(self):
        """Test as_css_unit is callable."""
        assert callable(as_css_unit)

    def test_as_css_unit_with_pixel_int(self):
        """Test as_css_unit with integer."""
        result = as_css_unit(10)
        assert "10" in result and "px" in result

    def test_as_css_unit_with_string(self):
        """Test as_css_unit with string."""
        result = as_css_unit("20%")
        assert result == "20%"

    def test_as_css_unit_with_float(self):
        """Test as_css_unit with float."""
        result = as_css_unit(1.5)
        assert "px" in result

    def test_as_css_unit_with_none(self):
        """Test as_css_unit with None."""
        result = as_css_unit(None)
        assert result is None


class TestAsCssPadding:
    """Tests for as_css_padding function."""

    def test_as_css_padding_is_callable(self):
        """Test as_css_padding is callable."""
        assert callable(as_css_padding)

    def test_as_css_padding_with_single_value(self):
        """Test as_css_padding with single value."""
        result = as_css_padding(10)
        assert result is not None

    def test_as_css_padding_with_string(self):
        """Test as_css_padding with string."""
        result = as_css_padding("10px")
        assert result is not None

    def test_as_css_padding_with_none(self):
        """Test as_css_padding with None."""
        result = as_css_padding(None)
        assert result is None
