"""Tests for shiny/ui/_input_update.py"""

from __future__ import annotations

from datetime import date, datetime
from typing import cast
from unittest.mock import MagicMock, patch

from shiny.module import ResolvedId
from shiny.ui._input_update import (
    _normalize_show_value,
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
    update_switch,
    update_task_button,
    update_text,
    update_text_area,
    update_tooltip,
)


def create_mock_session() -> MagicMock:
    """Create a mock session for testing update functions."""
    mock = MagicMock()
    mock._process_ui.return_value = {"html": "<div>test</div>", "deps": []}
    mock.ns.return_value = "test_id"
    mock.dynamic_route.return_value = "/dynamic/route"
    return mock


class TestUpdateActionButton:
    """Tests for update_action_button function."""

    def test_update_action_button_label(self) -> None:
        """Test updating action button with label."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            update_action_button("btn", label="New Label", session=mock_session)
        mock_session.send_input_message.assert_called_once()

    def test_update_action_button_icon(self) -> None:
        """Test updating action button with icon."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            update_action_button("btn", icon="icon-test", session=mock_session)
        mock_session.send_input_message.assert_called_once()

    def test_update_action_button_disabled(self) -> None:
        """Test updating action button disabled state."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            update_action_button("btn", disabled=True, session=mock_session)
        mock_session.send_input_message.assert_called_once()
        call_args = mock_session.send_input_message.call_args
        assert call_args[0][1]["disabled"] is True


class TestUpdateActionLink:
    """Tests for update_action_link function."""

    def test_update_action_link_label(self) -> None:
        """Test updating action link with label."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            update_action_link("link", label="New Link", session=mock_session)
        mock_session.send_input_message.assert_called_once()

    def test_update_action_link_icon(self) -> None:
        """Test updating action link with icon."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            update_action_link("link", icon="icon", session=mock_session)
        mock_session.send_input_message.assert_called_once()


class TestUpdateTaskButton:
    """Tests for update_task_button function."""

    def test_update_task_button_ready(self) -> None:
        """Test updating task button to ready state."""
        mock_session = create_mock_session()
        test_id = cast(ResolvedId, "test_id")
        manual_task_reset_buttons.add(test_id)
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            update_task_button("btn", state="ready", session=mock_session)
        assert test_id not in manual_task_reset_buttons
        mock_session.send_input_message.assert_called_once()

    def test_update_task_button_busy(self) -> None:
        """Test updating task button to busy state."""
        mock_session = create_mock_session()
        test_id = cast(ResolvedId, "test_id")
        manual_task_reset_buttons.discard(test_id)
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            update_task_button("btn", state="busy", session=mock_session)
        assert test_id in manual_task_reset_buttons
        manual_task_reset_buttons.discard(test_id)

    def test_update_task_button_none_state(self) -> None:
        """Test updating task button with no state change."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            update_task_button("btn", state=None, session=mock_session)
        mock_session.send_input_message.assert_called_once()


class TestUpdateCheckbox:
    """Tests for update_checkbox function."""

    def test_update_checkbox_value(self) -> None:
        """Test updating checkbox value."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            update_checkbox("chk", value=True, session=mock_session)
        call_args = mock_session.send_input_message.call_args
        assert call_args[0][1]["value"] is True

    def test_update_checkbox_label(self) -> None:
        """Test updating checkbox label."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            update_checkbox("chk", label="New Label", session=mock_session)
        mock_session.send_input_message.assert_called_once()


class TestUpdateSwitch:
    """Tests for update_switch function."""

    def test_update_switch_value(self) -> None:
        """Test updating switch value."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            update_switch("sw", value=False, session=mock_session)
        call_args = mock_session.send_input_message.call_args
        assert call_args[0][1]["value"] is False


class TestUpdateCheckboxGroup:
    """Tests for update_checkbox_group function."""

    def test_update_checkbox_group_choices(self) -> None:
        """Test updating checkbox group choices."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            with patch("shiny.ui._input_update.session_context"):
                update_checkbox_group(
                    "chkgrp", choices=["a", "b", "c"], session=mock_session
                )
        mock_session.send_input_message.assert_called_once()

    def test_update_checkbox_group_selected(self) -> None:
        """Test updating checkbox group selected values."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            update_checkbox_group("chkgrp", selected=["a"], session=mock_session)
        mock_session.send_input_message.assert_called_once()


class TestUpdateRadioButtons:
    """Tests for update_radio_buttons function."""

    def test_update_radio_buttons_choices(self) -> None:
        """Test updating radio buttons choices."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            with patch("shiny.ui._input_update.session_context"):
                update_radio_buttons(
                    "radio", choices=["x", "y", "z"], session=mock_session
                )
        mock_session.send_input_message.assert_called_once()

    def test_update_radio_buttons_selected(self) -> None:
        """Test updating radio buttons selected value."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            update_radio_buttons("radio", selected="x", session=mock_session)
        mock_session.send_input_message.assert_called_once()


class TestUpdateDate:
    """Tests for update_date function."""

    def test_update_date_value(self) -> None:
        """Test updating date value."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            update_date("dt", value=date(2024, 1, 15), session=mock_session)
        mock_session.send_input_message.assert_called_once()

    def test_update_date_min_max(self) -> None:
        """Test updating date min and max."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            update_date(
                "dt",
                min=date(2024, 1, 1),
                max=date(2024, 12, 31),
                session=mock_session,
            )
        mock_session.send_input_message.assert_called_once()

    def test_update_date_empty_string_value(self) -> None:
        """Test updating date with empty string clears value."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            update_date("dt", value="", session=mock_session)
        call_args = mock_session.send_input_message.call_args
        assert call_args[0][1]["value"] is None

    def test_update_date_empty_string_min_max(self) -> None:
        """Test updating date with empty string clears min/max."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            update_date("dt", min="", max="", session=mock_session)
        call_args = mock_session.send_input_message.call_args
        assert call_args[0][1]["min"] is None
        assert call_args[0][1]["max"] is None


class TestUpdateDateRange:
    """Tests for update_date_range function."""

    def test_update_date_range_start_end(self) -> None:
        """Test updating date range start and end."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            update_date_range(
                "dtr",
                start=date(2024, 1, 1),
                end=date(2024, 12, 31),
                session=mock_session,
            )
        mock_session.send_input_message.assert_called_once()

    def test_update_date_range_empty_strings(self) -> None:
        """Test updating date range with empty strings."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            update_date_range(
                "dtr", start="", end="", min="", max="", session=mock_session
            )
        call_args = mock_session.send_input_message.call_args
        assert call_args[0][1]["min"] is None
        assert call_args[0][1]["max"] is None
        assert call_args[0][1]["value"]["start"] is None
        assert call_args[0][1]["value"]["end"] is None


class TestUpdateNumeric:
    """Tests for update_numeric function."""

    def test_update_numeric_value(self) -> None:
        """Test updating numeric value."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            update_numeric("num", value=42.5, session=mock_session)
        call_args = mock_session.send_input_message.call_args
        assert call_args[0][1]["value"] == 42.5

    def test_update_numeric_range(self) -> None:
        """Test updating numeric min, max, step."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            update_numeric("num", min=0, max=100, step=5, session=mock_session)
        call_args = mock_session.send_input_message.call_args
        assert call_args[0][1]["min"] == 0
        assert call_args[0][1]["max"] == 100
        assert call_args[0][1]["step"] == 5


class TestUpdateSelect:
    """Tests for update_select function."""

    def test_update_select_choices(self) -> None:
        """Test updating select choices."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            update_select("sel", choices=["a", "b", "c"], session=mock_session)
        mock_session.send_input_message.assert_called_once()

    def test_update_select_selected_string(self) -> None:
        """Test updating select with string selected."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            update_select("sel", selected="a", session=mock_session)
        call_args = mock_session.send_input_message.call_args
        assert call_args[0][1]["value"] == ["a"]

    def test_update_select_selected_list(self) -> None:
        """Test updating select with list selected."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            update_select("sel", selected=["a", "b"], session=mock_session)
        call_args = mock_session.send_input_message.call_args
        assert call_args[0][1]["value"] == ["a", "b"]

    def test_update_select_no_choices(self) -> None:
        """Test updating select without choices."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            update_select("sel", label="New Label", session=mock_session)
        call_args = mock_session.send_input_message.call_args
        assert (
            "options" not in call_args[0][1] or call_args[0][1].get("options") is None
        )


class TestUpdateSelectize:
    """Tests for update_selectize function."""

    def test_update_selectize_client_side(self) -> None:
        """Test updating selectize in client-side mode."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            update_selectize(
                "selz", choices=["a", "b"], server=False, session=mock_session
            )
        mock_session.send_input_message.assert_called()

    def test_update_selectize_with_options(self) -> None:
        """Test updating selectize with options."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            with patch("shiny.ui._input_update.resolve_id", return_value="selz"):
                update_selectize(
                    "selz",
                    options={"placeholder": "Select..."},
                    session=mock_session,
                )
        mock_session.send_input_message.assert_called()

    def test_update_selectize_server_side(self) -> None:
        """Test updating selectize in server-side mode."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            update_selectize(
                "selz",
                choices=["a", "b", "c"],
                selected="a",
                server=True,
                session=mock_session,
            )
        mock_session.send_input_message.assert_called()
        mock_session.dynamic_route.assert_called()

    def test_update_selectize_server_side_dict_choices(self) -> None:
        """Test updating selectize server-side with dict choices."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            update_selectize(
                "selz",
                choices={"a": "Label A", "b": "Label B"},
                server=True,
                session=mock_session,
            )
        mock_session.send_input_message.assert_called()

    def test_update_selectize_server_side_optgroup(self) -> None:
        """Test updating selectize server-side with optgroup choices."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            update_selectize(
                "selz",
                choices={"Group 1": {"a": "A", "b": "B"}, "Group 2": {"c": "C"}},
                server=True,
                session=mock_session,
            )
        mock_session.send_input_message.assert_called()


class TestUpdateSlider:
    """Tests for update_slider function."""

    def test_update_slider_value(self) -> None:
        """Test updating slider value."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            update_slider("sld", value=50, session=mock_session)
        mock_session.send_input_message.assert_called_once()

    def test_update_slider_range_value(self) -> None:
        """Test updating slider with range value."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            update_slider("sld", value=(10, 90), session=mock_session)
        mock_session.send_input_message.assert_called_once()

    def test_update_slider_min_max(self) -> None:
        """Test updating slider min and max."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            update_slider("sld", min=0, max=100, step=5, session=mock_session)
        mock_session.send_input_message.assert_called_once()

    def test_update_slider_date_value(self) -> None:
        """Test updating slider with date value."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            update_slider("sld", value=date(2024, 6, 15), session=mock_session)
        mock_session.send_input_message.assert_called_once()

    def test_update_slider_datetime_value(self) -> None:
        """Test updating slider with datetime value."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            update_slider(
                "sld", value=datetime(2024, 6, 15, 12, 30), session=mock_session
            )
        mock_session.send_input_message.assert_called_once()


class TestUpdateText:
    """Tests for update_text and update_text_area functions."""

    def test_update_text_value(self) -> None:
        """Test updating text value."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            update_text("txt", value="new text", session=mock_session)
        call_args = mock_session.send_input_message.call_args
        assert call_args[0][1]["value"] == "new text"

    def test_update_text_placeholder(self) -> None:
        """Test updating text placeholder."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            update_text("txt", placeholder="Enter text...", session=mock_session)
        call_args = mock_session.send_input_message.call_args
        assert call_args[0][1]["placeholder"] == "Enter text..."

    def test_update_text_area_is_alias(self) -> None:
        """Test that update_text_area is an alias for update_text."""
        assert update_text_area is update_text


class TestUpdateNavs:
    """Tests for update_navs function."""

    def test_update_navs_selected(self) -> None:
        """Test updating navs selected value."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            with patch("shiny.ui._input_update.warn_deprecated"):
                update_navs("nav", selected="tab2", session=mock_session)
        mock_session.send_input_message.assert_called_once()


class TestUpdateNavset:
    """Tests for update_navset function."""

    def test_update_navset_selected(self) -> None:
        """Test updating navset selected value."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            update_navset("nav", selected="panel1", session=mock_session)
        call_args = mock_session.send_input_message.call_args
        assert call_args[0][1]["value"] == "panel1"


class TestUpdateTooltip:
    """Tests for update_tooltip function."""

    def test_update_tooltip_content(self) -> None:
        """Test updating tooltip content."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            with patch(
                "shiny.ui._input_update._session_on_flush_send_msg"
            ) as mock_flush:
                update_tooltip("tip", "New tooltip content", session=mock_session)
                mock_flush.assert_called()

    def test_update_tooltip_show(self) -> None:
        """Test updating tooltip show state."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            with patch(
                "shiny.ui._input_update._session_on_flush_send_msg"
            ) as mock_flush:
                update_tooltip("tip", show=True, session=mock_session)
                assert mock_flush.call_count >= 1


class TestUpdatePopover:
    """Tests for update_popover function."""

    def test_update_popover_content(self) -> None:
        """Test updating popover content."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            with patch(
                "shiny.ui._input_update._session_on_flush_send_msg"
            ) as mock_flush:
                update_popover("pop", "New content", session=mock_session)
                mock_flush.assert_called()

    def test_update_popover_title(self) -> None:
        """Test updating popover title."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            with patch(
                "shiny.ui._input_update._session_on_flush_send_msg"
            ) as mock_flush:
                update_popover("pop", title="New Title", session=mock_session)
                mock_flush.assert_called()

    def test_update_popover_show(self) -> None:
        """Test updating popover show state."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._input_update.require_active_session", return_value=mock_session
        ):
            with patch(
                "shiny.ui._input_update._session_on_flush_send_msg"
            ) as mock_flush:
                update_popover("pop", show=False, session=mock_session)
                mock_flush.assert_called()


class TestNormalizeShowValue:
    """Tests for _normalize_show_value helper function."""

    def test_normalize_show_value_true(self) -> None:
        """Test normalizing True to 'show'."""
        assert _normalize_show_value(True) == "show"

    def test_normalize_show_value_false(self) -> None:
        """Test normalizing False to 'hide'."""
        assert _normalize_show_value(False) == "hide"

    def test_normalize_show_value_none(self) -> None:
        """Test normalizing None to 'toggle'."""
        assert _normalize_show_value(None) == "toggle"
