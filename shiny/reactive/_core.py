"""Low-level reactive components."""

from __future__ import annotations

__all__ = (
    "isolate",
    "invalidate_later",
    "flush",
    "lock",
    "on_flushed",
    "get_current_context",
)

import asyncio
import contextlib
import time
import traceback
import typing
import warnings
from contextvars import ContextVar
from typing import TYPE_CHECKING, Awaitable, Callable, Generator, Optional, TypeVar

from .. import _utils
from .._datastructures import PriorityQueueFIFO
from .._docstring import add_example, no_example
from ..types import MISSING, MISSING_TYPE

if TYPE_CHECKING:
    from ..session import Session

T = TypeVar("T")


class ReactiveWarning(RuntimeWarning):
    pass


# By default warnings are shown once; we want to always show them.
warnings.simplefilter("always", ReactiveWarning)


class Context:
    """A reactive context"""

    def __init__(self) -> None:
        self.id: int = _reactive_environment.next_id()
        self._invalidated: bool = False
        self._invalidate_callbacks: list[Callable[[], None]] = []
        self._flush_callbacks: list[Callable[[], Awaitable[None]]] = []

    def __call__(self) -> typing.ContextManager[None]:
        return _reactive_environment.use_context(self)

    def invalidate(self) -> None:
        """Invalidate this context. It will immediately call the callbacks
        that have been registered with onInvalidate()."""

        if self._invalidated:
            return

        self._invalidated = True

        for cb in self._invalidate_callbacks:
            cb()

        self._invalidate_callbacks.clear()

    def on_invalidate(self, func: Callable[[], None]) -> None:
        """Register a function to be called when this context is invalidated"""
        if self._invalidated:
            func()
        else:
            self._invalidate_callbacks.append(func)

    def add_pending_flush(self, priority: int) -> None:
        """Tell the reactive environment that this context should be flushed the
        next time flushReact() called."""
        _reactive_environment.add_pending_flush(self, priority)

    def on_flush(self, func: Callable[[], Awaitable[None]]) -> None:
        """Register a function to be called when this context is flushed."""
        self._flush_callbacks.append(func)

    async def execute_flush_callbacks(self) -> None:
        """Execute all flush callbacks"""
        for cb in self._flush_callbacks:
            await cb()

        self._flush_callbacks.clear()


class Dependents:
    def __init__(self) -> None:
        self._dependents: dict[int, Context] = {}

    def register(self) -> None:
        ctx: Context = get_current_context()

        if ctx.id in self._dependents:
            # This context is already registered; no need to register it.
            return

        self._dependents[ctx.id] = ctx

        def on_invalidate_cb() -> None:
            if ctx.id in self._dependents:
                del self._dependents[ctx.id]

        ctx.on_invalidate(on_invalidate_cb)

    def invalidate(self) -> None:
        # TODO: Check sort order
        # Invalidate all dependents. This gets all the dependents as list, then iterates
        # over the list. It's done this way instead of iterating over keys because it's
        # possible that a dependent is removed from the dict while iterating over it.
        # https://github.com/posit-dev/py-shiny/issues/26
        ids = sorted(self._dependents.keys())
        for dep_ctx in [self._dependents[id] for id in ids]:
            dep_ctx.invalidate()


class ReactiveEnvironment:
    """The reactive environment"""

    def __init__(self) -> None:
        self._current_context: ContextVar[Optional[Context]] = ContextVar(
            "current_context", default=None
        )
        self._next_id: int = 0
        self._pending_flush_queue: PriorityQueueFIFO[Context] = PriorityQueueFIFO()
        self._flushed_callbacks = _utils.AsyncCallbacks()

    def next_id(self) -> int:
        """Return the next available id"""
        id = self._next_id
        self._next_id += 1
        return id

    @contextlib.contextmanager
    def use_context(self, ctx: Context) -> typing.Generator[None, None, None]:
        old = self._current_context.set(ctx)
        try:
            yield
        finally:
            self._current_context.reset(old)

    def current_context(self) -> Context:
        """Return the current `Context` object"""
        ctx = self._current_context.get()
        if ctx is None:
            raise RuntimeError("No current reactive context")
        return ctx

    def on_flushed(
        self, func: Callable[[], Awaitable[None]], once: bool = False
    ) -> Callable[[], None]:
        return self._flushed_callbacks.register(func, once=once)

    async def flush(self) -> None:
        """Flush all pending operations"""
        await self._flush_concurrent()
        await self._flushed_callbacks.invoke()

    async def _flush_concurrent(self) -> None:
        """Run all pending contexts concurrently using asyncio.gather().

        Uses an outer loop to handle effects that are newly invalidated during the
        current flush batch. Each iteration gathers all currently-pending contexts
        and runs them concurrently; if any of those effects invalidate other effects,
        those will be picked up in the next iteration.
        """
        while not self._pending_flush_queue.empty():
            tasks: list[typing.Awaitable[None]] = []
            while not self._pending_flush_queue.empty():
                ctx = self._pending_flush_queue.get()
                tasks.append(ctx.execute_flush_callbacks())

            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for result in results:
                    if isinstance(result, BaseException):
                        # Log the exception but don't re-raise; effects handle
                        # their own errors internally
                        traceback.print_exception(
                            type(result), result, result.__traceback__
                        )

    async def _flush_sequential(self) -> None:
        # Sequential flush: instead of storing the tasks in a list and calling gather()
        # on them later, just run each effect in sequence.
        while not self._pending_flush_queue.empty():
            ctx = self._pending_flush_queue.get()
            await ctx.execute_flush_callbacks()

    def add_pending_flush(self, ctx: Context, priority: int) -> None:
        self._pending_flush_queue.put(priority, ctx)

    @contextlib.contextmanager
    def isolate(self) -> Generator[None, None, None]:
        token = self._current_context.set(Context())
        try:
            yield
        finally:
            self._current_context.reset(token)


_reactive_environment = ReactiveEnvironment()


@add_example()
@contextlib.contextmanager
def isolate() -> Generator[None, None, None]:
    """
    Create a non-reactive scope within a reactive scope.

    Ordinarily, the simple act of reading a reactive value causes a relationship to be
    established between the caller and the reactive value, where a change to the
    reactive value will cause the caller to re-execute. (The same applies for the act of
    getting a reactive calculation's value.) `with isolate()` lets you read a reactive
    value or calculation without establishing this relationship.

    ``with isolate()`` can also be useful for calling reactive calculations at the
    console, which can be useful for debugging. To do so, wrap the calls to the reactive
    calculation with ``with isolate()``.

    Returns
    -------
    :
        A context manager that executes the given expression in a scope where reactive
        values can be read, but do not cause the reactive scope of the caller to be
        re-evaluated when they change.

    See Also
    --------
    * :func:`~shiny.reactive.event`
    """
    with _reactive_environment.isolate():
        yield


def get_current_context() -> Context:
    """
    Get the current reactive context.

    Returns
    -------
    :
        A `~shiny.reactive.Context` class.

    Raises
    ------
    RuntimeError
        If called outside of a reactive context.
    """
    return _reactive_environment.current_context()


@no_example()
async def flush() -> None:
    """
    Run any pending invalidations (i.e., flush the reactive environment).

    Warning
    -------
    You shouldn't ever need to call this function inside of a Shiny app. It's only
    useful for testing and running reactive code interactively in the console.
    """
    await _reactive_environment.flush()


@no_example()
def on_flushed(
    func: Callable[[], Awaitable[None]], once: bool = False
) -> Callable[[], None]:
    """
    Register a function to be called when the reactive environment is flushed.

    Parameters
    ----------
    func
        The function to be called when the reactive environment is flushed
    once
        Should the function be run once, and then cleared, or should it
        re-run each time the event occurs.

    Returns
    -------
    :
        A function that can be used to unregister the callback.

    See Also
    --------
    * :func:`~shiny.reactive.flush`
    """

    return _reactive_environment.on_flushed(func, once)


@no_example()
def lock() -> asyncio.Lock:
    """
    .. deprecated::
        The global reactive lock has been removed. Reactive locking is now handled
        per-session. This function returns a no-op lock for backward compatibility.
    """
    warnings.warn(
        "reactive.lock() is deprecated. The reactive lock is now per-session. "
        "This returns a no-op lock for backward compatibility.",
        DeprecationWarning,
        stacklevel=2,
    )
    return _noop_lock


class _NoOpLock:
    """A lock that does nothing, for backward compatibility with reactive.lock()."""

    async def __aenter__(self) -> None:
        pass

    async def __aexit__(self, *args: object) -> None:
        pass

    async def acquire(self) -> bool:
        return True

    def release(self) -> None:
        pass

    def locked(self) -> bool:
        return False


# Single instance used for backward compatibility
_noop_lock: asyncio.Lock = _NoOpLock()  # type: ignore[assignment]


@add_example()
def invalidate_later(
    delay: float, *, session: "MISSING_TYPE | Session | None" = MISSING
) -> None:
    """
    Scheduled Invalidation

    When called from within a reactive context, :func:`~shiny.reactive.invalidate_later`
    schedules the reactive context to be invalidated in the given number of seconds.

    Parameters
    ----------
    delay
        The number of seconds to wait before invalidating.

    Note
    ----
    When called within a reactive function (i.e., :func:`~shiny.reactive.effect`,
    :func:`~shiny.reactive.calc`, :class:`shiny.render.ui`, etc.), that reactive context
    is invalidated (and re-executes) after the interval has passed. The re-execution
    will reset the invalidation flag, so in a typical use case, the object will keep
    re-executing and waiting for the specified interval. It's possible to stop this
    cycle by adding conditional logic that prevents the ``invalidate_later`` from being
    run.
    """

    if isinstance(session, MISSING_TYPE):
        from ..session import get_current_session

        # If no session is provided, autodetect the current session (this
        # could be None if outside of a session).
        session = get_current_session()

    ctx = get_current_context()
    # Pass an absolute time to our subtask, rather than passing the delay directly, in
    # case the subtask doesn't get a chance to start sleeping until a significant amount
    # of time has passed.
    deadline = time.monotonic() + delay

    cancellable = True
    # unsub is used to unsubscribe from session.on_ended when time expires. We don't
    # want a ton of event handler registrations sitting there uselessly, keeping object
    # graphs from being gc'd.
    unsub: Optional[Callable[[], None]] = None

    async def _task(ctx: Context, deadline: float) -> None:
        nonlocal cancellable
        try:
            delay = deadline - time.monotonic()
            try:
                await asyncio.sleep(delay)
            except asyncio.CancelledError:
                # This happens when cancel_task is called due to the session ending, or
                # the context being invalidated due to some other reason. There's no
                # reason for us to keep waiting at that point, as ctx.invalidate() can
                # only be a no-op.
                return

            # Use the session's per-session lock if available, otherwise proceed
            # without a lock (e.g. when used outside of a session context).
            root_session = None
            if session is not None:
                try:
                    from ..session._session import AppSession

                    root = session.root_scope()
                    if isinstance(root, AppSession):
                        root_session = root
                except (AttributeError, TypeError):
                    pass

            if root_session is not None:

                async def _do_invalidate() -> None:
                    nonlocal cancellable
                    async with root_session._reactive_lock:
                        cancellable = False
                        ctx.invalidate()
                        await flush()

                await root_session._cycle_start_action(_do_invalidate)
            else:
                # No session or not a real AppSession; just invalidate directly
                cancellable = False
                ctx.invalidate()
                await flush()

        except BaseException:
            traceback.print_exc()
            raise
        finally:
            if unsub:
                unsub()

    task = asyncio.create_task(_task(ctx, deadline))

    def cancel_task():
        if cancellable and not task.cancelled():
            task.cancel()

    ctx.on_invalidate(cancel_task)
    if session:
        unsub = session.on_ended(cancel_task)
