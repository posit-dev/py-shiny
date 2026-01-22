"""Tests for shiny/ui/_progress.py"""

from __future__ import annotations

import warnings
from unittest.mock import MagicMock, patch

from shiny.ui._progress import Progress


def create_mock_session() -> MagicMock:
    """Create a mock session for testing Progress."""
    mock = MagicMock()
    mock.ns.return_value = "test_id"
    return mock


class TestProgress:
    """Tests for Progress class."""

    def test_progress_init(self) -> None:
        """Test Progress initialization."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._progress.require_active_session", return_value=mock_session
        ):
            with patch("shiny.ui._progress.rand_hex", return_value="abcd1234"):
                progress = Progress(min=0, max=100, session=mock_session)
        assert progress.min == 0
        assert progress.max == 100
        assert progress.value is None
        mock_session._send_progress.assert_called_once()
        call_args = mock_session._send_progress.call_args
        assert call_args[0][0] == "open"

    def test_progress_context_manager(self) -> None:
        """Test Progress as context manager."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._progress.require_active_session", return_value=mock_session
        ):
            with Progress(session=mock_session) as p:
                assert isinstance(p, Progress)
        calls = mock_session._send_progress.call_args_list
        assert calls[0][0][0] == "open"
        assert calls[1][0][0] == "close"

    def test_progress_set_value(self) -> None:
        """Test Progress.set() with value."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._progress.require_active_session", return_value=mock_session
        ):
            progress = Progress(min=0, max=100, session=mock_session)
            progress.set(value=50)
        assert progress.value == 50
        calls = mock_session._send_progress.call_args_list
        assert calls[1][0][0] == "update"

    def test_progress_set_message(self) -> None:
        """Test Progress.set() with message."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._progress.require_active_session", return_value=mock_session
        ):
            progress = Progress(session=mock_session)
            progress.set(message="Processing...")
        calls = mock_session._send_progress.call_args_list
        msg = calls[1][0][1]
        assert msg["message"] == "Processing..."

    def test_progress_set_detail(self) -> None:
        """Test Progress.set() with detail."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._progress.require_active_session", return_value=mock_session
        ):
            progress = Progress(session=mock_session)
            progress.set(detail="Step 1 of 10")
        calls = mock_session._send_progress.call_args_list
        msg = calls[1][0][1]
        assert msg["detail"] == "Step 1 of 10"

    def test_progress_set_after_close_warns(self) -> None:
        """Test that set() after close() warns."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._progress.require_active_session", return_value=mock_session
        ):
            progress = Progress(session=mock_session)
            progress.close()
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                progress.set(value=50)
                assert len(w) == 1
                assert "already closed" in str(w[0].message)

    def test_progress_inc(self) -> None:
        """Test Progress.inc() increments value."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._progress.require_active_session", return_value=mock_session
        ):
            progress = Progress(min=0, max=1, session=mock_session)
            progress.inc(amount=0.2)
            assert progress.value == 0.2
            progress.inc(amount=0.3)
            assert progress.value == 0.5

    def test_progress_inc_from_none(self) -> None:
        """Test Progress.inc() when value is None starts from min."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._progress.require_active_session", return_value=mock_session
        ):
            progress = Progress(min=10, max=100, session=mock_session)
            assert progress.value is None
            progress.inc(amount=5)
            assert progress.value == 15

    def test_progress_inc_caps_at_max(self) -> None:
        """Test Progress.inc() caps at max value."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._progress.require_active_session", return_value=mock_session
        ):
            progress = Progress(min=0, max=1, session=mock_session)
            progress.inc(amount=1.5)
            assert progress.value == 1

    def test_progress_close(self) -> None:
        """Test Progress.close()."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._progress.require_active_session", return_value=mock_session
        ):
            progress = Progress(session=mock_session)
            progress.close()
        calls = mock_session._send_progress.call_args_list
        assert calls[1][0][0] == "close"

    def test_progress_double_close_warns(self) -> None:
        """Test that close() after close() warns."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._progress.require_active_session", return_value=mock_session
        ):
            progress = Progress(session=mock_session)
            progress.close()
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                progress.close()
                assert len(w) == 1
                assert "already closed" in str(w[0].message)

    def test_progress_normalizes_value(self) -> None:
        """Test that set() normalizes value to 0-1 range."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._progress.require_active_session", return_value=mock_session
        ):
            progress = Progress(min=0, max=200, session=mock_session)
            progress.set(value=100)
        calls = mock_session._send_progress.call_args_list
        msg = calls[1][0][1]
        assert msg["value"] == 0.5

    def test_progress_inc_with_message_and_detail(self) -> None:
        """Test Progress.inc() with message and detail."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._progress.require_active_session", return_value=mock_session
        ):
            progress = Progress(session=mock_session)
            progress.inc(amount=0.1, message="Loading", detail="Please wait")
        calls = mock_session._send_progress.call_args_list
        msg = calls[1][0][1]
        assert msg["message"] == "Loading"
        assert msg["detail"] == "Please wait"
