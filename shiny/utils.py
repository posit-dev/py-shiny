from typing import Callable, Awaitable, Union, TypeVar, Tuple, Coroutine, Any
import inspect
import typing

T = TypeVar("T")

def wrap_async(fn: Callable[[], Union[T, Awaitable[T]]]) -> Tuple[Callable[[], Awaitable[T]], bool]:
    """
    Wrap a synchronous function that returns T, and return an async function
    that wraps the original function. If input is an async function, simply
    return the function. This also returns a boolean indicating whether the
    input function was async.
    """
    if inspect.iscoroutinefunction(fn):
        return typing.cast(Callable[[], Awaitable[T]], fn), True
    else:
        fn_sync = typing.cast(Callable[[], T], fn)
        async def fn_async() -> T:
            return fn_sync()

        return fn_async, False


def run_coro(coro: Coroutine[Any, Any, T]) -> T:
    while True:
        try:
            coro.send(None)
        except StopIteration as e:
            return e.value
