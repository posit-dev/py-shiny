"""Tests for shiny/ui/_chat.py - Chat exports."""

from shiny.ui._chat import (
    Chat,
    ChatExpress,
    chat_ui,
    ChatMessageDict,
    __all__,
)


class TestChatExports:
    """Tests for chat exports."""

    def test_chat_exported(self):
        """Test Chat is exported."""
        assert Chat is not None

    def test_chat_express_exported(self):
        """Test ChatExpress is exported."""
        assert ChatExpress is not None

    def test_chat_ui_exported(self):
        """Test chat_ui is exported."""
        assert chat_ui is not None
        assert callable(chat_ui)

    def test_chatmessagedict_exported(self):
        """Test ChatMessageDict is exported."""
        assert ChatMessageDict is not None


class TestChatAll:
    """Tests for __all__ exports."""

    def test_all_is_tuple(self):
        """Test __all__ is a tuple."""
        assert isinstance(__all__, tuple)

    def test_all_contains_chat(self):
        """Test __all__ contains Chat."""
        assert "Chat" in __all__

    def test_all_contains_chat_express(self):
        """Test __all__ contains ChatExpress."""
        assert "ChatExpress" in __all__

    def test_all_contains_chat_ui(self):
        """Test __all__ contains chat_ui."""
        assert "chat_ui" in __all__

    def test_all_contains_chatmessagedict(self):
        """Test __all__ contains ChatMessageDict."""
        assert "ChatMessageDict" in __all__
