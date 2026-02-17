"""Tests for shiny/ui/_input_check_radio.py module."""

from shiny.ui._input_check_radio import (
    input_checkbox,
    input_checkbox_group,
    input_radio_buttons,
    input_switch,
)


class TestInputCheckbox:
    """Tests for input_checkbox function."""

    def test_input_checkbox_is_callable(self):
        """Test input_checkbox is callable."""
        assert callable(input_checkbox)

    def test_input_checkbox_returns_tag(self):
        """Test input_checkbox returns a Tag."""
        from htmltools import Tag

        result = input_checkbox("my_checkbox", "Check me")
        assert isinstance(result, Tag)

    def test_input_checkbox_with_value(self):
        """Test input_checkbox with value parameter."""
        from htmltools import Tag

        result = input_checkbox("my_checkbox", "Check me", value=True)
        assert isinstance(result, Tag)


class TestInputCheckboxGroup:
    """Tests for input_checkbox_group function."""

    def test_input_checkbox_group_is_callable(self):
        """Test input_checkbox_group is callable."""
        assert callable(input_checkbox_group)

    def test_input_checkbox_group_returns_tag(self):
        """Test input_checkbox_group returns a Tag."""
        from htmltools import Tag

        result = input_checkbox_group(
            "my_group", "Select options", choices=["A", "B", "C"]
        )
        assert isinstance(result, Tag)


class TestInputRadioButtons:
    """Tests for input_radio_buttons function."""

    def test_input_radio_buttons_is_callable(self):
        """Test input_radio_buttons is callable."""
        assert callable(input_radio_buttons)

    def test_input_radio_buttons_returns_tag(self):
        """Test input_radio_buttons returns a Tag."""
        from htmltools import Tag

        result = input_radio_buttons(
            "my_radio", "Select option", choices=["A", "B", "C"]
        )
        assert isinstance(result, Tag)


class TestInputSwitch:
    """Tests for input_switch function."""

    def test_input_switch_is_callable(self):
        """Test input_switch is callable."""
        assert callable(input_switch)

    def test_input_switch_returns_tag(self):
        """Test input_switch returns a Tag."""
        from htmltools import Tag

        result = input_switch("my_switch", "Toggle me")
        assert isinstance(result, Tag)


class TestCheckRadioExported:
    """Tests for check/radio functions export."""

    def test_input_checkbox_in_ui(self):
        """Test input_checkbox is in ui module."""
        from shiny import ui

        assert hasattr(ui, "input_checkbox")

    def test_input_switch_in_ui(self):
        """Test input_switch is in ui module."""
        from shiny import ui

        assert hasattr(ui, "input_switch")
