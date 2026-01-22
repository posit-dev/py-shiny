"""Tests for shiny/ui/_input_numeric.py module."""

from shiny.ui._input_numeric import input_numeric


class TestInputNumeric:
    """Tests for input_numeric function."""

    def test_input_numeric_is_callable(self):
        """Test input_numeric is callable."""
        assert callable(input_numeric)

    def test_input_numeric_returns_tag(self):
        """Test input_numeric returns a Tag."""
        from htmltools import Tag

        result = input_numeric("my_numeric", "Enter number", value=0)
        assert isinstance(result, Tag)

    def test_input_numeric_with_min_max(self):
        """Test input_numeric with min and max parameters."""
        from htmltools import Tag

        result = input_numeric("my_numeric", "Enter number", value=50, min=0, max=100)
        assert isinstance(result, Tag)

    def test_input_numeric_with_step(self):
        """Test input_numeric with step parameter."""
        from htmltools import Tag

        result = input_numeric("my_numeric", "Enter number", value=0, step=0.1)
        assert isinstance(result, Tag)


class TestInputNumericExported:
    """Tests for numeric input functions export."""

    def test_input_numeric_in_ui(self):
        """Test input_numeric is in ui module."""
        from shiny import ui

        assert hasattr(ui, "input_numeric")
