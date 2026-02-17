"""Tests for shiny.reactive module."""

import pytest

from shiny.reactive import (
    Context,
    Value,
    isolate,
)
from shiny.reactive._core import Dependents, ReactiveEnvironment, ReactiveWarning


class TestReactiveValue:
    """Tests for reactive.Value class."""

    def test_value_creation(self):
        """Test creating a Value with initial value."""
        val = Value(10)
        with isolate():
            assert val.get() == 10

    def test_value_creation_generic(self):
        """Test creating a typed Value."""
        val: Value[str] = Value("hello")
        with isolate():
            assert val.get() == "hello"

    def test_value_set(self):
        """Test setting a value."""
        val = Value(10)
        result = val.set(20)
        assert result is True
        with isolate():
            assert val.get() == 20

    def test_value_set_same_value(self):
        """Test setting to the same value returns False."""
        val = Value(10)
        val.set(10)
        with isolate():
            result = val.set(val.get())
            assert result is False

    def test_value_call(self):
        """Test calling a Value returns its value."""
        val = Value(42)
        with isolate():
            assert val() == 42

    def test_value_read_only(self):
        """Test read-only Value raises on set."""
        val = Value(10, read_only=True)
        with pytest.raises(RuntimeError, match="read-only"):
            val.set(20)

    def test_value_unset(self):
        """Test unsetting a value."""
        val = Value(10)
        val.unset()
        # After unset, get() should raise SilentException
        from shiny.types import SilentException

        with pytest.raises(SilentException):
            with isolate():
                val.get()

    def test_value_is_set(self):
        """Test is_set method."""
        val = Value(10)
        with isolate():
            assert val.is_set() is True
        val.unset()
        with isolate():
            assert val.is_set() is False


class TestContext:
    """Tests for reactive Context."""

    def test_context_creation(self):
        """Test creating a Context."""
        ctx = Context()
        assert ctx.id >= 0
        assert ctx._invalidated is False

    def test_context_invalidate(self):
        """Test invalidating a Context."""
        ctx = Context()
        assert ctx._invalidated is False
        ctx.invalidate()
        assert ctx._invalidated is True

    def test_context_invalidate_twice(self):
        """Test invalidating a Context twice is safe."""
        ctx = Context()
        ctx.invalidate()
        ctx.invalidate()  # Should not raise
        assert ctx._invalidated is True

    def test_context_on_invalidate_callback(self):
        """Test on_invalidate callback is called."""
        ctx = Context()
        called: list[bool] = []
        ctx.on_invalidate(lambda: called.append(True))
        ctx.invalidate()
        assert called == [True]

    def test_context_on_invalidate_after_invalidation(self):
        """Test on_invalidate called immediately if already invalidated."""
        ctx = Context()
        ctx.invalidate()
        called: list[bool] = []
        ctx.on_invalidate(lambda: called.append(True))
        assert called == [True]


class TestDependents:
    """Tests for Dependents class."""

    def test_dependents_creation(self):
        """Test creating Dependents."""
        deps = Dependents()
        assert len(deps._dependents) == 0


class TestIsolate:
    """Tests for isolate context manager."""

    def test_isolate_basic(self):
        """Test basic isolate usage."""
        val = Value(10)
        with isolate():
            result = val.get()
        assert result == 10

    def test_isolate_nested(self):
        """Test nested isolate calls."""
        val = Value(10)
        with isolate():
            with isolate():
                result = val.get()
        assert result == 10


class TestReactiveEnvironment:
    """Tests for ReactiveEnvironment."""

    def test_environment_next_id(self):
        """Test next_id returns incrementing values."""
        env = ReactiveEnvironment()
        id1 = env.next_id()
        id2 = env.next_id()
        assert id2 > id1


class TestReactiveWarning:
    """Tests for ReactiveWarning."""

    def test_reactive_warning_is_warning(self):
        """Test ReactiveWarning is a RuntimeWarning."""
        assert issubclass(ReactiveWarning, RuntimeWarning)

    def test_reactive_warning_can_be_raised(self):
        """Test ReactiveWarning can be raised."""
        with pytest.warns(ReactiveWarning):
            import warnings

            warnings.warn("test", ReactiveWarning, stacklevel=2)
