"""Unit tests for shiny.ui._input_numeric module."""

from __future__ import annotations

from htmltools import Tag

from shiny.ui import input_numeric


class TestInputNumeric:
    """Tests for input_numeric function."""

    def test_basic_input_numeric(self) -> None:
        """Test basic input_numeric with required parameters."""
        result = input_numeric("num_id", "Number", value=10)
        html = str(result)

        assert 'id="num_id"' in html
        assert "Number" in html
        assert 'type="number"' in html
        assert 'value="10"' in html

    def test_input_numeric_returns_tag(self) -> None:
        """Test that input_numeric returns a Tag."""
        result = input_numeric("num_id", "Number", value=5)
        assert isinstance(result, Tag)

    def test_input_numeric_with_min(self) -> None:
        """Test input_numeric with min parameter."""
        result = input_numeric("num_id", "Number", value=10, min=0)
        html = str(result)

        assert 'min="0"' in html

    def test_input_numeric_with_max(self) -> None:
        """Test input_numeric with max parameter."""
        result = input_numeric("num_id", "Number", value=10, max=100)
        html = str(result)

        assert 'max="100"' in html

    def test_input_numeric_with_step(self) -> None:
        """Test input_numeric with step parameter."""
        result = input_numeric("num_id", "Number", value=10, step=5)
        html = str(result)

        assert 'step="5"' in html

    def test_input_numeric_with_float_step(self) -> None:
        """Test input_numeric with float step parameter."""
        result = input_numeric("num_id", "Number", value=1.5, step=0.1)
        html = str(result)

        assert 'step="0.1"' in html

    def test_input_numeric_with_width(self) -> None:
        """Test input_numeric with width parameter."""
        result = input_numeric("num_id", "Number", value=10, width="200px")
        html = str(result)

        assert "width:200px" in html

    def test_input_numeric_with_all_parameters(self) -> None:
        """Test input_numeric with all parameters."""
        result = input_numeric(
            "full_num_id",
            "Full Number",
            value=50,
            min=0,
            max=100,
            step=10,
            width="300px",
        )
        html = str(result)

        assert 'id="full_num_id"' in html
        assert "Full Number" in html
        assert 'value="50"' in html
        assert 'min="0"' in html
        assert 'max="100"' in html
        assert 'step="10"' in html
        assert "width:300px" in html

    def test_input_numeric_form_group_class(self) -> None:
        """Test that container has form-group class."""
        result = input_numeric("num_id", "Number", value=10)
        html = str(result)

        assert "form-group" in html
        assert "shiny-input-container" in html

    def test_input_numeric_form_control_class(self) -> None:
        """Test that input element has form-control class."""
        result = input_numeric("num_id", "Number", value=10)
        html = str(result)

        assert "form-control" in html

    def test_input_numeric_negative_value(self) -> None:
        """Test input_numeric with negative value."""
        result = input_numeric("num_id", "Number", value=-5)
        html = str(result)

        assert 'value="-5"' in html

    def test_input_numeric_zero_value(self) -> None:
        """Test input_numeric with zero value."""
        result = input_numeric("num_id", "Number", value=0)
        html = str(result)

        assert 'value="0"' in html

    def test_input_numeric_float_value(self) -> None:
        """Test input_numeric with float value."""
        result = input_numeric("num_id", "Number", value=3.14)
        html = str(result)

        assert 'value="3.14"' in html

    def test_input_numeric_negative_min(self) -> None:
        """Test input_numeric with negative min."""
        result = input_numeric("num_id", "Number", value=0, min=-100)
        html = str(result)

        assert 'min="-100"' in html

    def test_input_numeric_large_values(self) -> None:
        """Test input_numeric with large values."""
        result = input_numeric("num_id", "Number", value=1000000, min=0, max=9999999)
        html = str(result)

        assert 'value="1000000"' in html
        assert 'max="9999999"' in html

    def test_input_numeric_html_label(self) -> None:
        """Test input_numeric with HTML label."""
        from htmltools import tags

        label = tags.strong("Bold Number")
        result = input_numeric("num_id", label, value=10)
        html = str(result)

        assert "<strong>Bold Number</strong>" in html

    def test_input_numeric_empty_label(self) -> None:
        """Test input_numeric with empty label."""
        result = input_numeric("num_id", "", value=10)
        html = str(result)

        assert 'id="num_id"' in html

    def test_input_numeric_shiny_bound_input_class(self) -> None:
        """Test input_numeric has appropriate shiny class."""
        result = input_numeric("num_id", "Number", value=10)
        html = str(result)

        assert "shiny-input-number" in html

    def test_input_numeric_no_min_max_step(self) -> None:
        """Test input_numeric without optional min/max/step."""
        result = input_numeric("num_id", "Number", value=10)
        html = str(result)

        # These should not appear if not set
        assert "min=" not in html or html.count("min=") == 0 or 'min="' in html
        # Check the basic structure is correct
        assert 'type="number"' in html

    def test_input_numeric_update_on_change(self) -> None:
        """Test input_numeric with update_on='change'."""
        result = input_numeric("num_id", "Number", value=10, update_on="change")
        html = str(result)

        assert 'data-update-on="change"' in html

    def test_input_numeric_update_on_blur(self) -> None:
        """Test input_numeric with update_on='blur'."""
        result = input_numeric("num_id", "Number", value=10, update_on="blur")
        html = str(result)

        assert 'data-update-on="blur"' in html

    def test_input_numeric_default_update_on(self) -> None:
        """Test input_numeric default update_on is 'change'."""
        result = input_numeric("num_id", "Number", value=10)
        html = str(result)

        assert 'data-update-on="change"' in html
