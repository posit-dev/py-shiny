from __future__ import annotations

import pytest
from htmltools import Tag

from shiny import ui


# ============================================================================
# toolbar() tests
# ============================================================================
def test_toolbar_basic():
    t = ui.toolbar()
    assert isinstance(t, Tag)
    assert t.has_class("bslib-toolbar")
    assert t.has_class("bslib-gap-spacing")


def test_toolbar_align():
    # Default is right
    t_default = ui.toolbar()
    assert t_default.attrs.get("data-align") == "right"

    # Explicit right
    t_right = ui.toolbar(align="right")
    assert t_right.attrs.get("data-align") == "right"

    # Left
    t_left = ui.toolbar(align="left")
    assert t_left.attrs.get("data-align") == "left"


def test_toolbar_gap():
    # No gap
    t_no_gap = ui.toolbar()
    assert t_no_gap.attrs.get("style") is None

    # With gap
    t_gap = ui.toolbar(gap="10px")
    assert "gap:10px" in str(t_gap.attrs.get("style"))


def test_toolbar_contains_children():
    btn = ui.toolbar_input_button("btn1", "Button 1")
    t = ui.toolbar(btn)
    rendered = str(t)
    assert "btn1" in rendered


# ============================================================================
# toolbar_divider() tests
# ============================================================================
def test_toolbar_divider_basic():
    d = ui.toolbar_divider()
    assert isinstance(d, Tag)
    assert d.has_class("bslib-toolbar-divider")
    assert d.attrs.get("aria-hidden") == "true"


def test_toolbar_divider_width():
    d = ui.toolbar_divider(width="5px")
    style = str(d.attrs.get("style", ""))
    assert "--_divider-width:5px" in style


def test_toolbar_divider_gap():
    d = ui.toolbar_divider(gap="2rem")
    style = str(d.attrs.get("style", ""))
    assert "--_divider-gap:2rem" in style


# ============================================================================
# toolbar_input_button() tests
# ============================================================================
def test_toolbar_input_button_basic():
    btn = ui.toolbar_input_button("btn1", "Button Label")
    assert isinstance(btn, Tag)


def test_toolbar_input_button_with_icon_only():
    btn = ui.toolbar_input_button("btn1", "Save", icon="💾")
    rendered = str(btn)
    assert "btn1" in rendered
    assert "💾" in rendered
    # Label should be present but hidden for accessibility
    assert "Save" in rendered


def test_toolbar_input_button_with_icon_and_label():
    btn = ui.toolbar_input_button("btn1", "Save", icon="💾", show_label=True)
    rendered = str(btn)
    assert "btn1" in rendered
    assert "💾" in rendered
    assert "Save" in rendered


def test_toolbar_input_button_label_only():
    btn = ui.toolbar_input_button("btn1", "Click Me", icon=None, show_label=True)
    rendered = str(btn)
    assert "btn1" in rendered
    assert "Click Me" in rendered


def test_toolbar_input_button_no_icon_no_show_label_raises():
    with pytest.raises(ValueError, match="icon.*must be provided"):
        ui.toolbar_input_button("btn1", "Button", icon=None, show_label=False)


def test_toolbar_input_button_disabled():
    btn = ui.toolbar_input_button("btn1", "Button", disabled=True)
    rendered = str(btn)
    assert "disabled" in rendered


def test_toolbar_input_button_border():
    btn_no_border = ui.toolbar_input_button("btn1", "Button", border=False)
    assert "border-0" in str(btn_no_border)

    btn_with_border = ui.toolbar_input_button("btn2", "Button", border=True)
    assert "border-1" in str(btn_with_border)


def test_toolbar_input_button_tooltip_default():
    # Icon-only button should have tooltip by default
    btn = ui.toolbar_input_button("btn1", "Save", icon="💾")
    rendered = str(btn)
    # Should contain tooltip wrapper
    assert "bslib-tooltip" in rendered


def test_toolbar_input_button_tooltip_false():
    btn = ui.toolbar_input_button("btn1", "Save", icon="💾", tooltip=False)
    rendered = str(btn)
    # Should not contain tooltip wrapper
    assert "bslib-tooltip" not in rendered


def test_toolbar_input_button_tooltip_custom():
    btn = ui.toolbar_input_button("btn1", "Save", icon="💾", tooltip="Save your work")
    rendered = str(btn)
    assert "bslib-tooltip" in rendered
    assert "Save your work" in rendered


def test_toolbar_input_button_tooltip_show_label_default():
    # When show_label=True, tooltip should default to False
    btn = ui.toolbar_input_button("btn1", "Edit", icon="✏️", show_label=True)
    rendered = str(btn)
    assert "bslib-tooltip" not in rendered

    # When show_label=False, tooltip should default to True
    btn_icon_only = ui.toolbar_input_button("btn2", "Save", icon="💾", show_label=False)
    rendered_icon_only = str(btn_icon_only)
    assert "bslib-tooltip" in rendered_icon_only


def test_toolbar_input_button_empty_label_warning():
    # Empty string label should warn
    with pytest.warns(UserWarning, match="non-empty string label"):
        ui.toolbar_input_button("btn1", "", icon="💾")

    # Whitespace-only label should warn
    with pytest.warns(UserWarning, match="non-empty string label"):
        ui.toolbar_input_button("btn2", "   ", icon="💾")


# ============================================================================
# toolbar_input_select() tests
# ============================================================================

# --- Basic structure tests ---
def test_toolbar_input_select_basic():
    sel = ui.toolbar_input_select("sel1", "Choose", ["A", "B", "C"])
    assert isinstance(sel, Tag)
    assert sel.attrs.get("id") == "sel1"
    assert sel.has_class("bslib-toolbar-input-select")


def test_toolbar_input_select_internal_id():
    """Test that select element has internal ID to avoid conflicts."""
    sel = ui.toolbar_input_select("sel1", "Choose", ["A", "B"])
    rendered = str(sel)
    # The wrapper should have id="sel1"
    # The select should have id="sel1-select"
    assert 'id="sel1"' in rendered
    assert 'id="sel1-select"' in rendered


def test_toolbar_input_select_select_id_format():
    """Test that the select element has the correct internal ID format."""
    sel = ui.toolbar_input_select("myselect", "Choose", ["A", "B"])
    rendered = str(sel)
    # Wrapper has id="myselect", select has id="myselect-select"
    assert 'id="myselect"' in rendered
    assert 'id="myselect-select"' in rendered
    # Label should reference the select's internal ID
    assert 'for="myselect-select"' in rendered


def test_toolbar_input_select_no_bind_input():
    """Test that select has data-shiny-no-bind-input attribute."""
    sel = ui.toolbar_input_select("sel1", "Choose", ["A", "B"])
    rendered = str(sel)
    # This prevents Shiny from binding to the internal select directly
    assert "data-shiny-no-bind-input" in rendered


# --- Label validation tests ---
def test_toolbar_input_select_label_required():
    with pytest.raises(ValueError, match="non-empty string"):
        ui.toolbar_input_select("sel1", "", ["A", "B", "C"])

    with pytest.raises(ValueError, match="non-empty string"):
        ui.toolbar_input_select("sel1", "   ", ["A", "B", "C"])


def test_toolbar_input_select_label_type_validation():
    """Test that label must be a string."""
    # Non-string label should raise ValueError
    with pytest.raises(ValueError, match="non-empty string"):
        ui.toolbar_input_select("sel1", 123, ["A", "B"])  # type: ignore


def test_toolbar_input_select_label_for_attribute():
    """Test that label 'for' attribute points to select element."""
    sel = ui.toolbar_input_select("sel1", "Choose", ["A", "B"])
    rendered = str(sel)
    # Label should have for="sel1-select" matching the select's internal ID
    assert 'for="sel1-select"' in rendered


# --- Choices tests ---
def test_toolbar_input_select_choices_list():
    sel = ui.toolbar_input_select("sel1", "Choose", ["A", "B", "C"])
    rendered = str(sel)
    assert "A" in rendered
    assert "B" in rendered
    assert "C" in rendered


def test_toolbar_input_select_choices_dict():
    sel = ui.toolbar_input_select(
        "sel1", "Choose", {"a": "Choice A", "b": "Choice B"}
    )
    rendered = str(sel)
    assert "Choice A" in rendered
    assert "Choice B" in rendered
    assert 'value="a"' in rendered
    assert 'value="b"' in rendered


def test_toolbar_input_select_choices_optgroup():
    choices = {
        "Group 1": {"a1": "A1", "a2": "A2"},
        "Group 2": {"b1": "B1", "b2": "B2"},
    }
    sel = ui.toolbar_input_select("sel1", "Choose", choices)
    rendered = str(sel)
    assert "Group 1" in rendered
    assert "Group 2" in rendered
    assert "A1" in rendered
    assert "B2" in rendered


def test_toolbar_input_select_single_choice():
    """Test select with only one choice."""
    sel = ui.toolbar_input_select("sel1", "Choose", ["Only Option"])
    rendered = str(sel)
    assert "Only Option" in rendered
    # Should be auto-selected
    assert 'value="Only Option" selected' in rendered or 'selected value="Only Option"' in rendered


# --- Selection tests ---
def test_toolbar_input_select_selected():
    sel = ui.toolbar_input_select("sel1", "Choose", ["A", "B", "C"], selected="B")
    rendered = str(sel)
    # The selected option should have the selected attribute
    assert 'value="B" selected' in rendered or 'selected value="B"' in rendered


def test_toolbar_input_select_default_selected():
    """Test that first choice is selected by default when no selected value."""
    sel = ui.toolbar_input_select("sel1", "Choose", ["X", "Y", "Z"])
    rendered = str(sel)
    # X should be selected (first option)
    assert 'value="X" selected' in rendered or 'selected value="X"' in rendered


def test_toolbar_input_select_default_selected_dict():
    """Test that first choice is selected by default with dict choices."""
    sel = ui.toolbar_input_select(
        "sel1", "Choose", {"key1": "Label 1", "key2": "Label 2"}
    )
    rendered = str(sel)
    # First key should be selected
    assert 'value="key1" selected' in rendered or 'selected value="key1"' in rendered


def test_toolbar_input_select_default_selected_optgroup():
    """Test that first choice in first group is selected by default with optgroups."""
    choices = {
        "Group A": {"a1": "A1", "a2": "A2"},
        "Group B": {"b1": "B1", "b2": "B2"},
    }
    sel = ui.toolbar_input_select("sel1", "Choose", choices)
    rendered = str(sel)
    # First option in first group should be selected
    assert 'value="a1" selected' in rendered or 'selected value="a1"' in rendered


def test_toolbar_input_select_selected_in_optgroup():
    """Test selecting a specific value within an optgroup."""
    choices = {
        "Group A": {"a1": "A1", "a2": "A2"},
        "Group B": {"b1": "B1", "b2": "B2"},
    }
    sel = ui.toolbar_input_select("sel1", "Choose", choices, selected="b2")
    rendered = str(sel)
    # b2 should be selected
    assert 'value="b2" selected' in rendered or 'selected value="b2"' in rendered


# --- Icon and label tests ---
def test_toolbar_input_select_with_icon():
    sel = ui.toolbar_input_select("sel1", "Filter", ["All", "Active"], icon="🔍")
    rendered = str(sel)
    assert "🔍" in rendered
    assert "Filter" in rendered


def test_toolbar_input_select_icon_aria_hidden():
    """Test that icon is properly marked as decorative."""
    sel = ui.toolbar_input_select("sel1", "Filter", ["A", "B"], icon="🔍")
    rendered = str(sel)
    # Icon should be aria-hidden
    assert 'aria-hidden="true"' in rendered


def test_toolbar_input_select_empty_icon():
    """Test that empty icon element is created even when no icon provided."""
    sel = ui.toolbar_input_select("sel1", "Choose", ["A", "B"], icon=None)
    rendered = str(sel)
    # Icon container should still exist for dynamic updates
    assert "bslib-toolbar-icon" in rendered


def test_toolbar_input_select_show_label():
    sel_hidden = ui.toolbar_input_select("sel1", "Choose", ["A", "B"], show_label=False)
    rendered_hidden = str(sel_hidden)
    assert "visually-hidden" in rendered_hidden

    sel_shown = ui.toolbar_input_select("sel2", "Choose", ["A", "B"], show_label=True)
    rendered_shown = str(sel_shown)
    # Label should be visible (not have visually-hidden class on the label span)
    # This is a bit tricky to test, but we can check the structure
    assert "Choose" in rendered_shown


def test_toolbar_input_select_icon_and_label_both_visible():
    """Test that both icon and label can be visible at the same time."""
    sel = ui.toolbar_input_select(
        "sel1", "Filter", ["A", "B"], icon="🔍", show_label=True
    )
    rendered = str(sel)
    # Both should be present and label should not be visually-hidden
    assert "🔍" in rendered
    assert "Filter" in rendered
    # Check that label span doesn't have visually-hidden class
    # This is indirect, but we can verify the structure
    assert "bslib-toolbar-label" in rendered


# --- Tooltip tests ---
def test_toolbar_input_select_tooltip():
    sel = ui.toolbar_input_select("sel1", "Choose", ["A", "B"], tooltip=True)
    rendered = str(sel)
    assert "bslib-tooltip" in rendered

    sel_no_tooltip = ui.toolbar_input_select("sel2", "Choose", ["A", "B"], tooltip=False)
    rendered_no_tooltip = str(sel_no_tooltip)
    assert "bslib-tooltip" not in rendered_no_tooltip


def test_toolbar_input_select_custom_tooltip():
    sel = ui.toolbar_input_select("sel1", "Choose", ["A", "B"], tooltip="Custom tip")
    rendered = str(sel)
    assert "bslib-tooltip" in rendered
    assert "Custom tip" in rendered


def test_toolbar_input_select_tooltip_id():
    """Test that tooltip has predictable ID for programmatic updates."""
    sel = ui.toolbar_input_select("sel1", "Choose", ["A", "B"], tooltip=True)
    rendered = str(sel)
    # Tooltip should have ID sel1_tooltip
    assert 'id="sel1_tooltip"' in rendered


def test_toolbar_input_select_tooltip_label_combo():
    """Test tooltip behavior when both show_label and tooltip are explicitly set."""
    # show_label=True and tooltip=True (explicit override)
    sel1 = ui.toolbar_input_select(
        "sel1", "Filter", ["A", "B"], show_label=True, tooltip=True
    )
    rendered1 = str(sel1)
    # Should have both visible label and tooltip
    assert "bslib-tooltip" in rendered1
    assert "Filter" in rendered1

    # show_label=False and tooltip=False (explicit override)
    sel2 = ui.toolbar_input_select(
        "sel2", "Filter", ["A", "B"], show_label=False, tooltip=False
    )
    rendered2 = str(sel2)
    # Should have no tooltip
    assert "bslib-tooltip" not in rendered2


# --- Custom attributes tests ---
def test_toolbar_input_select_kwargs_only_named():
    # Should accept named arguments in kwargs
    sel = ui.toolbar_input_select("sel1", "Choose", ["A", "B"], data_foo="bar")
    rendered = str(sel)
    assert 'data-foo="bar"' in rendered or 'data_foo="bar"' in rendered


def test_toolbar_input_select_custom_attributes():
    """Test that custom attributes are applied to the wrapper div."""
    sel = ui.toolbar_input_select(
        "sel1", "Choose", ["A", "B"], data_testid="my-select", style="color: red;"
    )
    rendered = str(sel)
    assert 'data-testid="my-select"' in rendered or 'data_testid="my-select"' in rendered
    assert "color: red" in rendered or "color:red" in rendered


# ============================================================================
# update_toolbar_input_select() tests
# ============================================================================
def test_update_toolbar_input_select_exists():
    """Test that update function exists and is callable."""
    from shiny.ui import update_toolbar_input_select

    assert callable(update_toolbar_input_select)


# ============================================================================
# toolbar_spacer() tests
# ============================================================================
def test_toolbar_spacer_basic():
    """Test toolbar_spacer basic functionality."""
    spacer = ui.toolbar_spacer()
    assert isinstance(spacer, Tag)
    assert spacer.has_class("bslib-toolbar-spacer")
    assert spacer.attrs.get("aria-hidden") == "true"


# ============================================================================
# Integration tests
# ============================================================================
def test_toolbar_with_multiple_elements():
    t = ui.toolbar(
        ui.toolbar_input_button("btn1", "Button 1", icon="📝"),
        ui.toolbar_divider(),
        ui.toolbar_input_button("btn2", "Button 2", icon="💾"),
        ui.toolbar_input_select("sel1", "Choose", ["A", "B", "C"]),
        align="right",
        gap="0.5rem",
    )
    rendered = str(t)
    assert "btn1" in rendered
    assert "btn2" in rendered
    assert "sel1" in rendered
    assert "bslib-toolbar-divider" in rendered


def test_toolbar_in_card():
    """Test that toolbar works within a card header."""
    from shiny.ui import card, card_header

    c = card(
        card_header(
            "My Card",
            ui.toolbar(
                ui.toolbar_input_button("edit", "Edit", icon="✏️"),
                ui.toolbar_input_button("delete", "Delete", icon="🗑️"),
                align="right",
            ),
        ),
        "Card content",
    )
    rendered = str(c)
    assert "bslib-toolbar" in rendered
    assert "edit" in rendered
    assert "delete" in rendered


def test_toolbar_in_numeric_input_label():
    """Test that toolbar works as a label for numeric input."""
    numeric = ui.input_numeric(
        "quantity",
        label=ui.toolbar(
            ui.toolbar_spacer(),
            ui.toolbar_input_button("btn_preset_10", "10", show_label=True),
            ui.toolbar_input_button("btn_preset_50", "50", show_label=True),
            ui.toolbar_input_button("btn_reset", "Reset", icon="🔄"),
            align="right",
        ),
        value=1,
    )
    rendered = str(numeric)
    assert "bslib-toolbar" in rendered
    assert "btn_preset_10" in rendered
    assert "btn_preset_50" in rendered
    assert "btn_reset" in rendered
    # Toolbar should be in a label element
    assert "<label" in rendered


def test_toolbar_in_text_area_label():
    """Test that toolbar works as a label for text area input."""
    textarea = ui.input_text_area(
        "notes",
        label=ui.toolbar(
            ui.toolbar_input_button("btn_bold", "Bold", icon="💪", tooltip="Make text bold"),
            ui.toolbar_input_button("btn_italic", "Italic", icon="📝", tooltip="Make text italic"),
            ui.toolbar_divider(),
            ui.toolbar_input_select(
                "text_size",
                label="Text Size",
                choices=["small", "normal", "large"],
                selected="normal",
            ),
            ui.toolbar_spacer(),
            ui.toolbar_input_button("btn_clear", "Clear", icon="🗑️", border=True),
            align="right",
        ),
        placeholder="Type your notes here...",
    )
    rendered = str(textarea)
    assert "bslib-toolbar" in rendered
    assert "btn_bold" in rendered
    assert "btn_italic" in rendered
    assert "text_size" in rendered
    assert "btn_clear" in rendered
    assert "bslib-toolbar-divider" in rendered
    assert "bslib-toolbar-spacer" in rendered
    # Toolbar should be in a label element
    assert "<label" in rendered


def test_toolbar_in_submit_textarea():
    """Test that toolbar works in input_submit_textarea."""
    submit_textarea = ui.input_submit_textarea(
        "message",
        label="Message",
        placeholder="Compose your message...",
        toolbar=ui.toolbar(
            ui.toolbar_input_select(
                "priority",
                label="Priority",
                choices=["low", "medium", "high"],
                selected="medium",
                icon="🚩",
            ),
            ui.toolbar_divider(),
            ui.toolbar_input_button("btn_attach", "Attach", icon="📎", tooltip="Attach file"),
            ui.toolbar_input_button("btn_emoji", "Emoji", icon="😀", tooltip="Insert emoji"),
            align="right",
        ),
    )
    rendered = str(submit_textarea)
    assert "bslib-toolbar" in rendered
    assert "priority" in rendered
    assert "btn_attach" in rendered
    assert "btn_emoji" in rendered
    assert "bslib-toolbar-divider" in rendered
    # Toolbar should be present in submit textarea structure
    assert "message" in rendered
