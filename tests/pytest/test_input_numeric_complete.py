"""Comprehensive tests for shiny.ui._input_numeric module."""

from htmltools import Tag


class TestInputNumeric:
    """Tests for input_numeric function."""

    def test_input_numeric_basic(self):
        """input_numeric should create a numeric input."""
        from shiny.ui import input_numeric

        result = input_numeric("num", "Number", 0)
        assert isinstance(result, Tag)
        assert result.name == "div"
        # Find the input element
        input_elem = None
        for child in result.children:
            if hasattr(child, "name") and hasattr(child, "attrs"):
                if getattr(child, "name", None) == "input":  # type: ignore
                    input_elem = child
                    break
        assert input_elem is not None
        assert getattr(input_elem, "attrs", {}).get("type") == "number"  # type: ignore
        assert getattr(input_elem, "attrs", {}).get("id") == "num"  # type: ignore

    def test_input_numeric_with_label(self):
        """input_numeric should include label."""
        from shiny.ui import input_numeric

        result = input_numeric("num", "Enter Number", 5)
        html_str = str(result)
        assert "Enter Number" in html_str

    def test_input_numeric_with_value(self):
        """input_numeric should set initial value."""
        from shiny.ui import input_numeric

        result = input_numeric("num", "Number", 42)
        html_str = str(result)
        assert 'value="42"' in html_str

    def test_input_numeric_with_float_value(self):
        """input_numeric should accept float values."""
        from shiny.ui import input_numeric

        result = input_numeric("num", "Number", 3.14)
        html_str = str(result)
        assert "3.14" in html_str

    def test_input_numeric_with_min(self):
        """input_numeric should accept min parameter."""
        from shiny.ui import input_numeric

        result = input_numeric("num", "Number", 5, min=0)
        html_str = str(result)
        assert 'min="0"' in html_str

    def test_input_numeric_with_max(self):
        """input_numeric should accept max parameter."""
        from shiny.ui import input_numeric

        result = input_numeric("num", "Number", 5, max=10)
        html_str = str(result)
        assert 'max="10"' in html_str

    def test_input_numeric_with_step(self):
        """input_numeric should accept step parameter."""
        from shiny.ui import input_numeric

        result = input_numeric("num", "Number", 0, step=0.5)
        html_str = str(result)
        assert 'step="0.5"' in html_str

    def test_input_numeric_with_all_constraints(self):
        """input_numeric should accept min, max, and step together."""
        from shiny.ui import input_numeric

        result = input_numeric("num", "Number", 5, min=0, max=100, step=5)
        html_str = str(result)
        assert 'min="0"' in html_str
        assert 'max="100"' in html_str
        assert 'step="5"' in html_str

    def test_input_numeric_with_width(self):
        """input_numeric should accept width parameter."""
        from shiny.ui import input_numeric

        result = input_numeric("num", "Number", 0, width="200px")
        html_str = str(result)
        assert "200px" in html_str

    def test_input_numeric_update_on_change(self):
        """input_numeric should have change update mode by default."""
        from shiny.ui import input_numeric

        result = input_numeric("num", "Number", 0)
        html_str = str(result)
        assert 'data-update-on="change"' in html_str

    def test_input_numeric_update_on_blur(self):
        """input_numeric should accept blur update mode."""
        from shiny.ui import input_numeric

        result = input_numeric("num", "Number", 0, update_on="blur")
        html_str = str(result)
        assert 'data-update-on="blur"' in html_str

    def test_input_numeric_has_form_control_class(self):
        """input_numeric should have form-control class."""
        from shiny.ui import input_numeric

        result = input_numeric("num", "Number", 0)
        html_str = str(result)
        assert "form-control" in html_str

    def test_input_numeric_has_shiny_input_number_class(self):
        """input_numeric should have shiny-input-number class."""
        from shiny.ui import input_numeric

        result = input_numeric("num", "Number", 0)
        html_str = str(result)
        assert "shiny-input-number" in html_str

    def test_input_numeric_container_has_form_group(self):
        """input_numeric container should have form-group class."""
        from shiny.ui import input_numeric

        result = input_numeric("num", "Number", 0)
        assert "form-group" in result.attrs.get("class", "")
        assert "shiny-input-container" in result.attrs.get("class", "")

    def test_input_numeric_negative_values(self):
        """input_numeric should accept negative values."""
        from shiny.ui import input_numeric

        result = input_numeric("num", "Number", -5, min=-10, max=0)
        html_str = str(result)
        assert 'value="-5"' in html_str
        assert 'min="-10"' in html_str


class TestModuleExports:
    """Tests for module exports."""

    def test_module_imports_correctly(self):
        """Module should import without errors."""
        import shiny.ui._input_numeric  # noqa: F401, E501

    def test_all_exports_exist(self):
        """All items in __all__ should be importable."""
        from shiny.ui import _input_numeric

        for item in _input_numeric.__all__:
            assert hasattr(_input_numeric, item)
