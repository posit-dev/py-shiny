import asyncio
from typing import (
    Callable,
    Awaitable,
    Optional,
    Tuple,
    TypeVar,
    Dict,
    Any,
)
import os
import tempfile
import importlib
import inspect
import secrets
import typing

# ==============================================================================
# Misc utility functions
# ==============================================================================
def rand_hex(bytes: int) -> str:
    """
    Creates a random hexadecimal string of size `bytes`. The length in
    characters will be bytes*2.
    """
    format_str = "{{:0{}x}}".format(bytes * 2)
    return format_str.format(secrets.randbits(bytes * 8))


# ==============================================================================
# Async-related functions
# ==============================================================================

T = TypeVar("T")


def wrap_async(fn: Callable[[], T]) -> Callable[[], Awaitable[T]]:
    """
    Wrap a synchronous function that returns T, and return an async function
    that wraps the original function.
    """

    async def fn_async() -> T:
        return fn()

    return fn_async


def is_async_callable(obj: object) -> bool:
    """
    Returns True if `obj` is an `async def` function, or if it's an object with
    a `__call__` method which is an `async def` function.
    """
    if inspect.iscoroutinefunction(obj):
        return True
    if hasattr(obj, "__call__"):
        if inspect.iscoroutinefunction(obj.__call__):  # type: ignore
            return True

    return False


# See https://stackoverflow.com/a/59780868/412655 for an excellent explanation
# of how this stuff works.
# For a more in-depth explanation, see
# https://snarky.ca/how-the-heck-does-async-await-work-in-python-3-5/.
def run_coro_sync(coro: Awaitable[T]) -> T:
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

    raise RuntimeError(
        "async function yielded control; it did not finish in one iteration."
    )

class RunLoop:
    """Used to serialize sub-tasks, using a dedicated Task

    From other Tasks, you can use execute() to run logic on this Task and get the result
    (or error) back on the originating Task. Or, use schedule() to fire-and-forget,
    which might also be faster.
    """
    def __init__(self):
        self._task: Optional[asyncio.Task[None]] = None
        self._queue: asyncio.Queue[Awaitable[None]] = asyncio.Queue()

    async def _run(self) -> None:
        while True:
            coro = await self._queue.get()
            await coro

    def start(self):
        if self._task is None:
            self._task = asyncio.create_task(self._run())

    def stop(self):
        if self._task is not None:
            self._task.cancel()
            self._task = None

    async def execute(self, coro: Awaitable[T]) -> T:
        if asyncio.current_task() is self._task:
            raise RuntimeError("Cannot call RunLoop.execute() from its own captive Task")

        success = False
        result: Optional[T] = None
        error: Optional[BaseException] = None

        # I'm worried these events might be too expensive--can we use just one per Task?
        event = asyncio.Event()

        async def wrapper():
            nonlocal success, result, error
            try:
                result = await coro
                success = True
            except BaseException as err:
                error = err
                success = False
            finally:
                event.set()

        await self._queue.put(wrapper())
        await event.wait()
        if success:
            return typing.cast(T, result)
        else:
            raise typing.cast(BaseException, error)

    async def schedule(self, coro: Awaitable[None]) -> None:
        await self._queue.put(coro)


def drop_none(x: Dict[str, Any]) -> Dict[str, object]:
    return {k: v for k, v in x.items() if v is not None}


class Callbacks:
    def __init__(self) -> None:
        self._callbacks: Dict[str, Tuple[Callable[[], None], bool]] = {}
        self._id: int = 0

    def register(
        self, fn: Callable[[], None], once: bool = False
    ) -> Callable[[], None]:
        self._id += 1
        id = str(self._id)
        self._callbacks[id] = (fn, once)

        def _():
            del self._callbacks[id]

        return _

    def invoke(self) -> None:
        ids = list(self._callbacks.keys())
        for id in ids:
            fn, once = self._callbacks[id]
            try:
                fn()
            finally:
                if once:
                    del self._callbacks[id]

    def count(self) -> int:
        return len(self._callbacks)


# ==============================================================================
# System-related functions
# ==============================================================================

# Return directory that a package lives in.
def package_dir(package: str) -> str:
    with tempfile.TemporaryDirectory():
        pkg_file = importlib.import_module(".", package=package).__file__
        return os.path.dirname(pkg_file)
