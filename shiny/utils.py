from typing import Callable, Awaitable, Union, TypeVar, Coroutine, Any
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


# See https://stackoverflow.com/a/59780868/412655 for an excellent explanation
# of how this stuff works.
# For a more in-depth explanation, see
# https://snarky.ca/how-the-heck-does-async-await-work-in-python-3-5/.
def run_coro_sync(coro: Coroutine[Any, Any, T]) -> T:
    """
    Run a coroutine that is in fact synchronous. Given a coroutine (which is
    returned by calling an `async def` function), this function will run the
    coroutine for one iteration. If the coroutine completes, then return the
    value. If it does not complete, then it will throw a `RuntimeError`.

    What it means to be "in fact synchronous": the coroutine must not yield
    control to the event loop. A coroutine may have an `await` expression in it,
    and that may call another function that has an `await`, but the chain will
    only yield control if a `yield` statement bubbles through `await`s all the
    way up. For example, `await asyncio.sleep(0)` will have a `yield` which
    bubbles up to the next level. Note that a `yield` in a generator used the
    regular way (not with `await`) will not bubble up, since it is not awaited
    on.
    """
    if not inspect.iscoroutine(coro):
        raise TypeError("run_coro_sync requires a Coroutine object.")

    try:
        coro.send(None)
    except StopIteration as e:
        return e.value

    raise RuntimeError("async function yielded control; it did not finish in one iteration.")
