"""Tests for shiny/ui/_modal.py"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from htmltools import Tag

from shiny.ui._modal import modal, modal_button, modal_remove, modal_show


def create_mock_session() -> MagicMock:
    """Create a mock session for testing modal functions."""
    mock = MagicMock()
    mock._process_ui.return_value = {"html": "<div>test</div>", "deps": []}
    return mock


class TestModalButton:
    """Tests for modal_button function."""

    def test_modal_button_basic(self) -> None:
        """Test basic modal button creation."""
        result = modal_button("Close")
        assert isinstance(result, Tag)
        html = str(result)
        assert "Close" in html
        assert "btn" in html

    def test_modal_button_with_icon(self) -> None:
        """Test modal button with icon."""
        result = modal_button("Close", icon="icon-x")
        html = str(result)
        assert "Close" in html
        assert "icon-x" in html

    def test_modal_button_with_kwargs(self) -> None:
        """Test modal button with custom attributes."""
        result = modal_button("Close", id="close-btn", class_="custom-class")
        html = str(result)
        assert "close-btn" in html
        assert "custom-class" in html


class TestModal:
    """Tests for modal function."""

    def test_modal_basic(self) -> None:
        """Test basic modal creation."""
        result = modal("Hello, World!")
        assert isinstance(result, Tag)
        html = str(result)
        assert "modal" in html
        assert "Hello, World!" in html

    def test_modal_with_title(self) -> None:
        """Test modal with title."""
        result = modal("Content", title="My Title")
        html = str(result)
        assert "My Title" in html
        assert "modal-title" in html

    def test_modal_footer_none(self) -> None:
        """Test modal with no footer."""
        result = modal("Content", footer=None)
        html = str(result)
        assert "modal-footer" not in html

    def test_modal_custom_footer(self) -> None:
        """Test modal with custom footer."""
        result = modal("Content", footer="Custom Footer")
        html = str(result)
        assert "Custom Footer" in html
        assert "modal-footer" in html

    def test_modal_size_small(self) -> None:
        """Test modal with small size."""
        result = modal("Content", size="s")
        html = str(result)
        assert "modal-sm" in html

    def test_modal_size_large(self) -> None:
        """Test modal with large size."""
        result = modal("Content", size="l")
        html = str(result)
        assert "modal-lg" in html

    def test_modal_size_xl(self) -> None:
        """Test modal with xl size."""
        result = modal("Content", size="xl")
        html = str(result)
        assert "modal-xl" in html

    def test_modal_easy_close(self) -> None:
        """Test modal with easy close enabled."""
        result = modal("Content", easy_close=True)
        html = str(result)
        assert 'data-backdrop="static"' not in html

    def test_modal_no_easy_close(self) -> None:
        """Test modal with easy close disabled (default)."""
        result = modal("Content", easy_close=False)
        html = str(result)
        assert "static" in html

    def test_modal_no_fade(self) -> None:
        """Test modal without fade animation."""
        result = modal("Content", fade=False)
        html = str(result)
        assert 'class="modal"' in html


class TestModalShow:
    """Tests for modal_show function."""

    def test_modal_show(self) -> None:
        """Test showing a modal."""
        mock_session = create_mock_session()
        modal_ui = modal("Content")
        with patch("shiny.ui._modal.require_active_session", return_value=mock_session):
            modal_show(modal_ui, session=mock_session)
        mock_session._send_message_sync.assert_called_once()
        call_args = mock_session._send_message_sync.call_args[0][0]
        assert "modal" in call_args
        assert call_args["modal"]["type"] == "show"


class TestModalRemove:
    """Tests for modal_remove function."""

    def test_modal_remove(self) -> None:
        """Test removing a modal."""
        mock_session = create_mock_session()
        with patch("shiny.ui._modal.require_active_session", return_value=mock_session):
            modal_remove(session=mock_session)
        mock_session._send_message_sync.assert_called_once()
        call_args = mock_session._send_message_sync.call_args[0][0]
        assert "modal" in call_args
        assert call_args["modal"]["type"] == "remove"
