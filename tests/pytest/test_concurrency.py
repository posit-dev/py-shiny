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


# =============================================================================
# _flush_concurrent: outer loop catches newly-invalidated effects
# =============================================================================


@pytest.mark.asyncio
async def test_concurrent_flush_runs_newly_invalidated_chain():
    """
    Effect A sets a Value, which invalidates Effect B.
    Both must run within the same flush() call.
    Regression test for the batch-gather-without-outer-loop bug: without the
    outer while-loop in _flush_concurrent, Effect B would be silently dropped.
    """
    from shiny.reactive import Value, effect, flush

    x: Value[int] = Value(1)
    y: Value[int] = Value(0)
    b_ran_with: list[int] = []

    @effect()
    def effect_a():
        val = x()
        y.set(val * 10)

    @effect()
    def effect_b():
        b_ran_with.append(y())

    # Initial flush: both effects run
    await flush()
    assert b_ran_with == [10]

    # Now invalidate x; effect_a runs (sets y), then effect_b must also run
    # in the SAME flush — not be dropped
    x.set(2)
    b_ran_with.clear()
    await flush()

    assert b_ran_with == [20]


# =============================================================================
# _cycle_start_action_queue / _start_cycle
# =============================================================================


def _make_session():
    from shiny import App, ui
    from shiny._connection import MockConnection

    conn = MockConnection()
    return App(ui.TagList(), None)._create_session(conn)


@pytest.mark.asyncio
async def test_cycle_action_runs_immediately_when_idle():
    """Action queued when busy_count==0 executes without waiting."""
    session = _make_session()
    ran: list[str] = []

    async def action() -> None:
        ran.append("done")

    assert session._busy_count == 0
    await session._cycle_start_action(action)
    assert ran == ["done"]


@pytest.mark.asyncio
async def test_cycle_action_deferred_while_busy():
    """Action queued when busy_count>0 does NOT run until busy_count returns to 0."""
    import asyncio

    session = _make_session()
    ran: list[str] = []

    async def action() -> None:
        ran.append("done")

    session._increment_busy_count()
    assert session._busy_count == 1

    await session._cycle_start_action(action)
    assert ran == []  # still deferred

    session._decrement_busy_count()

    # Two yields: one for create_task scheduling, one for the task body
    await asyncio.sleep(0)
    await asyncio.sleep(0)

    assert ran == ["done"]


@pytest.mark.asyncio
async def test_cycle_actions_execute_in_fifo_order():
    """Two actions queued while busy execute in the order they were added."""
    import asyncio

    session = _make_session()
    order: list[int] = []

    async def action1() -> None:
        order.append(1)

    async def action2() -> None:
        order.append(2)

    session._increment_busy_count()
    await session._cycle_start_action(action1)
    await session._cycle_start_action(action2)
    assert order == []

    session._decrement_busy_count()
    # action1 runs; then _start_cycle schedules action2 via create_task
    await asyncio.sleep(0)
    await asyncio.sleep(0)
    await asyncio.sleep(0)
    await asyncio.sleep(0)

    assert order == [1, 2]


@pytest.mark.asyncio
async def test_start_cycle_aborts_if_busy_count_nonzero():
    """
    _start_cycle is scheduled via create_task, but before it runs a new
    effect increments busy_count. _start_cycle should abort.
    """
    import asyncio

    session = _make_session()
    ran: list[str] = []

    async def action() -> None:
        ran.append("done")

    # First effect finishes, scheduling _start_cycle
    session._increment_busy_count()
    await session._cycle_start_action(action)
    session._decrement_busy_count()
    # _start_cycle is now scheduled but hasn't run yet

    # New effect starts before _start_cycle runs
    session._increment_busy_count()

    # Let _start_cycle run — it should bail because busy_count == 1
    await asyncio.sleep(0)
    await asyncio.sleep(0)
    assert ran == []

    # Second effect finishes
    session._decrement_busy_count()
    await asyncio.sleep(0)
    await asyncio.sleep(0)
    assert ran == ["done"]


@pytest.mark.asyncio
async def test_cycle_queue_cleared_on_session_end():
    """Pending cycle actions are discarded when the session ends."""
    session = _make_session()
    ran: list[str] = []

    async def action() -> None:
        ran.append("done")

    session._increment_busy_count()
    await session._cycle_start_action(action)
    assert len(session._cycle_start_action_queue) == 1

    await session._run_session_ended_tasks()
    assert len(session._cycle_start_action_queue) == 0
    assert session._busy_count == 0
