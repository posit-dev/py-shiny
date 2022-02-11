"""Reactive components"""

__all__ = ("Value", "Calc", "CalcAsync", "calc", "Effect", "EffectAsync", "effect")

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
    overload,
)
import warnings

from ._core import Context, Dependents, ReactiveWarning
from .. import _utils
from ..types import MISSING, MISSING_TYPE, SilentException

if TYPE_CHECKING:
    from ..session import Session

T = TypeVar("T")

# ==============================================================================
# Value
# ==============================================================================
class Value(Generic[T]):
    # These overloads are necessary so that the following hold:
    # - Value() is marked by the type checker as an error, because the type T is
    #   unknown. (It is not a run-time error.)
    # - Value[int]() works.
    # - Value[int](1) works.
    # - Value(1) works, with T is inferred to be int.
    @overload
    def __init__(
        self, value: MISSING_TYPE = MISSING, *, read_only: bool = False
    ) -> None:
        ...

    @overload
    def __init__(self, value: T, *, read_only: bool = False) -> None:
        ...

    # If `value` is MISSING, then `get()` will raise a SilentException, until a new
    # value is set. Calling `unset()` will set the value to MISSING.
    def __init__(
        self, value: Union[T, MISSING_TYPE] = MISSING, *, read_only: bool = False
    ) -> None:
        self._value: T = value
        self._read_only: bool = read_only
        self._dependents: Dependents = Dependents()

    def __call__(self) -> T:
        return self.get()

    def get(self) -> T:
        self._dependents.register()

        if isinstance(self._value, MISSING_TYPE):
            raise SilentException

        return self._value

    def set(self, value: T) -> bool:
        if self._read_only:
            raise RuntimeError(
                "Can't set read-only Value. If you are trying to set an input value, use `update_xxx()` instead."
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

    def unset(self) -> None:
        self.set(MISSING)  # type: ignore

    def is_set(self) -> bool:
        self._dependents.register()
        return not isinstance(self._value, MISSING_TYPE)

    # Like unset(), except that this does not invalidate dependents.
    def freeze(self) -> None:
        self._value = MISSING


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
        self._fn: CalcFunctionAsync[T] = _utils.wrap_async(fn)
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
            import shiny.session

            # If no session is provided, autodetect the current session (this
            # could be None if outside of a session).
            session = shiny.session.get_current_session()
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
        return _utils.run_coro_sync(self.get_value())

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

        import shiny.session

        with shiny.session.session_context(self._session):
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
        if not _utils.is_async_callable(fn):
            raise TypeError(self.__class__.__name__ + " requires an async function")

        super().__init__(cast(CalcFunction[T], fn), session=session)
        self._is_async = True

    async def __call__(self) -> T:
        return await self.get_value()


# Note that the specified return type of calc() isn't exactly the same as the actual
# returned object -- the former specifes a Callable that takes a CalcFunction[T], and
# the latter is a Callable that takes CalcFunction[T] | CalcFunctionAsync[T]. Both are
# technically correct, since the CalcFunction's T encompasses both "regular" types V as
# well as Awatiable[V]. (We're using V to represent a generic type that is NOT itself
# Awaitable.) So if the T represents an Awaitable[V], then the type checker knows that
# the returned function will return a Calc[Awaitable[V]].
#
# However, if the calc() function is specified to return a Callable that takes
# CalcFunction[T] | CalcFunctionAsync[T], then if a CalcFunctionAsync is passed in, the
# type check will not know that the returned Calc object is a Calc[Awaitable[V]]. It
# will think that it's a [Calc[V]]. Then the type checker will think that the returned
# Calc object is not async when it actually is.
#
# To work around this, we say that calc() returns a Callable that takes a
# CalcFunction[T], instead of the union type. We're sort of tricking the type checker
# twice: once here, and once when we return a Calc object (which has a synchronous
# __call__ method) or CalcAsync object (which has an async __call__ method), and it
# works out.
def calc(
    *, session: Union[MISSING_TYPE, "Session", None] = MISSING
) -> Callable[[CalcFunction[T]], Calc[T]]:
    def create_calc(fn: Union[CalcFunction[T], CalcFunctionAsync[T]]) -> Calc[T]:
        if _utils.is_async_callable(fn):
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
        suspended: bool = False,
        priority: int = 0,
        session: Union[MISSING_TYPE, "Session", None] = MISSING,
    ) -> None:
        self.__name__ = fn.__name__
        self.__doc__ = fn.__doc__

        # The EffectAsync subclass will pass in an async function, but it tells the
        # static type checker that it's synchronous. wrap_async() is smart -- if is
        # passed an async function, it will not change it.
        self._fn: EffectFunctionAsync = _utils.wrap_async(fn)
        self._is_async: bool = False

        self._priority: int = priority
        self._suspended = suspended
        self._on_resume: Callable[[], None] = lambda: None

        self._invalidate_callbacks: list[Callable[[], None]] = []
        self._destroyed: bool = False
        self._ctx: Optional[Context] = None
        self._exec_count: int = 0

        self._session: Optional[Session]
        # Use `isinstance(x, MISSING_TYPE)`` instead of `x is MISSING` because
        # the type checker doesn't know that MISSING is the only instance of
        # MISSING_TYPE; this saves us from casting later on.
        if isinstance(session, MISSING_TYPE):
            import shiny.session

            # If no session is provided, autodetect the current session (this
            # could be None if outside of a session).
            session = shiny.session.get_current_session()
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

            if self._destroyed:
                return

            def _continue() -> None:
                ctx.add_pending_flush(self._priority)

            if self._suspended:
                self._on_resume = _continue
            else:
                _continue()

        async def on_flush_cb() -> None:
            if not self._destroyed:
                await self.run()

        ctx.on_invalidate(on_invalidate_cb)
        ctx.on_flush(on_flush_cb)

        return ctx

    async def run(self) -> None:
        ctx = self._create_context()
        self._exec_count += 1
        import shiny.session

        with shiny.session.session_context(self._session):
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

    def suspend(self) -> None:
        """
        Causes this observer to stop scheduling flushes (re-executions) in response to
        invalidations. If the observer was invalidated prior to this call but it has not
        re-executed yet (because it waits until on_flush is called) then that
        re-execution will still occur, because the flush is already scheduled.
        """
        self._suspended = True

    def resume(self) -> None:
        """
        Causes this observer to start re-executing in response to invalidations. If the
        observer was invalidated while suspended, then it will schedule itself for
        re-execution (pending flush).
        """
        if self._suspended:
            self._suspended = False
            self._on_resume()
            self._on_resume = lambda: None

    def set_priority(self, priority: int = 0) -> None:
        """
        Change this observer's priority. Note that if the observer is currently
        invalidated, then the change in priority will not take effect until the next
        invalidation--unless the observer is also currently suspended, in which case the
        priority change will be effective upon resume.
        """
        self._priority = priority

    def _on_session_ended_cb(self) -> None:
        self.destroy()


class EffectAsync(Effect):
    def __init__(
        self,
        fn: EffectFunctionAsync,
        *,
        suspended: bool = False,
        priority: int = 0,
        session: Union[MISSING_TYPE, "Session", None] = MISSING,
    ) -> None:
        if not _utils.is_async_callable(fn):
            raise TypeError(self.__class__.__name__ + " requires an async function")

        super().__init__(
            cast(EffectFunction, fn),
            suspended=suspended,
            session=session,
            priority=priority,
        )
        self._is_async = True


def effect(
    *,
    suspended: bool = False,
    priority: int = 0,
    session: Union[MISSING_TYPE, "Session", None] = MISSING,
) -> Callable[[Union[EffectFunction, EffectFunctionAsync]], Effect]:
    """[summary]

    Args:
        priority : [description]. Defaults to 0.
        session : [description]. Defaults to MISSING.

    Returns:
        [description]
    """

    def create_effect(fn: Union[EffectFunction, EffectFunctionAsync]) -> Effect:
        if _utils.is_async_callable(fn):
            fn = cast(EffectFunctionAsync, fn)
            return EffectAsync(
                fn, suspended=suspended, priority=priority, session=session
            )
        else:
            fn = cast(EffectFunction, fn)
            return Effect(fn, suspended=suspended, priority=priority, session=session)

    return create_effect
