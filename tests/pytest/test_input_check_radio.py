"""Tests for shiny.ui._input_check_radio module."""

from shiny.ui import input_checkbox, input_checkbox_group, input_radio_buttons


class TestInputCheckbox:
    """Tests for the input_checkbox function."""

    def test_basic_checkbox(self):
        """Test creating a basic checkbox."""
        result = input_checkbox("check1", "Accept terms")
        html = str(result)

        assert 'id="check1"' in html
        assert "Accept terms" in html
        assert 'type="checkbox"' in html
        assert "shiny-input-checkbox" in html

    def test_checkbox_checked(self):
        """Test checkbox that is initially checked."""
        result = input_checkbox("check2", "Enabled", value=True)
        html = str(result)

        assert "checked" in html

    def test_checkbox_unchecked(self):
        """Test checkbox that is initially unchecked."""
        result = input_checkbox("check3", "Disabled", value=False)
        html = str(result)

        # Should not have checked attribute when value is False
        assert 'checked="checked"' not in html

    def test_checkbox_with_width(self):
        """Test checkbox with custom width."""
        result = input_checkbox("check4", "Wide checkbox", width="300px")
        html = str(result)

        assert "300px" in html


class TestInputCheckboxGroup:
    """Tests for the input_checkbox_group function."""

    def test_basic_checkbox_group_list(self):
        """Test creating a checkbox group with list of choices."""
        result = input_checkbox_group(
            "group1", "Select options:", choices=["A", "B", "C"]
        )
        html = str(result)

        assert 'id="group1"' in html
        assert "Select options:" in html
        assert "A" in html
        assert "B" in html
        assert "C" in html

    def test_checkbox_group_dict(self):
        """Test creating a checkbox group with dict of choices."""
        result = input_checkbox_group(
            "group2",
            "Select options:",
            choices={"a": "Choice A", "b": "Choice B", "c": "Choice C"},
        )
        html = str(result)

        assert "Choice A" in html
        assert "Choice B" in html
        assert "Choice C" in html

    def test_checkbox_group_with_selected(self):
        """Test checkbox group with pre-selected values."""
        result = input_checkbox_group(
            "group3", "Select options:", choices=["A", "B", "C"], selected=["A", "C"]
        )
        html = str(result)

        assert 'id="group3"' in html

    def test_checkbox_group_inline(self):
        """Test checkbox group in inline layout."""
        result = input_checkbox_group(
            "group4", "Select options:", choices=["A", "B", "C"], inline=True
        )
        html = str(result)

        assert "inline" in html.lower() or "shiny-options-group" in html

    def test_checkbox_group_with_width(self):
        """Test checkbox group with custom width."""
        result = input_checkbox_group(
            "group5", "Options:", choices=["A", "B"], width="400px"
        )
        html = str(result)

        assert "400px" in html


class TestInputRadioButtons:
    """Tests for the input_radio_buttons function."""

    def test_basic_radio_buttons_list(self):
        """Test creating radio buttons with list of choices."""
        result = input_radio_buttons(
            "radio1", "Select one:", choices=["Option 1", "Option 2", "Option 3"]
        )
        html = str(result)

        assert 'id="radio1"' in html
        assert "Select one:" in html
        assert "Option 1" in html
        assert "Option 2" in html
        assert "Option 3" in html

    def test_radio_buttons_dict(self):
        """Test creating radio buttons with dict of choices."""
        result = input_radio_buttons(
            "radio2",
            "Select one:",
            choices={"opt1": "First Option", "opt2": "Second Option"},
        )
        html = str(result)

        assert "First Option" in html
        assert "Second Option" in html

    def test_radio_buttons_with_selected(self):
        """Test radio buttons with pre-selected value."""
        result = input_radio_buttons(
            "radio3", "Select one:", choices=["A", "B", "C"], selected="B"
        )
        html = str(result)

        assert 'id="radio3"' in html

    def test_radio_buttons_inline(self):
        """Test radio buttons in inline layout."""
        result = input_radio_buttons(
            "radio4", "Select one:", choices=["A", "B", "C"], inline=True
        )
        html = str(result)

        assert "inline" in html.lower() or "shiny-options-group" in html

    def test_radio_buttons_with_width(self):
        """Test radio buttons with custom width."""
        result = input_radio_buttons(
            "radio5", "Options:", choices=["A", "B"], width="300px"
        )
        html = str(result)

        assert "300px" in html
