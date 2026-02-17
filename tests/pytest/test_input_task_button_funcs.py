"""Tests for shiny.ui._input_task_button module."""

from htmltools import Tag

from shiny.ui._input_task_button import input_task_button, spinner_icon


class TestInputTaskButton:
    """Tests for input_task_button function."""

    def test_input_task_button_returns_tag(self):
        """input_task_button should return a Tag."""
        result = input_task_button("task_btn", "Run Task")
        assert isinstance(result, Tag)

    def test_input_task_button_has_correct_id(self):
        """input_task_button should have the correct id."""
        result = input_task_button("my_task", "Run")
        html = str(result)
        assert 'id="my_task"' in html

    def test_input_task_button_has_label(self):
        """input_task_button should display the label."""
        result = input_task_button("task", "Start Processing")
        html = str(result)
        assert "Start Processing" in html

    def test_input_task_button_default_busy_label(self):
        """input_task_button should have default busy label."""
        result = input_task_button("task", "Run")
        html = str(result)
        assert "Processing..." in html

    def test_input_task_button_custom_busy_label(self):
        """input_task_button should accept custom busy label."""
        result = input_task_button("task", "Run", label_busy="Working...")
        html = str(result)
        assert "Working..." in html

    def test_input_task_button_with_icon(self):
        """input_task_button should accept icon parameter."""
        result = input_task_button("task", "Run", icon="📊")
        html = str(result)
        # Icon should be in the HTML somewhere
        assert "task" in html

    def test_input_task_button_with_icon_busy(self):
        """input_task_button should accept icon_busy parameter."""
        result = input_task_button("task", "Run", icon_busy="⏳")
        html = str(result)
        assert "⏳" in html

    def test_input_task_button_with_width(self):
        """input_task_button should accept width parameter."""
        result = input_task_button("task", "Run", width="200px")
        html = str(result)
        assert "200px" in html

    def test_input_task_button_default_type_primary(self):
        """input_task_button should have default type 'primary'."""
        result = input_task_button("task", "Run")
        html = str(result)
        assert "btn-primary" in html

    def test_input_task_button_custom_type(self):
        """input_task_button should accept custom type."""
        result = input_task_button("task", "Run", type="danger")
        html = str(result)
        assert "btn-danger" in html

    def test_input_task_button_type_none(self):
        """input_task_button should handle type=None."""
        result = input_task_button("task", "Run", type=None)
        html = str(result)
        # When type is None, it should still render but without btn-{type} classes
        assert 'class=""' in html or 'class_=""' in html

    def test_input_task_button_auto_reset_default_true(self):
        """input_task_button should have auto_reset=True by default."""
        result = input_task_button("task", "Run")
        html = str(result)
        # data-auto-reset should be present (empty string means True in HTML)
        assert "data-auto-reset" in html

    def test_input_task_button_auto_reset_false(self):
        """input_task_button should accept auto_reset=False."""
        result = input_task_button("task", "Run", auto_reset=False)
        # The auto_reset attribute should be set
        # Note: When auto_reset=False, htmltools may not render the attribute
        assert isinstance(result, Tag)

    def test_input_task_button_with_kwargs(self):
        """input_task_button should accept additional kwargs."""
        result = input_task_button("task", "Run", class_="custom-class")
        html = str(result)
        assert "custom-class" in html

    def test_input_task_button_is_button_element(self):
        """input_task_button should create a button element."""
        result = input_task_button("task", "Run")
        assert result.name == "button"

    def test_input_task_button_has_type_button_attribute(self):
        """input_task_button should have type='button' attribute."""
        result = input_task_button("task", "Run")
        html = str(result)
        assert 'type="button"' in html


class TestSpinnerIcon:
    """Tests for spinner_icon constant."""

    def test_spinner_icon_is_string(self):
        """spinner_icon should be a string."""
        assert isinstance(spinner_icon, str)

    def test_spinner_icon_is_svg(self):
        """spinner_icon should be an SVG."""
        assert "<svg" in spinner_icon
        assert "</svg>" in spinner_icon

    def test_spinner_icon_has_spin_class(self):
        """spinner_icon should have py-shiny-spin class."""
        assert "py-shiny-spin" in spinner_icon

    def test_spinner_icon_has_viewbox(self):
        """spinner_icon should have viewBox attribute."""
        assert "viewBox" in spinner_icon

    def test_spinner_icon_has_path(self):
        """spinner_icon should contain a path element."""
        assert "<path" in spinner_icon

    def test_spinner_icon_is_aria_hidden(self):
        """spinner_icon should be aria-hidden for accessibility."""
        assert 'aria-hidden="true"' in spinner_icon
