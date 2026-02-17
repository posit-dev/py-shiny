"""Tests for shiny/types.py module."""

from shiny.types import (
    NavSetArg,
    SafeException,
    SilentCancelOutputException,
    SilentException,
)


class TestSafeException:
    """Tests for SafeException class."""

    def test_safe_exception_exists(self):
        """Test SafeException class exists."""
        assert SafeException is not None

    def test_safe_exception_is_exception(self):
        """Test SafeException is an exception class."""
        assert issubclass(SafeException, Exception)


class TestSilentException:
    """Tests for SilentException class."""

    def test_silent_exception_exists(self):
        """Test SilentException class exists."""
        assert SilentException is not None

    def test_silent_exception_is_exception(self):
        """Test SilentException is an exception class."""
        assert issubclass(SilentException, Exception)


class TestSilentCancelOutputException:
    """Tests for SilentCancelOutputException class."""

    def test_silent_cancel_output_exception_exists(self):
        """Test SilentCancelOutputException class exists."""
        assert SilentCancelOutputException is not None

    def test_silent_cancel_output_exception_is_exception(self):
        """Test SilentCancelOutputException is an exception class."""
        assert issubclass(SilentCancelOutputException, Exception)


class TestNavSetArg:
    """Tests for NavSetArg type."""

    def test_nav_set_arg_exists(self):
        """Test NavSetArg type exists."""
        assert NavSetArg is not None


class TestTypesExported:
    """Tests for types export."""

    def test_types_module_accessible(self):
        """Test types module is accessible."""
        from shiny import types

        assert types is not None
