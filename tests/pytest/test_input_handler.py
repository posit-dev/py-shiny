"""Tests for shiny/input_handler.py"""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Any, cast

import pytest

from shiny.input_handler import _InputHandlers, input_handlers
from shiny.module import ResolvedId

if TYPE_CHECKING:
    from shiny.session import Session


class TestInputHandlers:
    """Tests for the _InputHandlers class."""

    def test_singleton_instance(self) -> None:
        """Test that input_handlers is a singleton instance."""
        assert isinstance(input_handlers, _InputHandlers)

    def test_add_and_get_handler(self) -> None:
        """Test adding and retrieving a custom handler via decorator."""
        handlers = _InputHandlers()

        @handlers.add("test.custom")
        def custom_handler(value: Any, name: ResolvedId, session: Session) -> Any:
            return f"processed_{value}"

        assert "test.custom" in handlers
        retrieved = handlers["test.custom"]
        assert (
            retrieved(42, ResolvedId("test"), cast("Session", None)) == "processed_42"
        )

    def test_add_duplicate_handler_raises(self) -> None:
        """Test that adding a duplicate handler raises ValueError."""
        handlers = _InputHandlers()

        @handlers.add("test.dup")
        def handler1(value: Any, name: ResolvedId, session: Session) -> Any:
            return value

        with pytest.raises(ValueError, match="already registered"):

            @handlers.add("test.dup")
            def handler2(value: Any, name: ResolvedId, session: Session) -> Any:
                return value

    def test_add_with_force_replaces_handler(self) -> None:
        """Test that adding with force=True replaces existing handler."""
        handlers = _InputHandlers()

        @handlers.add("test.force")
        def handler1(value: Any, name: ResolvedId, session: Session) -> Any:
            return "handler1"

        @handlers.add("test.force", force=True)
        def handler2(value: Any, name: ResolvedId, session: Session) -> Any:
            return "handler2"

        result = handlers["test.force"]("x", ResolvedId("n"), cast("Session", None))
        assert result == "handler2"

    def test_remove_handler(self) -> None:
        """Test removing a handler."""
        handlers = _InputHandlers()

        @handlers.add("test.remove")
        def custom_handler(value: Any, name: ResolvedId, session: Session) -> Any:
            return value

        assert "test.remove" in handlers

        handlers.remove("test.remove")
        assert "test.remove" not in handlers

    def test_remove_nonexistent_handler_raises(self) -> None:
        """Test that removing non-existent handler raises KeyError."""
        handlers = _InputHandlers()
        with pytest.raises(KeyError):
            handlers.remove("nonexistent.handler")

    def test_process_value_with_unknown_type_raises(self) -> None:
        """Test _process_value raises ValueError for unknown type."""
        handlers = _InputHandlers()
        with pytest.raises(ValueError, match="No input handler registered"):
            handlers._process_value(
                "unknown.type", 42, ResolvedId("test_input"), cast("Session", None)
            )

    def test_process_value_with_registered_handler(self) -> None:
        """Test _process_value applies registered handler."""
        handlers = _InputHandlers()

        @handlers.add("test.double")
        def double_handler(value: Any, name: ResolvedId, session: Session) -> Any:
            return value * 2

        result = handlers._process_value(
            "test.double", 21, ResolvedId("test_input"), cast("Session", None)
        )
        assert result == 42


class TestBuiltInDateHandler:
    """Tests for the shiny.date input handler."""

    def test_shiny_date_handler_valid_string(self) -> None:
        """Test shiny.date handler parses valid date string."""
        result = input_handlers._process_value(
            "shiny.date", "2023-06-15", ResolvedId("date"), cast("Session", None)
        )
        assert result == datetime.date(2023, 6, 15)

    def test_shiny_date_handler_none(self) -> None:
        """Test shiny.date handler returns None for None."""
        result = input_handlers._process_value(
            "shiny.date", None, ResolvedId("date"), cast("Session", None)
        )
        assert result is None

    def test_shiny_date_handler_invalid_format(self) -> None:
        """Test shiny.date handler returns None for invalid date format."""
        result = input_handlers._process_value(
            "shiny.date", "not-a-date", ResolvedId("date"), cast("Session", None)
        )
        assert result is None

    def test_shiny_date_handler_with_list(self) -> None:
        """Test date handler with list of dates (for date range)."""
        result = input_handlers._process_value(
            "shiny.date",
            ["2023-01-01", "2023-12-31"],
            ResolvedId("date_range"),
            cast("Session", None),
        )
        assert isinstance(result, tuple)
        result_tuple = cast(tuple[datetime.date | None, datetime.date | None], result)
        assert len(result_tuple) == 2
        assert result_tuple[0] == datetime.date(2023, 1, 1)
        assert result_tuple[1] == datetime.date(2023, 12, 31)

    def test_shiny_date_handler_with_partial_list(self) -> None:
        """Test date handler with list containing None."""
        result = input_handlers._process_value(
            "shiny.date",
            ["2023-01-01", None],
            ResolvedId("date_range"),
            cast("Session", None),
        )
        assert isinstance(result, tuple)
        assert result[0] == datetime.date(2023, 1, 1)
        assert result[1] is None


class TestBuiltInDatetimeHandler:
    """Tests for the shiny.datetime input handler."""

    def test_shiny_datetime_handler_valid_timestamp(self) -> None:
        """Test shiny.datetime handler parses valid timestamp."""
        # Timestamp for 2023-06-15 14:30:45 UTC
        timestamp = 1686840645.0
        result = input_handlers._process_value(
            "shiny.datetime",
            timestamp,
            ResolvedId("datetime"),
            cast("Session", None),
        )
        assert isinstance(result, datetime.datetime)
        assert result.year == 2023
        assert result.month == 6
        assert result.day == 15

    def test_shiny_datetime_handler_int_timestamp(self) -> None:
        """Test shiny.datetime handler parses integer timestamp."""
        # Timestamp for 2023-01-01 00:00:00 UTC
        timestamp = 1672531200
        result = input_handlers._process_value(
            "shiny.datetime", timestamp, ResolvedId("datetime"), cast("Session", None)
        )
        assert isinstance(result, datetime.datetime)

    def test_shiny_datetime_handler_with_list(self) -> None:
        """Test datetime handler with list of timestamps."""
        timestamps = [1672531200.0, 1703980800.0]  # 2023-01-01 and 2023-12-31
        result = input_handlers._process_value(
            "shiny.datetime",
            timestamps,
            ResolvedId("datetime_range"),
            cast("Session", None),
        )
        assert isinstance(result, tuple)
        result_tuple = cast(
            tuple[datetime.datetime | None, datetime.datetime | None], result
        )
        assert len(result_tuple) == 2
        assert isinstance(result_tuple[0], datetime.datetime)
        assert isinstance(result_tuple[1], datetime.datetime)


class TestBuiltInActionHandler:
    """Tests for the shiny.action input handler."""

    def test_shiny_action_handler(self) -> None:
        """Test shiny.action handler returns ActionButtonValue."""
        from shiny.types import ActionButtonValue

        result = input_handlers._process_value(
            "shiny.action", 5, ResolvedId("btn"), cast("Session", None)
        )
        assert isinstance(result, ActionButtonValue)
        assert int(result) == 5

    def test_shiny_action_handler_zero(self) -> None:
        """Test shiny.action handler with zero value."""
        from shiny.types import ActionButtonValue

        result = input_handlers._process_value(
            "shiny.action", 0, ResolvedId("btn"), cast("Session", None)
        )
        assert isinstance(result, ActionButtonValue)
        assert int(result) == 0


class TestBuiltInNumberHandler:
    """Tests for the shiny.number input handler."""

    def test_shiny_number_handler_returns_string(self) -> None:
        """Test shiny.number handler returns value unchanged (as string)."""
        result = input_handlers._process_value(
            "shiny.number", "42.5", ResolvedId("num"), cast("Session", None)
        )
        # The number handler simply returns the value as-is
        assert result == "42.5"


class TestInputHandlerDecorator:
    """Tests for the input_handler decorator pattern."""

    def test_custom_handler_registration(self) -> None:
        """Test registering a custom input handler."""
        handlers = _InputHandlers()

        @handlers.add("test.decorator")
        def my_handler(value: Any, name: ResolvedId, session: Session) -> Any:
            return f"decorated_{value}"

        result = handlers._process_value(
            "test.decorator", "input", ResolvedId("name"), cast("Session", None)
        )
        assert result == "decorated_input"

    def test_handler_receives_correct_arguments(self) -> None:
        """Test that handler receives correct arguments."""
        handlers = _InputHandlers()
        received_args: dict[str, Any] = {}

        @handlers.add("test.capture")
        def capture_handler(value: Any, name: ResolvedId, session: Session) -> Any:
            received_args["value"] = value
            received_args["name"] = name
            received_args["session"] = session
            return value

        test_name = ResolvedId("test_name")
        handlers._process_value(
            "test.capture", "test_value", test_name, cast("Session", None)
        )

        assert received_args["value"] == "test_value"
        assert received_args["name"] == test_name

    def test_dict_like_access(self) -> None:
        """Test that _InputHandlers behaves like a dict."""
        handlers = _InputHandlers()

        @handlers.add("test.dict")
        def my_handler(value: Any, name: ResolvedId, session: Session) -> Any:
            return value

        # Test dict methods
        assert "test.dict" in handlers
        assert len(handlers) == 1
        assert list(handlers.keys()) == ["test.dict"]


class TestInputHandlersDocstring:
    """Test that documentation is properly attached."""

    def test_has_docstring(self) -> None:
        """Test that input_handlers has a docstring."""
        assert input_handlers.__doc__ is not None
        assert "Manage Shiny input handlers" in input_handlers.__doc__
