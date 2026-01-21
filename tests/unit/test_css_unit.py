"""Tests for shiny/ui/css/_css_unit.py"""

from shiny.ui.css import as_css_padding, as_css_unit


class TestAsCssUnit:
    """Tests for the as_css_unit function."""

    def test_as_css_unit_none(self):
        """Test as_css_unit with None."""
        result = as_css_unit(None)
        assert result is None

    def test_as_css_unit_zero(self):
        """Test as_css_unit with zero."""
        result = as_css_unit(0)
        assert result == "0"

    def test_as_css_unit_zero_float(self):
        """Test as_css_unit with zero float."""
        result = as_css_unit(0.0)
        assert result == "0"

    def test_as_css_unit_integer(self):
        """Test as_css_unit with integer."""
        result = as_css_unit(300)
        assert result is not None
        assert "300" in result
        assert "px" in result

    def test_as_css_unit_float(self):
        """Test as_css_unit with float."""
        result = as_css_unit(10.5)
        assert result is not None
        assert "px" in result

    def test_as_css_unit_string(self):
        """Test as_css_unit with string (passes through)."""
        result = as_css_unit("1em")
        assert result == "1em"

    def test_as_css_unit_percentage_string(self):
        """Test as_css_unit with percentage string."""
        result = as_css_unit("50%")
        assert result == "50%"

    def test_as_css_unit_px_string(self):
        """Test as_css_unit with px string."""
        result = as_css_unit("100px")
        assert result == "100px"


class TestAsCssPadding:
    """Tests for the as_css_padding function."""

    def test_as_css_padding_none(self):
        """Test as_css_padding with None."""
        result = as_css_padding(None)
        assert result is None

    def test_as_css_padding_single_int(self):
        """Test as_css_padding with single integer."""
        result = as_css_padding(10)
        assert result is not None
        assert "px" in result

    def test_as_css_padding_single_string(self):
        """Test as_css_padding with single string."""
        result = as_css_padding("1em")
        assert result == "1em"

    def test_as_css_padding_list_one(self):
        """Test as_css_padding with single element list."""
        result = as_css_padding([10])
        assert result is not None
        assert "px" in result

    def test_as_css_padding_list_two(self):
        """Test as_css_padding with two element list (top/bottom, left/right)."""
        result = as_css_padding([10, 20])
        assert result is not None

    def test_as_css_padding_list_three(self):
        """Test as_css_padding with three element list (top, left/right, bottom)."""
        result = as_css_padding([10, 20, 30])
        assert result is not None

    def test_as_css_padding_list_four(self):
        """Test as_css_padding with four element list (top, right, bottom, left)."""
        result = as_css_padding([10, 20, 30, 40])
        assert result is not None

    def test_as_css_padding_list_strings(self):
        """Test as_css_padding with string list."""
        result = as_css_padding(["1em", "2em"])
        assert result is not None
        assert "1em" in result
        assert "2em" in result

    def test_as_css_padding_mixed_list(self):
        """Test as_css_padding with mixed types in list."""
        result = as_css_padding([10, "1em"])
        assert result is not None
        assert "px" in result
        assert "1em" in result
