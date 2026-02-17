"""Tests for shiny/ui/css/_css_unit.py"""

from __future__ import annotations

from shiny.ui.css._css_unit import (
    as_css_padding,
    as_css_unit,
    as_grid_unit,
    isinstance_cssunit,
)


class TestAsCssUnit:
    """Tests for the as_css_unit function."""

    def test_none_returns_none(self) -> None:
        """Test that None returns None."""
        assert as_css_unit(None) is None

    def test_zero_returns_zero_string(self) -> None:
        """Test that 0 returns '0'."""
        assert as_css_unit(0) == "0"
        assert as_css_unit(0.0) == "0"

    def test_integer_returns_pixels(self) -> None:
        """Test that integers return pixel values."""
        result = as_css_unit(100)
        assert result.endswith("px")
        assert "100" in result

    def test_float_returns_pixels(self) -> None:
        """Test that floats return pixel values."""
        result = as_css_unit(100.5)
        assert result.endswith("px")
        assert "100" in result

    def test_string_passes_through(self) -> None:
        """Test that strings pass through unchanged."""
        assert as_css_unit("1em") == "1em"
        assert as_css_unit("50%") == "50%"
        assert as_css_unit("calc(100% - 20px)") == "calc(100% - 20px)"

    def test_negative_integer(self) -> None:
        """Test negative integer values."""
        result = as_css_unit(-10)
        assert result.endswith("px")
        assert "-10" in result


class TestAsCssPadding:
    """Tests for the as_css_padding function."""

    def test_none_returns_none(self) -> None:
        """Test that None returns None."""
        assert as_css_padding(None) is None

    def test_single_value(self) -> None:
        """Test single CSS unit value."""
        assert as_css_padding("1em") == "1em"
        assert "10" in as_css_padding(10)
        assert as_css_padding(0) == "0"

    def test_list_of_values(self) -> None:
        """Test list of CSS unit values."""
        result = as_css_padding(["1em", "2em"])
        assert result == "1em 2em"

    def test_list_with_mixed_types(self) -> None:
        """Test list with mixed types."""
        result = as_css_padding([10, "1em", 0, "2%"])
        assert "1em" in result
        assert "0" in result
        assert "2%" in result
        assert "px" in result

    def test_four_values(self) -> None:
        """Test four-value padding (top, right, bottom, left)."""
        result = as_css_padding(["1em", "2em", "3em", "4em"])
        assert result == "1em 2em 3em 4em"


class TestIsinstanceCssunit:
    """Tests for the isinstance_cssunit function."""

    def test_int_is_cssunit(self) -> None:
        """Test that int is a CssUnit."""
        assert isinstance_cssunit(10) is True

    def test_float_is_cssunit(self) -> None:
        """Test that float is a CssUnit."""
        assert isinstance_cssunit(10.5) is True

    def test_str_is_cssunit(self) -> None:
        """Test that str is a CssUnit."""
        assert isinstance_cssunit("1em") is True

    def test_none_is_not_cssunit(self) -> None:
        """Test that None is not a CssUnit."""
        assert isinstance_cssunit(None) is False

    def test_list_is_not_cssunit(self) -> None:
        """Test that list is not a CssUnit."""
        assert isinstance_cssunit([1, 2]) is False


class TestAsGridUnit:
    """Tests for the as_grid_unit function."""

    def test_none_returns_none(self) -> None:
        """Test that None returns None."""
        assert as_grid_unit(None) is None

    def test_integer_returns_pixels(self) -> None:
        """Test that integers return pixel values."""
        result = as_grid_unit(100)
        assert result is not None
        assert result.endswith("px")

    def test_auto_keyword(self) -> None:
        """Test 'auto' keyword."""
        assert as_grid_unit("auto") == "auto"
        assert as_grid_unit("AUTO") == "auto"
        assert as_grid_unit("Auto") == "auto"

    def test_min_content_keyword(self) -> None:
        """Test 'min-content' keyword."""
        assert as_grid_unit("min-content") == "min-content"
        assert as_grid_unit("MIN-CONTENT") == "min-content"

    def test_max_content_keyword(self) -> None:
        """Test 'max-content' keyword."""
        assert as_grid_unit("max-content") == "max-content"
        assert as_grid_unit("MAX-CONTENT") == "max-content"

    def test_minmax_function(self) -> None:
        """Test minmax() function passthrough."""
        result = as_grid_unit("minmax(100px, 1fr)")
        assert result == "minmax(100px, 1fr)"

    def test_fr_unit(self) -> None:
        """Test fr unit handling."""
        result = as_grid_unit("1fr")
        # fr units get passed through as_css_unit which should return them as-is
        assert result == "1fr"

    def test_regular_css_unit(self) -> None:
        """Test regular CSS unit passthrough."""
        assert as_grid_unit("50%") == "50%"
        assert as_grid_unit("10em") == "10em"
