from __future__ import annotations

import asyncio
import contextlib
import functools
import importlib
import inspect
import mimetypes
import os
import random
import secrets
import socketserver
import tempfile
from typing import Any, Awaitable, Callable, Optional, TypeVar, cast

from ._typing_extensions import ParamSpec, TypeGuard

CancelledError = asyncio.CancelledError


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


def drop_none(x: dict[str, Any]) -> dict[str, object]:
    return {k: v for k, v in x.items() if v is not None}


# Intended for use with json.load()'s object_hook parameter.
# Note also that object_hook is only called on dicts, not on lists, so this
# won't work for converting "top-level" lists to tuples
def lists_to_tuples(x: object) -> object:
    if isinstance(x, dict):
        x = cast("dict[str, object]", x)
        return {k: lists_to_tuples(v) for k, v in x.items()}
    elif isinstance(x, list):
        x = cast("list[object]", x)
        return tuple(lists_to_tuples(y) for y in x)
    else:
        # TODO: are there other mutable iterators that we want to make read only?
        return x


def guess_mime_type(
    url: "str | os.PathLike[str]",
    default: str = "application/octet-stream",
    strict: bool = True,
) -> str:
    """
    Guess the MIME type of a file. This is a wrapper for mimetypes.guess_type, but it
    only returns the type (and not encoding), and it allows a default value.
    """
    # Note that in the parameters above, "os.PathLike[str]" is in quotes to avoid
    # "TypeError: 'ABCMeta' object is not subscriptable", in Python<=3.8.
    return mimetypes.guess_type(url, strict)[0] or default


def random_port(
    min: int = 1024, max: int = 49151, host: str = "127.0.0.1", n: int = 20
) -> int:
    """Find an open TCP port

    Finds a random available TCP port for listening on, within a specified range
    of ports. The default range of ports to check is 1024 to 49151, which is the
    set of TCP User Ports. This function automatically excludes some ports which
    are considered unsafe by web browsers.

    Parameters
    ----------
    min
        Minimum port number.
    max
        Maximum port number, inclusive.
    host
        Before returning a port number, ensure that we can successfully bind it on this
        host.
    n
        Number of times to attempt before giving up.
    """

    # From https://chromium.googlesource.com/chromium/src.git/+/refs/heads/master/net/base/port_util.cc
    unsafe_ports = [
        1,
        7,
        9,
        11,
        13,
        15,
        17,
        19,
        20,
        21,
        22,
        23,
        25,
        37,
        42,
        43,
        53,
        69,
        77,
        79,
        87,
        95,
        101,
        102,
        103,
        104,
        109,
        110,
        111,
        113,
        115,
        117,
        119,
        123,
        135,
        137,
        139,
        143,
        161,
        179,
        389,
        427,
        465,
        512,
        513,
        514,
        515,
        526,
        530,
        531,
        532,
        540,
        548,
        554,
        556,
        563,
        587,
        601,
        636,
        989,
        990,
        993,
        995,
        1719,
        1720,
        1723,
        2049,
        3659,
        4045,
        5060,
        5061,
        6000,
        6566,
        6665,
        6666,
        6667,
        6668,
        6669,
        6697,
        10080,
    ]

    unusable = set([x for x in unsafe_ports if x >= min and x <= max])
    while n > 0:
        if (max - min + 1) <= len(unusable):
            break
        port = random.randint(min, max)
        if port in unusable:
            continue
        try:
            # See if we can successfully bind
            with socketserver.TCPServer(
                (host, port), socketserver.BaseRequestHandler, bind_and_activate=False
            ) as s:
                s.server_bind()
                return port
        except Exception:
            n -= 1
            continue

    raise RuntimeError("Failed to find a usable random port")


# ==============================================================================
# Private random stream
# ==============================================================================
def private_random_int(min: int, max: int) -> str:
    with private_seed():
        return str(random.randint(min, max))


@contextlib.contextmanager
def private_seed():
    state = random.getstate()
    global own_random_state
    try:
        random.setstate(own_random_state)
        yield
    finally:
        own_random_state = random.getstate()
        random.setstate(state)


# Initialize random state for shiny's own private stream of randomness.
current_random_state = random.getstate()
random.seed(secrets.randbits(128))
own_random_state = random.getstate()
random.setstate(current_random_state)

# ==============================================================================
# Async-related functions
# ==============================================================================

T = TypeVar("T")
P = ParamSpec("P")


def wrap_async(
    fn: Callable[P, T] | Callable[P, Awaitable[T]]
) -> Callable[P, Awaitable[T]]:
    """
    Given a synchronous function that returns T, return an async function that wraps the
    original function. If the input function is already async, then return it unchanged.
    """

    if is_async_callable(fn):
        return fn

    fn = cast(Callable[P, T], fn)

    @functools.wraps(fn)
    async def fn_async(*args: P.args, **kwargs: P.kwargs) -> T:
        return fn(*args, **kwargs)

    return fn_async


def is_async_callable(
    obj: Callable[P, T] | Callable[P, Awaitable[T]]
) -> TypeGuard[Callable[P, Awaitable[T]]]:
    """
    Returns True if `obj` is an `async def` function, or if it's an object with a
    `__call__` method which is an `async def` function. This function should generally
    be used in this code base instead of iscoroutinefunction().
    """
    if inspect.iscoroutinefunction(obj):
        return True
    if hasattr(obj, "__call__"):  # noqa: B004
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
    control to the event loop. A coroutine may have an `await` expression in it, and that may call another function that has an `await`, but the chain will
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


def run_coro_hybrid(coro: Awaitable[T]) -> "asyncio.Future[T]":
    """
    Synchronously runs the given coro up to its first yield, then runs the rest of the
    coro by scheduling it on the current event loop, as per normal. You can think of
    this as either a run_coro_sync() that keeps running in the future, or, as an
    asyncio.create_task() that starts executing immediately instead of via call_soon.

    The status/result/exception can be access through the returned future. Even if an
    error happens synchronously, run_coro_hybrid() will not throw, but rather the error
    will be reported through the future object.

    **PLEASE ONLY USE THIS IF IT'S ABSOLUTELY NECESSARY.** Relative to the official
    asyncio Task implementation, this is a hastily assembled hack job; who knows what
    unknown unknowns lurk here.
    """
    result_future: asyncio.Future[T] = asyncio.Future()

    if not inspect.iscoroutine(coro):
        raise TypeError("run_coro_hybrid requires a Coroutine object.")

    # Inspired by Task.__step method in cpython/Lib/asyncio/tasks.py
    def _step(fut: Optional["asyncio.Future[None]"] = None):
        assert result_future.cancelled() or not result_future.done()

        exc: Optional[BaseException] = None
        if fut:
            assert fut.done()
            try:
                fut.result()
            except BaseException as e:
                exc = e

        if result_future.cancelled():
            # This may cause fut.result()'s exception to be ignored. That's intentional.
            # The cancellation takes precedent, but if we don't call fut.result() first
            # to retrieve its error, Python will warn.
            exc = CancelledError()

        res: Optional[asyncio.Future[None]] = None
        try:
            if exc is None:
                res = coro.send(None)
            else:
                # Is it worth throwing here? Or just logging?
                res = coro.throw(exc)
        except StopIteration as e:
            # Done
            result_future.set_result(e.value)
            return
        except CancelledError:
            result_future.cancel()
            return
        except (KeyboardInterrupt, SystemExit) as e:
            result_future.set_exception(e)
            raise
        except BaseException as e:
            result_future.set_exception(e)
        else:
            # If we get here, the coro didn't finish. Schedule it for completion.
            if isinstance(res, asyncio.Future):
                res.add_done_callback(_step)
            elif res is None:
                # This case happens with asyncio.sleep(0)
                asyncio.get_running_loop().call_soon(_step)
            else:
                raise RuntimeError(f"coroutine yielded unknown value: {res!r}")

    _step()

    return result_future


# ==============================================================================
# Callback registry
# ==============================================================================
class Callbacks:
    def __init__(self) -> None:
        self._callbacks: dict[int, tuple[Callable[[], None], bool]] = {}
        self._id: int = 0

    def register(
        self, fn: Callable[[], None], once: bool = False
    ) -> Callable[[], None]:
        self._id += 1
        id = self._id
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
        self._callbacks: dict[int, tuple[Callable[[], Awaitable[None]], bool]] = {}
        self._id: int = 0

    def register(
        self, fn: Callable[[], Awaitable[None]], once: bool = False
    ) -> Callable[[], None]:
        self._id += 1
        id = self._id
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
