from typing import (
    Callable,
    Awaitable,
    Union,
    Tuple,
    TypeVar,
    Dict,
    Any,
    cast,
)
import functools
import os
import tempfile
import importlib
import inspect
import secrets

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


def wrap_async(
    fn: Union[Callable[[], T], Callable[[], Awaitable[T]]]
) -> Callable[[], Awaitable[T]]:
    """
    Given a synchronous function that returns T, return an async function that wraps the
    original function. If the input function is already async, then return it unchanged.
    """

    if is_async_callable(fn):
        return cast(Callable[[], Awaitable[T]], fn)

    fn = cast(Callable[[], T], fn)

    @functools.wraps(fn)
    async def fn_async() -> T:
        return fn()

    return fn_async


def is_async_callable(obj: object) -> bool:
    """
    Returns True if `obj` is an `async def` function, or if it's an object with a
    `__call__` method which is an `async def` function.
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


def drop_none(x: Dict[str, Any]) -> Dict[str, object]:
    return {k: v for k, v in x.items() if v is not None}


class Callbacks:
    def __init__(self) -> None:
        self._callbacks: dict[str, Tuple[Callable[[], None], bool]] = {}
        self._id: int = 0

    def register(
        self, fn: Callable[[], None], once: bool = False
    ) -> Callable[[], None]:
        self._id += 1
        id = str(self._id)
        self._callbacks[id] = (fn, once)

        def _():
            if id in self._callbacks:
                del self._callbacks[id]

        return _

    def invoke(self) -> None:
        # The list() wrapper is necessary to force collection of all the items before
        # iteration begins. This is necessary because self._callbacks may be mutated
        # by callbacks.
        for id, value in list(self._callbacks.items()):
            fn, once = value
            try:
                fn()
            finally:
                if once:
                    if id in self._callbacks:
                        del self._callbacks[id]

    def count(self) -> int:
        return len(self._callbacks)


class AsyncCallbacks:
    def __init__(self) -> None:
        self._callbacks: dict[str, Tuple[Callable[[], Awaitable[None]], bool]] = {}
        self._id: int = 0

    def register(
        self, fn: Callable[[], Awaitable[None]], once: bool = False
    ) -> Callable[[], None]:
        self._id += 1
        id = str(self._id)
        self._callbacks[id] = (fn, once)

        def _():
            if id in self._callbacks:
                del self._callbacks[id]

        return _

    async def invoke(self) -> None:
        # The list() wrapper is necessary to force collection of all the items before
        # iteration begins. This is necessary because self._callbacks may be mutated
        # by callbacks.
        for id, value in list(self._callbacks.items()):
            fn, once = value
            try:
                await fn()
            finally:
                if once:
                    if id in self._callbacks:
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
        if pkg_file is None:
            raise RuntimeError(f"Could not find package dir for '{package}'")
        return os.path.dirname(pkg_file)
