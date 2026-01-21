"""Tests for shiny/ui/_notification.py - notification functions."""

from unittest.mock import MagicMock, patch

from htmltools import tags

from shiny.ui._notification import notification_remove, notification_show


# =============================================================================
# Helper: Create mock session
# =============================================================================
def create_mock_session():
    """Create a mock session object for testing notification functions."""
    session = MagicMock()
    session._process_ui = MagicMock(
        side_effect=lambda x: (
            {"html": str(x), "deps": []} if x is not None else {"html": "", "deps": []}
        )
    )
    session._send_message_sync = MagicMock()
    return session


# =============================================================================
# Tests for notification_show
# =============================================================================
class TestNotificationShow:
    def test_basic_notification(self):
        """Test basic notification with simple text."""
        session = create_mock_session()
        with patch(
            "shiny.ui._notification.require_active_session", return_value=session
        ):
            result = notification_show("Hello, World!", session=session)

        session._send_message_sync.assert_called_once()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_notification_with_html(self):
        """Test notification with HTML content."""
        session = create_mock_session()
        with patch(
            "shiny.ui._notification.require_active_session", return_value=session
        ):
            result = notification_show(
                tags.div(tags.strong("Important"), " message"),
                session=session,
            )

        session._send_message_sync.assert_called_once()
        assert isinstance(result, str)

    def test_notification_with_action(self):
        """Test notification with action content."""
        session = create_mock_session()
        with patch(
            "shiny.ui._notification.require_active_session", return_value=session
        ):
            notification_show(
                "Message content",
                action=tags.a("Click here", href="#"),
                session=session,
            )

        session._send_message_sync.assert_called_once()
        call_args = session._send_message_sync.call_args[0][0]
        assert "notification" in call_args
        assert call_args["notification"]["message"]["action"] is not None

    def test_notification_duration_default(self):
        """Test notification with default duration (5 seconds)."""
        session = create_mock_session()
        with patch(
            "shiny.ui._notification.require_active_session", return_value=session
        ):
            notification_show("Test", session=session)

        call_args = session._send_message_sync.call_args[0][0]
        # Default duration is 5 seconds = 5000 ms
        assert call_args["notification"]["message"]["duration"] == 5000

    def test_notification_duration_custom(self):
        """Test notification with custom duration."""
        session = create_mock_session()
        with patch(
            "shiny.ui._notification.require_active_session", return_value=session
        ):
            notification_show("Test", duration=10, session=session)

        call_args = session._send_message_sync.call_args[0][0]
        assert call_args["notification"]["message"]["duration"] == 10000

    def test_notification_duration_none(self):
        """Test notification with no duration (persistent)."""
        session = create_mock_session()
        with patch(
            "shiny.ui._notification.require_active_session", return_value=session
        ):
            notification_show("Test", duration=None, session=session)

        call_args = session._send_message_sync.call_args[0][0]
        assert call_args["notification"]["message"]["duration"] is None

    def test_notification_duration_zero(self):
        """Test notification with zero duration."""
        session = create_mock_session()
        with patch(
            "shiny.ui._notification.require_active_session", return_value=session
        ):
            notification_show("Test", duration=0, session=session)

        call_args = session._send_message_sync.call_args[0][0]
        # Zero duration should not update (0 is falsy)
        assert (
            "duration" not in call_args["notification"]["message"]
            or call_args["notification"]["message"].get("duration") is None
        )

    def test_notification_close_button_true(self):
        """Test notification with close button enabled."""
        session = create_mock_session()
        with patch(
            "shiny.ui._notification.require_active_session", return_value=session
        ):
            notification_show("Test", close_button=True, session=session)

        call_args = session._send_message_sync.call_args[0][0]
        assert call_args["notification"]["message"]["closeButton"] is True

    def test_notification_close_button_false(self):
        """Test notification with close button disabled."""
        session = create_mock_session()
        with patch(
            "shiny.ui._notification.require_active_session", return_value=session
        ):
            notification_show("Test", close_button=False, session=session)

        call_args = session._send_message_sync.call_args[0][0]
        assert call_args["notification"]["message"]["closeButton"] is False

    def test_notification_custom_id(self):
        """Test notification with custom ID."""
        session = create_mock_session()
        with patch(
            "shiny.ui._notification.require_active_session", return_value=session
        ):
            result = notification_show("Test", id="my-notification", session=session)

        assert result == "my-notification"
        call_args = session._send_message_sync.call_args[0][0]
        assert call_args["notification"]["message"]["id"] == "my-notification"

    def test_notification_type_default(self):
        """Test notification with default type."""
        session = create_mock_session()
        with patch(
            "shiny.ui._notification.require_active_session", return_value=session
        ):
            notification_show("Test", session=session)

        call_args = session._send_message_sync.call_args[0][0]
        assert call_args["notification"]["message"]["type"] == "default"

    def test_notification_type_message(self):
        """Test notification with 'message' type."""
        session = create_mock_session()
        with patch(
            "shiny.ui._notification.require_active_session", return_value=session
        ):
            notification_show("Test", type="message", session=session)

        call_args = session._send_message_sync.call_args[0][0]
        assert call_args["notification"]["message"]["type"] == "message"

    def test_notification_type_warning(self):
        """Test notification with 'warning' type."""
        session = create_mock_session()
        with patch(
            "shiny.ui._notification.require_active_session", return_value=session
        ):
            notification_show("Test", type="warning", session=session)

        call_args = session._send_message_sync.call_args[0][0]
        assert call_args["notification"]["message"]["type"] == "warning"

    def test_notification_type_error(self):
        """Test notification with 'error' type."""
        session = create_mock_session()
        with patch(
            "shiny.ui._notification.require_active_session", return_value=session
        ):
            notification_show("Test", type="error", session=session)

        call_args = session._send_message_sync.call_args[0][0]
        assert call_args["notification"]["message"]["type"] == "error"

    def test_notification_message_structure(self):
        """Test notification message has correct structure."""
        session = create_mock_session()
        with patch(
            "shiny.ui._notification.require_active_session", return_value=session
        ):
            notification_show("Test", session=session)

        call_args = session._send_message_sync.call_args[0][0]
        assert "notification" in call_args
        assert call_args["notification"]["type"] == "show"
        message = call_args["notification"]["message"]
        assert "html" in message
        assert "action" in message
        assert "deps" in message
        assert "closeButton" in message
        assert "id" in message
        assert "type" in message

    def test_notification_returns_id(self):
        """Test that notification_show returns the notification ID."""
        session = create_mock_session()
        with patch(
            "shiny.ui._notification.require_active_session", return_value=session
        ):
            result = notification_show("Test", id="test-id", session=session)

        assert result == "test-id"

    def test_notification_generates_id_when_none(self):
        """Test that notification generates an ID when none provided."""
        session = create_mock_session()
        with patch(
            "shiny.ui._notification.require_active_session", return_value=session
        ):
            result = notification_show("Test", session=session)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_notification_float_duration(self):
        """Test notification with float duration."""
        session = create_mock_session()
        with patch(
            "shiny.ui._notification.require_active_session", return_value=session
        ):
            notification_show("Test", duration=2.5, session=session)

        call_args = session._send_message_sync.call_args[0][0]
        assert call_args["notification"]["message"]["duration"] == 2500


# =============================================================================
# Tests for notification_remove
# =============================================================================
class TestNotificationRemove:
    def test_basic_remove(self):
        """Test basic notification removal."""
        session = create_mock_session()
        with patch(
            "shiny.ui._notification.require_active_session", return_value=session
        ):
            result = notification_remove("my-notification", session=session)

        session._send_message_sync.assert_called_once()
        assert result == "my-notification"

    def test_remove_message_structure(self):
        """Test notification remove message has correct structure."""
        session = create_mock_session()
        with patch(
            "shiny.ui._notification.require_active_session", return_value=session
        ):
            notification_remove("test-id", session=session)

        call_args = session._send_message_sync.call_args[0][0]
        assert "notification" in call_args
        assert call_args["notification"]["type"] == "remove"
        assert call_args["notification"]["message"] == "test-id"

    def test_remove_returns_id(self):
        """Test that notification_remove returns the notification ID."""
        session = create_mock_session()
        with patch(
            "shiny.ui._notification.require_active_session", return_value=session
        ):
            result = notification_remove("notification-123", session=session)

        assert result == "notification-123"

    def test_remove_different_ids(self):
        """Test removing notifications with different IDs."""
        session = create_mock_session()
        with patch(
            "shiny.ui._notification.require_active_session", return_value=session
        ):
            result1 = notification_remove("id-1", session=session)
            result2 = notification_remove("id-2", session=session)

        assert result1 == "id-1"
        assert result2 == "id-2"
        assert session._send_message_sync.call_count == 2
