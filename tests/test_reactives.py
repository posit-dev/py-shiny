"""Tests for `shiny.reactives` and `shiny.reactcore`."""

import pytest
import asyncio
from typing import List
from shiny import reactives

from shiny.input_handlers import ActionButtonValue
import shiny.reactcore as reactcore
from shiny.decorators import *
from shiny.reactives import *
from shiny.validation import req

from .mocktime import MockTime


@pytest.mark.asyncio
async def test_flush_runs_newly_invalidated():
    """
    Make sure that a flush will also run any reactives that were invalidated
    during the flush.
    """

    v1 = ReactiveVal(1)
    v2 = ReactiveVal(2)

    v2_result = None

    # In practice, on the first flush, Observers run in the order that they were
    # created. Our test checks that o2 runs _after_ o1.
    @observe()
    def o2():
        nonlocal v2_result
        v2_result = v2()

    @observe()
    def o1():
        v2(v1())

    await reactcore.flush()
    assert v2_result == 1
    assert o2._exec_count == 2
    assert o1._exec_count == 1


@pytest.mark.asyncio
async def test_flush_runs_newly_invalidated_async():
    """
    Make sure that a flush will also run any reactives that were invalidated
    during the flush. (Same as previous test, but async.)
    """

    v1 = ReactiveVal(1)
    v2 = ReactiveVal(2)

    v2_result = None

    # In practice, on the first flush, Observers run in the order that they were
    # created. Our test checks that o2 runs _after_ o1.
    @observe_async()
    async def o2():
        nonlocal v2_result
        v2_result = v2()

    @observe_async()
    async def o1():
        v2(v1())

    await reactcore.flush()
    assert v2_result == 1
    assert o2._exec_count == 2
    assert o1._exec_count == 1


# ======================================================================
# Setting ReactiveVal to same value doesn't invalidate downstream
# ======================================================================
@pytest.mark.asyncio
async def test_reactive_val_same_no_invalidate():
    v = ReactiveVal(1)

    @observe()
    def o():
        v()

    await reactcore.flush()
    assert o._exec_count == 1

    v(1)
    await reactcore.flush()
    assert o._exec_count == 1


# ======================================================================
# Recursive calls to reactives
# ======================================================================
@pytest.mark.asyncio
async def test_recursive_reactive():
    v = ReactiveVal(5)

    @reactive()
    def r():
        if v() == 0:
            return 0
        v(v() - 1)
        r()

    @observe()
    def o():
        r()

    await reactcore.flush()
    assert o._exec_count == 2
    assert r._exec_count == 6
    with isolate():
        assert v() == 0


@pytest.mark.asyncio
async def test_recursive_reactive_async():
    v = ReactiveVal(5)

    @reactive_async()
    async def r():
        if v() == 0:
            return 0
        v(v() - 1)
        await r()

    @observe_async()
    async def o():
        await r()

    await reactcore.flush()
    assert o._exec_count == 2
    assert r._exec_count == 6
    with isolate():
        assert v() == 0


# ======================================================================
# async
# ======================================================================


@pytest.mark.asyncio
async def test_async_sequential():
    x: ReactiveVal[int] = ReactiveVal(1)
    results: list[int] = []
    exec_order: list[str] = []

    async def react_chain(n: int):
        @reactive_async()
        async def r():
            nonlocal exec_order
            exec_order.append(f"r{n}-1")
            await asyncio.sleep(0)
            exec_order.append(f"r{n}-2")
            return x() + 10

        @observe_async()
        async def _():
            nonlocal exec_order
            exec_order.append(f"o{n}-1")
            await asyncio.sleep(0)
            exec_order.append(f"o{n}-2")
            val = await r()
            exec_order.append(f"o{n}-3")
            results.append(val + n * 100)

    await asyncio.gather(react_chain(1), react_chain(2))
    await reactcore.flush()
    x(5)
    await reactcore.flush()

    assert results == [111, 211, 115, 215]

    # This is the order of execution if the async observers are run
    # sequentially. The `asyncio.sleep(0)` still yields control, but since there
    # are no other observers scheduled, it will simply resume at the same point.
    # fmt: off
    assert exec_order == [
        'o1-1', 'o1-2', 'r1-1', 'r1-2', 'o1-3',
        'o2-1', 'o2-2', 'r2-1', 'r2-2', 'o2-3',
        'o1-1', 'o1-2', 'r1-1', 'r1-2', 'o1-3',
        'o2-1', 'o2-2', 'r2-1', 'r2-2', 'o2-3'
    ]
    # fmt: on


# ======================================================================
# isolate()
# ======================================================================
@pytest.mark.asyncio
async def test_isolate_basic_without_context():
    # isolate() works with Reactive and ReactiveVal; allows executing without a
    # reactive context.
    v = ReactiveVal(1)

    @reactive()
    def r():
        return v() + 10

    def get_r():
        return r()

    with isolate():
        assert v() == 1
        assert (lambda: v())() == 1
        assert r() == 11
        assert (lambda: r())() == 11
        assert get_r() == 11


@pytest.mark.asyncio
async def test_isolate_prevents_dependency():
    v = ReactiveVal(1)

    @reactive()
    def r():
        return v() + 10

    v_dep = ReactiveVal(1)  # Use this only for invalidating the observer
    o_val = None

    @observe()
    def o():
        nonlocal o_val
        v_dep()
        with isolate():
            o_val = r()

    await reactcore.flush()
    assert o_val == 11

    # Changing v() shouldn't invalidate o
    v(2)
    await reactcore.flush()
    assert o_val == 11
    assert o._exec_count == 1

    # v_dep() should invalidate the observer
    v_dep(2)
    await reactcore.flush()
    assert o_val == 12
    assert o._exec_count == 2


# ======================================================================
# async isolate
# ======================================================================
@pytest.mark.asyncio
async def test_isolate_async_basic_value():
    async def f():
        return 123

    with isolate():
        assert await f() == 123


@pytest.mark.asyncio
async def test_isolate_async_basic_without_context():
    # async isolate works with Reactive and ReactiveVal; allows executing
    # without a reactive context.
    v = ReactiveVal(1)

    @reactive_async()
    async def r():
        return v() + 10

    async def get_r():
        return await r()

    with isolate():
        assert await r() == 11
        assert await get_r() == 11


@pytest.mark.asyncio
async def test_isolate_async_prevents_dependency():
    v = ReactiveVal(1)

    @reactive_async()
    async def r():
        return v() + 10

    v_dep = ReactiveVal(1)  # Use this only for invalidating the observer
    o_val = None

    @observe_async()
    async def o():
        nonlocal o_val
        v_dep()
        with isolate():
            o_val = await r()

    await reactcore.flush()
    assert o_val == 11

    # Changing v() shouldn't invalidate o
    v(2)
    await reactcore.flush()
    assert o_val == 11
    assert o._exec_count == 1

    # v_dep() should invalidate the observer
    v_dep(2)
    await reactcore.flush()
    assert o_val == 12
    assert o._exec_count == 2


# ======================================================================
# Priority for observers
# ======================================================================
@pytest.mark.asyncio
async def test_observer_priority():
    v = ReactiveVal(1)
    results: list[int] = []

    @observe(priority=1)
    def o1():
        nonlocal results
        v()
        results.append(1)

    @observe(priority=2)
    def o2():
        nonlocal results
        v()
        results.append(2)

    @observe(priority=1)
    def o3():
        nonlocal results
        v()
        results.append(3)

    await reactcore.flush()
    assert results == [2, 1, 3]

    # Add another observer with priority 2. Only this one will run (until we
    # invalidate others by changing v).
    @observe(priority=2)
    def o4():
        nonlocal results
        v()
        results.append(4)

    results.clear()
    await reactcore.flush()
    assert results == [4]

    # Change v and run again, to make sure results are stable
    results.clear()
    v(2)
    await reactcore.flush()
    assert results == [2, 4, 1, 3]

    results.clear()
    v(3)
    await reactcore.flush()
    assert results == [2, 4, 1, 3]


# Same as previous, but with async
@pytest.mark.asyncio
async def test_observer_async_priority():
    v = ReactiveVal(1)
    results: list[int] = []

    @observe_async(priority=1)
    async def o1():
        nonlocal results
        v()
        results.append(1)

    @observe_async(priority=2)
    async def o2():
        nonlocal results
        v()
        results.append(2)

    @observe_async(priority=1)
    async def o3():
        nonlocal results
        v()
        results.append(3)

    await reactcore.flush()
    assert results == [2, 1, 3]

    # Add another observer with priority 2. Only this one will run (until we
    # invalidate others by changing v).
    @observe_async(priority=2)
    async def o4():
        nonlocal results
        v()
        results.append(4)

    results.clear()
    await reactcore.flush()
    assert results == [4]

    # Change v and run again, to make sure results are stable
    results.clear()
    v(2)
    await reactcore.flush()
    assert results == [2, 4, 1, 3]

    results.clear()
    v(3)
    await reactcore.flush()
    assert results == [2, 4, 1, 3]


# ======================================================================
# Destroying observers
# ======================================================================
@pytest.mark.asyncio
async def test_observer_destroy():
    v = ReactiveVal(1)
    results: list[int] = []

    @observe()
    def o1():
        nonlocal results
        v()
        results.append(1)

    await reactcore.flush()
    assert results == [1]

    v(2)
    o1.destroy()
    await reactcore.flush()
    assert results == [1]

    # Same as above, but destroy before running first time
    v = ReactiveVal(1)
    results: list[int] = []

    @observe()
    def o2():
        nonlocal results
        v()
        results.append(1)

    o2.destroy()
    await reactcore.flush()
    assert results == []


# ======================================================================
# Error handling
# ======================================================================
@pytest.mark.asyncio
async def test_error_handling():
    vals: List[str] = []

    @observe()
    def _():
        vals.append("o1")

    @observe()
    def _():
        vals.append("o2-1")
        raise Exception("Error here!")
        vals.append("o2-2")

    @observe()
    def _():
        vals.append("o3")

    # Error in observer should get converted to warning.
    with pytest.warns(reactcore.ReactiveWarning):
        await reactcore.flush()
    # All observers should have executed.
    assert vals == ["o1", "o2-1", "o3"]

    vals: List[str] = []

    @reactive()
    def r():
        vals.append("r")
        raise Exception("Error here!")

    @observe()
    def _():
        vals.append("o1-1")
        r()
        vals.append("o1-2")

    @observe()
    def _():
        vals.append("o2")

    # Error in observer should get converted to warning.
    with pytest.warns(reactcore.ReactiveWarning):
        await reactcore.flush()
    assert vals == ["o1-1", "r", "o2"]


@pytest.mark.asyncio
async def test_reactive_error_rethrow():
    # Make sure reactives re-throw errors.
    vals: List[str] = []
    v = ReactiveVal(1)

    @reactive()
    def r():
        vals.append("r")
        raise Exception("Error here!")

    @observe()
    def _():
        v()
        vals.append("o1-1")
        r()
        vals.append("o1-2")

    @observe()
    def _():
        v()
        vals.append("o2-2")
        r()
        vals.append("o2-2")

    with pytest.warns(reactcore.ReactiveWarning):
        await reactcore.flush()
    assert vals == ["o1-1", "r", "o2-2"]

    v(2)
    with pytest.warns(reactcore.ReactiveWarning):
        await reactcore.flush()
    assert vals == ["o1-1", "r", "o2-2", "o1-1", "o2-2"]


# ======================================================================
# Invalidating dependents
# ======================================================================
# For https://github.com/rstudio/prism/issues/26
@pytest.mark.asyncio
async def test_dependent_invalidation():
    trigger = ReactiveVal(0)
    v = ReactiveVal(0)
    error_occurred = False

    @observe()
    def _():
        trigger()

        try:
            with isolate():
                r()
                val = v()
                v(val + 1)
        except Exception:
            nonlocal error_occurred
            error_occurred = True

    @observe()
    def _():
        r()

    @reactive()
    def r():
        return v()

    await reactcore.flush()
    trigger(1)
    await reactcore.flush()

    with isolate():
        val = v()

    assert val == 2
    assert error_occurred is False


# ------------------------------------------------------------
# req() pauses execution in @observe() and @reactive()
# ------------------------------------------------------------
@pytest.mark.asyncio
async def test_req():
    n_times = 0

    @observe()
    def _():
        req(False)
        nonlocal n_times
        n_times += 1

    await reactcore.flush()
    assert n_times == 0

    @observe()
    def _():
        req(True)
        nonlocal n_times
        n_times += 1

    await reactcore.flush()
    assert n_times == 1

    @reactive()
    def r():
        req(False)
        return 1

    val = None

    @observe()
    def _():
        nonlocal val
        val = r()

    await reactcore.flush()
    assert val is None

    @reactive()
    def r2():
        req(True)
        return 1

    @observe()
    def _():
        nonlocal val
        val = r2()

    await reactcore.flush()
    assert val == 1


@pytest.mark.asyncio
async def test_invalidate_later():
    mock_time = MockTime()
    with mock_time():

        @observe()
        def obs1():
            invalidate_later(1)

        # Initial run happens immediately
        await reactcore.flush()
        assert obs1._exec_count == 1

        # If not enough time passes, no re-execution occurs
        await mock_time.advance_time(0.5)
        assert obs1._exec_count == 1

        # Re-execute after one second (total)
        await mock_time.advance_time(0.5)
        assert obs1._exec_count == 2

        # Make sure it happens repeatedly
        await mock_time.advance_time(10)
        assert obs1._exec_count == 12

        # After destruction, no more re-executions
        obs1.destroy()
        await mock_time.advance_time(10)
        assert obs1._exec_count == 12


@pytest.mark.asyncio
async def test_invalidate_later_invalidation():
    mock_time = MockTime()
    with mock_time():
        rv = ReactiveVal(0)

        @observe()
        def obs1():
            if rv() == 0:
                invalidate_later(1)

        await reactcore.flush()
        assert obs1._exec_count == 1

        # Change rv, triggering invalidation of obs1. The expected behavior is that
        # the invalidation causes the invalidate_later call to be cancelled.
        rv(1)
        await reactcore.flush()
        assert obs1._exec_count == 2

        # Advance time to long after the invalidate_later would have fired, and ensure
        # nothing happens.
        await mock_time.advance_time(10)
        assert obs1._exec_count == 2
        await reactcore.flush()
        assert obs1._exec_count == 2


@pytest.mark.asyncio
async def test_mock_time():

    mock_time = MockTime()

    with mock_time():
        results: List[str] = []

        async def add_result_later(delay: float, msg: str):
            await asyncio.sleep(delay)
            results.append(msg)

        asyncio.create_task(add_result_later(10, "a"))
        asyncio.create_task(add_result_later(5, "b"))
        task_c = asyncio.create_task(add_result_later(15, "c"))

        await mock_time.advance_time(11)

        assert results == ["b", "a"]
        # Prevent asyncio from complaining about a pending task not being complete
        task_c.cancel()


# ------------------------------------------------------------
# @event() works as expected
# ------------------------------------------------------------
def test_event_decorator():
    n_times = 0

    # By default, runs every time that event expression is _not_ None (ignore_none=True)
    @observe()
    @event(lambda: None, lambda: ActionButtonValue(0))
    def _():
        nonlocal n_times
        n_times += 1

    asyncio.run(reactcore.flush())
    assert n_times == 0

    # Unless ignore_none=False
    @observe()
    @event(lambda: None, lambda: ActionButtonValue(0), ignore_none=False)
    def _():
        nonlocal n_times
        n_times += 1

    asyncio.run(reactcore.flush())
    assert n_times == 1

    # Or if one of the args is not None
    @observe()
    @event(lambda: None, lambda: ActionButtonValue(0), lambda: True)
    def _():
        nonlocal n_times
        n_times += 1

    asyncio.run(reactcore.flush())
    assert n_times == 2

    # Is invalidated properly by reactive vals
    r = ReactiveVal(1)

    @observe()
    @event(r)
    def _():
        nonlocal n_times
        n_times += 1

    asyncio.run(reactcore.flush())
    assert n_times == 3

    r(1)
    asyncio.run(reactcore.flush())
    assert n_times == 3

    r(2)
    asyncio.run(reactcore.flush())
    assert n_times == 4

    # Doesn't run on init
    r = ReactiveVal(1)

    @observe()
    @event(r, ignore_init=True)
    def _():
        nonlocal n_times
        n_times += 1

    asyncio.run(reactcore.flush())
    assert n_times == 4

    r(2)
    asyncio.run(reactcore.flush())
    assert n_times == 5

    # Isolates properly
    r = ReactiveVal(1)
    r2 = ReactiveVal(1)

    @observe()
    @event(r)
    def _():
        nonlocal n_times
        n_times += r2()

    asyncio.run(reactcore.flush())
    assert n_times == 6

    r2(2)
    asyncio.run(reactcore.flush())
    assert n_times == 6

    # works with @reactive()
    r2 = ReactiveVal(1)

    @reactive()
    @event(lambda: r2(), ignore_init=True)
    def r2b():
        return 1

    @observe()
    def _():
        nonlocal n_times
        n_times += r2b()

    asyncio.run(reactcore.flush())
    assert n_times == 6

    r2(2)
    asyncio.run(reactcore.flush())
    assert n_times == 7


# ------------------------------------------------------------
# @event() works as expected with async
# ------------------------------------------------------------
def test_event_async_decorator():
    n_times = 0

    # By default, runs every time that event expression is _not_ None (ignore_none=True)
    @observe_async()
    @event(lambda: None, lambda: ActionButtonValue(0))
    async def _():
        nonlocal n_times
        n_times += 1

    asyncio.run(reactcore.flush())
    assert n_times == 0

    # Unless ignore_none=False
    @observe_async()
    @event(lambda: None, lambda: ActionButtonValue(0), ignore_none=False)
    async def _():
        nonlocal n_times
        n_times += 1

    asyncio.run(reactcore.flush())
    assert n_times == 1

    # Or if one of the args is not None
    @observe_async()
    @event(lambda: None, lambda: ActionButtonValue(0), lambda: True)
    async def _():
        nonlocal n_times
        n_times += 1

    asyncio.run(reactcore.flush())
    assert n_times == 2

    # Is invalidated properly by reactive vals
    r = ReactiveVal(1)

    @observe_async()
    @event(r)
    async def _():
        nonlocal n_times
        n_times += 1

    asyncio.run(reactcore.flush())
    assert n_times == 3

    r(1)
    asyncio.run(reactcore.flush())
    assert n_times == 3

    r(2)
    asyncio.run(reactcore.flush())
    assert n_times == 4

    # Doesn't run on init
    r = ReactiveVal(1)

    @observe_async()
    @event(r, ignore_init=True)
    async def _():
        nonlocal n_times
        n_times += 1

    asyncio.run(reactcore.flush())
    assert n_times == 4

    r(2)
    asyncio.run(reactcore.flush())
    assert n_times == 5

    # Isolates properly
    r = ReactiveVal(1)
    r2 = ReactiveVal(1)

    @observe_async()
    @event(r)
    async def _():
        nonlocal n_times
        n_times += r2()

    asyncio.run(reactcore.flush())
    assert n_times == 6

    r2(2)
    asyncio.run(reactcore.flush())
    assert n_times == 6

    # works with @reactive()
    r2 = ReactiveVal(1)

    @reactive_async()
    @event(lambda: r2(), ignore_init=True)
    async def r2b():
        return 1

    @observe_async()
    async def _():
        nonlocal n_times
        n_times += await r2b()

    asyncio.run(reactcore.flush())
    assert n_times == 6

    r2(2)
    asyncio.run(reactcore.flush())
    assert n_times == 7
