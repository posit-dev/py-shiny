from typing import Callable, Awaitable, Union, TypeVar, Tuple, Coroutine, Any
import inspect
import typing

T = TypeVar("T")

def wrap_async(fn: Callable[[], Union[T, Awaitable[T]]]) -> Callable[[], Awaitable[T]]:
    """
    Wrap a synchronous function that returns T, and return an async function
    that wraps the original function.
    """
    fn_sync = typing.cast(Callable[[], T], fn)
    async def fn_async() -> T:
        return fn_sync()

    return fn_async


def run_coro_sync(coro: Coroutine[Any, Any, T]) -> T:
    """
    Run a coroutine that is in fact synchronous. Given a coroutine (which is
    returned by calling an `async def` function), this function will run the
    coroutine for one iteration. If the coroutine completes, then return the
    value. If it does not complete, then it will throw a `RuntimeError`.

    What it means to be "in fact synchronous": the coroutine must not give up
    control to the event loop. A coroutine may have an `await` expression in it,
    and that may call another function that has an `await`, but not all `await`s
    actually give up control. Things that do actually give up control are, for
    example, `asyncio.sleep()`, and functions that wait for I/O. Similarly, a
    `yield` statement in an awaited function (which must be decorated with
    `@types.coroutine` to be awaitable) also will give up control to the event
    loop. Note that a `yield` in a (non-awaited) generator function will not
    give up control.
    """
    try:
        coro.send(None)
    except StopIteration as e:
        return e.value

    raise RuntimeError("async function yielded control; it did not finish in one iteration.")
