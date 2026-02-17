"""Tests for shiny/ui/css/_css_unit.py module."""

from shiny.ui.css._css_unit import as_css_padding, as_css_unit


class TestAsCssUnit:
    """Tests for as_css_unit function."""

    def test_as_css_unit_is_callable(self):
        """Test as_css_unit is callable."""
        assert callable(as_css_unit)

    def test_as_css_unit_with_px(self):
        """Test as_css_unit with px value."""
        result = as_css_unit("100px")
        assert result == "100px"

    def test_as_css_unit_with_percent(self):
        """Test as_css_unit with percent value."""
        result = as_css_unit("50%")
        assert result == "50%"

    def test_as_css_unit_with_number(self):
        """Test as_css_unit with number value."""
        result = as_css_unit(100)
        assert "100" in result

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
        result = as_css_padding("10px")
        assert result is not None

    def test_as_css_padding_with_none(self):
        """Test as_css_padding with None."""
        result = as_css_padding(None)
        assert result is None
