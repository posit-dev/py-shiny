"""Tests for shiny._launchbrowser module."""

import logging
from unittest.mock import patch

from shiny._launchbrowser import LaunchBrowserHandler


class TestLaunchBrowserHandler:
    """Tests for LaunchBrowserHandler class."""

    def test_handler_is_logging_handler(self):
        """LaunchBrowserHandler should be a logging Handler."""
        handler = LaunchBrowserHandler()
        assert isinstance(handler, logging.Handler)

    def test_handler_initial_state(self):
        """LaunchBrowserHandler should start with _launched=False."""
        handler = LaunchBrowserHandler()
        assert handler._launched is False

    def test_emit_ignores_other_messages(self):
        """emit should ignore messages that don't indicate startup."""
        handler = LaunchBrowserHandler()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Some other message",
            args=(),
            exc_info=None,
        )
        handler.emit(record)
        # _launched should still be False
        assert handler._launched is False

    @patch.dict(
        "os.environ", {"SHINY_BROWSER_PORT": "8000", "SHINY_BROWSER_HOST": "localhost"}
    )
    @patch("webbrowser.open")
    @patch("shiny._launchbrowser.get_proxy_url", return_value="http://localhost:8000/")
    def test_emit_launches_browser_on_startup_message(self, mock_proxy, mock_open):
        """emit should launch browser when startup message detected."""
        handler = LaunchBrowserHandler()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Application startup complete.",
            args=(),
            exc_info=None,
        )
        handler.emit(record)
        # _launched should be True
        assert handler._launched is True
        # webbrowser.open should have been called
        mock_open.assert_called_once()

    @patch.dict(
        "os.environ", {"SHINY_BROWSER_PORT": "8000", "SHINY_BROWSER_HOST": "localhost"}
    )
    @patch("webbrowser.open")
    @patch("shiny._launchbrowser.get_proxy_url", return_value="http://localhost:8000/")
    def test_emit_only_launches_once(self, mock_proxy, mock_open):
        """emit should only launch browser once."""
        handler = LaunchBrowserHandler()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Application startup complete.",
            args=(),
            exc_info=None,
        )
        # First emit
        handler.emit(record)
        # Second emit
        handler.emit(record)
        # webbrowser.open should only have been called once
        assert mock_open.call_count == 1

    @patch.dict(
        "os.environ",
        {"SHINY_BROWSER_PORT": "invalid", "SHINY_BROWSER_HOST": "localhost"},
    )
    def test_emit_handles_invalid_port(self):
        """emit should handle non-numeric port gracefully."""
        handler = LaunchBrowserHandler()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Application startup complete.",
            args=(),
            exc_info=None,
        )
        # This should not raise an error
        handler.emit(record)
        # _launched should be True (message was detected)
        assert handler._launched is True

    def test_emit_skips_if_already_launched(self):
        """emit should skip processing if already launched."""
        handler = LaunchBrowserHandler()
        handler._launched = True
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Application startup complete.",
            args=(),
            exc_info=None,
        )
        # This should return early
        handler.emit(record)
        # Should still be True
        assert handler._launched is True
