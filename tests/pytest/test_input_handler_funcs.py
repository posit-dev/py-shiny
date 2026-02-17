"""Tests for shiny.input_handler module."""

from typing import Any

import pytest

from shiny.input_handler import _InputHandlers
from shiny.module import ResolvedId
from shiny.session import Session


class TestInputHandlers:
    """Tests for _InputHandlers class."""

    def test_input_handlers_add(self) -> None:
        """Test adding an input handler."""
        handlers = _InputHandlers()

        @handlers.add("test.type")
        def handler(value: Any, name: ResolvedId, session: Session) -> Any:
            return value * 2

        assert "test.type" in handlers

    def test_input_handlers_add_duplicate_raises(self) -> None:
        """Test adding duplicate handler raises error."""
        handlers = _InputHandlers()

        @handlers.add("test.type")
        def handler1(value: Any, name: ResolvedId, session: Session) -> Any:
            return value

        with pytest.raises(ValueError, match="already registered"):

            @handlers.add("test.type")
            def handler2(value: Any, name: ResolvedId, session: Session) -> Any:
                return value

    def test_input_handlers_add_with_force(self) -> None:
        """Test adding duplicate handler with force=True succeeds."""
        handlers = _InputHandlers()

        @handlers.add("test.type")
        def handler1(value: Any, name: ResolvedId, session: Session) -> Any:
            return value

        @handlers.add("test.type", force=True)
        def handler2(value: Any, name: ResolvedId, session: Session) -> Any:
            return value * 2

        assert "test.type" in handlers

    def test_input_handlers_remove(self) -> None:
        """Test removing an input handler."""
        handlers = _InputHandlers()

        @handlers.add("test.type")
        def handler(value: Any, name: ResolvedId, session: Session) -> Any:
            return value

        assert "test.type" in handlers
        handlers.remove("test.type")
        assert "test.type" not in handlers

    def test_input_handlers_remove_nonexistent_raises(self) -> None:
        """Test removing nonexistent handler raises error."""
        handlers = _InputHandlers()
        with pytest.raises(KeyError):
            handlers.remove("nonexistent.type")

    def test_input_handlers_process_value_nonexistent_raises(self) -> None:
        """Test processing with nonexistent handler raises error."""
        handlers = _InputHandlers()
        with pytest.raises(ValueError, match="No input handler registered"):
            handlers._process_value("nonexistent.type", "value", "name", None)  # type: ignore

    def test_input_handlers_multiple_types(self) -> None:
        """Test adding multiple different types."""
        handlers = _InputHandlers()

        @handlers.add("type.one")
        def handler1(value: Any, name: ResolvedId, session: Session) -> Any:
            return value

        @handlers.add("type.two")
        def handler2(value: Any, name: ResolvedId, session: Session) -> Any:
            return value

        assert "type.one" in handlers
        assert "type.two" in handlers

    def test_input_handlers_is_dict(self) -> None:
        """Test _InputHandlers behaves like a dict."""
        handlers = _InputHandlers()

        @handlers.add("test.type")
        def handler(value: Any, name: ResolvedId, session: Session) -> Any:
            return value

        # Dict-like operations
        assert len(handlers) == 1
        assert list(handlers.keys()) == ["test.type"]
