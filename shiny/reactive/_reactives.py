"""Reactive components"""

from __future__ import annotations

__all__ = ("Value", "Calc", "Calc_", "CalcAsync_", "Effect", "Effect_", "event")

import functools
import traceback
import warnings
from typing import (
    TYPE_CHECKING,
    Awaitable,
    Callable,
    Generic,
    Optional,
    TypeVar,
    cast,
    overload,
)

from .. import _utils
from .._docstring import add_example
from .._utils import is_async_callable, run_coro_sync
from .._validation import req
from ..render import RenderFunction
from ..types import MISSING, MISSING_TYPE, ActionButtonValue, SilentException
from ._core import Context, Dependents, ReactiveWarning, isolate

if TYPE_CHECKING:
    from ..session import Session

T = TypeVar("T")


# ==============================================================================
# Value
# ==============================================================================
@add_example()
class Value(Generic[T]):
    """
    Create a reactive value.

    Reactive values are the source of reactivity in Shiny. Changes to reactive values
    invalidate downstream reactive functions (:func:`~shiny.reactive.Calc`,
    :func:`~shiny.reactive.Effect`, and `render` functions decorated with `@output`).
    When these functions are invalidated, they get scheduled to re-execute.

    Shiny input values are read-only reactive values. For example, `input.x` is a
    reactive value object, and to get the current value, you can call `input.x()` or
    `input.x.get()`. When you do that inside of a reactive function, the function takes
    a dependency on the reactive value.

    Parameters
    ----------
    value
        An optional initial value.
    read_only
        If ``True``, then the reactive value cannot be `set()`.

    Returns
    -------
    :
        An instance of a reactive value.

    Raises
    ------
    ~shiny.types.SilentException
        If :func:`~Value.get` is called before a value is provided/set.

    Note
    ----
    A reactive value may only be read from within a reactive function (e.g.,
    :func:`~shiny.reactive.Calc`, :func:`~shiny.reactive.Effect`,
    :func:`shiny.render.text`, etc.) and, when doing so, the function takes a reactive
    dependency on the value (i.e., when the value changes, the calling reactive function
    will re-execute).

    See Also
    --------
    ~shiny.Inputs ~shiny.reactive.Calc ~shiny.reactive.Effect
    """

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
        self, value: T | MISSING_TYPE = MISSING, *, read_only: bool = False
    ) -> None:
        self._value: T | MISSING_TYPE = value
        self._read_only: bool = read_only
        self._value_dependents: Dependents = Dependents()
        self._is_set_dependents: Dependents = Dependents()

    def __call__(self) -> T:
        return self.get()

    def get(self) -> T:
        """
        Read the reactive value.

        Returns
        -------
        :
            A value.

        Raises
        ------
        ~shiny.types.SilentException
            If the value is not set.
        RuntimeError
            If called from outside a reactive function.
        """

        self._value_dependents.register()

        if isinstance(self._value, MISSING_TYPE):
            raise SilentException

        return self._value

    def set(self, value: T) -> bool:
        """
        Set the reactive value to a new value.

        Parameters
        ----------
        value
            A value.

        Returns
        -------
        :
            ``True`` if the value was set to a different value and ``False`` otherwise.

        Raises
        ------
        RuntimeError
            If called on a read-only reactive value.
        """
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

        if isinstance(self._value, MISSING_TYPE) != isinstance(value, MISSING_TYPE):
            self._is_set_dependents.invalidate()

        self._value = value
        self._value_dependents.invalidate()
        return True

    def unset(self) -> None:
        """
        Unset the reactive value.

        Returns
        -------
        :
            ``True`` if the value was set prior to this unsetting.
        """
        self.set(MISSING)  # type: ignore

    def is_set(self) -> bool:
        """
        Check if the reactive value is set.

        Returns
        -------
        :
            ``True`` if the value is set, ``False`` otherwise.
        """

        self._is_set_dependents.register()
        return not isinstance(self._value, MISSING_TYPE)

    def freeze(self) -> None:
        """
        Freeze the reactive value.

        Freezing is equivalent to unsetting the value, but it does not invalidate
        dependents.
        """
        self._value = MISSING


# ==============================================================================
# Calc
# ==============================================================================

CalcFunction = Callable[[], T]
CalcFunctionAsync = Callable[[], Awaitable[T]]


class Calc_(Generic[T]):
    """
    Mark a function as a reactive calculation.

    Warning
    -------
    Most users shouldn't use this class directly to initialize a reactive calculation
    (instead, use the :func:`~shiny.reactive.Calc` decorator).
    """

    def __init__(
        self,
        fn: CalcFunction[T],
        *,
        session: "MISSING_TYPE | Session | None" = MISSING,
    ) -> None:
        self.__name__ = fn.__name__
        self.__doc__ = fn.__doc__

        # The CalcAsync subclass will pass in an async function, but it tells the
        # static type checker that it's synchronous. wrap_async() is smart -- if is
        # passed an async function, it will not change it.
        self._fn: CalcFunctionAsync[T] = _utils.wrap_async(fn)
        self._is_async: bool = _utils.is_async_callable(fn)

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
            from ..session import get_current_session

            # If no session is provided, autodetect the current session (this
            # could be None if outside of a session).
            session = get_current_session()
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

    # TODO: should this be private?
    async def get_value(self) -> T:
        self._dependents.register()

        if self._invalidated or self._running:
            await self.update_value()

        if self._error:
            raise self._error[0]

        return self._value[0]

    # TODO: should this be private?
    async def update_value(self) -> None:
        self._ctx = Context()
        self._most_recent_ctx_id = self._ctx.id

        self._ctx.on_invalidate(self._on_invalidate_cb)

        self._exec_count += 1
        self._invalidated = False

        was_running = self._running
        self._running = True

        from ..session import session_context

        with session_context(self._session):
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


class CalcAsync_(Calc_[T]):
    """
    Mark an async function as a reactive calculation.

    Warning
    -------
    Most users shouldn't use this class directly to initialize a reactive calculation
    (instead, use the :func:`~shiny.reactive.Calc` decorator).
    """

    def __init__(
        self,
        fn: CalcFunctionAsync[T],
        *,
        session: "MISSING_TYPE | Session | None" = MISSING,
    ) -> None:
        if not _utils.is_async_callable(fn):
            raise TypeError(self.__class__.__name__ + " requires an async function")

        super().__init__(cast(CalcFunction[T], fn), session=session)

    async def __call__(self) -> T:  # pyright: ignore[reportIncompatibleMethodOverride]
        return await self.get_value()


@overload
def Calc(fn: CalcFunctionAsync[T]) -> CalcAsync_[T]:
    ...


@overload
def Calc(fn: CalcFunction[T]) -> Calc_[T]:
    ...


# Note that the specified return type of this Calc() overload (with a `session`) isn't
# exactly the same as the actual returned object -- the specified return type is a
# Callable that takes a CalcFunction[T], and actual return type is a Callable that takes
# CalcFunction[T] | CalcFunctionAsync[T]. Both are technically correct, since the
# CalcFunction's T encompasses both "regular" types V as well as Awatiable[V]. (We're
# using V to represent a generic type that is NOT itself Awaitable.) So if the T
# represents an Awaitable[V], then the type checker knows that the returned function
# will return a Calc[Awaitable[V]].
#
# However, if the Calc() function is specified to return a Callable that takes
# CalcFunction[T] | CalcFunctionAsync[T], then if a CalcFunctionAsync is passed in, the
# type check will not know that the returned Calc object is a Calc[Awaitable[V]]. It
# will think that it's a [Calc[V]]. Then the type checker will think that the returned
# Calc object is not async when it actually is.
#
# To work around this, we say that Calc() returns a Callable that takes a
# CalcFunction[T], instead of the union type. We're sort of tricking the type checker
# twice: once here, and once when we return a Calc object (which has a synchronous
# __call__ method) or CalcAsync object (which has an async __call__ method), and it
# works out.
@overload
def Calc(
    *, session: "MISSING_TYPE | Session | None" = MISSING
) -> Callable[[CalcFunction[T]], Calc_[T]]:
    ...


@add_example()
def Calc(
    fn: Optional[CalcFunction[T] | CalcFunctionAsync[T]] = None,
    *,
    session: "MISSING_TYPE | Session | None" = MISSING,
) -> Calc_[T] | Callable[[CalcFunction[T]], Calc_[T]]:
    """
    Mark a function as a reactive calculation.

    A reactive calculation is a function whose return value depends solely on other
    reactive value(s) (i.e., :class:`~shiny.Inputs`, :class:`~shiny.reactive.Value`,
    and other reactive calculations). Whenever a reactive value changes, any reactive
    calculations that depend on it are "invalidated" and automatically re-execute when
    necessary. If a reactive calculation is marked as invalidated, any other reactive
    calculations that recently called it are also marked as invalidated. In this way,
    invalidations ripple through reactive calculations that depend on each other.

    Parameters
    ----------
    session
        A :class:`~shiny.Session` instance. If not provided, it is inferred via
        :func:`~shiny.session.get_current_session`.

    Returns
    -------
    :
        A decorator that marks a function as a reactive calculation.

    Tip
    ---
    Reactive calculations should not produce any side effects; to reactively produce
    side effects, use :func:`~shiny.reactive.Effect` instead.

    See Also
    --------
    ~shiny.Inputs
    ~shiny.reactive.Value
    ~shiny.reactive.Effect
    ~shiny.reactive.invalidate_later
    ~shiny.reactive.event
    """

    def create_calc(fn: CalcFunction[T] | CalcFunctionAsync[T]) -> Calc_[T]:
        if _utils.is_async_callable(fn):
            return CalcAsync_(fn, session=session)
        else:
            fn = cast(CalcFunction[T], fn)
            return Calc_(fn, session=session)

    if fn is None:
        return create_calc
    else:
        return create_calc(fn)


# ==============================================================================
# Effect
# ==============================================================================

EffectFunction = Callable[[], None]
EffectFunctionAsync = Callable[[], Awaitable[None]]


class Effect_:
    """
    Mark a function as a reactive side effect.

    Warning
    -------
    Most users shouldn't use this class directly to initialize a reactive side effect
    (instead, use the :func:`Effect` decorator).
    """

    def __init__(
        self,
        fn: EffectFunction | EffectFunctionAsync,
        *,
        suspended: bool = False,
        priority: int = 0,
        session: "MISSING_TYPE | Session | None" = MISSING,
    ) -> None:
        self.__name__ = fn.__name__
        self.__doc__ = fn.__doc__

        # The EffectAsync subclass will pass in an async function, but it tells the
        # static type checker that it's synchronous. wrap_async() is smart -- if is
        # passed an async function, it will not change it.
        self._fn: EffectFunctionAsync = _utils.wrap_async(fn)
        # This indicates whether the user's effect function (before wrapping) is async.
        self._is_async: bool = _utils.is_async_callable(fn)

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
            from ..session import get_current_session

            # If no session is provided, autodetect the current session (this
            # could be None if outside of a session).
            session = get_current_session()
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
                if self._session:
                    self._session._send_message_sync({"busy": "busy"})

            if self._suspended:
                self._on_resume = _continue
            else:
                _continue()

        async def on_flush_cb() -> None:
            if not self._destroyed:
                await self._run()
            if self._session:
                self._session._send_message_sync({"busy": "idle"})

        ctx.on_invalidate(on_invalidate_cb)
        ctx.on_flush(on_flush_cb)

        return ctx

    async def _run(self) -> None:
        ctx = self._create_context()
        self._exec_count += 1

        from ..session import session_context

        with session_context(self._session):
            try:
                with ctx():
                    await self._fn()
            except SilentException:
                # It's OK for SilentException to cause an Effect to stop running
                pass
            except Exception as e:
                traceback.print_exc()

                warnings.warn(
                    "Error in Effect: " + str(e), ReactiveWarning, stacklevel=2
                )
                if self._session:
                    await self._session._unhandled_error(e)

    def on_invalidate(self, callback: Callable[[], None]) -> None:
        """
        Register a callback that will be called when this reactive effect is
        invalidated.

        Parameters
        ----------
        callback
            A callback that will be called when this reactive effect is invalidated.
        """
        self._invalidate_callbacks.append(callback)

    def destroy(self) -> None:
        """
        Destroy this reactive effect.

        Stops the observer from executing ever again, even if it is currently scheduled
        for re-execution.
        """
        self._destroyed = True

        if self._ctx is not None:
            self._ctx.invalidate()

    def suspend(self) -> None:
        """
        Suspend the effect.

        Pauses scheduling of flushes (re-executions) in response to invalidations. If
        the effect was invalidated prior to this call but it has not re-executed yet
        (because it waits until on_flush is called) then that re-execution will still
        occur, because the flush is already scheduled.
        """
        self._suspended = True

    def resume(self) -> None:
        """
        Resume the effect.

        Causes this effect to start re-executing in response to invalidations. If the
        effect was invalidated while suspended, then it will schedule itself for
        re-execution (pending flush).
        """
        if self._suspended:
            self._suspended = False
            self._on_resume()
            self._on_resume = lambda: None

    def set_priority(self, priority: int = 0) -> None:
        """
        Control the execution priority for this effect.

        Parameters
        ----------
        priority
            The new priority. A higher value means higher priority: an effect with a
            higher priority value will execute before all effects with lower priority
            values. Positive, negative, and zero values are allowed.

        Note
        ----
        If the observer is currently invalidated, then the change in priority will not
        take effect until the next invalidation--unless the observer is also currently
        suspended, in which case the priority change will be effective upon resume.
        """
        self._priority = priority

    def _on_session_ended_cb(self) -> None:
        self.destroy()


@overload
def Effect(fn: EffectFunction | EffectFunctionAsync) -> Effect_:
    ...


@overload
def Effect(
    *,
    suspended: bool = False,
    priority: int = 0,
    session: "MISSING_TYPE | Session | None" = MISSING,
) -> Callable[[EffectFunction | EffectFunctionAsync], Effect_]:
    ...


@add_example()
def Effect(
    fn: Optional[EffectFunction | EffectFunctionAsync] = None,
    *,
    suspended: bool = False,
    priority: int = 0,
    session: "MISSING_TYPE | Session | None" = MISSING,
) -> Effect_ | Callable[[EffectFunction | EffectFunctionAsync], Effect_]:
    """
    Mark a function as a reactive side effect.

    A reactive effect is like a reactive calculation (:func:`~shiny.reactive.Calc`) in
    that it can read reactive values and call reactive calculations, and will
    automatically re-execute when those dependencies change. But unlike reactive
    calculations, it doesn't return a result and can't be used as an input to other
    reactive expressions. Thus, observers are only useful for their side effects (for
    example, performing I/O).

    Another contrast between reactive calculations and effects is their execution
    strategy. Reactive calculations use lazy evaluation; that is, when their
    dependencies change, they don't re-execute right away but rather wait until they are
    called by someone else. Indeed, if they are not called then they will never
    re-execute. In contrast, effects use eager evaluation; as soon as their dependencies
    change, they schedule themselves to re-execute.

    Parameters
    ----------
    suspended
        If ``TRUE``, start the effect in a suspended state (i.e., it will not execute
        until resumed and invalidated).
    priority
        The new priority. A higher value means higher priority: an effect with a higher
        priority value will execute before all effects with lower priority values.
        Positive, negative, and zero values are allowed.
    session
        A :class:`~shiny.Session` instance. If not provided, it is inferred via
        :func:`~shiny.session.get_current_session`.

    Returns
    -------
    :
        A decorator that marks a function as a reactive effect (:class:`Effect_`).

    See Also
    --------
    ~shiny.Inputs
    ~shiny.reactive.Value
    ~shiny.reactive.Effect
    ~shiny.reactive.invalidate_later
    ~shiny.reactive.event
    """

    def create_effect(fn: EffectFunction | EffectFunctionAsync) -> Effect_:
        fn = cast(EffectFunction, fn)
        return Effect_(fn, suspended=suspended, priority=priority, session=session)

    if fn is None:
        return create_effect
    else:
        return create_effect(fn)


# ==============================================================================
# event decorator
# ==============================================================================
@add_example()
def event(
    *args: Callable[[], object] | Callable[[], Awaitable[object]],
    ignore_none: bool = True,
    ignore_init: bool = False,
) -> Callable[[Callable[[], T]], Callable[[], T]]:
    """
    Mark a function to react only when an "event" occurs.

    Shiny's reactive programming framework is primarily designed for calculated values
    (:func:`~shiny.reactive.Calc`) and side-effect-causing actions
    (:func:`~shiny.reactive.Effect`) that respond to **any** of their inputs changing.
    That's often what is desired in Shiny apps, but not always: sometimes you want to
    wait for a specific action to be taken from the user, like clicking an
    :func:`~shiny.ui.input_action_button`, before calculating or taking an action. A
    reactive value (or function) which triggers other calculation or action in this way
    is called an event.

    These situations demand a more imperative, "event handling" style of programming,
    which ``@reactive.event()`` provides. It does this by using the
    :func:`~shiny.reactive.isolate` primitive under-the-hood to essentially "limit" the
    set of reactive dependencies to those in ``args``.

    Parameters
    ----------
    args
        One or more callables that represent the event; most likely this will be a
        reactive input value linked to a :func:`~shiny.ui.input_action_button` or
        similar (e.g., ``input.click``), but it can also be a (reactive or non-reactive)
        function that returns a value.
    ignore_none
        Whether to ignore the event if the value is ``None`` or ``0``.
    ignore_init
        If ``False``, the event trigger on the first run.

    Returns
    -------
    :
        A decorator that marks a function as an event handler.

    Tip
    ----
    This decorator must be applied before the relevant reactivity decorator (i.e.,
    ``@reactive.event`` must be applied before ``@reactive.Effect``, ``@reactive.Calc``,
    ``@render.ui``, etc).
    """

    if any([not callable(arg) for arg in args]):
        raise TypeError(
            "All objects passed to event decorator must be callable.\n"
            + "If you are calling `@reactive.event(f())`, try calling `@reactive.event(f)` instead."
        )

    if len(args) == 0:
        raise TypeError(
            "`@reactive.event()` requires at least one argument, as in `@reactive.event(input.x)`.\n"
        )

    def decorator(user_fn: Callable[[], T]) -> Callable[[], T]:
        if not callable(user_fn):
            raise TypeError(
                "`@reactive.event()` must be applied to a function or Callable object.\n"
                + "It should usually be applied before `@Calc`,` @Effect`, `@output`, or `@render.xx` function.\n"
                + "In other words, `@reactive.event()` goes below the other decorators."
            )

        if isinstance(user_fn, Calc_):
            raise TypeError(
                "`@reactive.event()` must be applied before `@reactive.Calc`.\n"
                + "In other words, `@reactive.Calc` must be above `@reactive.event()`."
            )

        if isinstance(user_fn, RenderFunction):
            # At some point in the future, we may allow this condition, if we find an
            # use case. For now we'll disallow it, for simplicity.
            raise TypeError(
                "`@reactive.event()` must be applied before `@render.xx` .\n"
                + "In other words, `@render.xx` must be above `@reactive.event()`."
            )

        initialized = False

        async def trigger() -> None:
            vals: list[object] = []
            for arg in args:
                if is_async_callable(arg):
                    v = await arg()
                else:
                    v = arg()
                vals.append(v)

            nonlocal initialized
            if ignore_init and not initialized:
                initialized = True
                req(False)
            if ignore_none and all(map(_is_none_event, vals)):
                req(False)

        if is_async_callable(user_fn):

            @functools.wraps(user_fn)
            # Impossible to specify a return type here; we know T is
            # Awaitable[something] but I don't think there's a way to refer to the
            # `something`
            async def new_user_async_fn():
                await trigger()
                with isolate():
                    return await user_fn()

            return new_user_async_fn  # type: ignore

        elif any([is_async_callable(arg) for arg in args]):
            raise TypeError(
                "When decorating a synchronous function with @reactive.event(), all"
                + "arguments to @reactive.event() must be synchronous functions."
            )

        else:

            @functools.wraps(user_fn)
            def new_user_fn() -> T:
                run_coro_sync(trigger())
                with isolate():
                    return user_fn()

            return new_user_fn

    return decorator


def _is_none_event(val: object) -> bool:
    return val is None or (isinstance(val, ActionButtonValue) and val == 0)


# The code below is a test that the type checker is correctly inferring types. It should
# have some type errors as indicated. There doesn't seem to be a good way to run pyright
# and expect errors. Until that's supported, the best thing to do is uncomment the code
# below and check that the errors are highlighted in red as expected. See:
# https://github.com/microsoft/pyright/discussions/2163

# # fmt: off
# def test_calc():
#     @Calc(session=MISSING)
#     async def fas() -> int:
#         return 1

#     @Calc(session=MISSING)
#     def fs() -> int:
#         return 1

#     @Calc
#     async def fa() -> int:
#         return 1

#     @Calc
#     def f() -> int:
#         return 1

#     def test():
#         await fas()  # Should error
#         await fs()   # Should error
#         await fa()   # Should error
#         await f()    # Should error

#         fas()        # Should error
#         fs()
#         fa()         # Should error
#         f()

#     async def test_async():
#         await fas()
#         await fs()   # Should error
#         await fa()
#         await f()    # Should error

#         fas()        # Should error
#         fs()
#         fa()         # Should error
#         f()

# # fmt: off
# def test_event():
#     @event()
#     async def fas() -> int:
#         return 1

#     @event()
#     def fs() -> int:
#         return 1

#     @event()
#     async def fa() -> int:
#         return 1

#     @event()
#     def f() -> int:
#         return 1

#     def test():
#         await fas()  # Should error
#         await fs()   # Should error
#         await fa()   # Should error
#         await f()    # Should error

#         fas()        # Should error
#         fs()
#         fa()         # Should error
#         f()

#     async def test_async():
#         await fas()
#         await fs()   # Should error
#         await fa()
#         await f()    # Should error

#         fas()        # Should error
#         fs()
#         fa()         # Should error
#         f()
