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
