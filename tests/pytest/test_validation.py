"""Tests for shiny/_validation.py"""

from __future__ import annotations

import pytest

from shiny._validation import req
from shiny.types import (
    SilentCancelOutputException,
    SilentException,
    SilentOperationInProgressException,
)


class TestReq:
    """Tests for the req() function."""

    def test_no_args_returns_none(self) -> None:
        """Test that req() with no args returns None."""
        result = req()
        assert result is None

    def test_truthy_value_returns_first_arg(self) -> None:
        """Test that req() with truthy values returns first arg."""
        assert req(True) is True
        assert req("hello") == "hello"
        assert req(1) == 1
        assert req([1, 2, 3]) == [1, 2, 3]
        assert req({"a": 1}) == {"a": 1}

    def test_multiple_truthy_values_returns_first(self) -> None:
        """Test that req() with multiple truthy values returns the first."""
        result = req("first", "second", "third")
        assert result == "first"

    def test_false_raises_silent_exception(self) -> None:
        """Test that False raises SilentException."""
        with pytest.raises(SilentException):
            req(False)

    def test_none_raises_silent_exception(self) -> None:
        """Test that None raises SilentException."""
        with pytest.raises(SilentException):
            req(None)

    def test_zero_raises_silent_exception(self) -> None:
        """Test that 0 raises SilentException."""
        with pytest.raises(SilentException):
            req(0)

    def test_empty_string_raises_silent_exception(self) -> None:
        """Test that empty string raises SilentException."""
        with pytest.raises(SilentException):
            req("")

    def test_empty_list_raises_silent_exception(self) -> None:
        """Test that empty list raises SilentException."""
        with pytest.raises(SilentException):
            req([])

    def test_empty_dict_raises_silent_exception(self) -> None:
        """Test that empty dict raises SilentException."""
        with pytest.raises(SilentException):
            req({})

    def test_truthy_then_falsy_raises_exception(self) -> None:
        """Test that a falsy value anywhere in args raises exception."""
        with pytest.raises(SilentException):
            req(True, "hello", 0, "world")

    def test_cancel_output_true_raises_cancel_exception(self) -> None:
        """Test that cancel_output=True raises SilentCancelOutputException."""
        with pytest.raises(SilentCancelOutputException):
            req(False, cancel_output=True)

    def test_cancel_output_progress_raises_progress_exception(self) -> None:
        """Test that cancel_output='progress' raises SilentOperationInProgressException."""
        with pytest.raises(SilentOperationInProgressException):
            req(None, cancel_output="progress")

    def test_cancel_output_false_raises_silent_exception(self) -> None:
        """Test that cancel_output=False (default) raises SilentException."""
        with pytest.raises(SilentException):
            req(False, cancel_output=False)

    def test_truthy_with_cancel_output_returns_value(self) -> None:
        """Test that truthy values with cancel_output still return first value."""
        assert req("hello", cancel_output=True) == "hello"
        assert req("world", cancel_output="progress") == "world"

    def test_with_number_values(self) -> None:
        """Test req with various number values."""
        assert req(1) == 1
        assert req(0.1) == 0.1
        assert req(-1) == -1

        with pytest.raises(SilentException):
            req(0)
        with pytest.raises(SilentException):
            req(0.0)


class TestSilentExceptionTypes:
    """Tests for silent exception types exported from types."""

    def test_silent_exception_is_exception(self) -> None:
        """Test that SilentException is an Exception."""
        exc = SilentException()
        assert isinstance(exc, Exception)

    def test_silent_cancel_output_exception_is_exception(self) -> None:
        """Test that SilentCancelOutputException is an Exception."""
        exc = SilentCancelOutputException()
        assert isinstance(exc, Exception)

    def test_silent_operation_in_progress_exception_is_exception(self) -> None:
        """Test that SilentOperationInProgressException is an Exception."""
        exc = SilentOperationInProgressException()
        assert isinstance(exc, Exception)

    def test_exception_types_are_distinct(self) -> None:
        """Test that the exception types are distinct."""
        silent = SilentException()
        cancel = SilentCancelOutputException()
        progress = SilentOperationInProgressException()

        # Each should only be an instance of its own type (and parent classes)
        assert type(silent) is SilentException
        assert type(cancel) is SilentCancelOutputException
        assert type(progress) is SilentOperationInProgressException
