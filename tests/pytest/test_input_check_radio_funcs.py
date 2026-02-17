"""Tests for shiny.ui._input_check_radio module."""

from htmltools import Tag

from shiny.ui._input_check_radio import (
    input_checkbox,
    input_checkbox_group,
    input_radio_buttons,
    input_switch,
)


class TestInputCheckbox:
    """Tests for input_checkbox function."""

    def test_input_checkbox_basic(self) -> None:
        """Test basic input_checkbox creation."""
        result = input_checkbox("my_checkbox", "Check me")
        assert isinstance(result, Tag)

    def test_input_checkbox_has_id(self) -> None:
        """Test input_checkbox has correct id."""
        result = input_checkbox("checkbox_id", "Label")
        html = str(result)
        assert "checkbox_id" in html

    def test_input_checkbox_with_label(self) -> None:
        """Test input_checkbox with label."""
        result = input_checkbox("checkbox", "I agree to terms")
        html = str(result)
        assert "I agree to terms" in html

    def test_input_checkbox_value_true(self) -> None:
        """Test input_checkbox with value=True."""
        result = input_checkbox("checkbox", "Label", value=True)
        html = str(result)
        assert "checked" in html

    def test_input_checkbox_value_false(self) -> None:
        """Test input_checkbox with value=False."""
        result = input_checkbox("checkbox", "Label", value=False)
        html = str(result)
        assert "checkbox" in html

    def test_input_checkbox_with_width(self) -> None:
        """Test input_checkbox with width parameter."""
        result = input_checkbox("checkbox", "Label", width="200px")
        html = str(result)
        assert "checkbox" in html


class TestInputSwitch:
    """Tests for input_switch function."""

    def test_input_switch_basic(self) -> None:
        """Test basic input_switch creation."""
        result = input_switch("my_switch", "Toggle me")
        assert isinstance(result, Tag)

    def test_input_switch_has_id(self) -> None:
        """Test input_switch has correct id."""
        result = input_switch("switch_id", "Label")
        html = str(result)
        assert "switch_id" in html

    def test_input_switch_with_label(self) -> None:
        """Test input_switch with label."""
        result = input_switch("switch", "Enable feature")
        html = str(result)
        assert "Enable feature" in html

    def test_input_switch_value_true(self) -> None:
        """Test input_switch with value=True."""
        result = input_switch("switch", "Label", value=True)
        html = str(result)
        assert "checked" in html

    def test_input_switch_value_false(self) -> None:
        """Test input_switch with value=False."""
        result = input_switch("switch", "Label", value=False)
        html = str(result)
        assert "switch" in html

    def test_input_switch_with_width(self) -> None:
        """Test input_switch with width parameter."""
        result = input_switch("switch", "Label", width="150px")
        html = str(result)
        assert "switch" in html


class TestInputCheckboxGroup:
    """Tests for input_checkbox_group function."""

    def test_input_checkbox_group_basic(self) -> None:
        """Test basic input_checkbox_group creation."""
        result = input_checkbox_group("my_group", "Choose:", choices=["a", "b", "c"])
        assert isinstance(result, Tag)

    def test_input_checkbox_group_has_id(self) -> None:
        """Test input_checkbox_group has correct id."""
        result = input_checkbox_group("group_id", "Label", choices=["x", "y"])
        html = str(result)
        assert "group_id" in html

    def test_input_checkbox_group_with_label(self) -> None:
        """Test input_checkbox_group with label."""
        result = input_checkbox_group("group", "Select options:", choices=["a"])
        html = str(result)
        assert "Select options:" in html

    def test_input_checkbox_group_with_dict_choices(self) -> None:
        """Test input_checkbox_group with dict choices."""
        result = input_checkbox_group(
            "group", "Label", choices={"a": "Option A", "b": "Option B"}
        )
        html = str(result)
        assert "Option A" in html

    def test_input_checkbox_group_with_selected(self) -> None:
        """Test input_checkbox_group with selected values."""
        result = input_checkbox_group(
            "group", "Label", choices=["a", "b"], selected=["a"]
        )
        html = str(result)
        assert "checked" in html

    def test_input_checkbox_group_inline(self) -> None:
        """Test input_checkbox_group with inline=True."""
        result = input_checkbox_group("group", "Label", choices=["a", "b"], inline=True)
        html = str(result)
        assert "group" in html

    def test_input_checkbox_group_with_width(self) -> None:
        """Test input_checkbox_group with width parameter."""
        result = input_checkbox_group("group", "Label", choices=["a"], width="300px")
        html = str(result)
        assert "group" in html


class TestInputRadioButtons:
    """Tests for input_radio_buttons function."""

    def test_input_radio_buttons_basic(self) -> None:
        """Test basic input_radio_buttons creation."""
        result = input_radio_buttons("my_radio", "Choose one:", choices=["a", "b", "c"])
        assert isinstance(result, Tag)

    def test_input_radio_buttons_has_id(self) -> None:
        """Test input_radio_buttons has correct id."""
        result = input_radio_buttons("radio_id", "Label", choices=["x", "y"])
        html = str(result)
        assert "radio_id" in html

    def test_input_radio_buttons_with_label(self) -> None:
        """Test input_radio_buttons with label."""
        result = input_radio_buttons("radio", "Select one:", choices=["a"])
        html = str(result)
        assert "Select one:" in html

    def test_input_radio_buttons_with_dict_choices(self) -> None:
        """Test input_radio_buttons with dict choices."""
        result = input_radio_buttons(
            "radio", "Label", choices={"a": "Option A", "b": "Option B"}
        )
        html = str(result)
        assert "Option A" in html

    def test_input_radio_buttons_with_selected(self) -> None:
        """Test input_radio_buttons with selected value."""
        result = input_radio_buttons("radio", "Label", choices=["a", "b"], selected="b")
        html = str(result)
        assert "radio" in html

    def test_input_radio_buttons_inline(self) -> None:
        """Test input_radio_buttons with inline=True."""
        result = input_radio_buttons("radio", "Label", choices=["a", "b"], inline=True)
        html = str(result)
        assert "radio" in html

    def test_input_radio_buttons_with_width(self) -> None:
        """Test input_radio_buttons with width parameter."""
        result = input_radio_buttons("radio", "Label", choices=["a"], width="250px")
        html = str(result)
        assert "radio" in html
