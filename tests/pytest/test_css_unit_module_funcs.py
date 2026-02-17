"""Tests for shiny.ui.css._css_unit module."""

from shiny.ui.css._css_unit import (
    as_css_padding,
    as_css_unit,
    as_grid_unit,
    isinstance_cssunit,
)


class TestAsCssUnit:
    """Tests for as_css_unit function."""

    def test_as_css_unit_with_none(self):
        """as_css_unit with None should return None."""
        result = as_css_unit(None)
        assert result is None

    def test_as_css_unit_with_zero_int(self):
        """as_css_unit with 0 should return '0'."""
        result = as_css_unit(0)
        assert result == "0"

    def test_as_css_unit_with_zero_float(self):
        """as_css_unit with 0.0 should return '0'."""
        result = as_css_unit(0.0)
        assert result == "0"

    def test_as_css_unit_with_int(self):
        """as_css_unit with int should return px value."""
        result = as_css_unit(300)
        assert "px" in result
        assert "300" in result

    def test_as_css_unit_with_float(self):
        """as_css_unit with float should return px value."""
        result = as_css_unit(300.5)
        assert "px" in result
        assert "300" in result

    def test_as_css_unit_with_string(self):
        """as_css_unit with string should return as-is."""
        result = as_css_unit("1em")
        assert result == "1em"

    def test_as_css_unit_with_percentage_string(self):
        """as_css_unit with percentage string should return as-is."""
        result = as_css_unit("50%")
        assert result == "50%"

    def test_as_css_unit_with_rem(self):
        """as_css_unit with rem should return as-is."""
        result = as_css_unit("2rem")
        assert result == "2rem"


class TestAsCssPadding:
    """Tests for as_css_padding function."""

    def test_as_css_padding_with_none(self):
        """as_css_padding with None should return None."""
        result = as_css_padding(None)
        assert result is None

    def test_as_css_padding_with_single_value(self):
        """as_css_padding with single value should return string."""
        result = as_css_padding(10)
        assert "px" in result

    def test_as_css_padding_with_single_string(self):
        """as_css_padding with single string should return that string."""
        result = as_css_padding("1em")
        assert result == "1em"

    def test_as_css_padding_with_list(self):
        """as_css_padding with list should return space-separated values."""
        result = as_css_padding([0, "1em"])
        assert "0" in result
        assert "1em" in result
        assert " " in result

    def test_as_css_padding_with_four_values(self):
        """as_css_padding with four values should return all four."""
        result = as_css_padding([10, 20, 30, 40])
        # Should have 4 values separated by spaces
        parts = result.split()
        assert len(parts) == 4


class TestIsinstanceCssunit:
    """Tests for isinstance_cssunit function."""

    def test_isinstance_cssunit_with_int(self):
        """isinstance_cssunit should return True for int."""
        assert isinstance_cssunit(10) is True

    def test_isinstance_cssunit_with_float(self):
        """isinstance_cssunit should return True for float."""
        assert isinstance_cssunit(10.5) is True

    def test_isinstance_cssunit_with_string(self):
        """isinstance_cssunit should return True for string."""
        assert isinstance_cssunit("10px") is True

    def test_isinstance_cssunit_with_none(self):
        """isinstance_cssunit should return False for None."""
        assert isinstance_cssunit(None) is False

    def test_isinstance_cssunit_with_list(self):
        """isinstance_cssunit should return False for list."""
        assert isinstance_cssunit([10, 20]) is False

    def test_isinstance_cssunit_with_dict(self):
        """isinstance_cssunit should return False for dict."""
        assert isinstance_cssunit({"width": 10}) is False


class TestAsGridUnit:
    """Tests for as_grid_unit function."""

    def test_as_grid_unit_with_none(self):
        """as_grid_unit with None should return None."""
        result = as_grid_unit(None)
        assert result is None

    def test_as_grid_unit_with_int(self):
        """as_grid_unit with int should return px value."""
        result = as_grid_unit(100)
        assert "px" in result

    def test_as_grid_unit_with_auto(self):
        """as_grid_unit with 'auto' should return 'auto'."""
        result = as_grid_unit("auto")
        assert result == "auto"

    def test_as_grid_unit_with_auto_uppercase(self):
        """as_grid_unit with 'AUTO' should return 'auto' (lowercase)."""
        result = as_grid_unit("AUTO")
        assert result == "auto"

    def test_as_grid_unit_with_min_content(self):
        """as_grid_unit with 'min-content' should return 'min-content'."""
        result = as_grid_unit("min-content")
        assert result == "min-content"

    def test_as_grid_unit_with_max_content(self):
        """as_grid_unit with 'max-content' should return 'max-content'."""
        result = as_grid_unit("max-content")
        assert result == "max-content"

    def test_as_grid_unit_with_minmax(self):
        """as_grid_unit with minmax() should return as-is."""
        result = as_grid_unit("minmax(100px, 1fr)")
        assert result == "minmax(100px, 1fr)"

    def test_as_grid_unit_with_fr_unit(self):
        """as_grid_unit with fr unit should process correctly."""
        result = as_grid_unit("1fr")
        # fr units should be returned as-is or processed
        assert "fr" in result or "px" in result

    def test_as_grid_unit_with_percentage(self):
        """as_grid_unit with percentage should return as-is."""
        result = as_grid_unit("50%")
        assert result == "50%"
