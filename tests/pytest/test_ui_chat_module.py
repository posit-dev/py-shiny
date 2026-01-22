from __future__ import annotations


def test_chat_module_exports() -> None:
    import pytest

    pytest.importorskip("shinychat")
    from shiny.ui import _chat

    assert set(_chat.__all__) == {"Chat", "ChatExpress", "chat_ui", "ChatMessageDict"}
    assert callable(_chat.Chat)
    assert callable(_chat.ChatExpress)
    assert callable(_chat.chat_ui)
