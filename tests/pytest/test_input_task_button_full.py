"""Tests for shiny/ui/_input_task_button.py - Task button input and binding."""

from shiny.ui import input_task_button
from shiny.ui._input_task_button import bind_task_button, spinner_icon


class TestInputTaskButton:
    """Tests for input_task_button function."""

    def test_returns_tag(self):
        """Test input_task_button returns a Tag."""
        from htmltools import Tag

        result = input_task_button("test_id", "Click me")
        assert isinstance(result, Tag)

    def test_button_has_correct_id(self):
        """Test button has correct id attribute."""
        result = input_task_button("test_id", "Click me")
        assert result.attrs.get("id") == "test_id"

    def test_button_has_type_button(self):
        """Test button has type='button'."""
        result = input_task_button("test_id", "Click me")
        assert result.attrs.get("type") == "button"

    def test_button_has_bslib_class(self):
        """Test button has bslib-task-button class."""
        result = input_task_button("test_id", "Click me")
        assert "bslib-task-button" in str(result.attrs.get("class", ""))

    def test_button_default_type_primary(self):
        """Test button defaults to btn-primary type."""
        result = input_task_button("test_id", "Click me")
        assert "btn-primary" in str(result.attrs.get("class", ""))

    def test_button_custom_type(self):
        """Test button with custom type."""
        result = input_task_button("test_id", "Click me", type="danger")
        assert "btn-danger" in str(result.attrs.get("class", ""))

    def test_button_no_type(self):
        """Test button with type=None."""
        result = input_task_button("test_id", "Click me", type=None)
        classes = str(result.attrs.get("class", ""))
        assert "btn-primary" not in classes
        assert "btn-" not in classes or "bslib" in classes

    def test_button_with_width(self):
        """Test button with width style."""
        result = input_task_button("test_id", "Click me", width="200px")
        style = result.attrs.get("style", "")
        assert "width" in str(style)

    def test_button_auto_reset_default_true(self):
        """Test auto_reset defaults to True."""
        result = input_task_button("test_id", "Click me")
        # When auto_reset=True, data-auto-reset is present as empty string (truthy attr)
        html = str(result)
        assert "data-auto-reset" in html

    def test_button_auto_reset_false(self):
        """Test auto_reset can be set to False."""
        result = input_task_button("test_id", "Click me", auto_reset=False)
        # When auto_reset=False, data-auto-reset attribute should not be present
        html = str(result)
        assert "data-auto-reset" not in html

    def test_button_with_icon(self):
        """Test button with icon."""
        from htmltools import tags

        icon = tags.i(class_="fa fa-check")
        result = input_task_button("test_id", "Click me", icon=icon)
        html = str(result)
        assert "fa fa-check" in html

    def test_button_with_label_busy(self):
        """Test button with custom busy label."""
        result = input_task_button("test_id", "Click me", label_busy="Please wait...")
        html = str(result)
        assert "Please wait..." in html

    def test_button_has_switch_inline_component(self):
        """Test button contains bslib-switch-inline component."""
        result = input_task_button("test_id", "Click me")
        html = str(result)
        assert "bslib-switch-inline" in html

    def test_button_has_ready_slot(self):
        """Test button has ready slot."""
        result = input_task_button("test_id", "Click me")
        html = str(result)
        assert 'slot="ready"' in html

    def test_button_has_busy_slot(self):
        """Test button has busy slot."""
        result = input_task_button("test_id", "Click me")
        html = str(result)
        assert 'slot="busy"' in html


class TestSpinnerIcon:
    """Tests for spinner_icon constant."""

    def test_spinner_icon_is_string(self):
        """Test spinner_icon is a string."""
        assert isinstance(spinner_icon, str)

    def test_spinner_icon_contains_svg(self):
        """Test spinner_icon contains SVG."""
        assert "<svg" in spinner_icon
        assert "</svg>" in spinner_icon

    def test_spinner_icon_has_spin_class(self):
        """Test spinner_icon has py-shiny-spin class."""
        assert "py-shiny-spin" in spinner_icon

    def test_spinner_icon_has_path(self):
        """Test spinner_icon has path element."""
        assert "<path" in spinner_icon


class TestBindTaskButton:
    """Tests for bind_task_button function."""

    def test_bind_task_button_callable(self):
        """Test bind_task_button is callable."""
        assert callable(bind_task_button)

    def test_bind_task_button_returns_callable_when_no_task(self):
        """Test bind_task_button returns callable when task is None."""
        result = bind_task_button(button_id="btn")
        assert callable(result)

    def test_bind_task_button_returns_task_when_no_session(self):
        """Test bind_task_button returns task unchanged when no session."""

        # Create a mock ExtendedTask-like object
        class MockExtendedTask:
            pass

        # When there's no session, it should return the task unchanged
        # This tests the early return path
        mock_task = MockExtendedTask()
        # bind_task_button needs an ExtendedTask but will return it
        # unchanged if there's no session
        result = bind_task_button(mock_task, button_id="btn")  # type: ignore
        assert result is mock_task
