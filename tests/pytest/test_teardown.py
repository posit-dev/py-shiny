"""Tests for reactive teardown behavior."""

import pytest

from shiny.reactive import DestroyedReactiveError, Value, effect, flush, isolate


def test_destroyed_reactive_error_is_exception():
    assert issubclass(DestroyedReactiveError, Exception)
    err = DestroyedReactiveError("test message")
    assert str(err) == "test message"


@pytest.mark.asyncio
async def test_value_teardown_unsets_value():
    """After _teardown(), value is unset."""
    v = Value(42)
    with isolate():
        assert v.is_set() is True
    v._teardown()
    with isolate():
        assert v.is_set() is False


@pytest.mark.asyncio
async def test_value_teardown_invalidates_value_dependents():
    """_teardown() invalidates downstream value dependents."""
    v = Value(10)
    call_count = 0

    @effect()
    def _():
        nonlocal call_count
        try:
            v()
        except Exception:
            pass
        call_count += 1

    await flush()
    assert call_count == 1

    v._teardown()
    await flush()
    assert call_count == 2


@pytest.mark.asyncio
async def test_value_teardown_invalidates_is_set_dependents():
    """_teardown() invalidates is_set() dependents."""
    v = Value(10)
    is_set_results: list[bool] = []

    @effect()
    def _():
        is_set_results.append(v.is_set())

    await flush()
    assert is_set_results == [True]

    v._teardown()
    await flush()
    assert is_set_results == [True, False]


@pytest.mark.asyncio
async def test_value_teardown_is_idempotent():
    """Second _teardown() call is a no-op."""
    v = Value(42)
    call_count = 0

    @effect()
    def _():
        nonlocal call_count
        try:
            v()
        except Exception:
            pass
        call_count += 1

    await flush()
    assert call_count == 1

    v._teardown()
    await flush()
    assert call_count == 2

    # Second teardown should NOT invalidate again
    v._teardown()
    await flush()
    assert call_count == 2


@pytest.mark.asyncio
async def test_value_teardown_works_on_read_only():
    """_teardown() works on read-only values (input values)."""
    v = Value(42, read_only=True)
    with isolate():
        assert v.is_set() is True
    v._teardown()
    with isolate():
        assert v.is_set() is False
