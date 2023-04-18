from __future__ import annotations

import functools
import os
from operator import eq
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Optional, TypeVar, cast

from .. import _utils, reactive
from .._docstring import add_example
from ..types import MISSING, MISSING_TYPE

if TYPE_CHECKING:
    from ..session import Session

__all__ = ("poll", "file_reader")

T = TypeVar("T")


@add_example()
def poll(
    poll_func: Callable[[], Any] | Callable[[], Awaitable[Any]],
    interval_secs: float = 1,
    *,
    equals: Callable[[Any, Any], bool] = eq,
    priority: int = 0,
    session: MISSING_TYPE | Session | None = MISSING,
) -> Callable[[Callable[[], T]], Callable[[], T]]:
    """
    Create a reactive polling object.

    Polling is a technique that approximates "real-time" or streaming updates, using a
    data source that does not actually have push notifications but does have a quick way
    to repeatedly check for changes on demand.

    A reactive polling object is constructed using two functions: a polling function,
    which is a fast-running, inexpensive function that is used to determine whether some
    data source has changed (such as the timestamp of a file, or a `SELECT MAX(updated)
    FROM table` query); and a slower-running reading function that actually loads and
    returns the data that is desired. The `poll()` function is intended to be used as a
    decorator: the poll function is passed as the `poll_func` arg to `@poll()`, while
    the data reading function is the target of the decorator.

    Reactive consumers can invoke the resulting polling object to get the current data,
    and will automatically invalidate when the polling function detects a change.
    Polling objects also cache the results of the read function; for this reason, apps
    where all sessions depend on the same data source may want to declare the polling
    object at the top level of app.py (outside of the server function).

    Both `poll_func` and the decorated (data reading) function can read reactive values
    and ~shiny.reactive.Calc objects. Any invalidations triggered by reactive
    dependencies will apply to the reactive polling object immediately (not waiting for
    the `interval_secs` delay to expire).

    Parameters
    ----------
    poll_func
        A function to be called frequently to determine whether a data source has
        changed. The return value should be something that can be compared inexpensively
        using `==`. Both regular functions and coroutine functions are allowed.

        Note that the `poll_func` should NOT return a bool that indicates whether the
        data source has changed. Rather, each `poll_func` return value will be checked
        for equality with its preceding `poll_func` return value (using `==` semantics
        by default), and if it differs, the data source will be considered changed.
    interval_secs
        The number of seconds to wait after each `poll_func` invocation before polling
        again. Note: depending on what other tasks are executing, the actual wait time
        may far exceed this value.
    equals
        The function that will be used to compare each `poll_func` return value with its
        immediate predecessor.
    priority
        Reactive polling is implemented using an ~shiny.reactive.Effect to call
        `poll_func` on a timer; use the `priority` argument to control the order of this
        Effect's execution versus other Effects in your app. See ~shiny.reactive.Effect
        for more details.
    session
        A :class:`~shiny.Session` instance. If not provided, it is inferred via
        :func:`~shiny.session.get_current_session`. If there is no current session (i.e.
        `poll` is being created outside of the server function), the lifetime of this
        reactive poll object will not be tied to any specific session.

    Returns
    -------
    :
        A decorator that should be applied to a no-argument function that (expensively)
    reads whatever data is desired. (This function may be a regular function or a
    coroutine function.) The result of the decorator is a reactive ~shiny.reactive.Calc
    that always returns up-to-date data, and invalidates callers when changes are
    detected via polling.

    See Also
    --------
    ~shiny.reactive.file_reader
    """

    with reactive.isolate():
        last_value: reactive.Value[Any] = reactive.Value(poll_func())
        last_error: reactive.Value[Optional[Exception]] = reactive.Value(None)

    @reactive.Effect(priority=priority, session=session)
    async def _():
        try:
            if _utils.is_async_callable(poll_func):
                new = await poll_func()
            else:
                new = poll_func()

            with reactive.isolate():
                old = last_value.get()

            try:
                is_equal = equals(old, new)
            except Exception as e:
                # For example, pandas DataFrame throws if you try to compare it to a
                # non-comparable object
                raise TypeError(
                    "The reactive.poll polling function returned an object that "
                    "couldn't be compared with a previously returned object. Try "
                    "modifying your polling function to return a simpler type, like a "
                    "str, float, list, or dict."
                ) from e
            if not isinstance(is_equal, bool):
                # Comparison succeeded, but we don't understand the result
                if equals is eq:
                    # We used == but it didn't work
                    raise TypeError(
                        "The reactive.poll polling function returned an object "
                        "that doesn't implement a simple == operator. Try "
                        "modifying your polling function to return a simpler type, "
                        "like a str, float, list, or dict."
                    )
                else:
                    # The caller passed in a custom function
                    raise TypeError(
                        "The reactive.poll `equals` function returned a non-bool "
                        "value"
                    )

            # If we got here, the comparison succeeded. Need to make sure the error is
            # cleared, but don't unnecessarily call last_error.set(); at the time of
            # this writing, we haven't made a final decision on whether reactive.Value
            # will ignore sets if the new value is identical to the existing one.
            with reactive.isolate():
                if last_error.get() is not None:
                    last_error.set(None)

            if not is_equal:
                last_value.set(new)
        except Exception as e:
            # Either the polling function threw an error, or we failed to compare its
            # result with a previous result. Either way, we failed; save the error so
            # that it can be exposed to whoever's trying to use the poll object.
            last_error.set(e)
        finally:
            reactive.invalidate_later(interval_secs)

    def wrapper(fn: Callable[[], T]) -> Callable[[], T]:
        if _utils.is_async_callable(fn):

            @reactive.Calc(session=session)
            @functools.wraps(fn)
            async def result_async() -> T:
                # If an error occurred, raise it
                err = last_error.get()
                if err is not None:
                    raise err

                # Take dependency on polling result
                last_value.get()

                # Note that we also depend on the main function
                return await fn()

            # In this code path, the cast is necessary because result_async() has an
            # incorrect signature due to limitations in Python's type hints. In this
            # path, T is already an Awaitable. The signature should really be `async def
            # result_async() -> Awaited[T]`, but there's no Awaited type in Python. So
            # instead we'll just cast() it.
            return cast(Callable[[], T], result_async)

        else:

            @reactive.Calc(session=session)
            @functools.wraps(fn)
            def result_sync() -> T:
                # If an error occurred, raise it
                err = last_error.get()
                if err is not None:
                    raise err

                # Take dependency on polling result
                last_value.get()

                # Note that we also depend on the main function
                return fn()

            return result_sync

    return wrapper


@add_example()
def file_reader(
    filepath: str
    | os.PathLike[str]
    | Callable[[], str]
    | Callable[[], os.PathLike[str]],
    interval_secs: float = 1,
    *,
    priority: int = 1,
    session: MISSING_TYPE | Session | None = MISSING,
) -> Callable[[Callable[[], T]], Callable[[], T]]:
    """
    Create a reactive file reader.

    This is a decorator, meant to be applied to a no-argument function that reads data
    from a file on disk. Whenever the file changes (or to be precise, the file size or
    last modified time changes), past readers of the data are reactively invalidated.
    This makes it incredibly easy to write apps that automatically update all of their
    outputs as soon as files on disk change.

    Note that `file_reader` works only on single files, not directories of files.

    Both the `filepath` function and the decorated (file reading) function can read
    reactive values and ~shiny.reactive.Calc objects. Any invalidations triggered by
    reactive dependencies will apply to the reactive file reader object immediately (not
    waiting for the `interval_secs` delay to expire).

    Parameters
    ----------
    filepath
        Either a string indicating the file path to be monitored, or, a no-argument
        function that returns such a string. The latter is useful if the file to be
        monitored depends on some user input, the current date/time, etc.

        The file path provided MUST exist, otherwise Shiny will treat it as an unhandled
        error and close the session.

        If a function is used, make sure it is high performance (or is cached, i.e. use
        a ~shiny.reactive.Calc), as it will be called very frequently.
    interval_secs
        The number of seconds to wait after each time the file metadata is checked.
        Note: depending on what other tasks are executing, the actual wait time may far
        exceed this value.
    priority
        Reactive polling is implemented using an ~shiny.reactive.Effect to call
        `poll_func` on a timer; use the `priority` argument to control the order of this
        Effect's execution versus other Effects in your app. See ~shiny.reactive.Effect
        for more details.
    session
        A :class:`~shiny.Session` instance. If not provided, it is inferred via
        :func:`~shiny.session.get_current_session`. If there is no current session (i.e.
        `poll` is being created outside of the server function), the lifetime of this
        reactive poll object will not be tied to any specific session.

    Returns
    -------
    :
        A decorator that should be applied to a no-argument function that (expensively)
    reads whatever data is desired. (This function may be a regular function or a
    coroutine function.) The result of the decorator is a reactive ~shiny.reactive.Calc
    that always returns up-to-date data, and invalidates callers when changes are
    detected via polling.

    See Also
    --------
    ~shiny.reactive.poll
    """

    if isinstance(filepath, str):
        # Normalize filepath so it's always a function

        filepath_value = filepath

        def filepath_func_str() -> str:
            return filepath_value

        filepath = filepath_func_str
    elif isinstance(filepath, os.PathLike):
        filepath_value = filepath

        def filepath_func_pathlike() -> os.PathLike[str]:
            return filepath_value

        filepath = filepath_func_pathlike

    def check_timestamp():
        path = filepath()
        return (path, os.path.getmtime(path), os.path.getsize(path))

    def wrapper(fn: Callable[[], T]) -> Callable[[], T]:
        if _utils.is_async_callable(fn):

            @poll(
                check_timestamp,
                interval_secs=interval_secs,
                priority=priority,
                session=session,
            )
            @functools.wraps(fn)
            async def reader_async():
                return await fn()

            # See poll() for explanation of why this cast is needed.
            return cast(Callable[[], T], reader_async)
        else:

            @poll(
                check_timestamp,
                interval_secs=interval_secs,
                priority=priority,
                session=session,
            )
            @functools.wraps(fn)
            def reader():
                return fn()

            return reader

    return wrapper
