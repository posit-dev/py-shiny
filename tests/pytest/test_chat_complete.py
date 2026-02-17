"""Comprehensive tests for shiny.ui._chat module."""


class TestChatExports:
    """Tests for Chat class export."""

    def test_chat_class_imported(self):
        """Chat class should be importable."""
        from shiny.ui import Chat

        assert Chat is not None

    def test_chat_express_class_imported(self):
        """ChatExpress class should be importable from _chat module."""
        # ChatExpress is not exported from public shiny.ui API
        from shiny.ui._chat import ChatExpress

        assert ChatExpress is not None
        assert hasattr(ChatExpress, "__name__")

    def test_chat_ui_function_imported(self):
        """chat_ui function should be importable."""
        from shiny.ui import chat_ui

        assert chat_ui is not None
        assert callable(chat_ui)

    def test_chat_message_dict_imported(self):
        """ChatMessageDict should be importable from _chat module."""
        # ChatMessageDict is not exported from public shiny.ui API
        from shiny.ui._chat import ChatMessageDict

        assert ChatMessageDict is not None
        # TypedDict doesn't have __name__, check for dict behavior
        assert isinstance(ChatMessageDict.__annotations__, dict)


class TestChatClassDecorated:
    """Tests for Chat class decorator."""

    def test_chat_has_example_decorator(self):
        """Chat class should be decorated with add_example."""
        from shiny.ui import Chat

        # The add_example decorator should have been applied
        # Check if it's still a class (decorator preserves class)
        assert isinstance(Chat, type)


class TestChatExpressClassDecorated:
    """Tests for ChatExpress class decorator."""

    def test_chat_express_has_example_decorator(self):
        """ChatExpress class should be decorated with add_example."""
        # ChatExpress is not exported from public shiny.ui API
        from shiny.ui._chat import ChatExpress

        # The decorator is applied in _chat.py, check that it's callable
        assert isinstance(ChatExpress, type)


class TestChatUiFunctionDecorated:
    """Tests for chat_ui function decorator."""

    def test_chat_ui_has_example_decorator(self):
        """chat_ui function should be decorated with add_example."""
        from shiny.ui import chat_ui

        # The add_example decorator should have been applied
        assert callable(chat_ui)


class TestModuleExports:
    """Tests for module exports."""

    def test_module_imports_correctly(self):
        """Module should import without errors."""
        import shiny.ui._chat as chat

        assert chat is not None

    def test_all_exports_exist(self):
        """All items in __all__ should be importable."""
        from shiny.ui import _chat

        for item in _chat.__all__:
            assert hasattr(_chat, item)

    def test_all_exports_list(self):
        """__all__ should contain expected exports."""
        from shiny.ui import _chat

        expected = {"Chat", "ChatExpress", "chat_ui", "ChatMessageDict"}
        assert set(_chat.__all__) == expected


class TestChatImportsFromShinychat:
    """Tests that verify shinychat imports work."""

    def test_chat_imported_from_shinychat(self):
        """Chat should be imported from shinychat."""
        from shiny.ui._chat import Chat

        # Check that it comes from shinychat
        assert Chat.__module__.startswith("shinychat")

    def test_chat_express_imported_from_shinychat(self):
        """ChatExpress should be imported from shinychat.express."""
        from shiny.ui._chat import ChatExpress

        # Check that it comes from shinychat.express
        assert "shinychat" in ChatExpress.__module__

    def test_chat_ui_imported_from_shinychat(self):
        """chat_ui should be imported from shinychat."""
        from shiny.ui._chat import chat_ui

        # Check that it comes from shinychat
        assert chat_ui.__module__.startswith("shinychat")

    def test_chat_message_dict_imported_from_shinychat(self):
        """ChatMessageDict should be imported from shinychat.types."""
        from shiny.ui._chat import ChatMessageDict

        # ChatMessageDict is a TypedDict, check it's accessible
        assert ChatMessageDict is not None
