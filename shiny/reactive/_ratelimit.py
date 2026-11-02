"""Slow down how often a reactive calc invalidates: debounce and throttle."""

from __future__ import annotations

__all__ = ("debounce", "throttle")

import functools
import time
from typing import TYPE_CHECKING, Any, Callable, Literal, Optional, TypeVar, cast

from .. import otel
from .._docstring import add_example
from ..otel._labels import set_otel_label_modifier
from ..types import MISSING, MISSING_TYPE
from ._core import invalidate_later, isolate
from ._reactives import Calc_, Value, calc, effect, event

if TYPE_CHECKING:
    from ..session import Session

T = TypeVar("T")


@add_example()
def debounce(
    delay_secs: float | Callable[[], float],
    *,
    priority: int = 100,
    session: MISSING_TYPE | Session | None = MISSING,
) -> Callable[[Callable[[], T]], Callable[[], T]]:
    """
    Wait for a reactive calculation to stop changing before invalidating its readers.

    Every time the decorated calculation invalidates, the timer starts over. Readers of
    the debounced calculation are invalidated only after `delay_secs` pass without
    another change. This is useful when only the final value matters (for example,
    while a user is typing) and the work that depends on it is slow.

    With a 3-unit window, where each character is one unit of time and `o` is an
    invalidation:

    ```
    source:    ooo-oo-oo----
    debounce:  -----------o-
    ```

    Parameters
    ----------
    delay_secs
        The number of seconds to wait after the last change. You may also pass a
        no-argument function or :func:`~shiny.reactive.calc` that returns the number of
        seconds, for example to let the user control the window.
    priority
        Debouncing is implemented with :func:`~shiny.reactive.effect`s. Use this
        argument to set their priority. It should be higher than the priority of the
        effects and outputs that read the debounced calculation (which default to 0).
    session
        A :class:`~shiny.Session` instance. If not provided, a session is inferred via
        :func:`~shiny.session.get_current_session`.

    Returns
    -------
    :
        A decorator for a no-argument function or :func:`~shiny.reactive.calc`
        (regular or async). The result is a :func:`~shiny.reactive.calc` that returns
        the decorated function's value but invalidates its readers only after the
        changes stop.

    Note
    ----
    The decorated function may still run as often as before (or more often). Only the
    invalidation of its readers is slowed down, so use this when the decorated function
    is cheap and the work downstream of it is expensive.

    Times are minimums: if the event loop is busy when the timer is due, the
    invalidation waits until it is free.

    See Also
    --------
    * :func:`~shiny.reactive.throttle`
    * :func:`~shiny.reactive.invalidate_later`
    """
    delay_fn = _as_delay_fn(delay_secs)

    def wrapper(fn: Callable[[], T]) -> Callable[[], T]:
        source = _as_calc(fn, session=session)

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

        result = _event_calc(fn, source, trigger, kind="debounce", session=session)

        async def prime():
            # Cache the result right away. Otherwise a first read that comes after
            # the source changed would return the new value without waiting.
            try:
                await _read_quietly(result)
            finally:
                primer.destroy()

        with otel.suppress():
            primer = effect(priority=priority, session=session)(prime)

        return cast(Callable[[], T], result)

    return wrapper


@add_example()
def throttle(
    delay_secs: float | Callable[[], float],
    *,
    priority: int = 100,
    session: MISSING_TYPE | Session | None = MISSING,
) -> Callable[[Callable[[], T]], Callable[[], T]]:
    """
    Invalidate the readers of a reactive calculation at most once per time window.

    When the decorated calculation invalidates, its readers are invalidated right away
    unless they were already invalidated in the last `delay_secs`. In that case they
    are invalidated once at the end of the window. Unlike
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
    delay_secs
        The minimum number of seconds between invalidations. You may also pass a
        no-argument function or :func:`~shiny.reactive.calc` that returns the number of
        seconds, for example to let the user control the window.
    priority
        Throttling is implemented with :func:`~shiny.reactive.effect`s. Use this
        argument to set their priority. It should be higher than the priority of the
        effects and outputs that read the throttled calculation (which default to 0).
    session
        A :class:`~shiny.Session` instance. If not provided, a session is inferred via
        :func:`~shiny.session.get_current_session`.

    Returns
    -------
    :
        A decorator for a no-argument function or :func:`~shiny.reactive.calc`
        (regular or async). The result is a :func:`~shiny.reactive.calc` that returns
        the decorated function's value but invalidates its readers at most once per
        `delay_secs`.

    Note
    ----
    The decorated function may still run as often as before (or more often). Only the
    invalidation of its readers is slowed down, so use this when the decorated function
    is cheap and the work downstream of it is expensive.

    Times are minimums: if the event loop is busy when the timer is due, the
    invalidation waits until it is free.

    See Also
    --------
    * :func:`~shiny.reactive.debounce`
    * :func:`~shiny.reactive.invalidate_later`
    """
    delay_fn = _as_delay_fn(delay_secs)

    def wrapper(fn: Callable[[], T]) -> Callable[[], T]:
        source = _as_calc(fn, session=session)

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

        result = _event_calc(fn, source, trigger, kind="throttle", session=session)
        return cast(Callable[[], T], result)

    return wrapper


def _as_delay_fn(delay_secs: float | Callable[[], float]) -> Callable[[], float]:
    if callable(delay_secs):
        return delay_secs
    return lambda: delay_secs


def _as_calc(
    fn: Callable[[], T], *, session: MISSING_TYPE | Session | None
) -> Calc_[T]:
    if isinstance(fn, Calc_):
        return cast(Calc_[T], fn)
    # A plain function gets a hidden calc, so the effects and the result share one run
    with otel.suppress():
        return calc(session=session)(fn)


async def _read_quietly(source: Calc_[Any]) -> None:
    """Read `source` to depend on it. Its errors are for its readers, not for us."""
    try:
        await source.get_value()
    except Exception:
        pass


def _event_calc(
    fn: Callable[[], T],
    source: Calc_[T],
    trigger: Value[int],
    *,
    kind: Literal["debounce", "throttle"],
    session: MISSING_TYPE | Session | None,
) -> Calc_[T]:
    """
    The calc users get: `source`'s value, but invalidated only by `trigger`.

    It is named after the user's function and is the only one of the reactives
    behind `kind` that records an OTel span, as `reactive.calc <kind> <name>`.
    """
    # Copy the name, source location, and `@otel.suppress` mark of the user's
    # function. A calc keeps it (wrapped) in `_fn`; copying the calc's own `__dict__`
    # would copy its state.
    user_fn: Callable[[], Any] = (
        cast(Calc_[Any], fn)._fn if isinstance(fn, Calc_) else fn
    )

    if source._is_async:

        @functools.wraps(user_fn)
        async def read_async():
            return await source.get_value()

        read = cast(Callable[[], T], read_async)
    else:

        @functools.wraps(user_fn)
        def read_sync() -> T:
            return source()

        read = read_sync

    read = event(trigger, ignore_none=False)(read)
    set_otel_label_modifier(read, kind, mode="replace")
    return calc(session=session)(read)
