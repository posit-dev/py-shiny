#!/usr/bin/env python

"""Tests for `shiny.reactives` and `shiny.reactcore`."""

import pytest
import asyncio

import shiny.reactcore as reactcore
from shiny.reactives import *


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
    @Observer
    def o2():
        nonlocal v2_result
        v2_result = v2()
    @Observer
    def o1():
        v2(v1())

    asyncio.run(reactcore.flush())
    assert(v2_result == 1)
    assert(o2._exec_count == 2)
    assert(o1._exec_count == 1)


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
    @ObserverAsync
    async def o2():
        nonlocal v2_result
        v2_result = v2()
    @ObserverAsync
    async def o1():
        v2(v1())

    asyncio.run(reactcore.flush())
    assert(v2_result == 1)
    assert(o2._exec_count == 2)
    assert(o1._exec_count == 1)

# ======================================================================
# isolate()
# ======================================================================
def test_isolate_basic_value():
    # isolate() returns basic value
    assert isolate(lambda: 123) == 123
    assert isolate(lambda: None) is None

def test_isolate_basic_without_context():
    # isolate() works with Reactive and ReactiveVal; allows executing without a
    # reactive context.
    v = ReactiveVal(1)
    @Reactive
    def r():
        return v() + 10

    def get_r():
        return r()

    assert isolate(lambda: v()) == 1
    assert isolate(v) == 1
    assert isolate(lambda: r()) == 11
    assert isolate(r) == 11
    assert isolate(get_r) == 11

def test_isolate_prevents_dependency():
    v = ReactiveVal(1)
    @Reactive
    def r():
        return v() + 10

    v_dep = ReactiveVal(1)  # Use this only for invalidating the observer
    o_val = None
    @Observer
    def o():
        nonlocal o_val
        v_dep()
        o_val = isolate(lambda: r())

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
# isolate_async()
# ======================================================================
def test_isolate_async_basic_value():
    async def f():
        return 123
    async def go():
        assert await isolate_async(f) == 123
    asyncio.run(go())


def test_isolate_async_basic_without_context():
    # isolate_async() works with Reactive and ReactiveVal; allows executing
    # without a reactive context.
    v = ReactiveVal(1)
    @ReactiveAsync
    async def r():
        return v() + 10
    async def get_r():
        return await r()
    async def go():
        assert await isolate_async(r) == 11
        assert await isolate_async(get_r) == 11
    asyncio.run(go())


def test_isolate_async_prevents_dependency():
    v = ReactiveVal(1)
    @ReactiveAsync
    async def r():
        return v() + 10

    v_dep = ReactiveVal(1)  # Use this only for invalidating the observer
    o_val = None
    @ObserverAsync
    async def o():
        nonlocal o_val
        v_dep()
        o_val = await isolate_async(r)

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
