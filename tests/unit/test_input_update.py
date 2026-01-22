"""Tests for shiny/ui/_input_update.py - session-dependent update functions."""

from datetime import date
from typing import Callable
from unittest.mock import MagicMock, patch

from htmltools import tags

from shiny.ui._input_update import (
    _normalize_show_value,
    _update_choice_input,
    manual_task_reset_buttons,
    update_action_button,
    update_action_link,
    update_checkbox,
    update_checkbox_group,
    update_date,
    update_date_range,
    update_navs,
    update_navset,
    update_numeric,
    update_popover,
    update_radio_buttons,
    update_select,
    update_selectize,
    update_slider,
    update_task_button,
    update_text,
    update_text_area,
    update_tooltip,
)
from shiny._namespaces import ResolvedId


# =============================================================================
# Helper: Create mock session
# =============================================================================
def create_mock_session() -> MagicMock:
    """Create a mock session object for testing update functions."""

    def _process_ui(value: object) -> dict[str, object] | None:
        if value is None:
            return None
        return {"html": str(value), "deps": []}

    def _on_flush(fn: Callable[[], None]) -> Callable[[], None]:
        return fn

    def _ns(value: str) -> str:
        return f"ns_{value}"

    session = MagicMock()
    session._process_ui = MagicMock(side_effect=_process_ui)
    session.send_input_message = MagicMock()
    session._send_message_sync = MagicMock()
    session.on_flush = MagicMock(side_effect=_on_flush)
    session.ns = MagicMock(side_effect=_ns)
    session.dynamic_route = MagicMock(return_value="/dynamic/route")
    return session


# =============================================================================
# Tests for update_action_button
# =============================================================================
class TestUpdateActionButton:
    def test_basic_update(self):
        """Test basic action button update with label."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_action_button("btn", label="New Label", session=session)

        session.send_input_message.assert_called_once()
        call_args = session.send_input_message.call_args
        assert call_args[0][0] == "btn"
        assert "label" in call_args[0][1]

    def test_update_with_icon(self):
        """Test action button update with icon."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_action_button(
                "btn", icon=tags.i(class_="fa fa-check"), session=session
            )

        session.send_input_message.assert_called_once()

    def test_update_disabled(self):
        """Test action button update with disabled state."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_action_button("btn", disabled=True, session=session)

        call_args = session.send_input_message.call_args
        assert call_args[0][1]["disabled"] is True

    def test_update_all_params(self):
        """Test action button update with all parameters."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_action_button(
                "btn",
                label="Updated",
                icon=tags.i(class_="icon"),
                disabled=False,
                session=session,
            )

        session.send_input_message.assert_called_once()


# =============================================================================
# Tests for update_action_link
# =============================================================================
class TestUpdateActionLink:
    def test_basic_update(self):
        """Test basic action link update."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_action_link("link", label="New Link", session=session)

        session.send_input_message.assert_called_once()
        assert session.send_input_message.call_args[0][0] == "link"

    def test_update_with_icon(self):
        """Test action link update with icon."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_action_link(
                "link", icon=tags.i(class_="fa fa-link"), session=session
            )

        session.send_input_message.assert_called_once()


# =============================================================================
# Tests for update_task_button
# =============================================================================
class TestUpdateTaskButton:
    def test_update_state_ready(self):
        """Test task button update to ready state."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_task_button("task_btn", state="ready", session=session)

        session.send_input_message.assert_called_once()
        # Ready state should remove from manual set
        assert "ns_task_btn" not in manual_task_reset_buttons

    def test_update_state_busy(self):
        """Test task button update to busy state."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_task_button("task_btn2", state="busy", session=session)

        # Busy state should add to manual set
        assert "ns_task_btn2" in manual_task_reset_buttons
        # Cleanup
        manual_task_reset_buttons.discard(ResolvedId("ns_task_btn2"))

    def test_update_state_none(self):
        """Test task button update with no state change."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_task_button("task_btn", session=session)

        session.send_input_message.assert_called_once()


# =============================================================================
# Tests for update_checkbox
# =============================================================================
class TestUpdateCheckbox:
    def test_update_label(self):
        """Test checkbox update with new label."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_checkbox("cb", label="New Label", session=session)

        session.send_input_message.assert_called_once()

    def test_update_value_true(self):
        """Test checkbox update with True value."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_checkbox("cb", value=True, session=session)

        call_args = session.send_input_message.call_args
        assert call_args[0][1]["value"] is True

    def test_update_value_false(self):
        """Test checkbox update with False value."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_checkbox("cb", value=False, session=session)

        call_args = session.send_input_message.call_args
        assert call_args[0][1]["value"] is False


# =============================================================================
# Tests for update_switch (same implementation as checkbox)
# =============================================================================
class TestUpdateSwitch:
    def test_update_switch(self):
        """Test switch update."""
        from shiny.ui._input_update import update_switch

        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_switch("sw", label="Switch Label", value=True, session=session)

        session.send_input_message.assert_called_once()


# =============================================================================
# Tests for update_checkbox_group
# =============================================================================
class TestUpdateCheckboxGroup:
    def test_update_choices_list(self):
        """Test checkbox group update with list choices."""
        session = create_mock_session()
        with (
            patch(
                "shiny.ui._input_update.require_active_session", return_value=session
            ),
            patch("shiny.ui._input_update.session_context"),
        ):
            update_checkbox_group(
                "cbg", choices=["A", "B", "C"], selected="A", session=session
            )

        session.send_input_message.assert_called_once()

    def test_update_choices_dict(self):
        """Test checkbox group update with dict choices."""
        session = create_mock_session()
        with (
            patch(
                "shiny.ui._input_update.require_active_session", return_value=session
            ),
            patch("shiny.ui._input_update.session_context"),
        ):
            update_checkbox_group(
                "cbg",
                choices={"a": "Option A", "b": "Option B"},
                selected=["a"],
                session=session,
            )

        session.send_input_message.assert_called_once()

    def test_update_label_only(self):
        """Test checkbox group update with label only."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_checkbox_group("cbg", label="New Group Label", session=session)

        session.send_input_message.assert_called_once()

    def test_update_inline(self):
        """Test checkbox group update with inline option."""
        session = create_mock_session()
        with (
            patch(
                "shiny.ui._input_update.require_active_session", return_value=session
            ),
            patch("shiny.ui._input_update.session_context"),
        ):
            update_checkbox_group(
                "cbg", choices=["X", "Y"], inline=True, session=session
            )

        session.send_input_message.assert_called_once()


# =============================================================================
# Tests for update_radio_buttons
# =============================================================================
class TestUpdateRadioButtons:
    def test_update_choices(self):
        """Test radio buttons update with choices."""
        session = create_mock_session()
        with (
            patch(
                "shiny.ui._input_update.require_active_session", return_value=session
            ),
            patch("shiny.ui._input_update.session_context"),
        ):
            update_radio_buttons(
                "rb",
                choices=["Red", "Green", "Blue"],
                selected="Green",
                session=session,
            )

        session.send_input_message.assert_called_once()

    def test_update_label(self):
        """Test radio buttons update with label."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_radio_buttons("rb", label="Choose Color", session=session)

        session.send_input_message.assert_called_once()


# =============================================================================
# Tests for _update_choice_input (internal function)
# =============================================================================
class TestUpdateChoiceInput:
    def test_checkbox_type(self):
        """Test internal choice input update for checkbox type."""
        session = create_mock_session()
        with (
            patch(
                "shiny.ui._input_update.require_active_session", return_value=session
            ),
            patch("shiny.ui._input_update.session_context"),
        ):
            _update_choice_input(
                "test", type="checkbox", choices=["1", "2"], session=session
            )

        session.send_input_message.assert_called_once()

    def test_radio_type(self):
        """Test internal choice input update for radio type."""
        session = create_mock_session()
        with (
            patch(
                "shiny.ui._input_update.require_active_session", return_value=session
            ),
            patch("shiny.ui._input_update.session_context"),
        ):
            _update_choice_input(
                "test", type="radio", choices=["A", "B"], session=session
            )

        session.send_input_message.assert_called_once()


# =============================================================================
# Tests for update_date
# =============================================================================
class TestUpdateDate:
    def test_update_value_date_obj(self):
        """Test date update with date object."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_date("date_input", value=date(2024, 1, 15), session=session)

        session.send_input_message.assert_called_once()

    def test_update_value_string(self):
        """Test date update with string value."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_date("date_input", value="2024-06-01", session=session)

        session.send_input_message.assert_called_once()

    def test_update_min_max(self):
        """Test date update with min and max."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_date(
                "date_input",
                min=date(2024, 1, 1),
                max=date(2024, 12, 31),
                session=session,
            )

        session.send_input_message.assert_called_once()

    def test_update_clear_value(self):
        """Test date update to clear value with empty string."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_date("date_input", value="", session=session)

        call_args = session.send_input_message.call_args
        assert call_args[0][1]["value"] is None

    def test_update_clear_min_max(self):
        """Test date update to clear min/max with empty strings."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_date("date_input", min="", max="", session=session)

        call_args = session.send_input_message.call_args
        assert call_args[0][1]["min"] is None
        assert call_args[0][1]["max"] is None

    def test_update_label(self):
        """Test date update with label."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_date("date_input", label="Select Date", session=session)

        session.send_input_message.assert_called_once()


# =============================================================================
# Tests for update_date_range
# =============================================================================
class TestUpdateDateRange:
    def test_update_start_end(self):
        """Test date range update with start and end."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_date_range(
                "date_range",
                start=date(2024, 1, 1),
                end=date(2024, 12, 31),
                session=session,
            )

        session.send_input_message.assert_called_once()
        call_args = session.send_input_message.call_args
        assert "value" in call_args[0][1]

    def test_update_min_max(self):
        """Test date range update with min and max."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_date_range(
                "date_range",
                min=date(2020, 1, 1),
                max=date(2030, 12, 31),
                session=session,
            )

        session.send_input_message.assert_called_once()

    def test_update_clear_values(self):
        """Test date range update to clear values."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_date_range(
                "date_range", start="", end="", min="", max="", session=session
            )

        call_args = session.send_input_message.call_args
        assert call_args[0][1]["min"] is None
        assert call_args[0][1]["max"] is None
        assert call_args[0][1]["value"]["start"] is None
        assert call_args[0][1]["value"]["end"] is None


# =============================================================================
# Tests for update_numeric
# =============================================================================
class TestUpdateNumeric:
    def test_update_value(self):
        """Test numeric update with value."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_numeric("num", value=42, session=session)

        call_args = session.send_input_message.call_args
        assert call_args[0][1]["value"] == 42

    def test_update_min_max_step(self):
        """Test numeric update with min, max, step."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_numeric("num", min=0, max=100, step=5, session=session)

        call_args = session.send_input_message.call_args
        assert call_args[0][1]["min"] == 0
        assert call_args[0][1]["max"] == 100
        assert call_args[0][1]["step"] == 5

    def test_update_label(self):
        """Test numeric update with label."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_numeric("num", label="Enter Number", session=session)

        session.send_input_message.assert_called_once()

    def test_update_float_value(self):
        """Test numeric update with float value."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_numeric("num", value=3.14159, session=session)

        call_args = session.send_input_message.call_args
        assert call_args[0][1]["value"] == 3.14159


# =============================================================================
# Tests for update_select
# =============================================================================
class TestUpdateSelect:
    def test_update_choices_list(self):
        """Test select update with list choices."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_select("sel", choices=["A", "B", "C"], session=session)

        session.send_input_message.assert_called_once()

    def test_update_choices_dict(self):
        """Test select update with dict choices."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_select(
                "sel",
                choices={"a": "Alpha", "b": "Beta"},
                selected="a",
                session=session,
            )

        session.send_input_message.assert_called_once()

    def test_update_selected_string(self):
        """Test select update with string selected."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_select("sel", choices=["X", "Y"], selected="X", session=session)

        call_args = session.send_input_message.call_args
        assert call_args[0][1]["value"] == ["X"]

    def test_update_selected_list(self):
        """Test select update with list selected (multi-select)."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_select(
                "sel", choices=["X", "Y", "Z"], selected=["X", "Z"], session=session
            )

        call_args = session.send_input_message.call_args
        assert call_args[0][1]["value"] == ["X", "Z"]

    def test_update_label_only(self):
        """Test select update with label only."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_select("sel", label="Choose One", session=session)

        session.send_input_message.assert_called_once()


# =============================================================================
# Tests for update_selectize
# =============================================================================
class TestUpdateSelectize:
    def test_update_client_side(self):
        """Test selectize update (client-side, server=False)."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_selectize(
                "selz",
                choices=["A", "B", "C"],
                selected="B",
                server=False,
                session=session,
            )

        session.send_input_message.assert_called()

    def test_update_server_side(self):
        """Test selectize update (server-side, server=True)."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_selectize(
                "selz",
                choices=["A", "B", "C"],
                selected="A",
                server=True,
                session=session,
            )

        session.send_input_message.assert_called()
        session.dynamic_route.assert_called()

    def test_update_with_options(self):
        """Test selectize update with options."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_selectize(
                "selz",
                options={"maxOptions": 500, "placeholder": "Search..."},
                session=session,
            )

        session.send_input_message.assert_called()

    def test_update_server_with_optgroups(self):
        """Test selectize update with optgroups (server-side)."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_selectize(
                "selz",
                choices={
                    "Fruits": {"apple": "Apple", "banana": "Banana"},
                    "Vegetables": {"carrot": "Carrot", "potato": "Potato"},
                },
                server=True,
                session=session,
            )

        session.send_input_message.assert_called()


# =============================================================================
# Tests for update_slider
# =============================================================================
class TestUpdateSlider:
    def test_update_value(self):
        """Test slider update with value."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_slider("slider", value=50, session=session)

        session.send_input_message.assert_called_once()

    def test_update_range_value(self):
        """Test slider update with range value (tuple)."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_slider("slider", value=(25, 75), session=session)

        session.send_input_message.assert_called_once()

    def test_update_min_max(self):
        """Test slider update with min and max."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_slider("slider", min=0, max=1000, session=session)

        session.send_input_message.assert_called_once()

    def test_update_step(self):
        """Test slider update with step."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_slider("slider", step=10, session=session)

        session.send_input_message.assert_called_once()

    def test_update_date_slider(self):
        """Test slider update with date values."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_slider(
                "slider",
                value=date(2024, 6, 15),
                min=date(2024, 1, 1),
                max=date(2024, 12, 31),
                session=session,
            )

        session.send_input_message.assert_called_once()

    def test_update_label(self):
        """Test slider update with label."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_slider("slider", label="Select Value", session=session)

        session.send_input_message.assert_called_once()


# =============================================================================
# Tests for update_text and update_text_area
# =============================================================================
class TestUpdateText:
    def test_update_value(self):
        """Test text update with value."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_text("txt", value="New text", session=session)

        call_args = session.send_input_message.call_args
        assert call_args[0][1]["value"] == "New text"

    def test_update_placeholder(self):
        """Test text update with placeholder."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_text("txt", placeholder="Enter text...", session=session)

        call_args = session.send_input_message.call_args
        assert call_args[0][1]["placeholder"] == "Enter text..."

    def test_update_label(self):
        """Test text update with label."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_text("txt", label="Text Input", session=session)

        session.send_input_message.assert_called_once()

    def test_update_text_area_alias(self):
        """Test that update_text_area is an alias for update_text."""
        assert update_text_area is update_text


# =============================================================================
# Tests for update_navs and update_navset
# =============================================================================
class TestUpdateNavs:
    def test_update_navs_deprecated(self):
        """Test update_navs shows deprecation warning."""
        session = create_mock_session()
        with (
            patch(
                "shiny.ui._input_update.require_active_session", return_value=session
            ),
            patch("shiny.ui._input_update.warn_deprecated") as mock_warn,
        ):
            update_navs("nav", selected="tab2", session=session)

        mock_warn.assert_called_once()

    def test_update_navset(self):
        """Test update_navset updates nav selection."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=session
        ):
            update_navset("nav", selected="panel1", session=session)

        call_args = session.send_input_message.call_args
        assert call_args[0][1]["value"] == "panel1"


# =============================================================================
# Tests for update_tooltip
# =============================================================================
class TestUpdateTooltip:
    def test_update_content(self):
        """Test tooltip update with new content."""
        session = create_mock_session()
        with (
            patch(
                "shiny.ui._input_update.require_active_session", return_value=session
            ),
            patch("shiny.ui._input_update._session_on_flush_send_msg") as mock_send,
        ):
            update_tooltip("tip", "New tooltip content", session=session)

        mock_send.assert_called()

    def test_update_show(self):
        """Test tooltip update to show."""
        session = create_mock_session()
        with (
            patch(
                "shiny.ui._input_update.require_active_session", return_value=session
            ),
            patch("shiny.ui._input_update._session_on_flush_send_msg") as mock_send,
        ):
            update_tooltip("tip", show=True, session=session)

        # Should be called for toggle
        assert mock_send.call_count >= 1

    def test_update_hide(self):
        """Test tooltip update to hide."""
        session = create_mock_session()
        with (
            patch(
                "shiny.ui._input_update.require_active_session", return_value=session
            ),
            patch("shiny.ui._input_update._session_on_flush_send_msg") as mock_send,
        ):
            update_tooltip("tip", show=False, session=session)

        assert mock_send.call_count >= 1


# =============================================================================
# Tests for update_popover
# =============================================================================
class TestUpdatePopover:
    def test_update_content(self):
        """Test popover update with new content."""
        session = create_mock_session()
        with (
            patch(
                "shiny.ui._input_update.require_active_session", return_value=session
            ),
            patch("shiny.ui._input_update._session_on_flush_send_msg") as mock_send,
        ):
            update_popover("pop", "New popover content", session=session)

        mock_send.assert_called()

    def test_update_title(self):
        """Test popover update with new title."""
        session = create_mock_session()
        with (
            patch(
                "shiny.ui._input_update.require_active_session", return_value=session
            ),
            patch("shiny.ui._input_update._session_on_flush_send_msg") as mock_send,
        ):
            update_popover("pop", title="New Title", session=session)

        mock_send.assert_called()

    def test_update_show_hide(self):
        """Test popover update show/hide."""
        session = create_mock_session()
        with (
            patch(
                "shiny.ui._input_update.require_active_session", return_value=session
            ),
            patch("shiny.ui._input_update._session_on_flush_send_msg") as mock_send,
        ):
            update_popover("pop", show=True, session=session)

        mock_send.assert_called()


# =============================================================================
# Tests for _normalize_show_value
# =============================================================================
class TestNormalizeShowValue:
    def test_none_returns_toggle(self):
        """Test None returns 'toggle'."""
        assert _normalize_show_value(None) == "toggle"

    def test_true_returns_show(self):
        """Test True returns 'show'."""
        assert _normalize_show_value(True) == "show"

    def test_false_returns_hide(self):
        """Test False returns 'hide'."""
        assert _normalize_show_value(False) == "hide"
