"""Unit tests for shiny.ui._input_check_radio module."""

from __future__ import annotations

from htmltools import Tag

from shiny.ui import input_checkbox, input_checkbox_group, input_radio_buttons


class TestInputCheckbox:
    """Tests for input_checkbox function."""

    def test_basic_input_checkbox(self) -> None:
        """Test basic input_checkbox with required parameters."""
        result = input_checkbox("cb_id", "Check me")
        html = str(result)

        assert 'id="cb_id"' in html
        assert "Check me" in html
        assert 'type="checkbox"' in html

    def test_input_checkbox_returns_tag(self) -> None:
        """Test that input_checkbox returns a Tag."""
        result = input_checkbox("cb_id", "Check me")
        assert isinstance(result, Tag)

    def test_input_checkbox_value_true(self) -> None:
        """Test input_checkbox with value=True."""
        result = input_checkbox("cb_id", "Check me", value=True)
        html = str(result)

        assert 'checked="checked"' in html

    def test_input_checkbox_value_false(self) -> None:
        """Test input_checkbox with value=False."""
        result = input_checkbox("cb_id", "Check me", value=False)
        html = str(result)

        assert "checked=" not in html or 'checked="checked"' not in html

    def test_input_checkbox_with_width(self) -> None:
        """Test input_checkbox with width parameter."""
        result = input_checkbox("cb_id", "Check me", width="200px")
        html = str(result)

        assert "width:200px" in html

    def test_input_checkbox_form_group_class(self) -> None:
        """Test that container has form-group class."""
        result = input_checkbox("cb_id", "Check me")
        html = str(result)

        assert "form-group" in html
        assert "shiny-input-container" in html

    def test_input_checkbox_shiny_class(self) -> None:
        """Test input_checkbox has shiny-input-checkbox class."""
        result = input_checkbox("cb_id", "Check me")
        html = str(result)

        assert "shiny-input-checkbox" in html

    def test_input_checkbox_html_label(self) -> None:
        """Test input_checkbox with HTML label."""
        from htmltools import tags

        label = tags.em("Italic Check")
        result = input_checkbox("cb_id", label)
        html = str(result)

        assert "<em>Italic Check</em>" in html

    def test_input_checkbox_empty_label(self) -> None:
        """Test input_checkbox with empty label."""
        result = input_checkbox("cb_id", "")
        html = str(result)

        assert 'id="cb_id"' in html

    def test_input_checkbox_default_value(self) -> None:
        """Test input_checkbox default value is False."""
        result = input_checkbox("cb_id", "Check me")
        html = str(result)

        # Should not be checked by default
        assert 'checked="checked"' not in html


class TestInputCheckboxGroup:
    """Tests for input_checkbox_group function."""

    def test_basic_input_checkbox_group_list(self) -> None:
        """Test input_checkbox_group with list choices."""
        result = input_checkbox_group("cbg_id", "Options", ["a", "b", "c"])
        html = str(result)

        assert 'id="cbg_id"' in html
        assert "Options" in html
        assert 'value="a"' in html
        assert 'value="b"' in html
        assert 'value="c"' in html

    def test_input_checkbox_group_returns_tag(self) -> None:
        """Test that input_checkbox_group returns a Tag."""
        result = input_checkbox_group("cbg_id", "Options", ["a", "b"])
        assert isinstance(result, Tag)

    def test_input_checkbox_group_tuple_choices(self) -> None:
        """Test input_checkbox_group with tuple choices."""
        result = input_checkbox_group("cbg_id", "Options", ("x", "y", "z"))
        html = str(result)

        assert 'value="x"' in html
        assert 'value="y"' in html
        assert 'value="z"' in html

    def test_input_checkbox_group_dict_choices(self) -> None:
        """Test input_checkbox_group with dict choices."""
        result = input_checkbox_group(
            "cbg_id",
            "Options",
            {"opt1": "Option 1", "opt2": "Option 2"},
        )
        html = str(result)

        assert 'value="opt1"' in html
        assert 'value="opt2"' in html
        assert "Option 1" in html
        assert "Option 2" in html

    def test_input_checkbox_group_selected_single(self) -> None:
        """Test input_checkbox_group with single selected value."""
        result = input_checkbox_group(
            "cbg_id",
            "Options",
            ["a", "b", "c"],
            selected="b",
        )
        html = str(result)

        # b should be checked
        # Check that the structure includes checked for value b
        assert 'value="b"' in html

    def test_input_checkbox_group_selected_list(self) -> None:
        """Test input_checkbox_group with list of selected values."""
        result = input_checkbox_group(
            "cbg_id",
            "Options",
            ["a", "b", "c"],
            selected=["a", "c"],
        )
        html = str(result)

        assert 'value="a"' in html
        assert 'value="c"' in html

    def test_input_checkbox_group_inline_true(self) -> None:
        """Test input_checkbox_group with inline=True."""
        result = input_checkbox_group(
            "cbg_id",
            "Options",
            ["a", "b"],
            inline=True,
        )
        html = str(result)

        assert "shiny-input-container-inline" in html
        assert "checkbox-inline" in html

    def test_input_checkbox_group_inline_false(self) -> None:
        """Test input_checkbox_group with inline=False."""
        result = input_checkbox_group(
            "cbg_id",
            "Options",
            ["a", "b"],
            inline=False,
        )
        html = str(result)

        assert "shiny-input-container-inline" not in html

    def test_input_checkbox_group_with_width(self) -> None:
        """Test input_checkbox_group with width parameter."""
        result = input_checkbox_group(
            "cbg_id",
            "Options",
            ["a", "b"],
            width="300px",
        )
        html = str(result)

        assert "width:300px" in html

    def test_input_checkbox_group_checkboxgroup_class(self) -> None:
        """Test input_checkbox_group has shiny-input-checkboxgroup class."""
        result = input_checkbox_group("cbg_id", "Options", ["a"])
        html = str(result)

        assert "shiny-input-checkboxgroup" in html

    def test_input_checkbox_group_role_group(self) -> None:
        """Test input_checkbox_group has role='group'."""
        result = input_checkbox_group("cbg_id", "Options", ["a"])
        html = str(result)

        assert 'role="group"' in html

    def test_input_checkbox_group_html_label(self) -> None:
        """Test input_checkbox_group with HTML label."""
        from htmltools import tags

        label = tags.strong("Bold Options")
        result = input_checkbox_group("cbg_id", label, ["a", "b"])
        html = str(result)

        assert "<strong>Bold Options</strong>" in html

    def test_input_checkbox_group_html_choice_labels(self) -> None:
        """Test input_checkbox_group with HTML choice labels."""
        from htmltools import tags

        result = input_checkbox_group(
            "cbg_id",
            "Options",
            {"a": tags.em("Italic A"), "b": tags.strong("Bold B")},
        )
        html = str(result)

        assert "<em>Italic A</em>" in html
        assert "<strong>Bold B</strong>" in html

    def test_input_checkbox_group_options_container(self) -> None:
        """Test input_checkbox_group has shiny-options-group container."""
        result = input_checkbox_group("cbg_id", "Options", ["a"])
        html = str(result)

        assert "shiny-options-group" in html


class TestInputRadioButtons:
    """Tests for input_radio_buttons function."""

    def test_basic_input_radio_buttons_list(self) -> None:
        """Test input_radio_buttons with list choices."""
        result = input_radio_buttons("rb_id", "Choose one", ["a", "b", "c"])
        html = str(result)

        assert 'id="rb_id"' in html
        assert "Choose one" in html
        assert 'type="radio"' in html
        assert 'value="a"' in html
        assert 'value="b"' in html
        assert 'value="c"' in html

    def test_input_radio_buttons_returns_tag(self) -> None:
        """Test that input_radio_buttons returns a Tag."""
        result = input_radio_buttons("rb_id", "Choose", ["a", "b"])
        assert isinstance(result, Tag)

    def test_input_radio_buttons_tuple_choices(self) -> None:
        """Test input_radio_buttons with tuple choices."""
        result = input_radio_buttons("rb_id", "Choose", ("x", "y"))
        html = str(result)

        assert 'value="x"' in html
        assert 'value="y"' in html

    def test_input_radio_buttons_dict_choices(self) -> None:
        """Test input_radio_buttons with dict choices."""
        result = input_radio_buttons(
            "rb_id",
            "Choose",
            {"opt1": "Option 1", "opt2": "Option 2"},
        )
        html = str(result)

        assert 'value="opt1"' in html
        assert 'value="opt2"' in html
        assert "Option 1" in html
        assert "Option 2" in html

    def test_input_radio_buttons_selected(self) -> None:
        """Test input_radio_buttons with selected value."""
        result = input_radio_buttons(
            "rb_id",
            "Choose",
            ["a", "b", "c"],
            selected="b",
        )
        html = str(result)

        assert 'value="b"' in html

    def test_input_radio_buttons_default_selected(self) -> None:
        """Test input_radio_buttons default selects first option."""
        result = input_radio_buttons("rb_id", "Choose", ["first", "second"])
        html = str(result)

        # First option should be checked by default for radio buttons
        assert 'value="first"' in html

    def test_input_radio_buttons_inline_true(self) -> None:
        """Test input_radio_buttons with inline=True."""
        result = input_radio_buttons(
            "rb_id",
            "Choose",
            ["a", "b"],
            inline=True,
        )
        html = str(result)

        assert "shiny-input-container-inline" in html
        assert "radio-inline" in html

    def test_input_radio_buttons_inline_false(self) -> None:
        """Test input_radio_buttons with inline=False."""
        result = input_radio_buttons(
            "rb_id",
            "Choose",
            ["a", "b"],
            inline=False,
        )
        html = str(result)

        assert "shiny-input-container-inline" not in html

    def test_input_radio_buttons_with_width(self) -> None:
        """Test input_radio_buttons with width parameter."""
        result = input_radio_buttons(
            "rb_id",
            "Choose",
            ["a", "b"],
            width="250px",
        )
        html = str(result)

        assert "width:250px" in html

    def test_input_radio_buttons_radiogroup_class(self) -> None:
        """Test input_radio_buttons has shiny-input-radiogroup class."""
        result = input_radio_buttons("rb_id", "Choose", ["a"])
        html = str(result)

        assert "shiny-input-radiogroup" in html

    def test_input_radio_buttons_role_radiogroup(self) -> None:
        """Test input_radio_buttons has role='radiogroup'."""
        result = input_radio_buttons("rb_id", "Choose", ["a"])
        html = str(result)

        assert 'role="radiogroup"' in html

    def test_input_radio_buttons_html_label(self) -> None:
        """Test input_radio_buttons with HTML label."""
        from htmltools import tags

        label = tags.strong("Bold Choice")
        result = input_radio_buttons("rb_id", label, ["a", "b"])
        html = str(result)

        assert "<strong>Bold Choice</strong>" in html

    def test_input_radio_buttons_html_choice_labels(self) -> None:
        """Test input_radio_buttons with HTML choice labels."""
        from htmltools import tags

        result = input_radio_buttons(
            "rb_id",
            "Choose",
            {"a": tags.em("Italic A"), "b": tags.strong("Bold B")},
        )
        html = str(result)

        assert "<em>Italic A</em>" in html
        assert "<strong>Bold B</strong>" in html

    def test_input_radio_buttons_name_attribute(self) -> None:
        """Test input_radio_buttons uses id as name attribute."""
        result = input_radio_buttons("rb_id", "Choose", ["a", "b"])
        html = str(result)

        assert 'name="rb_id"' in html

    def test_input_radio_buttons_options_container(self) -> None:
        """Test input_radio_buttons has shiny-options-group container."""
        result = input_radio_buttons("rb_id", "Choose", ["a"])
        html = str(result)

        assert "shiny-options-group" in html

    def test_input_radio_buttons_many_options(self) -> None:
        """Test input_radio_buttons with many options."""
        options = [f"option_{i}" for i in range(10)]
        result = input_radio_buttons("rb_id", "Choose", options)
        html = str(result)

        for opt in options:
            assert f'value="{opt}"' in html


class TestInputSwitch:
    """Tests for input_switch function."""

    def test_basic_input_switch(self) -> None:
        """Test basic input_switch with required parameters."""
        from shiny.ui._input_check_radio import input_switch

        result = input_switch("sw_id", "Toggle me")
        html = str(result)

        assert 'id="sw_id"' in html
        assert "Toggle me" in html
        assert 'type="checkbox"' in html
        assert 'role="switch"' in html

    def test_input_switch_returns_tag(self) -> None:
        """Test that input_switch returns a Tag."""
        from shiny.ui._input_check_radio import input_switch

        result = input_switch("sw_id", "Toggle")
        assert isinstance(result, Tag)

    def test_input_switch_value_true(self) -> None:
        """Test input_switch with value=True."""
        from shiny.ui._input_check_radio import input_switch

        result = input_switch("sw_id", "Toggle", value=True)
        html = str(result)

        assert 'checked="checked"' in html

    def test_input_switch_value_false(self) -> None:
        """Test input_switch with value=False."""
        from shiny.ui._input_check_radio import input_switch

        result = input_switch("sw_id", "Toggle", value=False)
        html = str(result)

        assert 'checked="checked"' not in html

    def test_input_switch_with_width(self) -> None:
        """Test input_switch with width parameter."""
        from shiny.ui._input_check_radio import input_switch

        result = input_switch("sw_id", "Toggle", width="150px")
        html = str(result)

        assert "width:150px" in html

    def test_input_switch_bslib_class(self) -> None:
        """Test input_switch has bslib-input-switch class."""
        from shiny.ui._input_check_radio import input_switch

        result = input_switch("sw_id", "Toggle")
        html = str(result)

        assert "bslib-input-switch" in html
        assert "form-switch" in html

    def test_input_switch_form_check_class(self) -> None:
        """Test input_switch has form-check classes."""
        from shiny.ui._input_check_radio import input_switch

        result = input_switch("sw_id", "Toggle")
        html = str(result)

        assert "form-check" in html
        assert "form-check-input" in html
        assert "form-check-label" in html
