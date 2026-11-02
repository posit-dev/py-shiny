"""Slow down how often a reactive function invalidates: debounce and throttle."""

from __future__ import annotations

__all__ = ("debounce", "throttle")

import functools
import time
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Literal,
    Optional,
    TypeVar,
    cast,
    overload,
)

from .. import _utils, otel
from .._docstring import add_example
from ..otel._labels import set_otel_label_modifier
from ..types import MISSING, MISSING_TYPE
from ._core import invalidate_later, isolate
from ._reactives import (
    FUNC_ATTR_RATE_LIMIT,
    Calc_,
    CalcAsync_,
    Effect_,
    Value,
    calc,
    effect,
    event,
    rate_limit_misuse_message,
)

if TYPE_CHECKING:
    from ..session import Session

T = TypeVar("T")


@overload
def debounce(
    delay_secs: float | Callable[[], float],
    /,
    *,
    priority: int = 100,
    session: MISSING_TYPE | Session | None = MISSING,
) -> Callable[[Callable[[], T]], Callable[[], T]]: ...


@overload
def debounce(
    fn: Callable[[], Awaitable[T]],
    delay_secs: float | Callable[[], float],
    /,
    *,
    priority: int = 100,
    session: MISSING_TYPE | Session | None = MISSING,
) -> CalcAsync_[T]: ...


@overload
def debounce(
    fn: Callable[[], T],
    delay_secs: float | Callable[[], float],
    /,
    *,
    priority: int = 100,
    session: MISSING_TYPE | Session | None = MISSING,
) -> Calc_[T]: ...


@add_example()
def debounce(
    fn: Any = MISSING,
    /,
    delay_secs: Any = MISSING,
    *,
    priority: int = 100,
    session: MISSING_TYPE | Session | None = MISSING,
) -> Any:
    """
    Wait for a reactive function to stop changing before invalidating its readers.

    Every time the decorated function's reactive dependencies change, the timer starts
    over. Readers are invalidated only after `delay_secs` pass without another change.
    This is useful when only the final value matters (for example, while a user is
    typing) and the work that depends on it is slow.

    With a 3-unit window, where each character is one unit of time and `o` is an
    invalidation:

    ```
    source:    ooo-oo-oo----
    debounce:  -----------o-
    ```

    Parameters
    ----------
    fn
        Only when called as ``debounce(fn, delay_secs)`` instead of as a decorator: the
        no-argument function to limit, such as a :func:`~shiny.reactive.calc` or an
        input (``input.text``).
    delay_secs
        The number of seconds to wait after the last change. You may also pass a
        synchronous no-argument function or :func:`~shiny.reactive.calc` that returns the
        number of seconds, for example to let the user control the window. It must
        always return a number. If it stops early (for example with
        :func:`~shiny.req`), the timer doesn't start, and readers aren't invalidated
        until it returns a number again. If it raises any other error, the session
        closes.
    priority
        Debouncing is implemented with :func:`~shiny.reactive.effect`s. Use this
        argument to set their priority. It should be higher than the priority of the
        effects and outputs that read the debounced function (which default to 0).
    session
        A :class:`~shiny.Session` instance. If not provided, a session is inferred via
        :func:`~shiny.session.get_current_session`.

    Returns
    -------
    :
        A decorator for a no-argument function (regular or async). The result returns
        the decorated function's value, but its readers are invalidated only after the
        changes stop.
        Called as ``(fn, delay_secs)``, it returns a :func:`~shiny.reactive.calc`
        that does the same for `fn`.

    Note
    ----
    The decorated function may still run as often as before (or more often). Only the
    invalidation of its readers is slowed down, so use this when the decorated function
    is cheap and the work downstream of it is expensive.

    Times are minimums: if the event loop is busy when the timer is due, the
    invalidation waits until it is free.

    Tip
    ---
    Like :func:`~shiny.reactive.event`, this decorator must be applied before
    ``@reactive.calc`` (i.e., ``@reactive.calc`` must be above it). It can't be used
    with ``@reactive.effect`` or ``@render.xx``, which have no value for readers to
    wait on: read the limited calc from them instead. An effect can react to it with
    ``@reactive.event(<calc>)``.

    To limit a function you already have, such as an existing calc or an input, call
    it as ``debounce(fn, delay_secs)``. That returns a calc, so there's no decorator to
    put in order.

    See Also
    --------
    * :func:`~shiny.reactive.throttle`
    * :func:`~shiny.reactive.invalidate_later`
    """
    return _decorator_or_calc(
        _debounce, fn, delay_secs, kind="debounce", priority=priority, session=session
    )


def _debounce(
    delay_secs: float | Callable[[], float],
    *,
    priority: int,
    session: MISSING_TYPE | Session | None,
) -> Callable[[Callable[[], T]], Callable[[], T]]:
    delay_fn = _as_delay_fn(delay_secs)

    def wrapper(fn: Callable[[], T]) -> Callable[[], T]:
        source = _source_calc(fn, kind="debounce", session=session)

        with otel.suppress():
            # Bumped to invalidate the result's readers
            trigger = Value(0)
            # When the timer fires; None if it isn't running
            deadline: Value[Optional[float]] = Value(None)
            first_run = True

            @effect(priority=priority, session=session)
            async def _tracker():
                nonlocal first_run
                await _read_quietly(source)
                if first_run:
                    # Only a change should start the timer
                    first_run = False
                    return
                # The value (or possibly the delay) changed. Start or reset the timer.
                deadline.set(time.monotonic() + delay_fn())

            @effect(priority=priority, session=session)
            def _timer():
                when = deadline()
                if when is None:
                    return
                now = time.monotonic()
                if now >= when:
                    with isolate():
                        trigger.set(trigger() + 1)
                    deadline.set(None)
                else:
                    invalidate_later(when - now)

        result = _result_calc(source, trigger, session=session)

        async def prime():
            # Cache the result right away. Otherwise a first read that comes after
            # the source changed would return the new value without waiting.
            try:
                await _read_quietly(result)
            finally:
                primer.destroy()

        with otel.suppress():
            primer = effect(priority=priority, session=session)(prime)

        return _user_reader(fn, result, kind="debounce")

    return wrapper


@overload
def throttle(
    delay_secs: float | Callable[[], float],
    /,
    *,
    priority: int = 100,
    session: MISSING_TYPE | Session | None = MISSING,
) -> Callable[[Callable[[], T]], Callable[[], T]]: ...


@overload
def throttle(
    fn: Callable[[], Awaitable[T]],
    delay_secs: float | Callable[[], float],
    /,
    *,
    priority: int = 100,
    session: MISSING_TYPE | Session | None = MISSING,
) -> CalcAsync_[T]: ...


@overload
def throttle(
    fn: Callable[[], T],
    delay_secs: float | Callable[[], float],
    /,
    *,
    priority: int = 100,
    session: MISSING_TYPE | Session | None = MISSING,
) -> Calc_[T]: ...


@add_example()
def throttle(
    fn: Any = MISSING,
    /,
    delay_secs: Any = MISSING,
    *,
    priority: int = 100,
    session: MISSING_TYPE | Session | None = MISSING,
) -> Any:
    """
    Invalidate the readers of a reactive function at most once per time window.

    When the decorated function's reactive dependencies change, its readers are
    invalidated right away unless they were already invalidated in the last
    `delay_secs`. In that case they are invalidated once at the end of the window. Unlike
    :func:`~shiny.reactive.debounce`, new changes don't restart the window, so a source
    that keeps changing still updates its readers regularly.

    With a 3-unit window, where each character is one unit of time and `o` is an
    invalidation:

    ```
    source:    ooo-oo-oo----
    throttle:  o--o--o--o---
    ```

    Parameters
    ----------
    fn
        Only when called as ``throttle(fn, delay_secs)`` instead of as a decorator: the
        no-argument function to limit, such as a :func:`~shiny.reactive.calc` or an
        input (``input.text``).
    delay_secs
        The minimum number of seconds between invalidations. You may also pass a
        synchronous no-argument function or :func:`~shiny.reactive.calc` that returns the
        number of seconds, for example to let the user control the window. It must
        always return a number. If it stops early (for example with
        :func:`~shiny.req`), the timer doesn't start, and readers aren't invalidated
        until it returns a number again. If it raises any other error, the session
        closes.
    priority
        Throttling is implemented with :func:`~shiny.reactive.effect`s. Use this
        argument to set their priority. It should be higher than the priority of the
        effects and outputs that read the throttled function (which default to 0).
    session
        A :class:`~shiny.Session` instance. If not provided, a session is inferred via
        :func:`~shiny.session.get_current_session`.

    Returns
    -------
    :
        A decorator for a no-argument function (regular or async). The result returns
        the decorated function's value, but its readers are invalidated at most once
        per `delay_secs`.
        Called as ``(fn, delay_secs)``, it returns a :func:`~shiny.reactive.calc`
        that does the same for `fn`.

    Note
    ----
    The decorated function may still run as often as before (or more often). Only the
    invalidation of its readers is slowed down, so use this when the decorated function
    is cheap and the work downstream of it is expensive.

    Times are minimums: if the event loop is busy when the timer is due, the
    invalidation waits until it is free.

    Tip
    ---
    Like :func:`~shiny.reactive.event`, this decorator must be applied before
    ``@reactive.calc`` (i.e., ``@reactive.calc`` must be above it). It can't be used
    with ``@reactive.effect`` or ``@render.xx``, which have no value for readers to
    wait on: read the limited calc from them instead. An effect can react to it with
    ``@reactive.event(<calc>)``.

    To limit a function you already have, such as an existing calc or an input, call
    it as ``throttle(fn, delay_secs)``. That returns a calc, so there's no decorator to
    put in order.

    See Also
    --------
    * :func:`~shiny.reactive.debounce`
    * :func:`~shiny.reactive.invalidate_later`
    """
    return _decorator_or_calc(
        _throttle, fn, delay_secs, kind="throttle", priority=priority, session=session
    )


def _throttle(
    delay_secs: float | Callable[[], float],
    *,
    priority: int,
    session: MISSING_TYPE | Session | None,
) -> Callable[[Callable[[], T]], Callable[[], T]]:
    delay_fn = _as_delay_fn(delay_secs)

    def wrapper(fn: Callable[[], T]) -> Callable[[], T]:
        source = _source_calc(fn, kind="throttle", session=session)

        with otel.suppress():
            # Bumped to invalidate the result's readers
            trigger = Value(0)
            # When the readers were last invalidated; None if never
            last_triggered_at: Value[Optional[float]] = Value(None)
            # Whether to invalidate the readers when the window ends
            pending = Value(False)

        def secs_left() -> float:
            last = last_triggered_at()
            if last is None:
                return 0
            return max(0, last + delay_fn() - time.monotonic())

        def fire() -> None:
            last_triggered_at.set(time.monotonic())
            with isolate():
                trigger.set(trigger() + 1)
            pending.set(False)

        with otel.suppress():

            @effect(priority=priority, session=session)
            async def _tracker():
                await _read_quietly(source)
                with isolate():
                    if pending():
                        # Already scheduled for the end of the window
                        return
                    if secs_left() > 0:
                        # First change in this window: fire when it ends
                        pending.set(True)
                    else:
                        fire()

            @effect(priority=priority, session=session)
            def _timer():
                if not pending():
                    return
                left = secs_left()
                if left > 0:
                    invalidate_later(left)
                else:
                    fire()

        result = _result_calc(source, trigger, session=session)
        return _user_reader(fn, result, kind="throttle")

    return wrapper


def _decorator_or_calc(
    limiter: Callable[..., Callable[[Callable[[], Any]], Callable[[], Any]]],
    fn: Any,
    delay_secs: Any,
    *,
    kind: Literal["debounce", "throttle"],
    priority: int,
    session: MISSING_TYPE | Session | None,
) -> Any:
    """
    Handle both ways to call `debounce`/`throttle`: `(delay_secs)` gives a decorator,
    and `(fn, delay_secs)` gives a calc.
    """
    if isinstance(fn, MISSING_TYPE):
        # Called as `(delay_secs=...)`
        return limiter(delay_secs, priority=priority, session=session)
    if isinstance(delay_secs, MISSING_TYPE):
        # Called as `(delay_secs)`; the one argument landed in `fn`
        return limiter(fn, priority=priority, session=session)

    # Called as `(fn, delay_secs)`. `fn` may be a calc here: there's no decorator to
    # put in the wrong order. Wrapping it in `_call` lets it past the decorator's
    # checks, and keeps `functools.wraps()` from copying a calc's attributes.
    _check_fn(fn, kind=kind, stacklevel=5)
    reader = limiter(delay_secs, priority=priority, session=session)(_call(fn))
    # `fn` records its own spans, if it's a calc
    with otel.suppress():
        return calc(session=session)(reader)


def _as_delay_fn(delay_secs: float | Callable[[], float]) -> Callable[[], float]:
    """Check `delay_secs`, then return a function that gives the delay in seconds."""
    if not callable(delay_secs):
        _check_delay(delay_secs)
        return lambda: delay_secs
    if _utils.is_async_callable(delay_secs):
        raise TypeError("`delay_secs` must be a number or a synchronous function.")
    delay_fn = delay_secs

    def checked_delay() -> float:
        return _check_delay(delay_fn())

    return checked_delay


def _check_delay(delay_secs: object) -> float:
    """Raise if `delay_secs` isn't a non-negative number of seconds."""
    if isinstance(delay_secs, bool) or not isinstance(delay_secs, (int, float)):
        raise TypeError(
            f"`delay_secs` must be a number of seconds, not {type(delay_secs).__name__}."
        )
    if delay_secs < 0:
        raise ValueError(f"`delay_secs` must be 0 or more, not {delay_secs}.")
    return delay_secs


def _source_calc(
    fn: Callable[[], T],
    *,
    kind: Literal["debounce", "throttle"],
    session: MISSING_TYPE | Session | None,
) -> Calc_[T]:
    """Check the decorated function, then wrap it in a hidden calc."""
    if isinstance(fn, Calc_):
        name = f"reactive.{kind}"
        raise TypeError(
            f"`@{name}()` must be applied before `@reactive.calc`.\n"
            + f"In other words, `@reactive.calc` must be above `@{name}()`."
        )

    _check_fn(fn, kind=kind, stacklevel=5)

    # The effects and the result share this calc's runs. It calls `fn` through
    # `_call`, so that the calc doesn't check (and warn about) `fn`'s parameters again.
    with otel.suppress():
        return calc(session=session)(_call(fn))


def _check_fn(
    fn: object, *, kind: Literal["debounce", "throttle"], stacklevel: int
) -> None:
    """Raise if `fn` isn't a no-argument function that may be limited."""
    name = f"reactive.{kind}"

    # This is here instead of at the top of the .py file in order to avoid a
    # circular dependency.
    from ..render.renderer import Renderer

    if isinstance(fn, Renderer):
        raise TypeError(rate_limit_misuse_message("render.xx", kind))
    if isinstance(fn, Effect_):
        raise TypeError(rate_limit_misuse_message("reactive.effect", kind))
    if not callable(fn):
        raise TypeError(f"`@{name}()` must be applied to a function.")

    _utils.validate_no_params(fn, name, stacklevel=stacklevel)


async def _read_quietly(source: Calc_[Any]) -> None:
    """Read `source` to depend on it. Its errors are for its readers, not for us."""
    try:
        await source.get_value()
    except Exception:
        pass


def _result_calc(
    source: Calc_[T],
    trigger: Value[int],
    *,
    session: MISSING_TYPE | Session | None,
) -> Calc_[T]:
    """A hidden calc with `source`'s value, invalidated only by `trigger`."""
    read = event(trigger, ignore_none=False)(_call(source))
    with otel.suppress():
        return calc(session=session)(read)


def _user_reader(
    fn: Callable[[], T],
    result: Calc_[T],
    *,
    kind: Literal["debounce", "throttle"],
) -> Callable[[], T]:
    """
    The function users get: it reads `result`, so its readers wait for `trigger`.

    It carries `fn`'s name, source location, and OTel marks, so a calc above it
    records its span as `reactive.calc <kind> <name>`.
    """
    read = functools.wraps(fn)(_call(result))
    set_otel_label_modifier(read, kind, mode="prepend")
    setattr(read, FUNC_ATTR_RATE_LIMIT, kind)
    return read


def _call(fn: Callable[[], T]) -> Callable[[], T]:
    """A new no-argument function that calls `fn`, async if `fn` is."""
    if _utils.is_async_callable(fn):

        async def call_async():
            return await fn()

        return cast(Callable[[], T], call_async)

    def call_sync() -> T:
        return fn()

    return call_sync
