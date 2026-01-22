"""Tests for shiny/ui/_input_numeric.py - Numeric input."""

from htmltools import Tag

from shiny.ui import input_numeric


class TestInputNumeric:
    """Tests for input_numeric function."""

    def test_input_numeric_returns_tag(self):
        """Test input_numeric returns a Tag."""
        result = input_numeric("num_id", "Enter a number", 0)
        assert isinstance(result, Tag)

    def test_input_numeric_has_correct_id(self):
        """Test input_numeric has correct id."""
        result = input_numeric("num_id", "Enter a number", 0)
        html = str(result)
        assert "num_id" in html

    def test_input_numeric_has_label(self):
        """Test input_numeric has label."""
        result = input_numeric("num_id", "Enter a number", 0)
        html = str(result)
        assert "Enter a number" in html

    def test_input_numeric_has_value(self):
        """Test input_numeric has initial value."""
        result = input_numeric("num_id", "Number", 42)
        html = str(result)
        assert 'value="42"' in html

    def test_input_numeric_has_type_number(self):
        """Test input_numeric has type=number."""
        result = input_numeric("num_id", "Number", 0)
        html = str(result)
        assert 'type="number"' in html

    def test_input_numeric_with_min(self):
        """Test input_numeric with min parameter."""
        result = input_numeric("num_id", "Number", 5, min=0)
        html = str(result)
        assert 'min="0"' in html

    def test_input_numeric_with_max(self):
        """Test input_numeric with max parameter."""
        result = input_numeric("num_id", "Number", 5, max=100)
        html = str(result)
        assert 'max="100"' in html

    def test_input_numeric_with_step(self):
        """Test input_numeric with step parameter."""
        result = input_numeric("num_id", "Number", 5, step=0.5)
        html = str(result)
        assert 'step="0.5"' in html

    def test_input_numeric_with_width(self):
        """Test input_numeric with width."""
        result = input_numeric("num_id", "Number", 0, width="200px")
        html = str(result)
        assert "200px" in html

    def test_input_numeric_float_value(self):
        """Test input_numeric with float value."""
        result = input_numeric("num_id", "Number", 3.14)
        html = str(result)
        assert "3.14" in html


class TestInputNumericAll:
    """Tests for __all__ exports."""

    def test_input_numeric_in_all(self):
        """Test input_numeric is in __all__."""
        from shiny.ui._input_numeric import __all__

        assert "input_numeric" in __all__
