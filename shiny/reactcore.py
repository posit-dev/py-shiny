"""Low-level reactive components."""


import contextlib
from typing import Callable, Optional, Awaitable, TypeVar
from contextvars import ContextVar
import asyncio
import typing
import warnings

from .datastructures import PriorityQueueFIFO
from . import utils

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
        if ctx.id not in self._dependents:
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
        # https://github.com/rstudio/prism/issues/26
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
        self.lock = asyncio.Lock()
        self._flushed_callbacks = utils.AsyncCallbacks()

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
        """Return the current Context object"""
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
        await self._flush_sequential()
        await self._flushed_callbacks.invoke()

    async def _flush_sequential(self) -> None:
        # Sequential flush: instead of storing the tasks in a list and calling gather()
        # on them later, just run each effect in sequence.
        while not self._pending_flush_queue.empty():
            ctx = self._pending_flush_queue.get()
            await ctx.execute_flush_callbacks()

    def add_pending_flush(self, ctx: Context, priority: int) -> None:
        self._pending_flush_queue.put(priority, ctx)

    @contextlib.contextmanager
    def isolate(self):
        token = self._current_context.set(Context())
        try:
            yield
        finally:
            self._current_context.reset(token)


_reactive_environment = ReactiveEnvironment()


@contextlib.contextmanager
def isolate():
    with _reactive_environment.isolate():
        yield


def get_current_context() -> Context:
    return _reactive_environment.current_context()


async def flush() -> None:
    await _reactive_environment.flush()


def on_flushed(
    func: Callable[[], Awaitable[None]], once: bool = False
) -> Callable[[], None]:
    return _reactive_environment.on_flushed(func, once)


def lock() -> asyncio.Lock:
    """A lock that should be held whenever manipulating the reactive graph."""
    return _reactive_environment.lock
