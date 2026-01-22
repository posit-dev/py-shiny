"""Tests for shiny/ui/_navs_dynamic.py"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from shiny.ui._navs_dynamic import insert_nav_panel, remove_nav_panel, update_nav_panel


def create_mock_session() -> MagicMock:
    """Create a mock session for testing nav panel functions."""
    mock = MagicMock()
    mock._process_ui.return_value = {"html": "<div>test</div>", "deps": []}
    return mock


def create_mock_nav() -> MagicMock:
    """Create a mock nav item."""
    mock = MagicMock()
    mock.resolve.return_value = (MagicMock(), MagicMock())
    return mock


class TestInsertNavPanel:
    """Tests for insert_nav_panel function."""

    def test_insert_nav_panel_basic(self) -> None:
        """Test basic nav panel insertion."""
        mock_session = create_mock_session()
        mock_nav = create_mock_nav()
        with patch(
            "shiny.ui._navs_dynamic.require_active_session", return_value=mock_session
        ):
            insert_nav_panel("navset", mock_nav, session=mock_session)
        mock_session._send_message_sync.assert_called_once()
        call_args = mock_session._send_message_sync.call_args[0][0]
        assert "shiny-insert-tab" in call_args

    def test_insert_nav_panel_with_target(self) -> None:
        """Test nav panel insertion with target."""
        mock_session = create_mock_session()
        mock_nav = create_mock_nav()
        with patch(
            "shiny.ui._navs_dynamic.require_active_session", return_value=mock_session
        ):
            insert_nav_panel("navset", mock_nav, target="tab1", session=mock_session)
        call_args = mock_session._send_message_sync.call_args[0][0]
        assert call_args["shiny-insert-tab"]["target"] == "tab1"

    def test_insert_nav_panel_position_before(self) -> None:
        """Test nav panel insertion with position='before'."""
        mock_session = create_mock_session()
        mock_nav = create_mock_nav()
        with patch(
            "shiny.ui._navs_dynamic.require_active_session", return_value=mock_session
        ):
            insert_nav_panel(
                "navset", mock_nav, position="before", session=mock_session
            )
        call_args = mock_session._send_message_sync.call_args[0][0]
        assert call_args["shiny-insert-tab"]["position"] == "before"

    def test_insert_nav_panel_select(self) -> None:
        """Test nav panel insertion with select=True."""
        mock_session = create_mock_session()
        mock_nav = create_mock_nav()
        with patch(
            "shiny.ui._navs_dynamic.require_active_session", return_value=mock_session
        ):
            insert_nav_panel("navset", mock_nav, select=True, session=mock_session)
        call_args = mock_session._send_message_sync.call_args[0][0]
        assert call_args["shiny-insert-tab"]["select"] is True

    def test_insert_nav_panel_string(self) -> None:
        """Test nav panel insertion with string nav (for menu items)."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._navs_dynamic.require_active_session", return_value=mock_session
        ):
            with patch("shiny.ui._navs_dynamic.menu_string_as_nav") as mock_menu:
                mock_nav = create_mock_nav()
                mock_menu.return_value = mock_nav
                insert_nav_panel("navset", "Menu Item", session=mock_session)
                mock_menu.assert_called_once_with("Menu Item")


class TestRemoveNavPanel:
    """Tests for remove_nav_panel function."""

    def test_remove_nav_panel(self) -> None:
        """Test removing a nav panel."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._navs_dynamic.require_active_session", return_value=mock_session
        ):
            remove_nav_panel("navset", "tab1", session=mock_session)
        mock_session._send_message_sync.assert_called_once()
        call_args = mock_session._send_message_sync.call_args[0][0]
        assert "shiny-remove-tab" in call_args
        assert call_args["shiny-remove-tab"]["target"] == "tab1"


class TestUpdateNavPanel:
    """Tests for update_nav_panel function."""

    def test_update_nav_panel_show(self) -> None:
        """Test showing a nav panel."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._navs_dynamic.require_active_session", return_value=mock_session
        ):
            update_nav_panel("navset", "tab1", method="show", session=mock_session)
        mock_session._send_message_sync.assert_called_once()
        call_args = mock_session._send_message_sync.call_args[0][0]
        assert "shiny-change-tab-visibility" in call_args
        assert call_args["shiny-change-tab-visibility"]["type"] == "show"

    def test_update_nav_panel_hide(self) -> None:
        """Test hiding a nav panel."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._navs_dynamic.require_active_session", return_value=mock_session
        ):
            update_nav_panel("navset", "tab1", method="hide", session=mock_session)
        call_args = mock_session._send_message_sync.call_args[0][0]
        assert call_args["shiny-change-tab-visibility"]["type"] == "hide"
