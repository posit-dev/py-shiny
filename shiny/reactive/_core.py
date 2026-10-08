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
from typing import (
    TYPE_CHECKING,
    Awaitable,
    Callable,
    Generator,
    Literal,
    Optional,
    TypeVar,
)

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
        """Add this context to the reactive effect queue, to run in the next round."""
        _reactive_environment.enqueue_effect(self, priority)

    def on_flush(self, func: Callable[[], Awaitable[None]]) -> None:
        """Register a function to be called when a round takes this context from the
        reactive effect queue."""
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


# The task running the current round, effect, or session output flush. Tasks created
# from it inherit this value, which lets `wait_for_idle()` tell whether it was called
# from within a run that is still going (directly or through a task it started).
_enclosing_run: ContextVar[Optional["asyncio.Task[object]"]] = ContextVar(
    "enclosing_run", default=None
)


def _is_alive(
    loop: Optional[asyncio.AbstractEventLoop],
) -> TypeGuard[asyncio.AbstractEventLoop]:
    return loop is not None and not loop.is_closed() and loop.is_running()


class ReactiveEnvironment:
    """
    The reactive environment.

    Terms used throughout the reactive system:

    * **Reactive effect queue**: the single, process-wide priority queue of reactive
      effect contexts waiting to run. Invalidating an effect adds it to this queue.
    * **Round**: one drain of the reactive effect queue, followed by the
      round-finished callbacks. A round starts each effect in its own task and does
      not wait for any effect's async part.
    * **Idle**: the reactive effect queue is empty, and no round, effect, or session
      output flush task is running. `reactive.flush()` waits until idle.
    * **Cycle** (per session): one action (such as an input change), the effects it
      starts, and the output flush that ends it. One cycle can span several rounds,
      and one round can advance the cycles of several sessions.
    * **Output flush** (per session): sending a session's outputs to the client,
      once that session's effects have finished.
    """

    def __init__(self) -> None:
        self._current_context: ContextVar[Optional[Context]] = ContextVar(
            "current_context", default=None
        )
        self._next_id: int = 0
        self._effect_queue: PriorityQueueFIFO[Context] = PriorityQueueFIFO()
        self._round_finished_callbacks = _utils.AsyncCallbacks()
        self._round_requested: bool = False
        # The event loop Shiny runs on, for requests made from other threads.
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._round_running: bool = False
        # Resolved by the next round to start (see `wait_for_next_round()`).
        self._next_round_waiters: list[asyncio.Future[None]] = []
        # Set when a round is requested while one is running.
        self._rerun_round: bool = False
        # Strong references to fire-and-forget tasks (rounds, effect runs, and session
        # output flushes); the event loop only keeps weak ones.
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

    def on_round_finished(
        self, func: Callable[[], Awaitable[None]], once: bool = False
    ) -> Callable[[], None]:
        """Register a function to be called at the end of every round."""
        return self._round_finished_callbacks.register(func, once=once)

    async def run_round(self) -> None:
        """
        Run one round: start every context in the reactive effect queue, then invoke
        the round-finished callbacks.

        This never waits for an effect's async part: each context runs in its own
        task. Priority orders when effects start, not when they finish.
        """
        # Don't start a second round while one is running; the running one requests
        # another when it finishes.
        self._adopt_loop(asyncio.get_running_loop())
        if self._round_running:
            self._rerun_round = True
            return
        self._round_running = True
        self._rerun_round = False
        self._round_requested = False
        self._loop = asyncio.get_running_loop()
        waiters = self._next_round_waiters
        self._next_round_waiters = []
        token = _enclosing_run.set(asyncio.current_task())
        try:
            # Wrap the round in a reactive_update span (or no-op if not collecting)
            async with shiny_otel_span(
                "reactive_update",
                infer_session_id=True,
                required_level=OtelCollectLevel.REACTIVE_UPDATE,
                collection_level=_get_env_level(),
            ):
                while not self._effect_queue.empty():
                    ctx = self._effect_queue.get()
                    self._spawn(self._run_context(ctx))
                    # CPython runs ready callbacks FIFO, so the task's sync part runs
                    # now, and anything it invalidates is queued before we take the
                    # next ctx.
                    await _yield_to_loop()
                await self._round_finished_callbacks.invoke()
        finally:
            _enclosing_run.reset(token)
            self._round_running = False
            for waiter in waiters:
                if not waiter.done():
                    waiter.set_result(None)
            if (
                self._rerun_round
                or self._next_round_waiters
                or not self._effect_queue.empty()
            ):
                self._round_requested = False
                self.request_round()

    async def _run_context(self, ctx: Context) -> None:
        _enclosing_run.set(asyncio.current_task())
        await ctx.execute_flush_callbacks()

    async def wait_for_next_round(self) -> None:
        """
        Return once a complete round that starts after this call has finished.

        Runs that round itself when none is running; otherwise waits for the round
        that the running one requests when it finishes.
        """
        self._adopt_loop(asyncio.get_running_loop())
        if not self._round_running:
            await self.run_round()
            return
        waiter: asyncio.Future[None] = asyncio.get_running_loop().create_future()
        self._next_round_waiters.append(waiter)
        self._rerun_round = True
        await waiter

    async def wait_for_idle(self) -> None:
        """
        Run rounds until idle: the reactive effect queue is empty and no round,
        effect, or session output flush task is running.

        Returns right away when called from within a round, effect, or output flush
        that is
        still going, including from a task it started (e.g. via `asyncio.gather()`
        or `asyncio.wait_for()`): that run may be waiting on the caller, so waiting
        here could deadlock. A task started by an effect that has since finished
        (e.g. an extended task's body) waits as usual.
        """
        owner = _enclosing_run.get()
        if owner is not None and not owner.done():
            return
        current = asyncio.current_task()
        while True:
            await self.wait_for_next_round()
            running = {t for t in self._tasks if not t.done() and t is not current}
            if not running and self._effect_queue.empty():
                return
            if running:
                await asyncio.wait(running)

    def request_round(self) -> None:
        """
        Schedule a single round on the next event-loop iteration. Requests made before
        it runs are merged into it.

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
            # touches `_round_requested` and schedules the round.
            try:
                home.call_soon_threadsafe(self.request_round)
            except RuntimeError:
                pass  # The loop closed in the meantime.
            return
        if loop is None:
            # No loop at all (e.g. a reactive graph built synchronously); whoever
            # runs the graph will call `run_round()` explicitly.
            return
        self._adopt_loop(loop)
        self._loop = loop
        if self._round_requested:
            return
        self._round_requested = True
        # A fresh context keeps the requester's session and OTel span out of the round.
        loop.call_soon(self._start_requested_round, context=contextvars.Context())

    def _adopt_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """
        Discard round state left by an event loop that has stopped.

        A round (or request) stranded on a loop that stopped mid-round, such as a
        previous `test_server()` run's, can never finish. Without this, later rounds
        would return as if one were running, and `wait_for_next_round()` would wait
        forever.
        """
        old = self._loop
        if old is None or old is loop or _is_alive(old):
            return
        self._round_running = False
        self._rerun_round = False
        self._round_requested = False
        self._next_round_waiters = []
        # Stop waiting on the dead loop's tasks, but keep them: if collected, their
        # coroutines' `finally` blocks would run (and fail) in whatever runs then.
        # ponytail: never freed; only loops that stop mid-round (tests, repeated
        # `test_server()` runs) leave any.
        self._abandoned_tasks |= self._tasks
        self._tasks = set()
        self._loop = loop

    def _start_requested_round(self) -> None:
        if self._round_requested:
            self._spawn(self.run_round())

    def _spawn(self, coro: Awaitable[None]) -> "asyncio.Task[None]":
        task = asyncio.ensure_future(coro)
        self._tasks.add(task)
        task.add_done_callback(self._on_task_done)
        return task

    def _on_task_done(self, task: asyncio.Task[None]) -> None:
        self._tasks.discard(task)
        if not task.cancelled() and (err := task.exception()) is not None:
            # Effects report their own errors; this only catches bugs in a round or
            # output flush.
            traceback.print_exception(type(err), err, err.__traceback__)

    def enqueue_effect(self, ctx: Context, priority: int) -> None:
        self._effect_queue.put(priority, ctx)
        self.request_round()

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

    Runs rounds until the reactive environment is idle: the reactive effect queue is
    empty, every started effect (including its async part) has finished, and each
    session's resulting outputs have been sent. That covers every session, not only
    the caller's, so in an app it can wait on other sessions' slow effects.

    Note
    ----
    Called from within an effect, or from a task started by an effect that is still
    running (e.g. via `asyncio.create_task()` or `asyncio.gather()`), this returns
    right away without waiting: the effect may be waiting on the caller, so waiting
    could deadlock. Dependents still run in the next round, but code right after
    this call can't rely on them having run yet. A task that outlives the effect
    that started it (such as an extended task's body) waits as usual.
    """
    await _reactive_environment.wait_for_idle()


@no_example()
def on_flushed(
    func: Callable[[], Awaitable[None]], once: bool = False
) -> Callable[[], None]:
    """
    Register a function to be called at the end of every round.

    A round starts every effect in the reactive effect queue, without waiting for
    their async parts. One call to :func:`~shiny.reactive.flush` can run several
    rounds.

    Parameters
    ----------
    func
        The function to be called at the end of every round.
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

    return _reactive_environment.on_round_finished(func, once)


class _NoOpLock(asyncio.Lock):
    """
    What :func:`~shiny.reactive.lock` returns: an :class:`asyncio.Lock` that never
    blocks, so any number of holders can hold it at once.
    """

    async def acquire(self) -> Literal[True]:
        return True

    def release(self) -> None:
        pass

    def locked(self) -> bool:
        return False


@no_example()
def lock() -> asyncio.Lock:
    """
    Deprecated. Set a reactive value directly instead.

    Apart from emitting a deprecation warning, this function does nothing. It
    returns an :class:`asyncio.Lock` that never blocks, so holding it neither pauses
    reactive processing nor keeps out other code that holds it. Code that needs
    mutual exclusion of its own should create its own :class:`asyncio.Lock`.

    To change reactive state from outside a reactive context (for example, from a
    background :class:`asyncio.Task`), set the :class:`~shiny.reactive.value`
    directly. Setting it schedules a round, so there's no need to call
    :func:`~shiny.reactive.flush` afterwards:

    ```python
    # Deprecated
    async with reactive.lock():
        current_query.set(query)
        await reactive.flush()

    # Use instead
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
        "reactive.lock() is deprecated, does nothing, and will be removed in a future "
        "version of shiny. To change reactive state from a background task, set the "
        "reactive value directly: a flush is scheduled automatically, so "
        "`await reactive.flush()` is not needed. To apply the change once the "
        "session's effects have finished, use `session.run_once_when_idle()`."
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
            # The resulting round is requested with a fresh context, so its
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
    # that re-arms itself would keep `wait_for_idle()` waiting forever.
    _timer_tasks.add(task)
    task.add_done_callback(_timer_tasks.discard)

    def cancel_task():
        if cancellable and not task.cancelled():
            task.cancel()

    ctx.on_invalidate(cancel_task)
    if session:
        unsub = session.on_ended(cancel_task)
