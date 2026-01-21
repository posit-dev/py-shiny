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


# ============================================================================
# toolbar_input_select() tests
# ============================================================================
def test_toolbar_input_select_basic():
    sel = ui.toolbar_input_select("sel1", "Choose", ["A", "B", "C"])
    assert isinstance(sel, Tag)
    assert sel.attrs.get("id") == "sel1"
    assert sel.has_class("bslib-toolbar-input-select")


def test_toolbar_input_select_label_required():
    with pytest.raises(ValueError, match="non-empty string"):
        ui.toolbar_input_select("sel1", "", ["A", "B", "C"])

    with pytest.raises(ValueError, match="non-empty string"):
        ui.toolbar_input_select("sel1", "   ", ["A", "B", "C"])


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


def test_toolbar_input_select_selected():
    sel = ui.toolbar_input_select("sel1", "Choose", ["A", "B", "C"], selected="B")
    rendered = str(sel)
    # The selected option should have the selected attribute
    assert 'value="B" selected' in rendered or 'selected value="B"' in rendered


def test_toolbar_input_select_with_icon():
    sel = ui.toolbar_input_select("sel1", "Filter", ["All", "Active"], icon="🔍")
    rendered = str(sel)
    assert "🔍" in rendered
    assert "Filter" in rendered


def test_toolbar_input_select_show_label():
    sel_hidden = ui.toolbar_input_select("sel1", "Choose", ["A", "B"], show_label=False)
    rendered_hidden = str(sel_hidden)
    assert "visually-hidden" in rendered_hidden

    sel_shown = ui.toolbar_input_select("sel2", "Choose", ["A", "B"], show_label=True)
    rendered_shown = str(sel_shown)
    # Label should be visible (not have visually-hidden class on the label span)
    # This is a bit tricky to test, but we can check the structure
    assert "Choose" in rendered_shown


def test_toolbar_input_select_tooltip():
    sel = ui.toolbar_input_select("sel1", "Choose", ["A", "B"], tooltip=True)
    rendered = str(sel)
    assert "bslib-tooltip" in rendered

    sel_no_tooltip = ui.toolbar_input_select("sel2", "Choose", ["A", "B"], tooltip=False)
    rendered_no_tooltip = str(sel_no_tooltip)
    assert "bslib-tooltip" not in rendered_no_tooltip


def test_toolbar_input_select_kwargs_only_named():
    # Should accept named arguments in kwargs
    sel = ui.toolbar_input_select("sel1", "Choose", ["A", "B"], data_foo="bar")
    rendered = str(sel)
    assert 'data-foo="bar"' in rendered or 'data_foo="bar"' in rendered


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
