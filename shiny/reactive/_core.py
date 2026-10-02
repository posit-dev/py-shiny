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
import contextvars
import time
import traceback
import types
import typing
import warnings
from contextvars import ContextVar
from typing import TYPE_CHECKING, Awaitable, Callable, Generator, Optional, TypeVar

from .. import _utils
from .._datastructures import PriorityQueueFIFO
from .._docstring import add_example, no_example
from .._typing_extensions import TypeGuard
from ..otel._collect import OtelCollectLevel, _get_env_level
from ..otel._span_wrappers import shiny_otel_span
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


@types.coroutine
def _yield_to_loop() -> Generator[None, None, None]:
    # What `asyncio.sleep(0)` does, without going through a patchable function.
    yield


# The task running the current flush or effect. Tasks created from it inherit this
# value, which lets `flush_settled()` tell whether it was called from within a flush
# or effect run that is still going (directly or through a task it started).
_flush_owner: ContextVar[Optional["asyncio.Task[object]"]] = ContextVar(
    "flush_owner", default=None
)


def _is_alive(
    loop: Optional[asyncio.AbstractEventLoop],
) -> TypeGuard[asyncio.AbstractEventLoop]:
    return loop is not None and not loop.is_closed() and loop.is_running()


class ReactiveEnvironment:
    """The reactive environment"""

    def __init__(self) -> None:
        self._current_context: ContextVar[Optional[Context]] = ContextVar(
            "current_context", default=None
        )
        self._next_id: int = 0
        self._pending_flush_queue: PriorityQueueFIFO[Context] = PriorityQueueFIFO()
        self._flushed_callbacks = _utils.AsyncCallbacks()
        self._flush_requested: bool = False
        # The event loop Shiny runs on, for requests made from other threads.
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._in_flush: bool = False
        # Resolved by the next flush to start (see `flush_pass()`).
        self._flush_pass_waiters: list[asyncio.Future[None]] = []
        # Set when a flush is requested while one is active.
        self._rerun_flush: bool = False
        # Strong references to fire-and-forget tasks (flushes and effect runs); the
        # event loop only keeps weak ones.
        self._tasks: set[asyncio.Task[None]] = set()
        # Tasks stranded on an event loop that stopped (see `_adopt_loop()`).
        self._abandoned_tasks: set[asyncio.Task[None]] = set()

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
        """
        Start every pending context, then invoke the flushed callbacks.

        This never waits for an effect's async part: each context runs in its own
        task. Priority orders when effects start, not when they finish.
        """
        # Don't start a second flush while one is active; the active one runs again
        # when it finishes.
        self._adopt_loop(asyncio.get_running_loop())
        if self._in_flush:
            self._rerun_flush = True
            return
        self._in_flush = True
        self._rerun_flush = False
        self._flush_requested = False
        self._loop = asyncio.get_running_loop()
        waiters = self._flush_pass_waiters
        self._flush_pass_waiters = []
        token = _flush_owner.set(asyncio.current_task())
        try:
            # Wrap entire flush cycle in reactive_update span (or no-op if not collecting)
            async with shiny_otel_span(
                "reactive_update",
                infer_session_id=True,
                required_level=OtelCollectLevel.REACTIVE_UPDATE,
                collection_level=_get_env_level(),
            ):
                while not self._pending_flush_queue.empty():
                    ctx = self._pending_flush_queue.get()
                    self._spawn(self._run_context(ctx))
                    # CPython runs ready callbacks FIFO, so the task's sync part runs
                    # now, and anything it invalidates is queued before we take the
                    # next ctx.
                    await _yield_to_loop()
                await self._flushed_callbacks.invoke()
        finally:
            _flush_owner.reset(token)
            self._in_flush = False
            for waiter in waiters:
                if not waiter.done():
                    waiter.set_result(None)
            if (
                self._rerun_flush
                or self._flush_pass_waiters
                or not self._pending_flush_queue.empty()
            ):
                self._flush_requested = False
                self.request_flush()

    async def _run_context(self, ctx: Context) -> None:
        _flush_owner.set(asyncio.current_task())
        await ctx.execute_flush_callbacks()

    async def flush_pass(self) -> None:
        """Run one complete flush that starts after this call, or wait for one."""
        self._adopt_loop(asyncio.get_running_loop())
        if not self._in_flush:
            await self.flush()
            return
        waiter: asyncio.Future[None] = asyncio.get_running_loop().create_future()
        self._flush_pass_waiters.append(waiter)
        self._rerun_flush = True
        await waiter

    async def flush_settled(self) -> None:
        """
        Flush until nothing is pending and no flush or effect task is running.

        Returns right away when called from within a flush or effect run that is
        still going, including from a task it started (e.g. via `asyncio.gather()`
        or `asyncio.wait_for()`): that run may be waiting on the caller, so waiting
        here could deadlock. A task started by an effect that has since finished
        (e.g. an extended task's body) waits as usual.
        """
        owner = _flush_owner.get()
        if owner is not None and not owner.done():
            return
        current = asyncio.current_task()
        while True:
            await self.flush_pass()
            running = {t for t in self._tasks if not t.done() and t is not current}
            if not running and self._pending_flush_queue.empty():
                return
            if running:
                await asyncio.wait(running)

    def request_flush(self) -> None:
        """
        Schedule a single flush on the next event-loop pass. Requests made before it
        runs are merged into it.

        Safe to call from another thread: the request is handed to the event loop
        Shiny runs on. (That makes only the *request* thread-safe. Reactive state
        itself must be changed on the loop's thread, e.g. with
        `loop.call_soon_threadsafe(value.set, x)`.)
        """
        try:
            loop: Optional[asyncio.AbstractEventLoop] = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        home = self._loop
        if _is_alive(home) and loop is not home:
            # Another thread: retry on the loop's own thread, so only that thread
            # touches `_flush_requested` and schedules the flush.
            try:
                home.call_soon_threadsafe(self.request_flush)
            except RuntimeError:
                pass  # The loop closed in the meantime.
            return
        if loop is None:
            # No loop at all (e.g. a reactive graph built synchronously); whoever
            # runs the graph will call flush() explicitly.
            return
        self._adopt_loop(loop)
        self._loop = loop
        if self._flush_requested:
            return
        self._flush_requested = True
        # A fresh context keeps the requester's session and OTel span out of the flush.
        loop.call_soon(self._start_requested_flush, context=contextvars.Context())

    def _adopt_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """
        Discard flush state left by an event loop that has stopped.

        A flush (or request) stranded on a loop that stopped mid-flush, such as a
        previous `test_server()` run's, can never finish. Without this, later
        flushes would return as if one were active, and `flush_pass()` would wait
        forever.
        """
        old = self._loop
        if old is None or old is loop or _is_alive(old):
            return
        self._in_flush = False
        self._rerun_flush = False
        self._flush_requested = False
        self._flush_pass_waiters = []
        # Stop waiting on the dead loop's tasks, but keep them: if collected, their
        # coroutines' `finally` blocks would run (and fail) in whatever runs then.
        # ponytail: never freed; only loops that stop mid-flush (tests, repeated
        # `test_server()` runs) leave any.
        self._abandoned_tasks |= self._tasks
        self._tasks = set()
        self._loop = loop

    def _start_requested_flush(self) -> None:
        if self._flush_requested:
            self._spawn(self.flush())

    def _spawn(self, coro: Awaitable[None]) -> "asyncio.Task[None]":
        task = asyncio.ensure_future(coro)
        self._tasks.add(task)
        task.add_done_callback(self._on_task_done)
        return task

    def _on_task_done(self, task: asyncio.Task[None]) -> None:
        self._tasks.discard(task)
        if not task.cancelled() and (err := task.exception()) is not None:
            # Effects report their own errors; this only catches bugs in the flush.
            traceback.print_exception(type(err), err, err.__traceback__)

    def add_pending_flush(self, ctx: Context, priority: int) -> None:
        self._pending_flush_queue.put(priority, ctx)
        self.request_flush()

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
    Setting a :class:`~shiny.reactive.value` already schedules a flush, so code that
    sets one (from a background task, for example) doesn't need to call this.

    Returns once every started effect, including its async part, has finished, and
    each session's resulting outputs have been sent. That covers every session, not
    only the caller's, so in an app it can wait on other sessions' slow effects.

    Note
    ----
    Called from within an effect, or from a task started by an effect that is still
    running (e.g. via `asyncio.create_task()` or `asyncio.gather()`), this returns
    right away without waiting: the effect may be waiting on the caller, so waiting
    could deadlock. Dependents still run on the next flush, but code right after
    this call can't rely on them having run yet. A task that outlives the effect
    that started it (such as an extended task's body) waits as usual.
    """
    await _reactive_environment.flush_settled()


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


class _NoOpLock:
    """
    What :func:`~shiny.reactive.lock` returns: it has the methods of an
    :class:`asyncio.Lock`, but it never blocks.
    """

    async def __aenter__(self) -> None:
        return None

    async def __aexit__(self, *args: object) -> None:
        return None

    async def acquire(self) -> bool:
        return True

    def release(self) -> None:
        pass

    def locked(self) -> bool:
        return False


@no_example()
def lock() -> _NoOpLock:
    """
    Deprecated. Set a reactive value directly instead.

    This function does nothing. It returns an object with the methods of an
    :class:`asyncio.Lock` that never blocks, so holding it neither pauses reactive
    processing nor keeps out other code that holds it.

    To change reactive state from a different :class:`~asyncio.Task` than the one
    running the Shiny :class:`~shiny.Session` (for example, a background task),
    set the :class:`~shiny.reactive.value` directly. Setting it schedules a
    reactive flush, so there's no need to call :func:`~shiny.reactive.flush`
    afterwards:

    ```python
    # Before
    async with reactive.lock():
        current_query.set(query)
        await reactive.flush()

    # After
    current_query.set(query)
    ```

    Effects of a session that are paused at an ``await`` see the new value as soon
    as it is set. To apply the change only once the session's effects have
    finished, as Shiny does for input changes from the client, use
    :meth:`~shiny.Session.run_once_when_idle`:

    ```python
    session.run_once_when_idle(lambda: current_query.set(query))
    ```
    """
    # Imported here because `shiny._deprecated` imports `shiny.reactive`.
    from .._deprecated import warn_deprecated

    warn_deprecated(
        "reactive.lock() is deprecated and does nothing. To change reactive state "
        "from a background task, set the reactive value directly: a flush is "
        "scheduled automatically, so `await reactive.flush()` is not needed. To apply "
        "the change once the session's effects have finished, use "
        "`session.run_once_when_idle()`."
    )
    return _NoOpLock()


_timer_tasks: set[asyncio.Task[None]] = set()


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

            # Prevent the ctx.invalidate() from killing our own task. (Another way
            # to accomplish this is to unregister our ctx.on_invalidate handler, but
            # ctx.on_invalidate doesn't currently allow unregistration.)
            cancellable = False

            # Like an input change, the invalidation waits until the session is idle.
            # The resulting flush is requested with a fresh context, so its
            # reactive_update span has no parent.
            if session:
                session.run_once_when_idle(ctx.invalidate)
            else:
                ctx.invalidate()

        except BaseException:
            traceback.print_exc()
            raise
        finally:
            if unsub:
                unsub()

    task = asyncio.create_task(_task(ctx, deadline))
    # Keep a strong reference; not in `_reactive_environment._tasks`, since a timer
    # that re-arms itself would keep `flush_settled()` waiting forever.
    _timer_tasks.add(task)
    task.add_done_callback(_timer_tasks.discard)

    def cancel_task():
        if cancellable and not task.cancelled():
            task.cancel()

    ctx.on_invalidate(cancel_task)
    if session:
        unsub = session.on_ended(cancel_task)
