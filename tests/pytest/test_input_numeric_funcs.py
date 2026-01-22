"""Tests for shiny.ui._input_numeric module."""

from htmltools import Tag

from shiny.ui._input_numeric import input_numeric


class TestInputNumeric:
    """Tests for input_numeric function."""

    def test_input_numeric_basic(self) -> None:
        """Test basic input_numeric creation."""
        result = input_numeric("my_numeric", "Number:", value=0)
        assert isinstance(result, Tag)

    def test_input_numeric_has_id(self) -> None:
        """Test input_numeric has correct id."""
        result = input_numeric("numeric_id", "Label", value=10)
        html = str(result)
        assert "numeric_id" in html

    def test_input_numeric_with_label(self) -> None:
        """Test input_numeric with label."""
        result = input_numeric("numeric", "Enter a number:", value=0)
        html = str(result)
        assert "Enter a number:" in html

    def test_input_numeric_with_value(self) -> None:
        """Test input_numeric with initial value."""
        result = input_numeric("numeric", "Label", value=42)
        html = str(result)
        assert "42" in html

    def test_input_numeric_with_min(self) -> None:
        """Test input_numeric with min parameter."""
        result = input_numeric("numeric", "Label", value=5, min=0)
        html = str(result)
        assert "min" in html

    def test_input_numeric_with_max(self) -> None:
        """Test input_numeric with max parameter."""
        result = input_numeric("numeric", "Label", value=5, max=100)
        html = str(result)
        assert "max" in html

    def test_input_numeric_with_step(self) -> None:
        """Test input_numeric with step parameter."""
        result = input_numeric("numeric", "Label", value=0, step=0.1)
        html = str(result)
        assert "step" in html

    def test_input_numeric_with_width(self) -> None:
        """Test input_numeric with width parameter."""
        result = input_numeric("numeric", "Label", value=0, width="150px")
        html = str(result)
        assert "numeric" in html

    def test_input_numeric_float_value(self) -> None:
        """Test input_numeric with float value."""
        result = input_numeric("numeric", "Label", value=3.14)
        html = str(result)
        assert "3.14" in html

    def test_input_numeric_negative_value(self) -> None:
        """Test input_numeric with negative value."""
        result = input_numeric("numeric", "Label", value=-10)
        html = str(result)
        assert "-10" in html

    def test_input_numeric_type_attribute(self) -> None:
        """Test input_numeric has type=number."""
        result = input_numeric("numeric", "Label", value=0)
        html = str(result)
        assert 'type="number"' in html
