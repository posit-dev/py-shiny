"""Tests for `shiny.utils` async-related functions."""

import contextvars
import pytest
import asyncio
from typing import Iterator, List

from shiny._utils import run_coro_sync, run_coro_hybrid


def range_sync(n: int) -> Iterator[int]:
    """
    An implementation of `range()` which uses `yield`, but doesn't actually
    give up control to the event loop.
    """
    num = 0
    while num < n:
        yield num
        num += 1


async def make_list_sync(n: int) -> List[int]:
    """
    An `async` function that is in fact synchronous; it does not actually give
    up control.
    """
    x: list[int] = []
    for i in range_sync(n):
        x.append(i)
    return x


async def make_list_async(n: int) -> List[int]:
    """An `async` function that gives up control."""
    x: list[int] = []
    for i in range_sync(n):
        await asyncio.sleep(0)
        x.append(i)
    return x


def test_run_coro_sync():
    # Running a coroutine that is in fact synchronous works fine.
    res = run_coro_sync(make_list_sync(1))
    assert res == [0]

    res = run_coro_sync(make_list_sync(3))
    assert res == [0, 1, 2]

    # Should error because the asyncio.sleep() gives up control.
    with pytest.raises(RuntimeError):
        run_coro_sync(make_list_async(1))

    with pytest.raises(RuntimeError):
        run_coro_sync(make_list_async(3))

    # Same with a direct call to asyncio.sleep()
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

        await asyncio.sleep(0)

        # Calling run_coro_sync() should be the same as when called normally
        # (from a regular function, not an async function run by asyncio.run()).
        res = run_coro_sync(make_list_sync(3))
        assert res == [0, 1, 2]

        with pytest.raises(RuntimeError):
            run_coro_sync(make_list_async(3))
        with pytest.raises(RuntimeError):
            run_coro_sync(asyncio.sleep(0))

    asyncio.run(async_main())


def test_run_coro_sync_type_check():
    # Should raise an error if passed a regular generator (as opposed to a
    # coroutine object).
    with pytest.raises(TypeError):
        run_coro_sync(range_sync(0))  # type: ignore


def test_async_generator():
    # run_coro_sync() can't run async generators, but it can run async functions
    # which call async generators.

    # An async generator
    async def async_gen_range(n: int):
        for i in range(n):
            yield i

    # An async function which uses the generator
    async def main(n: int):
        x: list[int] = []
        async for i in async_gen_range(n):
            x.append(i)
        return x

    # Running the async function works fine.
    res = run_coro_sync(main(3))
    assert res == [0, 1, 2]

    # Attempting to run the async generator results in an error, because it
    # doesn't return a coroutine object.
    with pytest.raises(TypeError):
        run_coro_sync(async_gen_range(3))  # type: ignore


def test_create_task():
    # Should be OK to call create_task().
    async def create_task_wrapper():
        async def inner():
            asyncio.create_task(make_list_async(3))

        run_coro_sync(inner())

    asyncio.run(create_task_wrapper())

    # Should not be OK to await a task, because it doesn't complete immediately.
    async def create_task_wrapper2():
        async def inner():
            await asyncio.create_task(make_list_async(3))

        run_coro_sync(inner())

    with pytest.raises(RuntimeError):
        asyncio.run(create_task_wrapper2())


@pytest.mark.asyncio
async def test_coro_hybrid():
    state = 0

    async def test_task() -> int:
        nonlocal state
        state = 1
        await asyncio.sleep(0)
        state = 2
        await asyncio.sleep(0.1)
        state = 3
        return 100

    assert state == 0
    fut = run_coro_hybrid(test_task())
    assert state == 1
    await asyncio.sleep(0.01)
    assert state == 2
    await asyncio.sleep(0.1)
    assert state == 3
    assert await fut == 100


@pytest.mark.asyncio
async def test_coro_hybrid_throw():
    async def test_task_throw():
        raise ValueError("boom")

    fut = run_coro_hybrid(test_task_throw())
    with pytest.raises(ValueError):
        await fut


@pytest.mark.asyncio
async def test_coro_hybrid_throw_later():

    state = 0

    async def test_task_throw_later():
        nonlocal state
        state = 1
        await asyncio.sleep(0.1)
        raise ValueError("boom")

    fut = run_coro_hybrid(test_task_throw_later())
    assert state == 1
    with pytest.raises(ValueError):
        await fut


@pytest.mark.asyncio
async def test_coro_hybrid_cancel():
    state = 0

    async def test_task_cancel():
        nonlocal state
        state = 1
        await asyncio.sleep(0)
        state = 2

    fut = run_coro_hybrid(test_task_cancel())
    assert state == 1
    fut.cancel()
    await asyncio.sleep(0.1)
    assert state == 1


@pytest.mark.asyncio
async def test_coro_hybrid_self_cancel():
    state = 0

    fut: asyncio.Future[None]

    async def test_task_cancel():
        nonlocal state
        state = 1
        await asyncio.sleep(0)
        fut.cancel()
        await asyncio.sleep(0)
        state = 2

    fut = run_coro_hybrid(test_task_cancel())
    assert state == 1
    await asyncio.sleep(0.1)
    assert state == 1
    with pytest.raises(asyncio.CancelledError):
        await fut
    assert state == 1


@pytest.mark.asyncio
async def test_coro_hybrid_self_cancel2():
    state = 0

    async def test_task_cancel():
        nonlocal state
        state = 1
        await asyncio.sleep(0)
        raise asyncio.CancelledError()

    fut = run_coro_hybrid(test_task_cancel())
    assert state == 1
    await asyncio.sleep(0.1)
    assert state == 1
    with pytest.raises(asyncio.CancelledError):
        await fut
    assert state == 1


@pytest.mark.asyncio
async def test_coro_hybrid_context():
    test = contextvars.ContextVar("test", default=False)

    async def test_ctx():
        assert test.get()
        await asyncio.sleep(0)
        assert test.get()
        await asyncio.sleep(0.1)
        assert test.get()

    def do():
        # Set our context's copy of `test` to True. Since test_ctx() is being launched
        # within our context, it should see test.get() == True, whereas any code outside
        # our context will continue to see test.get() == False.
        test.set(True)
        return run_coro_hybrid(test_ctx())

    inner_ctx = contextvars.copy_context()
    fut = inner_ctx.run(do)
    assert not test.get()
    await fut
    assert not test.get()
