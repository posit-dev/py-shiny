"""Tests for shiny/ui/_notification.py"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from shiny.ui._notification import notification_remove, notification_show


def create_mock_session() -> MagicMock:
    """Create a mock session for testing notification functions."""
    mock = MagicMock()
    mock._process_ui.return_value = {"html": "<div>test</div>", "deps": []}
    return mock


class TestNotificationShow:
    """Tests for notification_show function."""

    def test_notification_show_basic(self) -> None:
        """Test showing a basic notification."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._notification.require_active_session", return_value=mock_session
        ):
            result = notification_show("Hello", session=mock_session)
        assert isinstance(result, str)
        mock_session._send_message_sync.assert_called_once()
        call_args = mock_session._send_message_sync.call_args[0][0]
        assert "notification" in call_args
        assert call_args["notification"]["type"] == "show"

    def test_notification_show_with_action(self) -> None:
        """Test notification with action content."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._notification.require_active_session", return_value=mock_session
        ):
            result = notification_show(
                "Message", action="Click here", session=mock_session
            )
        assert isinstance(result, str)
        mock_session._send_message_sync.assert_called_once()

    def test_notification_show_with_duration(self) -> None:
        """Test notification with custom duration."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._notification.require_active_session", return_value=mock_session
        ):
            notification_show("Message", duration=10, session=mock_session)
        call_args = mock_session._send_message_sync.call_args[0][0]
        assert call_args["notification"]["message"]["duration"] == 10000

    def test_notification_show_with_duration_none(self) -> None:
        """Test notification with None duration (persistent)."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._notification.require_active_session", return_value=mock_session
        ):
            notification_show("Message", duration=None, session=mock_session)
        call_args = mock_session._send_message_sync.call_args[0][0]
        assert call_args["notification"]["message"]["duration"] is None

    def test_notification_show_no_close_button(self) -> None:
        """Test notification without close button."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._notification.require_active_session", return_value=mock_session
        ):
            notification_show("Message", close_button=False, session=mock_session)
        call_args = mock_session._send_message_sync.call_args[0][0]
        assert call_args["notification"]["message"]["closeButton"] is False

    def test_notification_show_with_custom_id(self) -> None:
        """Test notification with custom ID."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._notification.require_active_session", return_value=mock_session
        ):
            result = notification_show("Message", id="my-notif", session=mock_session)
        assert result == "my-notif"
        call_args = mock_session._send_message_sync.call_args[0][0]
        assert call_args["notification"]["message"]["id"] == "my-notif"

    def test_notification_show_with_type_message(self) -> None:
        """Test notification with message type."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._notification.require_active_session", return_value=mock_session
        ):
            notification_show("Message", type="message", session=mock_session)
        call_args = mock_session._send_message_sync.call_args[0][0]
        assert call_args["notification"]["message"]["type"] == "message"

    def test_notification_show_with_type_warning(self) -> None:
        """Test notification with warning type."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._notification.require_active_session", return_value=mock_session
        ):
            notification_show("Message", type="warning", session=mock_session)
        call_args = mock_session._send_message_sync.call_args[0][0]
        assert call_args["notification"]["message"]["type"] == "warning"

    def test_notification_show_with_type_error(self) -> None:
        """Test notification with error type."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._notification.require_active_session", return_value=mock_session
        ):
            notification_show("Message", type="error", session=mock_session)
        call_args = mock_session._send_message_sync.call_args[0][0]
        assert call_args["notification"]["message"]["type"] == "error"


class TestNotificationRemove:
    """Tests for notification_remove function."""

    def test_notification_remove(self) -> None:
        """Test removing a notification."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._notification.require_active_session", return_value=mock_session
        ):
            result = notification_remove("my-notif", session=mock_session)
        assert result == "my-notif"
        mock_session._send_message_sync.assert_called_once()
        call_args = mock_session._send_message_sync.call_args[0][0]
        assert call_args["notification"]["type"] == "remove"
        assert call_args["notification"]["message"] == "my-notif"
