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
import sys
import tempfile
import warnings
from pathlib import Path
from types import CoroutineType, ModuleType
from typing import (
    Any,
    AsyncIterable,
    Awaitable,
    Callable,
    Generator,
    Iterable,
    Optional,
    TypeVar,
    cast,
)

from ._typing_extensions import ParamSpec, TypeGuard

CancelledError = asyncio.CancelledError

T = TypeVar("T")


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


# Given a dictionary, return a new dictionary with the keys sorted by length.
def sort_keys_length(x: dict[str, T], descending: bool = False) -> dict[str, T]:
    sorted_keys = sorted(x.keys(), key=len, reverse=descending)
    return {key: x[key] for key in sorted_keys}


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
    if url:
        # Work around issue #1601, some installations of Windows 10 return text/plain
        # as the mime type for .js files
        _, ext = os.path.splitext(os.fspath(str(url)))
        if ext.lower() in [".js", ".mjs", ".cjs"]:
            return "text/javascript"
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


def private_random_id(prefix: str = "", bytes: int = 3) -> str:
    if prefix != "" and not prefix.endswith("_"):
        prefix += "_"

    with private_seed():
        return prefix + rand_hex(bytes)


@contextlib.contextmanager
def private_seed() -> Generator[None, None, None]:
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

R = TypeVar("R")  # Return type
P = ParamSpec("P")


def wrap_async(
    fn: Callable[P, R] | Callable[P, Awaitable[R]],
) -> Callable[P, Awaitable[R]]:
    """
    Given a synchronous function that returns R, return an async function that wraps the
    original function. If the input function is already async, then return it unchanged.
    """

    if is_async_callable(fn):
        return fn

    fn = cast(Callable[P, R], fn)

    @functools.wraps(fn)
    async def fn_async(*args: P.args, **kwargs: P.kwargs) -> R:
        return fn(*args, **kwargs)

    return fn_async


# # TODO: Barret - Future: Q: Keep code?
# class WrapAsync(Generic[P, R]):
#     """
#     Make a function asynchronous.

#     Parameters
#     ----------
#     fn
#         Function to make asynchronous.

#     Returns
#     -------
#     :
#         Asynchronous function (within the `WrapAsync` instance)
#     """

#     def __init__(self, fn: Callable[P, R] | Callable[P, Awaitable[R]]):
#         if isinstance(fn, WrapAsync):
#             fn = cast(WrapAsync[P, R], fn)
#             return fn
#         self._is_async = is_async_callable(fn)
#         self._fn = wrap_async(fn)

#     async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
#         """
#         Call the asynchronous function.
#         """
#         return await self._fn(*args, **kwargs)

#     @property
#     def is_async(self) -> bool:
#         """
#         Was the original function asynchronous?

#         Returns
#         -------
#         :
#             Whether the original function is asynchronous.
#         """
#         return self._is_async

#     @property
#     def fn(self) -> Callable[P, R] | Callable[P, Awaitable[R]]:
#         """
#         Retrieve the original function

#         Returns
#         -------
#         :
#             Original function supplied to the `WrapAsync` constructor.
#         """
#         return self._fn


# This function should generally be used in this code base instead of
# `iscoroutinefunction()`.
def is_async_callable(
    obj: Callable[P, R] | Callable[P, Awaitable[R]],
) -> TypeGuard[Callable[P, Awaitable[R]]]:
    """
    Determine if an object is an async function.

    This is a more general version of `inspect.iscoroutinefunction()`, which only works
    on functions. This function works on any object that has a `__call__` method, such
    as a class instance.

    Returns
    -------
    :
        Returns True if `obj` is an `async def` function, or if it's an object with a
        `__call__` method which is an `async def` function.
    """
    if inspect.iscoroutinefunction(obj):
        return True
    if hasattr(obj, "__call__"):  # noqa: B004
        if inspect.iscoroutinefunction(obj.__call__):  # type: ignore
            return True

    return False


# def not_is_async_callable(
#     obj: Callable[P, T] | Callable[P, Awaitable[T]]
# ) -> TypeGuard[Callable[P, T]]:
#     return not is_async_callable(obj)


# See https://stackoverflow.com/a/59780868/412655 for an excellent explanation
# of how this stuff works.
# For a more in-depth explanation, see
# https://snarky.ca/how-the-heck-does-async-await-work-in-python-3-5/.
def run_coro_sync(coro: Awaitable[R]) -> R:
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

    # Pyright needs a little help here
    coro = cast("CoroutineType[Any, Any, R]", coro)

    try:
        coro.send(None)
    except StopIteration as e:
        return e.value

    raise RuntimeError(
        "async function yielded control; it did not finish in one iteration."
    )


def run_coro_hybrid(coro: Awaitable[R]) -> "asyncio.Future[R]":
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
    result_future: asyncio.Future[R] = asyncio.Future()

    if not inspect.iscoroutine(coro):
        raise TypeError("run_coro_hybrid requires a Coroutine object.")

    # Pyright needs a little help here
    coro = cast("CoroutineType[Any, Any, R]", coro)

    # Inspired by Task.__step method in cpython/Lib/asyncio/tasks.py
    def _step(fut: Optional["asyncio.Future[None]"] = None):
        assert result_future.cancelled() or not result_future.done()

        exc: Optional[BaseException] = None
        if fut:
            assert fut.done()
            try:
                fut.result()
            except BaseException as e:  # noqa: B036
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
        except BaseException as e:  # noqa: B036
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


def wrap_async_iterable(x: Iterable[Any] | AsyncIterable[Any]) -> AsyncIterable[Any]:
    """
    Given any iterable, return an async iterable. The async iterable will yield the
    values of the original iterable, but will also yield control to the event loop
    after each value. This is useful when you want to interleave processing with other
    tasks, or when you want to simulate an async iterable from a regular iterable.
    """

    if isinstance(x, AsyncIterable):
        return x

    if not isinstance(x, Iterable):
        raise TypeError("wrap_async_iterable requires an Iterable object.")

    return MakeIterableAsync(x)


class MakeIterableAsync:
    def __init__(self, iterable: Iterable[Any]):
        self.iterable = iterable

    def __aiter__(self):
        self.iterator = iter(self.iterable)
        return self

    async def __anext__(self):
        try:
            value = next(self.iterator)
            await asyncio.sleep(0)  # Yield control to the event loop
            return value
        except StopIteration:
            raise StopAsyncIteration


# ==============================================================================
# Callback registry
# ==============================================================================
class Callbacks:
    def __init__(self) -> None:
        self._callbacks: dict[int, tuple[Callable[..., None], bool]] = {}
        self._id: int = 0

    def register(
        self, fn: Callable[..., None], once: bool = False
    ) -> Callable[[], None]:
        self._id += 1
        id = self._id
        self._callbacks[id] = (fn, once)

        def _():
            if id in self._callbacks:
                del self._callbacks[id]

        return _

    def invoke(self, *args: Any, **kwargs: Any) -> None:
        # The list() wrapper is necessary to force collection of all the items before
        # iteration begins. This is necessary because self._callbacks may be mutated
        # by callbacks.
        for id, value in list(self._callbacks.items()):
            fn, once = value
            try:
                fn(*args, **kwargs)
            finally:
                if once:
                    if id in self._callbacks:
                        del self._callbacks[id]

    def count(self) -> int:
        return len(self._callbacks)


CancelCallback = Callable[[], None]


class AsyncCallbacks:
    def __init__(self) -> None:
        self._callbacks: dict[int, tuple[Callable[..., Awaitable[None]], bool]] = {}
        self._id: int = 0

    def register(
        self, fn: Callable[..., Awaitable[None]], once: bool = False
    ) -> CancelCallback:
        self._id += 1
        id = self._id
        self._callbacks[id] = (fn, once)

        def cancel_callback():
            if id in self._callbacks:
                del self._callbacks[id]

        return cancel_callback

    async def invoke(self, *args: Any, **kwargs: Any) -> None:
        # The list() wrapper is necessary to force collection of all the items before
        # iteration begins. This is necessary because self._callbacks may be mutated
        # by callbacks.
        for id, value in list(self._callbacks.items()):
            fn, once = value
            try:
                await fn(*args, **kwargs)
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


class ModuleImportWarning(ImportWarning):
    pass


warnings.simplefilter("always", ModuleImportWarning)


def import_module_from_path(module_name: str, path: Path):
    import importlib.util

    if not path.is_absolute():
        raise ValueError("Path must be absolute")

    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not import module {module_name} from path: {path}")

    module = importlib.util.module_from_spec(spec)

    prev_module: ModuleType | None = None

    if module_name in sys.modules:
        prev_module = sys.modules[module_name]
        warnings.warn(
            f"A module named {module_name} is already loaded, but is being loaded again.",
            ModuleImportWarning,
            stacklevel=1,
        )

    sys.modules[module_name] = module

    try:
        spec.loader.exec_module(module)
    except Exception:
        if prev_module is None:
            del sys.modules[module_name]
        else:
            sys.modules[module_name] = prev_module
        raise
    return module
