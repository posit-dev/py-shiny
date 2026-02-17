"""Tests for shiny.types module - Exception classes."""

import pytest

from shiny.types import (
    SafeException,
    SilentCancelOutputException,
    SilentException,
    SilentOperationInProgressException,
)


class TestSilentException:
    """Tests for SilentException class."""

    def test_silent_exception_creation(self) -> None:
        """Test creating SilentException."""
        exc = SilentException()
        assert isinstance(exc, Exception)

    def test_silent_exception_can_be_raised(self) -> None:
        """Test SilentException can be raised."""
        with pytest.raises(SilentException):
            raise SilentException()

    def test_silent_exception_is_base_exception(self) -> None:
        """Test SilentException is an Exception."""
        exc = SilentException()
        assert isinstance(exc, BaseException)


class TestSilentCancelOutputException:
    """Tests for SilentCancelOutputException class."""

    def test_creation(self) -> None:
        """Test creating SilentCancelOutputException."""
        exc = SilentCancelOutputException()
        assert isinstance(exc, Exception)

    def test_can_be_raised(self) -> None:
        """Test SilentCancelOutputException can be raised."""
        with pytest.raises(SilentCancelOutputException):
            raise SilentCancelOutputException()

    def test_is_base_exception(self) -> None:
        """Test SilentCancelOutputException is a BaseException."""
        exc = SilentCancelOutputException()
        assert isinstance(exc, BaseException)


class TestSilentOperationInProgressException:
    """Tests for SilentOperationInProgressException class."""

    def test_creation(self) -> None:
        """Test creating SilentOperationInProgressException."""
        exc = SilentOperationInProgressException()
        assert isinstance(exc, Exception)

    def test_can_be_raised(self) -> None:
        """Test SilentOperationInProgressException can be raised."""
        with pytest.raises(SilentOperationInProgressException):
            raise SilentOperationInProgressException()

    def test_is_silent_exception(self) -> None:
        """Test SilentOperationInProgressException is a SilentException."""
        exc = SilentOperationInProgressException()
        assert isinstance(exc, SilentException)


class TestSafeException:
    """Tests for SafeException class."""

    def test_creation_with_message(self) -> None:
        """Test creating SafeException with message."""
        exc = SafeException("Safe error message")
        assert str(exc) == "Safe error message"

    def test_can_be_raised(self) -> None:
        """Test SafeException can be raised."""
        with pytest.raises(SafeException):
            raise SafeException("error")

    def test_is_exception(self) -> None:
        """Test SafeException is an Exception."""
        exc = SafeException("test")
        assert isinstance(exc, Exception)

    def test_message_preserved(self) -> None:
        """Test exception message is preserved."""
        exc = SafeException("my custom message")
        assert "my custom message" in str(exc)

    def test_empty_message(self) -> None:
        """Test SafeException with empty message."""
        exc = SafeException("")
        assert str(exc) == ""

    def test_multiline_message(self) -> None:
        """Test SafeException with multiline message."""
        message = "Line 1\nLine 2\nLine 3"
        exc = SafeException(message)
        assert str(exc) == message


class TestExceptionHierarchy:
    """Tests for exception class hierarchy."""

    def test_silent_operation_inherits_from_silent(self) -> None:
        """Test SilentOperationInProgressException inherits from SilentException."""
        exc = SilentOperationInProgressException()
        assert isinstance(exc, SilentException)

    def test_safe_exception_not_silent(self) -> None:
        """Test that SafeException is not a SilentException."""
        exc = SafeException("test")
        assert not isinstance(exc, SilentException)

    def test_different_exception_types(self) -> None:
        """Test that different exceptions are distinct types."""
        silent = SilentException()
        cancel = SilentCancelOutputException()
        progress = SilentOperationInProgressException()
        safe = SafeException("test")

        assert type(silent) is not type(cancel)
        assert type(cancel) is not type(progress)
        assert type(safe) is not type(silent)
