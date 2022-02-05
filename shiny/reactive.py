"""Reactive components"""

__all__ = (
    "Value",
    "Calc",
    "CalcAsync",
    "calc",
    "Effect",
    "EffectAsync",
    "effect",
    "isolate",
    "invalidate_later",
)

import asyncio
import time
import traceback
from typing import (
    TYPE_CHECKING,
    Optional,
    Callable,
    Awaitable,
    TypeVar,
    Union,
    Generic,
    cast,
)
import typing
import inspect
import warnings

from .reactcore import Context, Dependents, ReactiveWarning
from . import reactcore
from . import utils
from .types import MISSING, MISSING_TYPE
from .validation import SilentException

if TYPE_CHECKING:
    from .session import Session

T = TypeVar("T")

# ==============================================================================
# Value
# ==============================================================================
class Value(Generic[T]):
    def __init__(self, value: T, *, _read_only: bool = False) -> None:
        self._value: T = value
        self._read_only: bool = _read_only
        self._dependents: Dependents = Dependents()

    # Calling the object is equivalent to `.get()`
    def __call__(self) -> T:
        self._dependents.register()
        return self._value

    def get(self) -> T:
        self._dependents.register()
        return self._value

    def set(self, value: T) -> bool:
        if self._read_only:
            raise RuntimeError(
                "Can't set read-only reactive.Value. If you are trying to set an input value, use `update_xxx()` instead."
            )
        return self._set(value)

    # The ._set() method allows setting read-only Value objects. This is used when the
    # Value is part of a session.Inputs object, and the session wants to set it.
    def _set(self, value: T) -> bool:
        if self._value is value:
            return False

        self._value = value
        self._dependents.invalidate()
        return True


# ==============================================================================
# Calc
# ==============================================================================

CalcFunction = Callable[[], T]
CalcFunctionAsync = Callable[[], Awaitable[T]]


class Calc(Generic[T]):
    def __init__(
        self,
        fn: CalcFunction[T],
        *,
        session: Union[MISSING_TYPE, "Session", None] = MISSING,
    ) -> None:
        self.__name__ = fn.__name__
        self.__doc__ = fn.__doc__

        # The CalcAsync subclass will pass in an async function, but it tells the
        # static type checker that it's synchronous. wrap_async() is smart -- if is
        # passed an async function, it will not change it.
        self._fn: CalcFunctionAsync[T] = utils.wrap_async(fn)
        self._is_async: bool = False

        self._dependents: Dependents = Dependents()
        self._invalidated: bool = True
        self._running: bool = False
        self._most_recent_ctx_id: int = -1
        self._ctx: Optional[Context] = None
        self._exec_count: int = 0

        self._session: Optional[Session]
        # Use `isinstance(x, MISSING_TYPE)`` instead of `x is MISSING` because
        # the type checker doesn't know that MISSING is the only instance of
        # MISSING_TYPE; this saves us from casting later on.
        if isinstance(session, MISSING_TYPE):
            # If no session is provided, autodetect the current session (this
            # could be None if outside of a session).
            session = shiny_session.get_current_session()
        self._session = session

        # Use lists to hold (optional) value and error, instead of Optional[T],
        # because it makes typing more straightforward. For example if
        # .get_value() simply returned self._value, self._value had type
        # Optional[T], then the return type for get_value() would have to be
        # Optional[T].
        self._value: list[T] = []
        self._error: list[Exception] = []

    def __call__(self) -> T:
        # Run the Coroutine (synchronously), and then return the value.
        # If the Coroutine yields control, then an error will be raised.
        return utils.run_coro_sync(self.get_value())

    async def get_value(self) -> T:
        self._dependents.register()

        if self._invalidated or self._running:
            await self.update_value()

        if self._error:
            raise self._error[0]

        return self._value[0]

    async def update_value(self) -> None:
        self._ctx = Context()
        self._most_recent_ctx_id = self._ctx.id

        self._ctx.on_invalidate(self._on_invalidate_cb)

        self._exec_count += 1
        self._invalidated = False

        was_running = self._running
        self._running = True

        with shiny_session.session_context(self._session):
            try:
                with self._ctx():
                    await self._run_func()
            finally:
                self._running = was_running

    def _on_invalidate_cb(self) -> None:
        self._invalidated = True
        self._value.clear()  # Allow old value to be GC'd
        self._dependents.invalidate()
        self._ctx = None  # Allow context to be GC'd

    async def _run_func(self) -> None:
        self._error.clear()
        try:
            self._value.append(await self._fn())
        except Exception as err:
            self._error.append(err)


class CalcAsync(Calc[T]):
    def __init__(
        self,
        fn: CalcFunctionAsync[T],
        *,
        session: Union[MISSING_TYPE, "Session", None] = MISSING,
    ) -> None:
        if not inspect.iscoroutinefunction(fn):
            raise TypeError(self.__class__.__name__ + " requires an async function")

        super().__init__(cast(CalcFunction[T], fn), session=session)
        self._is_async = True

    async def __call__(self) -> T:
        return await self.get_value()


def calc(
    *, session: Union[MISSING_TYPE, "Session", None] = MISSING
) -> Callable[[Union[CalcFunction[T], CalcFunctionAsync[T]]], Calc[T]]:
    def create_calc(fn: Union[CalcFunction[T], CalcFunctionAsync[T]]) -> Calc[T]:
        if inspect.iscoroutinefunction(fn):
            fn = cast(CalcFunctionAsync[T], fn)
            return CalcAsync(fn, session=session)
        else:
            fn = cast(CalcFunction[T], fn)
            return Calc(fn, session=session)

    return create_calc


# ==============================================================================
# Effect
# ==============================================================================

EffectFunction = Callable[[], None]
EffectFunctionAsync = Callable[[], Awaitable[None]]


class Effect:
    def __init__(
        self,
        fn: EffectFunction,
        *,
        priority: int = 0,
        session: Union[MISSING_TYPE, "Session", None] = MISSING,
    ) -> None:
        self.__name__ = fn.__name__
        self.__doc__ = fn.__doc__

        # The EffectAsync subclass will pass in an async function, but it tells the
        # static type checker that it's synchronous. wrap_async() is smart -- if is
        # passed an async function, it will not change it.
        self._fn: EffectFunctionAsync = utils.wrap_async(fn)
        self._is_async: bool = False

        self._priority: int = priority

        self._invalidate_callbacks: list[Callable[[], None]] = []
        self._destroyed: bool = False
        self._ctx: Optional[Context] = None
        self._exec_count: int = 0

        self._session: Optional[Session]
        # Use `isinstance(x, MISSING_TYPE)`` instead of `x is MISSING` because
        # the type checker doesn't know that MISSING is the only instance of
        # MISSING_TYPE; this saves us from casting later on.
        if isinstance(session, MISSING_TYPE):
            # If no session is provided, autodetect the current session (this
            # could be None if outside of a session).
            session = shiny_session.get_current_session()
        self._session = session

        if self._session is not None:
            self._session.on_ended(self._on_session_ended_cb)

        # Defer the first running of this until flushReact is called
        self._create_context().invalidate()

    def _create_context(self) -> Context:
        ctx = Context()

        # Store the context explicitly in Effect object
        # TODO: More explanation here
        self._ctx = ctx

        def on_invalidate_cb() -> None:
            # Context is invalidated, so we don't need to store a reference to it
            # anymore.
            self._ctx = None

            for cb in self._invalidate_callbacks:
                cb()

            # TODO: Wrap this stuff up in a continue callback, depending on if suspended?
            ctx.add_pending_flush(self._priority)

        async def on_flush_cb() -> None:
            if not self._destroyed:
                await self.run()

        ctx.on_invalidate(on_invalidate_cb)
        ctx.on_flush(on_flush_cb)

        return ctx

    async def run(self) -> None:
        ctx = self._create_context()
        self._exec_count += 1

        with shiny_session.session_context(self._session):
            try:
                with ctx():
                    await self._fn()
            except SilentException:
                # It's OK for SilentException to cause an Effect to stop running
                pass
            except Exception as e:
                traceback.print_exc()

                warnings.warn("Error in Effect: " + str(e), ReactiveWarning)
                if self._session:
                    await self._session.unhandled_error(e)

    def on_invalidate(self, callback: Callable[[], None]) -> None:
        self._invalidate_callbacks.append(callback)

    def destroy(self) -> None:
        self._destroyed = True

        if self._ctx is not None:
            self._ctx.invalidate()

    def _on_session_ended_cb(self) -> None:
        self.destroy()


class EffectAsync(Effect):
    def __init__(
        self,
        fn: EffectFunctionAsync,
        *,
        priority: int = 0,
        session: Union[MISSING_TYPE, "Session", None] = MISSING,
    ) -> None:
        if not inspect.iscoroutinefunction(fn):
            raise TypeError(self.__class__.__name__ + " requires an async function")

        super().__init__(cast(EffectFunction, fn), session=session, priority=priority)
        self._is_async = True


def effect(
    *, priority: int = 0, session: Union[MISSING_TYPE, "Session", None] = MISSING
) -> Callable[[Union[EffectFunction, EffectFunctionAsync]], Effect]:
    """[summary]

    Args:
        priority : [description]. Defaults to 0.
        session : [description]. Defaults to MISSING.

    Returns:
        [description]
    """

    def create_effect(fn: Union[EffectFunction, EffectFunctionAsync]) -> Effect:
        if inspect.iscoroutinefunction(fn):
            fn = cast(EffectFunctionAsync, fn)
            return EffectAsync(fn, priority=priority, session=session)
        else:
            fn = cast(EffectFunction, fn)
            return Effect(fn, priority=priority, session=session)

    return create_effect


# ==============================================================================
# Miscellaneous functions
# ==============================================================================
def isolate():
    """
    Can be used via `with isolate():` to wrap code blocks whose reactive reads should
    not result in reactive dependencies being taken (that is, we want to read reactive
    values but are not interested in automatically reexecuting when those particular
    values change).
    """
    return reactcore.isolate()


def invalidate_later(delay: float) -> None:
    ctx = reactcore.get_current_context()
    # Pass an absolute time to our subtask, rather than passing the delay directly, in
    # case the subtask doesn't get a chance to start sleeping until a significant amount
    # of time has passed.
    deadline = time.monotonic() + delay

    cancellable = True

    async def _task(ctx: Context, deadline: float):
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

            async with reactcore.lock():
                # Prevent the ctx.invalidate() from killing our own task. (Another way
                # to accomplish this is to unregister our ctx.on_invalidate handler, but
                # ctx.on_invalidate doesn't currently allow unregistration.)
                cancellable = False

                ctx.invalidate()
                await reactcore.flush()

        except BaseException:
            traceback.print_exc()
            raise

    task = asyncio.create_task(_task(ctx, deadline))

    def cancel_task():
        if cancellable:
            task.cancel()

    ctx.on_invalidate(cancel_task)


# Import here at the bottom seems to fix a circular dependency problem.
# Need to import as shiny_session to avoid naming conflicts with function params named
# `session`.
from . import session as shiny_session
