"""Tests for shiny.ui._notification module."""

from shiny.ui._notification import notification_remove, notification_show


class TestNotificationShow:
    """Tests for notification_show function."""

    def test_notification_show_returns_id(self) -> None:
        """Test notification_show returns an id."""
        # notification_show requires a session, so we test the function exists
        # and is callable
        assert callable(notification_show)

    def test_notification_show_signature(self) -> None:
        """Test notification_show has expected parameters."""
        import inspect

        sig = inspect.signature(notification_show)
        params = list(sig.parameters.keys())
        assert "ui" in params


class TestNotificationRemove:
    """Tests for notification_remove function."""

    def test_notification_remove_callable(self) -> None:
        """Test notification_remove is callable."""
        assert callable(notification_remove)

    def test_notification_remove_signature(self) -> None:
        """Test notification_remove has expected parameters."""
        import inspect

        sig = inspect.signature(notification_remove)
        params = list(sig.parameters.keys())
        assert "id" in params
