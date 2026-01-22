"""Tests for shiny/ui/_notification.py module."""

from shiny.ui._notification import (
    notification_remove,
    notification_show,
)


class TestNotificationShow:
    """Tests for notification_show function."""

    def test_notification_show_is_callable(self):
        """Test notification_show is callable."""
        assert callable(notification_show)


class TestNotificationRemove:
    """Tests for notification_remove function."""

    def test_notification_remove_is_callable(self):
        """Test notification_remove is callable."""
        assert callable(notification_remove)


class TestNotificationExported:
    """Tests for notification functions export."""

    def test_notification_show_in_ui(self):
        """Test notification_show is in ui module."""
        from shiny import ui

        assert hasattr(ui, "notification_show")

    def test_notification_remove_in_ui(self):
        """Test notification_remove is in ui module."""
        from shiny import ui

        assert hasattr(ui, "notification_remove")
