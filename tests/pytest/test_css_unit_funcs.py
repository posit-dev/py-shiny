"""Tests for shiny.ui.css._css_unit module."""

from shiny.ui.css._css_unit import CssUnit, as_css_padding, as_css_unit


class TestAsCssUnit:
    """Tests for as_css_unit function."""

    def test_as_css_unit_none(self) -> None:
        """Test as_css_unit with None."""
        result = as_css_unit(None)
        assert result is None

    def test_as_css_unit_string(self) -> None:
        """Test as_css_unit with string."""
        result = as_css_unit("100px")
        assert result == "100px"

    def test_as_css_unit_int(self) -> None:
        """Test as_css_unit with int."""
        result = as_css_unit(100)
        # Returns format like "100.000000px"
        assert result is not None
        assert result.endswith("px")
        assert "100" in result

    def test_as_css_unit_float(self) -> None:
        """Test as_css_unit with float."""
        result = as_css_unit(50.5)
        # Returns format like "50.500000px"
        assert result is not None
        assert result.endswith("px")
        assert "50" in result

    def test_as_css_unit_zero(self) -> None:
        """Test as_css_unit with zero."""
        result = as_css_unit(0)
        assert result == "0"

    def test_as_css_unit_with_percent(self) -> None:
        """Test as_css_unit with percent string."""
        result = as_css_unit("50%")
        assert result == "50%"

    def test_as_css_unit_with_rem(self) -> None:
        """Test as_css_unit with rem string."""
        result = as_css_unit("2rem")
        assert result == "2rem"

    def test_as_css_unit_with_em(self) -> None:
        """Test as_css_unit with em string."""
        result = as_css_unit("1.5em")
        assert result == "1.5em"


class TestAsCssPadding:
    """Tests for as_css_padding function."""

    def test_as_css_padding_none(self) -> None:
        """Test as_css_padding with None."""
        result = as_css_padding(None)
        assert result is None

    def test_as_css_padding_string(self) -> None:
        """Test as_css_padding with string."""
        result = as_css_padding("10px")
        assert result == "10px"

    def test_as_css_padding_int(self) -> None:
        """Test as_css_padding with int."""
        result = as_css_padding(10)
        # Returns format like "10.000000px"
        assert result is not None
        assert result.endswith("px")
        assert "10" in result

    def test_as_css_padding_list_one(self) -> None:
        """Test as_css_padding with single value list."""
        result = as_css_padding([10])
        # Returns format like "10.000000px"
        assert result is not None
        assert result.endswith("px")
        assert "10" in result

    def test_as_css_padding_list_two(self) -> None:
        """Test as_css_padding with two value list."""
        result = as_css_padding([10, 20])
        # Returns format like "10.000000px 20.000000px"
        assert result is not None
        parts = result.split()
        assert len(parts) == 2
        assert all(p.endswith("px") for p in parts)

    def test_as_css_padding_list_three(self) -> None:
        """Test as_css_padding with three value list."""
        result = as_css_padding([10, 20, 30])
        # Returns format like "10.000000px 20.000000px 30.000000px"
        assert result is not None
        parts = result.split()
        assert len(parts) == 3
        assert all(p.endswith("px") for p in parts)

    def test_as_css_padding_list_four(self) -> None:
        """Test as_css_padding with four value list."""
        result = as_css_padding([10, 20, 30, 40])
        # Returns format like "10.000000px 20.000000px 30.000000px 40.000000px"
        assert result is not None
        parts = result.split()
        assert len(parts) == 4
        assert all(p.endswith("px") for p in parts)

    def test_as_css_padding_list_strings(self) -> None:
        """Test as_css_padding with list of strings."""
        result = as_css_padding(["1rem", "2rem"])
        assert result == "1rem 2rem"


class TestCssUnitType:
    """Tests for CssUnit type."""

    def test_css_unit_accepts_string(self) -> None:
        """Test CssUnit type accepts string."""
        value: CssUnit = "100px"
        assert as_css_unit(value) == "100px"

    def test_css_unit_accepts_int(self) -> None:
        """Test CssUnit type accepts int."""
        value: CssUnit = 100
        result = as_css_unit(value)
        assert result is not None
        assert result.endswith("px")
        assert "100" in result

    def test_css_unit_accepts_float(self) -> None:
        """Test CssUnit type accepts float."""
        value: CssUnit = 50.5
        result = as_css_unit(value)
        assert result is not None
        assert result.endswith("px")
        assert "50" in result
