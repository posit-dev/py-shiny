"""Tests for the R Shiny-style concurrency model."""

import warnings

import pytest

from shiny import reactive
from shiny.session._session import OutBoundMessageQueues


# =============================================================================
# OutBoundMessageQueues.is_empty()
# =============================================================================


def test_omq_is_empty_when_newly_created():
    """Freshly constructed OMQ reports empty."""
    omq = OutBoundMessageQueues()
    assert omq.is_empty() is True


def test_omq_is_empty_false_when_value_added():
    omq = OutBoundMessageQueues()
    omq.set_value("x", 1)
    assert omq.is_empty() is False


def test_omq_is_empty_false_when_error_added():
    omq = OutBoundMessageQueues()
    omq.set_error("x", {"message": "oops"})
    assert omq.is_empty() is False


def test_omq_is_empty_false_when_input_message_added():
    omq = OutBoundMessageQueues()
    omq.add_input_message("x", {"type": "update", "value": 1})
    assert omq.is_empty() is False


def test_omq_is_empty_after_reset():
    omq = OutBoundMessageQueues()
    omq.set_value("x", 1)
    omq.reset()
    assert omq.is_empty() is True


# =============================================================================
# reactive.lock() deprecation
# =============================================================================


@pytest.mark.asyncio
async def test_reactive_lock_emits_deprecation_warning():
    """reactive.lock() should emit DeprecationWarning."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        reactive.lock()
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "deprecated" in str(w[0].message).lower()


@pytest.mark.asyncio
async def test_noop_lock_works_as_context_manager():
    """async with reactive.lock(): should complete without error (backward compat)."""
    with warnings.catch_warnings(record=True):
        warnings.simplefilter("always")
        lock = reactive.lock()
    # Should not raise
    async with lock:
        pass


@pytest.mark.asyncio
async def test_noop_lock_locked_returns_false():
    """_NoOpLock.locked() always returns False."""
    with warnings.catch_warnings(record=True):
        warnings.simplefilter("always")
        lock = reactive.lock()
    assert lock.locked() is False
