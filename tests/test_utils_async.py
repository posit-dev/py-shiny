#!/usr/bin/env python

"""Tests for `shiny.utils` async-related functions."""

import pytest
import asyncio
from typing import Any, Iterator
import types

from shiny.utils import run_coro_sync

def range_sync(n: int) -> Iterator[int]:
    """
    An implementation of `range()` which uses `yield`, but doesn't actually
    give up control to the event loop.
    """
    num = 0
    while num < n:
        yield num
        num += 1

@types.coroutine
def sleep0() -> None:
    """
    This is essentially the same as `asyncio.sleep(0)`. Because it's decorated
    with `@types.coroutine` AND has a `yield`, when called with `await
    sleep0()`, it actually gives up control.
    """
    yield

async def make_list_sync(n: int) -> list[int]:
    """
    An `async` function that is in fact synchronous; it does not actually give
    up control.
    """
    x: list[int] = []
    for i in range_sync(n):
        x.append(i)
    return x

async def make_list_async(n: int) -> list[int]:
    """An `async` function that gives up control."""
    x: list[int] = []
    for i in range_sync(n):
        await sleep0()
        x.append(i)
    return x



def test_run_coro_sync():
    # Running a coroutine that is in fact synchronous works fine.
    res = run_coro_sync(make_list_sync(1))
    assert res == [0]

    res = run_coro_sync(make_list_sync(3))
    assert res == [0, 1, 2]

    # Should error because the sleep0() gives up control.
    with pytest.raises(RuntimeError):
        run_coro_sync(make_list_async(1))

    with pytest.raises(RuntimeError):
        run_coro_sync(make_list_async(3))

    # Same with a direct call to sleep0() or asyncio.sleep()
    with pytest.raises(RuntimeError):
       run_coro_sync(sleep0())

    with pytest.raises(RuntimeError):
       run_coro_sync(asyncio.sleep(0))

    with pytest.raises(RuntimeError):
       run_coro_sync(asyncio.sleep(0.1))


def test_run_coro_async():
    async def async_main():
        # awaited calls to the in-fact-synchronous function are OK.
        res = await make_list_sync(3)
        assert res == [0, 1, 2]

        # awaited calls to the async function are OK.
        res = await make_list_async(3)
        assert res == [0, 1, 2]

        await sleep0()

        # Calling run_coro_sync() should be the same as when called normally
        # (from a regular function, not an async function run by asyncio.run()).
        res = run_coro_sync(make_list_sync(3))
        assert res == [0, 1, 2]

        with pytest.raises(RuntimeError):
            run_coro_sync(make_list_async(3))
        with pytest.raises(RuntimeError):
            run_coro_sync(sleep0())


    asyncio.run(async_main())
