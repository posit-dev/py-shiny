"""Tests for `shiny.reactive`."""

import asyncio
from typing import List

import pytest

from shiny import App, render, req, ui
from shiny._connection import MockConnection
from shiny.reactive import Value, calc, effect, event, flush, invalidate_later, isolate
from shiny.reactive._core import ReactiveWarning
from shiny.types import ActionButtonValue, SilentException

from .mocktime import MockTime


@pytest.mark.asyncio
async def test_flush_runs_newly_invalidated():
    """
    Make sure that a flush will also run any calcs that were invalidated during the
    flush.
    """

    v1 = Value(1)
    v2 = Value(2)

    v2_result = None

    # In practice, on the first flush, Effects run in the order that they were created.
    # Our test checks that o2 runs _after_ o1.
    @effect()
    def o2():
        nonlocal v2_result
        v2_result = v2()

    @effect()
    def o1():
        v2.set(v1())

    await flush()
    assert v2_result == 1
    assert o2._exec_count == 2
    assert o1._exec_count == 1


@pytest.mark.asyncio
async def test_flush_runs_newly_invalidated_async():
    """
    Make sure that a flush will also run any calcs that were invalidated during the
    flush. (Same as previous test, but async.)
    """

    v1 = Value(1)
    v2 = Value(2)

    v2_result = None

    # In practice, on the first flush, Effects run in the order that they were
    # created. Our test checks that o2 runs _after_ o1.
    @effect()
    async def o2():
        nonlocal v2_result
        v2_result = v2()

    @effect()
    async def o1():
        v2.set(v1())

    await flush()
    assert v2_result == 1
    assert o2._exec_count == 2
    assert o1._exec_count == 1


# ======================================================================
# Setting Value to same value doesn't invalidate downstream
# ======================================================================
@pytest.mark.asyncio
async def test_reactive_value_same_no_invalidate():
    v = Value(1)

    @effect()
    def o():
        v()

    await flush()
    assert o._exec_count == 1

    v.set(1)
    await flush()
    assert o._exec_count == 1


# ======================================================================
# Intializing reactive.Value to MISSING, and unsetting
# ======================================================================
@pytest.mark.asyncio
async def test_reactive_value_unset():
    v = Value[int]()

    with isolate():
        assert v.is_set() is False
        with pytest.raises(SilentException):
            v(warn_if_missing=False)

    val: int = 0

    @effect()
    def o():
        nonlocal val
        val = v(warn_if_missing=False)

    await flush()
    assert o._exec_count == 1
    assert val == 0

    v.set(1)
    await flush()
    assert o._exec_count == 2
    assert val == 1
    with isolate():
        assert v.is_set() is True

    v.unset()
    await flush()
    assert o._exec_count == 3
    assert val == 1
    with isolate():
        assert v.is_set() is False
        with pytest.raises(SilentException):
            v(warn_if_missing=False)


# ======================================================================
# reactive.Value.is_set() invalidates dependents only when set state changes
# ======================================================================
@pytest.mark.asyncio
async def test_reactive_value_is_set():
    v = Value[int]()
    v_is_set: bool = False

    @effect()
    def o():
        nonlocal v_is_set
        v_is_set = v.is_set()

    await flush()
    assert o._exec_count == 1
    assert v_is_set is False

    v.set(1)
    await flush()
    assert o._exec_count == 2
    assert v_is_set is True

    v.set(2)
    await flush()
    assert o._exec_count == 2
    assert v_is_set is True

    v.unset()
    await flush()
    assert o._exec_count == 3
    assert v_is_set is False

    v.unset()
    await flush()
    assert o._exec_count == 3
    assert v_is_set is False

    v.set(1)
    await flush()
    assert o._exec_count == 4
    assert v_is_set is True


# ======================================================================
# Recursive calls to calcs
# ======================================================================
@pytest.mark.asyncio
async def test_recursive_calc():
    v = Value(5)

    @calc()
    def r():
        if v() == 0:
            return 0
        v.set(v() - 1)
        r()

    @effect()
    def o():
        r()

    await flush()
    assert o._exec_count == 2
    assert r._exec_count == 6
    with isolate():
        assert v() == 0


@pytest.mark.asyncio
async def test_recursive_async_calc():
    v = Value(5)

    @calc()
    async def r() -> int:
        if v() == 0:
            return 0
        v.set(v() - 1)
        return await r()

    @effect()
    async def o():
        await r()

    await flush()
    assert o._exec_count == 2
    assert r._exec_count == 6
    with isolate():
        assert v() == 0


# ======================================================================
# async
# ======================================================================


@pytest.mark.asyncio
async def test_async_sequential():
    x: Value[int] = Value(1)
    results: list[int] = []
    exec_order: list[str] = []

    async def react_chain(n: int):
        @calc()
        async def r():
            exec_order.append(f"r{n}-1")
            await asyncio.sleep(0)
            exec_order.append(f"r{n}-2")
            return x() + 10

        @effect()
        async def _():
            exec_order.append(f"o{n}-1")
            await asyncio.sleep(0)
            exec_order.append(f"o{n}-2")
            val = await r()
            exec_order.append(f"o{n}-3")
            results.append(val + n * 100)

    await asyncio.gather(react_chain(1), react_chain(2))
    await flush()
    x.set(5)
    await flush()

    assert results == [111, 211, 115, 215]

    # This is the order of execution if the async effects are run sequentially. The
    # `asyncio.sleep(0)` still yields control, but since there are no other effects
    # scheduled, it will simply resume at the same point.
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
    # isolate() works with calc and Value; allows executing without a reactive context.
    v = Value(1)

    @calc()
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
    v = Value(1)

    @calc()
    def r():
        return v() + 10

    v_dep = Value(1)  # Use this only for invalidating the effect
    o_val = None

    @effect()
    def o():
        nonlocal o_val
        v_dep()
        with isolate():
            o_val = r()

    await flush()
    assert o_val == 11

    # Changing v() shouldn't invalidate o
    v.set(2)
    await flush()
    assert o_val == 11
    assert o._exec_count == 1

    # v_dep() should invalidate the effect
    v_dep.set(2)
    await flush()
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
    # async isolate works with calc and Value; allows executing without a reactive
    # context.
    v = Value(1)

    @calc()
    async def r():
        return v() + 10

    async def get_r():
        return await r()

    with isolate():
        assert await r() == 11
        assert await get_r() == 11


@pytest.mark.asyncio
async def test_isolate_async_prevents_dependency():
    v = Value(1)

    @calc()
    async def r():
        return v() + 10

    v_dep = Value(1)  # Use this only for invalidating the effect
    o_val = None

    @effect()
    async def o():
        nonlocal o_val
        v_dep()
        with isolate():
            o_val = await r()

    await flush()
    assert o_val == 11

    # Changing v() shouldn't invalidate o
    v.set(2)
    await flush()
    assert o_val == 11
    assert o._exec_count == 1

    # v_dep() should invalidate the effect
    v_dep.set(2)
    await flush()
    assert o_val == 12
    assert o._exec_count == 2


# ======================================================================
# Priority for effects
# ======================================================================
@pytest.mark.asyncio
async def test_effect_priority():
    v = Value(1)
    results: list[int] = []

    @effect(priority=1)
    def o1():
        v()
        results.append(1)

    @effect(priority=2)
    def o2():
        v()
        results.append(2)

    @effect(priority=1)
    def o3():
        v()
        results.append(3)

    await flush()
    assert results == [2, 1, 3]

    # Add another effect with priority 2. Only this one will run (until we
    # invalidate others by changing v).
    @effect(priority=2)
    def o4():
        v()
        results.append(4)

    results.clear()
    await flush()
    assert results == [4]

    # Change v and run again, to make sure results are stable
    results.clear()
    v.set(2)
    await flush()
    assert results == [2, 4, 1, 3]

    results.clear()
    v.set(3)
    await flush()
    assert results == [2, 4, 1, 3]


# Same as previous, but with async
@pytest.mark.asyncio
async def test_async_effect_priority():
    v = Value(1)
    results: list[int] = []

    @effect(priority=1)
    async def o1():
        v()
        results.append(1)

    @effect(priority=2)
    async def o2():
        v()
        results.append(2)

    @effect(priority=1)
    async def o3():
        v()
        results.append(3)

    await flush()
    assert results == [2, 1, 3]

    # Add another effect with priority 2. Only this one will run (until we
    # invalidate others by changing v).
    @effect(priority=2)
    async def o4():
        v()
        results.append(4)

    results.clear()
    await flush()
    assert results == [4]

    # Change v and run again, to make sure results are stable
    results.clear()
    v.set(2)
    await flush()
    assert results == [2, 4, 1, 3]

    results.clear()
    v.set(3)
    await flush()
    assert results == [2, 4, 1, 3]


# ======================================================================
# Destroying effects
# ======================================================================
@pytest.mark.asyncio
async def test_effect_destroy():
    v = Value(1)
    results: list[int] = []

    @effect()
    def o1():
        v()
        results.append(1)

    await flush()
    assert results == [1]

    v.set(2)
    o1.destroy()
    await flush()
    assert results == [1]

    # Same as above, but destroy before running first time
    v = Value(1)
    results: list[int] = []

    @effect()
    def o2():
        v()
        results.append(1)

    o2.destroy()
    await flush()
    assert results == []


# ======================================================================
# Error handling
# ======================================================================
@pytest.mark.asyncio
async def test_error_handling():
    vals: List[str] = []

    @effect()
    def _():
        vals.append("o1")

    @effect()
    def _():
        vals.append("o2-1")
        raise Exception("Error here!")
        vals.append("o2-2")

    @effect()
    def _():
        vals.append("o3")

    # Error in effect should get converted to warning.
    with pytest.warns(ReactiveWarning):
        await flush()
    # All effects should have executed.
    assert vals == ["o1", "o2-1", "o3"]

    vals: List[str] = []

    @calc()
    def r():
        vals.append("r")
        raise Exception("Error here!")

    @effect()
    def _():
        vals.append("o1-1")
        r()
        vals.append("o1-2")

    @effect()
    def _():
        vals.append("o2")

    # Error in effect should get converted to warning.
    with pytest.warns(ReactiveWarning):
        await flush()
    assert vals == ["o1-1", "r", "o2"]


@pytest.mark.asyncio
async def test_calc_error_rethrow():
    # Make sure calcs re-throw errors.
    vals: List[str] = []
    v = Value(1)

    @calc()
    def r():
        vals.append("r")
        raise Exception("Error here!")

    @effect()
    def _():
        v()
        vals.append("o1-1")
        r()
        vals.append("o1-2")

    @effect()
    def _():
        v()
        vals.append("o2-2")
        r()
        vals.append("o2-2")

    with pytest.warns(ReactiveWarning):
        await flush()
    assert vals == ["o1-1", "r", "o2-2"]

    v.set(2)
    with pytest.warns(ReactiveWarning):
        await flush()
    assert vals == ["o1-1", "r", "o2-2", "o1-1", "o2-2"]


# ======================================================================
# Invalidating dependents
# ======================================================================
# For https://github.com/posit-dev/py-shiny/issues/26
@pytest.mark.asyncio
async def test_dependent_invalidation():
    trigger = Value(0)
    v = Value(0)
    error_occurred = False

    @effect()
    def _():
        trigger()

        try:
            with isolate():
                r()
                val = v()
                v.set(val + 1)
        except Exception:
            nonlocal error_occurred
            error_occurred = True

    @effect()
    def _():
        r()

    @calc()
    def r():
        return v()

    await flush()
    trigger.set(1)
    await flush()

    with isolate():
        val = v()

    assert val == 2
    assert error_occurred is False


# ------------------------------------------------------------
# req() pauses execution in @effect() and @calc()
# ------------------------------------------------------------
@pytest.mark.asyncio
async def test_req():
    n_times = 0

    @effect()
    def _():
        req(False)
        nonlocal n_times
        n_times += 1

    await flush()
    assert n_times == 0

    @effect()
    def _():
        req(True)
        nonlocal n_times
        n_times += 1

    await flush()
    assert n_times == 1

    @calc()
    def r():
        req(False)
        return 1

    val = None

    @effect()
    def _():
        nonlocal val
        val = r()

    await flush()
    assert val is None

    @calc()
    def r2():
        req(True)
        return 1

    @effect()
    def _():
        nonlocal val
        val = r2()

    await flush()
    assert val == 1


@pytest.mark.asyncio
async def test_invalidate_later():
    mock_time = MockTime()
    with mock_time():

        @effect()
        def obs1():
            invalidate_later(1)

        # Initial run happens immediately
        await flush()
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
        rv = Value(0)

        @effect()
        def obs1():
            if rv() == 0:
                invalidate_later(1)

        await flush()
        assert obs1._exec_count == 1

        # Change rv, triggering invalidation of obs1. The expected behavior is that
        # the invalidation causes the invalidate_later call to be cancelled.
        rv.set(1)
        await flush()
        assert obs1._exec_count == 2

        # Advance time to long after the invalidate_later would have fired, and ensure
        # nothing happens.
        await mock_time.advance_time(10)
        assert obs1._exec_count == 2
        await flush()
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
# @reactive.event() works as expected
# ------------------------------------------------------------
@pytest.mark.asyncio
async def test_event_decorator():
    n_times = 0

    # By default, runs every time that event expression is _not_ None (ignore_none=True)
    @effect()
    @event(lambda: None, lambda: ActionButtonValue(0))
    def _():
        nonlocal n_times
        n_times += 1

    await flush()
    assert n_times == 0

    # Unless ignore_none=False
    @effect()
    @event(lambda: None, lambda: ActionButtonValue(0), ignore_none=False)
    def _():
        nonlocal n_times
        n_times += 1

    await flush()
    assert n_times == 1

    # Or if one of the args is not None
    @effect()
    @event(lambda: None, lambda: ActionButtonValue(0), lambda: True)
    def _():
        nonlocal n_times
        n_times += 1

    await flush()
    assert n_times == 2

    # Is invalidated properly by reactive values
    v = Value(1)

    @effect()
    @event(v)
    def _():
        nonlocal n_times
        n_times += 1

    await flush()
    assert n_times == 3

    v.set(1)
    await flush()
    assert n_times == 3

    v.set(2)
    await flush()
    assert n_times == 4

    # Doesn't run on init
    v = Value(1)

    @effect()
    @event(v, ignore_init=True)
    def _():
        nonlocal n_times
        n_times += 1

    await flush()
    assert n_times == 4

    v.set(2)
    await flush()
    assert n_times == 5

    # Isolates properly
    v = Value(1)
    v2 = Value(1)

    @effect()
    @event(v)
    def _():
        nonlocal n_times
        n_times += v2()

    await flush()
    assert n_times == 6

    v2.set(2)
    await flush()
    assert n_times == 6

    # works with @calc()
    v2 = Value(1)

    @calc()
    @event(lambda: v2(), ignore_init=True)
    def r2b():
        return 1

    @effect()
    def _():
        nonlocal n_times
        n_times += r2b()

    await flush()
    assert n_times == 6

    v2.set(2)
    await flush()
    assert n_times == 7


# ------------------------------------------------------------
# @event() works as expected with async
# ------------------------------------------------------------
@pytest.mark.asyncio
async def test_event_async_decorator():
    n_times = 0

    # By default, runs every time that event expression is _not_ None (ignore_none=True)
    @effect()
    @event(lambda: None, lambda: ActionButtonValue(0))
    async def _():
        nonlocal n_times
        n_times += 1

    await flush()
    assert n_times == 0

    # Unless ignore_none=False
    @effect()
    @event(lambda: None, lambda: ActionButtonValue(0), ignore_none=False)
    async def _():
        nonlocal n_times
        n_times += 1

    await flush()
    assert n_times == 1

    # Or if one of the args is not None
    @effect()
    @event(lambda: None, lambda: ActionButtonValue(0), lambda: True)
    async def _():
        nonlocal n_times
        n_times += 1

    await flush()
    assert n_times == 2

    # Is invalidated properly by reactive values
    v = Value(1)

    @effect()
    @event(v)
    async def _():
        nonlocal n_times
        n_times += 1

    await flush()
    assert n_times == 3

    v.set(1)
    await flush()
    assert n_times == 3

    v.set(2)
    await flush()
    assert n_times == 4

    # Doesn't run on init
    v = Value(1)

    @effect()
    @event(v, ignore_init=True)
    async def _():
        nonlocal n_times
        n_times += 1

    await flush()
    assert n_times == 4

    v.set(2)
    await flush()
    assert n_times == 5

    # Isolates properly
    v = Value(1)
    v2 = Value(1)

    @effect()
    @event(v)
    async def _():
        nonlocal n_times
        n_times += v2()

    await flush()
    assert n_times == 6

    v2.set(2)
    await flush()
    assert n_times == 6

    # works with @calc()
    v2 = Value(1)

    @calc()
    async def r_a():
        await asyncio.sleep(0)  # Make sure the async function yields control
        return 1

    @calc()
    @event(lambda: v2(), r_a, ignore_init=True)
    async def r2b():
        await asyncio.sleep(0)  # Make sure the async function yields control
        return 1

    @effect()
    async def _():
        nonlocal n_times
        await asyncio.sleep(0)
        n_times += await r2b()

    await flush()
    assert n_times == 6

    v2.set(2)
    await flush()
    assert n_times == 7


# ------------------------------------------------------------
# @event() handles silent exceptions in event function
# ------------------------------------------------------------
@pytest.mark.asyncio
async def test_event_silent_exception():
    n_times = 0
    x = Value[bool]()

    @effect()
    @event(lambda: x(warn_if_missing=False))
    def _():
        nonlocal n_times
        n_times += 1

    await flush()
    assert n_times == 0

    x.set(True)
    await flush()
    assert n_times == 1

    x.unset()
    await flush()
    assert n_times == 1

    x.set(True)
    await flush()
    assert n_times == 2


# ------------------------------------------------------------
# @event() handles silent exceptions in event function, async
# ------------------------------------------------------------
@pytest.mark.asyncio
async def test_event_silent_exception_async():
    n_times = 0
    x = Value[bool]()

    async def req_fn() -> int:
        await asyncio.sleep(0)
        x(warn_if_missing=False)
        return 1234

    @effect()
    @event(req_fn)
    async def _():
        await asyncio.sleep(0)
        nonlocal n_times
        n_times += 1

    await flush()
    assert n_times == 0

    x.set(True)
    await flush()
    assert n_times == 1

    x.unset()
    await flush()
    assert n_times == 1

    x.set(True)
    await flush()
    assert n_times == 2


# ------------------------------------------------------------
# @event() throws runtime errors if passed wrong type
# ------------------------------------------------------------
@pytest.mark.asyncio
async def test_event_type_check():
    with pytest.raises(TypeError):
        # Should complain about missing argument to @event().
        @event()
        async def _(): ...

    with pytest.raises(TypeError):
        # Should complain that @event() can't take the result of @Effect (which returns
        # None).
        @event(lambda: 1)  # pyright: ignore[reportArgumentType]
        @effect()
        async def _(): ...

    with pytest.raises(TypeError):
        # Should complain that @event must be applied before @Calc.
        @event(lambda: 1)
        @calc()
        async def _(): ...

    with pytest.raises(TypeError):
        # Should complain that @event must be applied before @render.text. At some point
        # in the future, this may be allowed.
        @event(lambda: 1)  # pyright: ignore[reportArgumentType]
        @render.text
        async def _(): ...

    with pytest.raises(TypeError):
        # Should complain that @event must be applied before @output.
        @event(lambda: 1)  # pyright: ignore[reportArgumentType]
        @render.text
        async def _(): ...

    # These are OK
    @event(lambda: 1)
    async def _(): ...

    @effect()
    @event(lambda: 1)
    async def _(): ...

    @calc()
    @event(lambda: 1)
    async def _(): ...

    @render.text
    @event(lambda: 1)
    async def _(): ...


# ------------------------------------------------------------
# @output() throws runtime errors if passed wrong type
# ------------------------------------------------------------
@pytest.mark.asyncio
async def test_output_type_check():
    conn = MockConnection()
    session = App(ui.TagList(), None)._create_session(conn)
    output = session.output

    with pytest.raises(TypeError):
        # Should complain about bare function
        @output  # pyright: ignore[reportArgumentType,reportUntypedFunctionDecorator]
        def _(): ...

    with pytest.raises(TypeError):
        # Should complain about @event
        @output  # pyright: ignore[reportArgumentType,reportUntypedFunctionDecorator]
        @event(lambda: 1)
        def _(): ...

    with pytest.raises(TypeError):
        # Should complain about @event, even with render.text. Although maybe in the
        # future this will be allowed.
        @output  # pyright: ignore[reportArgumentType,reportUntypedFunctionDecorator]
        @event(lambda: 1)  # pyright: ignore[reportArgumentType]
        @render.text
        def _(): ...

    with pytest.raises(TypeError):
        # Should complain about @Calc
        @output  # pyright: ignore[reportArgumentType,reportUntypedFunctionDecorator]
        @calc
        def _(): ...

    with pytest.raises(TypeError):
        # Should complain about @Effet
        @output  # pyright: ignore[reportArgumentType,reportUntypedFunctionDecorator]
        @effect
        def _(): ...

    @render.text
    def _(): ...

    @render.plot
    @event(lambda: 1)
    def _(): ...


# ------------------------------------------------------------
# @effect()'s .suspend()/.resume() works as expected
# ------------------------------------------------------------
@pytest.mark.asyncio
async def test_effect_pausing():
    a = Value(float(1))

    @calc()
    def funcA():
        return a()

    @effect()
    def obsB():
        funcA()

    # Important: suspend() only affects effect at invalidation time

    # Effects are invalidated at creation time, so it will run once regardless
    # of being suspended
    obsB.suspend()
    await flush()
    assert funcA._exec_count == 1
    assert obsB._exec_count == 1

    # When resuming, if nothing changed, don't do anything
    obsB.resume()
    await flush()
    assert funcA._exec_count == 1
    assert obsB._exec_count == 1

    # Make sure suspended effects do not flush, but do invalidate
    obsB_invalidated = False

    def _():
        nonlocal obsB_invalidated
        obsB_invalidated = True

    obsB.on_invalidate(_)
    obsB.suspend()
    a.set(2)
    await flush()
    assert obsB_invalidated
    assert funcA._exec_count == 1
    assert obsB._exec_count == 1

    obsB.resume()
    a.set(2.5)
    obsB.suspend()
    await flush()
    assert funcA._exec_count == 2
    assert obsB._exec_count == 2

    a.set(3)
    await flush()
    assert funcA._exec_count == 2
    assert obsB._exec_count == 2

    # If on_invalidate() is added _after_ obsB is suspended and the a changes,
    # then it shouldn't get run (on_invalidate runs on invalidation, not on flush)
    a.set(4)
    obsB_invalidated2 = False

    def _():
        nonlocal obsB_invalidated2
        obsB_invalidated2 = True

    obsB.on_invalidate(_)
    obsB.resume()
    await flush()
    assert not obsB_invalidated2
    assert funcA._exec_count == 3
    assert obsB._exec_count == 3

    obsB.suspend()
    a.set(5)
    obsB.destroy()
    obsB.resume()
    await flush()
    assert funcA._exec_count == 3
    assert obsB._exec_count == 3


# ------------------------------------------------------------
# @effect()'s .suspend()/.resume() works as expected (with async)
# ------------------------------------------------------------
@pytest.mark.asyncio
async def test_effect_async_pausing():
    a = Value(float(1))

    @calc()
    async def funcA():
        return a()

    @effect()
    async def obsB():
        await funcA()

    # Important: suspend() only affects effect at invalidation time

    # Effects are invalidated at creation time, so it will run once regardless
    # of being suspended
    obsB.suspend()
    await flush()
    assert funcA._exec_count == 1
    assert obsB._exec_count == 1

    # When resuming, if nothing changed, don't do anything
    obsB.resume()
    await flush()
    assert funcA._exec_count == 1
    assert obsB._exec_count == 1

    # Make sure suspended effects do not flush, but do invalidate
    obsB_invalidated = False

    def _():
        nonlocal obsB_invalidated
        obsB_invalidated = True

    obsB.on_invalidate(_)
    obsB.suspend()
    a.set(2)
    await flush()
    assert obsB_invalidated
    assert funcA._exec_count == 1
    assert obsB._exec_count == 1

    obsB.resume()
    a.set(2.5)
    obsB.suspend()
    await flush()
    assert funcA._exec_count == 2
    assert obsB._exec_count == 2

    a.set(3)
    await flush()
    assert funcA._exec_count == 2
    assert obsB._exec_count == 2

    # If on_invalidate() is added _after_ obsB is suspended and a changes,
    # then it shouldn't get run (on_invalidate runs on invalidation, not on flush)
    a.set(4)
    obsB_invalidated2 = False

    def _():
        nonlocal obsB_invalidated2
        obsB_invalidated2 = True

    obsB.on_invalidate(_)
    obsB.resume()
    await flush()
    assert not obsB_invalidated2
    assert funcA._exec_count == 3
    assert obsB._exec_count == 3

    obsB.suspend()
    a.set(5)
    obsB.destroy()
    obsB.resume()
    await flush()
    assert funcA._exec_count == 3
    assert obsB._exec_count == 3


@pytest.mark.asyncio
async def test_observer_async_suspended_resumed_observers_run_at_most_once():
    a = Value(1)

    @effect()
    async def obs():
        print(a())

    # First flush should run obs once
    assert obs._exec_count == 0
    await flush()
    assert obs._exec_count == 1

    # Modify the dependency at each stage of suspend/resume/flush should still
    # only result in one run of obs()
    a.set(2)
    obs.suspend()
    a.set(3)
    obs.resume()
    a.set(4)
    await flush()
    assert obs._exec_count == 2


# ======================================================================
# reactive.Value.get() with default parameter
# ======================================================================
@pytest.mark.asyncio
async def test_reactive_value_get_with_default():
    # Test with unset value - should return default
    v = Value[int]()

    with isolate():
        assert v.get(default=42) == 42
        assert v.get(default=0) == 0
        assert v.get(default=None) is None

    # Test after setting value - should return value, not default
    v.set(100)
    with isolate():
        assert v.get(default=42) == 100
        assert v.get(default=0) == 100

    # Test after unsetting - should return default again
    v.unset()
    with isolate():
        assert v.get(default=99) == 99


@pytest.mark.asyncio
async def test_reactive_value_call_with_default():
    # Test that __call__ also supports default parameter
    v = Value[str]()

    with isolate():
        assert v(default="hello") == "hello"
        assert v(default=None) is None

    v.set("world")
    with isolate():
        assert v(default="hello") == "world"

    v.unset()
    with isolate():
        assert v(default="fallback") == "fallback"


@pytest.mark.asyncio
async def test_reactive_value_default_in_reactive_context():
    # Test using default parameter within reactive contexts
    v = Value[int]()
    result = None

    @effect()
    def obs():
        nonlocal result
        result = v.get(default=10)

    await flush()
    assert result == 10
    assert obs._exec_count == 1

    # Setting the value should invalidate and return new value
    v.set(50)
    await flush()
    assert result == 50
    assert obs._exec_count == 2

    # Unsetting should use default again
    v.unset()
    await flush()
    assert result == 10
    assert obs._exec_count == 3


@pytest.mark.asyncio
async def test_reactive_value_no_default_raises_silent_exception():
    # Test that without default, unset value still raises SilentException
    v = Value[int]()

    with isolate():
        with pytest.raises(SilentException):
            v.get()
        with pytest.raises(SilentException):
            v()


# ======================================================================
# reactive.Value warning behavior
# ======================================================================
@pytest.mark.asyncio
async def test_reactive_value_missing_warning():
    # Test that reading unset value with warn_if_missing=True logs warning
    v = Value[int]()

    with isolate():
        with pytest.warns(
            ReactiveWarning, match="Attempted to read a `reactive.value`"
        ):
            try:
                v.get()
            except SilentException:
                pass


@pytest.mark.asyncio
async def test_reactive_value_suppress_warning():
    # Test that warn_if_missing=False suppresses the warning
    v = Value[int]()

    with isolate():
        # Should not produce a warning
        with pytest.raises(SilentException):
            v.get(warn_if_missing=False)


@pytest.mark.asyncio
async def test_reactive_value_default_no_warning():
    # Test that providing a default doesn't generate warning
    v = Value[int]()

    with isolate():
        # Should not raise or warn when default is provided
        result = v.get(default=42)
        assert result == 42


@pytest.mark.asyncio
async def test_input_value_missing_warning():
    # Test that reading unset input value shows input-specific warning
    conn = MockConnection()
    session = App(ui.TagList(), None)._create_session(conn)
    input = session.input

    # Access an input that doesn't exist yet
    with isolate():
        with pytest.warns(
            ReactiveWarning, match=r"Attempted to read `input\.test_input\(\)`"
        ):
            try:
                input.test_input()
            except SilentException:
                pass


@pytest.mark.asyncio
async def test_input_value_with_default():
    # Test that input values can use default parameter
    conn = MockConnection()
    session = App(ui.TagList(), None)._create_session(conn)
    input = session.input

    with isolate():
        # Should return default without warning or exception
        result = input.test_input(default="fallback")
        assert result == "fallback"


@pytest.mark.asyncio
async def test_input_value_suppress_warning():
    # Test that warn_if_missing=False suppresses input warning
    conn = MockConnection()
    session = App(ui.TagList(), None)._create_session(conn)
    input = session.input

    with isolate():
        # Should not produce a warning
        with pytest.raises(SilentException):
            input.test_input(warn_if_missing=False)
