"""Tests for shiny/ui/_progress.py - Progress class."""

import warnings
from unittest.mock import MagicMock, patch

from shiny.ui._progress import Progress


# =============================================================================
# Helper: Create mock session
# =============================================================================
def create_mock_session():
    """Create a mock session object for testing Progress class."""
    session = MagicMock()
    session._send_progress = MagicMock()
    session.ns = MagicMock(side_effect=lambda x: f"ns_{x}")
    return session


# =============================================================================
# Tests for Progress class initialization
# =============================================================================
class TestProgressInit:
    def test_basic_init(self):
        """Test basic Progress initialization."""
        session = create_mock_session()
        with patch("shiny.ui._progress.require_active_session", return_value=session):
            progress = Progress(session=session)

        assert progress.min == 0
        assert progress.max == 1
        assert progress.value is None
        assert progress._closed is False
        session._send_progress.assert_called_once_with(
            "open", {"id": progress._id, "style": "notification"}
        )

    def test_init_with_min_max(self):
        """Test Progress initialization with custom min/max."""
        session = create_mock_session()
        with patch("shiny.ui._progress.require_active_session", return_value=session):
            progress = Progress(min=10, max=100, session=session)

        assert progress.min == 10
        assert progress.max == 100

    def test_init_sends_open_message(self):
        """Test Progress sends 'open' message on init."""
        session = create_mock_session()
        with patch("shiny.ui._progress.require_active_session", return_value=session):
            Progress(session=session)

        session._send_progress.assert_called_once()
        call_args = session._send_progress.call_args
        assert call_args[0][0] == "open"
        assert "id" in call_args[0][1]
        assert call_args[0][1]["style"] == "notification"


# =============================================================================
# Tests for Progress.set()
# =============================================================================
class TestProgressSet:
    def test_set_value(self):
        """Test Progress.set() with value."""
        session = create_mock_session()
        with patch("shiny.ui._progress.require_active_session", return_value=session):
            progress = Progress(min=0, max=100, session=session)
            progress.set(value=50)

        assert progress.value == 50
        # Called twice: once for open, once for update
        assert session._send_progress.call_count == 2
        update_call = session._send_progress.call_args_list[1]
        assert update_call[0][0] == "update"
        # Normalized value: (50 - 0) / (100 - 0) = 0.5
        assert update_call[0][1]["value"] == 0.5

    def test_set_message(self):
        """Test Progress.set() with message."""
        session = create_mock_session()
        with patch("shiny.ui._progress.require_active_session", return_value=session):
            progress = Progress(session=session)
            progress.set(message="Processing...")

        update_call = session._send_progress.call_args_list[1]
        assert update_call[0][1]["message"] == "Processing..."

    def test_set_detail(self):
        """Test Progress.set() with detail."""
        session = create_mock_session()
        with patch("shiny.ui._progress.require_active_session", return_value=session):
            progress = Progress(session=session)
            progress.set(detail="Step 1 of 10")

        update_call = session._send_progress.call_args_list[1]
        assert update_call[0][1]["detail"] == "Step 1 of 10"

    def test_set_all_params(self):
        """Test Progress.set() with all parameters."""
        session = create_mock_session()
        with patch("shiny.ui._progress.require_active_session", return_value=session):
            progress = Progress(min=0, max=100, session=session)
            progress.set(value=25, message="Loading", detail="25%")

        update_call = session._send_progress.call_args_list[1]
        assert update_call[0][1]["value"] == 0.25
        assert update_call[0][1]["message"] == "Loading"
        assert update_call[0][1]["detail"] == "25%"

    def test_set_value_normalization_min_max(self):
        """Test Progress.set() normalizes value between 0 and 1."""
        session = create_mock_session()
        with patch("shiny.ui._progress.require_active_session", return_value=session):
            progress = Progress(min=10, max=110, session=session)
            progress.set(value=60)  # (60-10)/(110-10) = 0.5

        update_call = session._send_progress.call_args_list[1]
        assert update_call[0][1]["value"] == 0.5

    def test_set_value_clamp_above_max(self):
        """Test Progress.set() clamps value above max to 1."""
        session = create_mock_session()
        with patch("shiny.ui._progress.require_active_session", return_value=session):
            progress = Progress(min=0, max=100, session=session)
            progress.set(value=150)  # Above max

        update_call = session._send_progress.call_args_list[1]
        assert update_call[0][1]["value"] == 1.0

    def test_set_value_clamp_below_min(self):
        """Test Progress.set() clamps value below min to 0."""
        session = create_mock_session()
        with patch("shiny.ui._progress.require_active_session", return_value=session):
            progress = Progress(min=0, max=100, session=session)
            progress.set(value=-50)  # Below min

        update_call = session._send_progress.call_args_list[1]
        assert update_call[0][1]["value"] == 0.0

    def test_set_none_value(self):
        """Test Progress.set() with None value hides progress bar."""
        session = create_mock_session()
        with patch("shiny.ui._progress.require_active_session", return_value=session):
            progress = Progress(session=session)
            progress.set(value=None, message="Working")

        # Value should not be in message if None
        update_call = session._send_progress.call_args_list[1]
        assert "value" not in update_call[0][1]

    def test_set_after_close_warns(self):
        """Test Progress.set() after close shows warning."""
        session = create_mock_session()
        with patch("shiny.ui._progress.require_active_session", return_value=session):
            progress = Progress(session=session)
            progress.close()

            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                result = progress.set(value=50)
                assert len(w) == 1
                assert "already closed" in str(w[0].message)
                assert result is None


# =============================================================================
# Tests for Progress.inc()
# =============================================================================
class TestProgressInc:
    def test_inc_default_amount(self):
        """Test Progress.inc() with default amount."""
        session = create_mock_session()
        with patch("shiny.ui._progress.require_active_session", return_value=session):
            progress = Progress(min=0, max=1, session=session)
            progress.inc()

        assert progress.value == 0.1  # Default increment

    def test_inc_custom_amount(self):
        """Test Progress.inc() with custom amount."""
        session = create_mock_session()
        with patch("shiny.ui._progress.require_active_session", return_value=session):
            progress = Progress(min=0, max=1, session=session)
            progress.inc(amount=0.25)

        assert progress.value == 0.25

    def test_inc_from_none(self):
        """Test Progress.inc() when value is None starts from min."""
        session = create_mock_session()
        with patch("shiny.ui._progress.require_active_session", return_value=session):
            progress = Progress(min=10, max=100, session=session)
            assert progress.value is None
            progress.inc(amount=5)

        assert progress.value == 15  # min + amount = 10 + 5

    def test_inc_with_message(self):
        """Test Progress.inc() with message."""
        session = create_mock_session()
        with patch("shiny.ui._progress.require_active_session", return_value=session):
            progress = Progress(session=session)
            progress.inc(message="Processing")

        update_call = session._send_progress.call_args_list[1]
        assert update_call[0][1]["message"] == "Processing"

    def test_inc_with_detail(self):
        """Test Progress.inc() with detail."""
        session = create_mock_session()
        with patch("shiny.ui._progress.require_active_session", return_value=session):
            progress = Progress(session=session)
            progress.inc(detail="Item 1")

        update_call = session._send_progress.call_args_list[1]
        assert update_call[0][1]["detail"] == "Item 1"

    def test_inc_clamps_at_max(self):
        """Test Progress.inc() clamps at max value."""
        session = create_mock_session()
        with patch("shiny.ui._progress.require_active_session", return_value=session):
            progress = Progress(min=0, max=1, session=session)
            progress.set(value=0.9)
            progress.inc(amount=0.5)  # Would exceed max

        assert progress.value == 1.0  # Clamped at max

    def test_inc_multiple_times(self):
        """Test Progress.inc() multiple times."""
        session = create_mock_session()
        with patch("shiny.ui._progress.require_active_session", return_value=session):
            progress = Progress(min=0, max=100, session=session)
            progress.inc(amount=10)
            progress.inc(amount=20)
            progress.inc(amount=30)

        assert progress.value == 60  # 0 + 10 + 20 + 30


# =============================================================================
# Tests for Progress.close()
# =============================================================================
class TestProgressClose:
    def test_close(self):
        """Test Progress.close() sends close message."""
        session = create_mock_session()
        with patch("shiny.ui._progress.require_active_session", return_value=session):
            progress = Progress(session=session)
            progress.close()

        assert progress._closed is True
        # Check close message was sent
        close_call = session._send_progress.call_args_list[-1]
        assert close_call[0][0] == "close"

    def test_close_twice_warns(self):
        """Test Progress.close() twice shows warning."""
        session = create_mock_session()
        with patch("shiny.ui._progress.require_active_session", return_value=session):
            progress = Progress(session=session)
            progress.close()

            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                result = progress.close()
                assert len(w) == 1
                assert "already closed" in str(w[0].message)
                assert result is None


# =============================================================================
# Tests for Progress context manager
# =============================================================================
class TestProgressContextManager:
    def test_context_manager_enter(self):
        """Test Progress as context manager - __enter__."""
        session = create_mock_session()
        with patch("shiny.ui._progress.require_active_session", return_value=session):
            progress = Progress(session=session)
            result = progress.__enter__()

        assert result is progress

    def test_context_manager_exit(self):
        """Test Progress as context manager - __exit__."""
        session = create_mock_session()
        with patch("shiny.ui._progress.require_active_session", return_value=session):
            progress = Progress(session=session)
            progress.__exit__(None, None, None)

        assert progress._closed is True

    def test_with_statement(self):
        """Test Progress with 'with' statement."""
        session = create_mock_session()
        with patch("shiny.ui._progress.require_active_session", return_value=session):
            with Progress(session=session) as progress:
                progress.set(value=0.5, message="Half done")
                assert progress._closed is False

            # After exiting the context, should be closed
            assert progress._closed is True

    def test_with_statement_exception(self):
        """Test Progress with 'with' statement when exception occurs."""
        session = create_mock_session()
        with patch("shiny.ui._progress.require_active_session", return_value=session):
            try:
                with Progress(session=session) as progress:
                    raise ValueError("Test exception")
            except ValueError:
                pass

            # Should still be closed even after exception
            assert progress._closed is True


# =============================================================================
# Tests for Progress style
# =============================================================================
class TestProgressStyle:
    def test_default_style(self):
        """Test Progress default style is 'notification'."""
        assert Progress._style == "notification"

    def test_style_in_messages(self):
        """Test Progress style is included in messages."""
        session = create_mock_session()
        with patch("shiny.ui._progress.require_active_session", return_value=session):
            Progress(session=session)

        open_call = session._send_progress.call_args_list[0]
        assert open_call[0][1]["style"] == "notification"
