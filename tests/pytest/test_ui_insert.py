"""Tests for shiny/ui/_insert.py"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from shiny.ui._insert import insert_ui, remove_ui


def create_mock_session() -> MagicMock:
    """Create a mock session for testing insert/remove UI functions."""
    mock = MagicMock()
    mock._process_ui.return_value = {"html": "<div>test</div>", "deps": []}
    return mock


class TestInsertUI:
    """Tests for insert_ui function."""

    def test_insert_ui_default_where(self) -> None:
        """Test insert_ui with default where parameter."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._insert.require_active_session", return_value=mock_session
        ):
            insert_ui("<div>content</div>", selector="#target", session=mock_session)
        mock_session.on_flushed.assert_called_once()

    def test_insert_ui_immediate(self) -> None:
        """Test insert_ui with immediate=True."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._insert.require_active_session", return_value=mock_session
        ):
            insert_ui(
                "<div>content</div>",
                selector="#target",
                immediate=True,
                session=mock_session,
            )
        mock_session._send_insert_ui.assert_called_once()
        mock_session.on_flushed.assert_not_called()

    def test_insert_ui_where_before_begin(self) -> None:
        """Test insert_ui with where='beforeBegin'."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._insert.require_active_session", return_value=mock_session
        ):
            insert_ui(
                "<div>content</div>",
                selector="#target",
                where="beforeBegin",
                immediate=True,
                session=mock_session,
            )
        call_args = mock_session._send_insert_ui.call_args
        assert call_args.kwargs["where"] == "beforeBegin"

    def test_insert_ui_where_after_begin(self) -> None:
        """Test insert_ui with where='afterBegin'."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._insert.require_active_session", return_value=mock_session
        ):
            insert_ui(
                "<div>content</div>",
                selector="#target",
                where="afterBegin",
                immediate=True,
                session=mock_session,
            )
        call_args = mock_session._send_insert_ui.call_args
        assert call_args.kwargs["where"] == "afterBegin"

    def test_insert_ui_where_after_end(self) -> None:
        """Test insert_ui with where='afterEnd'."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._insert.require_active_session", return_value=mock_session
        ):
            insert_ui(
                "<div>content</div>",
                selector="#target",
                where="afterEnd",
                immediate=True,
                session=mock_session,
            )
        call_args = mock_session._send_insert_ui.call_args
        assert call_args.kwargs["where"] == "afterEnd"

    def test_insert_ui_with_multiple(self) -> None:
        """Test insert_ui with multiple=True."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._insert.require_active_session", return_value=mock_session
        ):
            insert_ui(
                "<div>content</div>",
                selector=".target",
                multiple=True,
                immediate=True,
                session=mock_session,
            )
        call_args = mock_session._send_insert_ui.call_args
        assert call_args.kwargs["multiple"] is True


class TestRemoveUI:
    """Tests for remove_ui function."""

    def test_remove_ui_default(self) -> None:
        """Test remove_ui with defaults."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._insert.require_active_session", return_value=mock_session
        ):
            remove_ui(selector="#target", session=mock_session)
        mock_session.on_flushed.assert_called_once()

    def test_remove_ui_immediate(self) -> None:
        """Test remove_ui with immediate=True."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._insert.require_active_session", return_value=mock_session
        ):
            remove_ui(selector="#target", immediate=True, session=mock_session)
        mock_session._send_remove_ui.assert_called_once()
        mock_session.on_flushed.assert_not_called()

    def test_remove_ui_with_multiple(self) -> None:
        """Test remove_ui with multiple=True."""
        mock_session = create_mock_session()
        with patch(
            "shiny.ui._insert.require_active_session", return_value=mock_session
        ):
            remove_ui(
                selector=".target", multiple=True, immediate=True, session=mock_session
            )
        call_args = mock_session._send_remove_ui.call_args
        assert call_args.kwargs["multiple"] is True
