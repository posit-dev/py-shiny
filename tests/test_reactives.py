"""Tests for `shiny.reactives` and `shiny.reactcore`."""

import pytest
import asyncio

import shiny.reactcore as reactcore
from shiny.reactives import *
from shiny.validation import req


def test_flush_runs_newly_invalidated():
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

    asyncio.run(reactcore.flush())
    assert v2_result == 1
    assert o2._exec_count == 2
    assert o1._exec_count == 1


def test_flush_runs_newly_invalidated_async():
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

    asyncio.run(reactcore.flush())
    assert v2_result == 1
    assert o2._exec_count == 2
    assert o1._exec_count == 1


# ======================================================================
# Setting ReactiveVal to same value doesn't invalidate downstream
# ======================================================================
def test_reactive_val_same_no_invalidate():
    v = ReactiveVal(1)

    @observe()
    def o():
        v()

    asyncio.run(reactcore.flush())
    assert o._exec_count == 1

    v(1)
    asyncio.run(reactcore.flush())
    assert o._exec_count == 1


test_reactive_val_same_no_invalidate()

# ======================================================================
# Recursive calls to reactives
# ======================================================================
def test_recursive_reactive():
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

    asyncio.run(reactcore.flush())
    assert o._exec_count == 2
    assert r._exec_count == 6
    with isolate():
        assert v() == 0


def test_recursive_reactive_async():
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

    asyncio.run(reactcore.flush())
    assert o._exec_count == 2
    assert r._exec_count == 6
    with isolate():
        assert v() == 0


# ======================================================================
# Concurrent/sequential async
# ======================================================================
def test_async_concurrent():
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

    async def go():
        await asyncio.gather(react_chain(1), react_chain(2))

        await reactcore.flush()

        x(5)
        await reactcore.flush()

    asyncio.run(go())

    assert results == [111, 211, 115, 215]

    # fmt: off
    # This is the order of execution if async observers are run with separate
    # (interleaved) tasks. When it hits an `asyncio.sleep(0)`, it will yield
    # control and then the other observer in the other task will run.
    assert exec_order == [
        'o1-1', 'o2-1',
        'o1-2', 'o2-2',
        'r1-1', 'r2-1',
        'r1-2', 'r2-2',
        'o1-3', 'o2-3',
        'o1-1', 'o2-1',
        'o1-2', 'o2-2',
        'r1-1', 'r2-1',
        'r1-2', 'r2-2',
        'o1-3', 'o2-3'
    ]
    # fmt: on


def test_async_sequential():
    # Same as previous, but with a sequential flush, as in
    # `flush(concurrent=False)`.
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

    async def go():
        await asyncio.gather(react_chain(1), react_chain(2))

        await reactcore.flush(concurrent=False)

        x(5)
        await reactcore.flush(concurrent=False)

    asyncio.run(go())

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
def test_isolate_basic_without_context():
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


def test_isolate_prevents_dependency():
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

    asyncio.run(reactcore.flush())
    assert o_val == 11

    # Changing v() shouldn't invalidate o
    v(2)
    asyncio.run(reactcore.flush())
    assert o_val == 11
    assert o._exec_count == 1

    # v_dep() should invalidate the observer
    v_dep(2)
    asyncio.run(reactcore.flush())
    assert o_val == 12
    assert o._exec_count == 2


# ======================================================================
# async isolate
# ======================================================================
def test_isolate_async_basic_value():
    async def f():
        return 123

    async def go():
        with isolate():
            assert await f() == 123

    asyncio.run(go())


def test_isolate_async_basic_without_context():
    # async isolate works with Reactive and ReactiveVal; allows executing
    # without a reactive context.
    v = ReactiveVal(1)

    @reactive_async()
    async def r():
        return v() + 10

    async def get_r():
        return await r()

    async def go():
        with isolate():
            assert await r() == 11
            assert await get_r() == 11

    asyncio.run(go())


def test_isolate_async_prevents_dependency():
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

    asyncio.run(reactcore.flush())
    assert o_val == 11

    # Changing v() shouldn't invalidate o
    v(2)
    asyncio.run(reactcore.flush())
    assert o_val == 11
    assert o._exec_count == 1

    # v_dep() should invalidate the observer
    v_dep(2)
    asyncio.run(reactcore.flush())
    assert o_val == 12
    assert o._exec_count == 2


# ======================================================================
# Priority for observers
# ======================================================================
def test_observer_priority():
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

    asyncio.run(reactcore.flush())
    assert results == [2, 1, 3]

    # Add another observer with priority 2. Only this one will run (until we
    # invalidate others by changing v).
    @observe(priority=2)
    def o4():
        nonlocal results
        v()
        results.append(4)

    results.clear()
    asyncio.run(reactcore.flush())
    assert results == [4]

    # Change v and run again, to make sure results are stable
    results.clear()
    v(2)
    asyncio.run(reactcore.flush())
    assert results == [2, 4, 1, 3]

    results.clear()
    v(3)
    asyncio.run(reactcore.flush())
    assert results == [2, 4, 1, 3]


# Same as previous, but with async
def test_observer_async_priority():
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

    asyncio.run(reactcore.flush())
    assert results == [2, 1, 3]

    # Add another observer with priority 2. Only this one will run (until we
    # invalidate others by changing v).
    @observe_async(priority=2)
    async def o4():
        nonlocal results
        v()
        results.append(4)

    results.clear()
    asyncio.run(reactcore.flush())
    assert results == [4]

    # Change v and run again, to make sure results are stable
    results.clear()
    v(2)
    asyncio.run(reactcore.flush())
    assert results == [2, 4, 1, 3]

    results.clear()
    v(3)
    asyncio.run(reactcore.flush())
    assert results == [2, 4, 1, 3]


# ======================================================================
# Destroying observers
# ======================================================================
def test_observer_destroy():
    v = ReactiveVal(1)
    results: list[int] = []

    @observe()
    def o1():
        nonlocal results
        v()
        results.append(1)

    asyncio.run(reactcore.flush())
    assert results == [1]

    v(2)
    o1.destroy()
    asyncio.run(reactcore.flush())
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
    asyncio.run(reactcore.flush())
    assert results == []


# ======================================================================
# Invalidating dependents
# ======================================================================
# For https://github.com/rstudio/prism/issues/26
def test_dependent_invalidation():
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

    asyncio.run(reactcore.flush())
    trigger(1)
    asyncio.run(reactcore.flush())

    with isolate():
        val = v()

    assert val == 2
    assert error_occurred == False


# ------------------------------------------------------------
# req() pauses execution in @observe() and @reactive()
# ------------------------------------------------------------
def test_req():
    n_times = 0

    @observe()
    def _():
        req(False)
        nonlocal n_times
        n_times += 1

    asyncio.run(reactcore.flush())
    assert n_times == 0

    @observe()
    def _():
        req(True)
        nonlocal n_times
        n_times += 1

    asyncio.run(reactcore.flush())
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

    asyncio.run(reactcore.flush())
    assert val is None

    @reactive()
    def r2():
        req(True)
        return 1

    @observe()
    def _():
        nonlocal val
        val = r2()

    asyncio.run(reactcore.flush())
    assert val == 1
