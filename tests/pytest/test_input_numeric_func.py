"""Tests for shiny.ui._input_numeric module."""

from shiny.ui import input_numeric


class TestInputNumeric:
    """Tests for the input_numeric function."""

    def test_basic_numeric(self):
        """Test creating a basic numeric input."""
        result = input_numeric("num1", "Number:", 10)
        html = str(result)

        assert 'id="num1"' in html
        assert "Number:" in html
        assert 'type="number"' in html
        assert 'value="10"' in html
        assert "shiny-input-number" in html
        assert "form-control" in html

    def test_numeric_with_min(self):
        """Test numeric input with min value."""
        result = input_numeric("num2", "Number:", 50, min=0)
        html = str(result)

        assert 'min="0"' in html

    def test_numeric_with_max(self):
        """Test numeric input with max value."""
        result = input_numeric("num3", "Number:", 50, max=100)
        html = str(result)

        assert 'max="100"' in html

    def test_numeric_with_min_max(self):
        """Test numeric input with both min and max."""
        result = input_numeric("num4", "Number:", 50, min=0, max=100)
        html = str(result)

        assert 'min="0"' in html
        assert 'max="100"' in html

    def test_numeric_with_step(self):
        """Test numeric input with step value."""
        result = input_numeric("num5", "Number:", 0, step=0.1)
        html = str(result)

        assert 'step="0.1"' in html

    def test_numeric_with_step_integer(self):
        """Test numeric input with integer step."""
        result = input_numeric("num6", "Number:", 0, step=5)
        html = str(result)

        assert 'step="5"' in html

    def test_numeric_with_width(self):
        """Test numeric input with custom width."""
        result = input_numeric("num7", "Number:", 0, width="200px")
        html = str(result)

        assert "200px" in html

    def test_numeric_with_float_value(self):
        """Test numeric input with float value."""
        result = input_numeric("num8", "Number:", 3.14)
        html = str(result)

        assert 'value="3.14"' in html

    def test_numeric_with_negative_value(self):
        """Test numeric input with negative value."""
        result = input_numeric("num9", "Number:", -10)
        html = str(result)

        assert 'value="-10"' in html

    def test_numeric_with_update_on_change(self):
        """Test numeric input with update_on=change."""
        result = input_numeric("num10", "Number:", 0, update_on="change")
        html = str(result)

        assert 'data-update-on="change"' in html

    def test_numeric_with_update_on_blur(self):
        """Test numeric input with update_on=blur."""
        result = input_numeric("num11", "Number:", 0, update_on="blur")
        html = str(result)

        assert 'data-update-on="blur"' in html

    def test_numeric_with_all_options(self):
        """Test numeric input with all options."""
        result = input_numeric(
            "num12",
            "Complete Input:",
            value=50,
            min=0,
            max=100,
            step=5,
            width="300px",
            update_on="blur",
        )
        html = str(result)

        assert 'id="num12"' in html
        assert 'value="50"' in html
        assert 'min="0"' in html
        assert 'max="100"' in html
        assert 'step="5"' in html
        assert "300px" in html
        assert 'data-update-on="blur"' in html

    def test_numeric_zero_value(self):
        """Test numeric input with zero value."""
        result = input_numeric("num13", "Zero:", 0)
        html = str(result)

        assert 'value="0"' in html

    def test_numeric_with_decimal_step(self):
        """Test numeric input with decimal step."""
        result = input_numeric("num14", "Decimal:", 0.5, step=0.01)
        html = str(result)

        assert 'step="0.01"' in html
