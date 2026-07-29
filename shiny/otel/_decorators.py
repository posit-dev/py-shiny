"""
User-facing OpenTelemetry collection control APIs (``suppress`` and ``collect``)
usable as decorators or context managers.
"""

from __future__ import annotations

from contextvars import Token
from typing import Any, Callable, TypeVar, overload

from ._collect import OtelCollectLevel, _current_collect_level
from ._function_attrs import set_otel_collect_level_on_func

__all__ = ("collect", "suppress")

T = TypeVar("T", bound=Callable[..., Any])


class _OtelContext:
    """Per-use context manager returned by suppress() or collect(). Owns its own Token."""

    def __init__(self, level: OtelCollectLevel) -> None:
        self._level = level
        self._token: Token[OtelCollectLevel | None] | None = None

    def __enter__(self) -> None:
        self._token = _current_collect_level.set(self._level)
        return None

    def __exit__(self, *_: object) -> None:
        if self._token is not None:
            _current_collect_level.reset(self._token)
            self._token = None


def _stamp_or_raise(func: Any, level: OtelCollectLevel, name: str) -> Any:
    """Validate func and stamp it with level, or raise a descriptive TypeError."""
    # Reject reactive objects — decorator must wrap the plain function.
    # These checks must come before the callable() check because some
    # reactive objects (e.g., Effect_) are not callable.
    from shiny.reactive._reactives import Calc_, Effect_
    from shiny.render.renderer import Renderer

    if isinstance(func, Calc_):
        raise TypeError(
            f"otel.{name} cannot be used on @reactive.calc objects. "
            f"Apply @otel.{name} before @reactive.calc:\n"
            f"  @reactive.calc\n"
            f"  @otel.{name}\n"
            f"  def my_calc(): ..."
        )

    if isinstance(func, Effect_):
        raise TypeError(
            f"otel.{name} cannot be used on @reactive.effect objects. "
            f"Apply @otel.{name} before @reactive.effect:\n"
            f"  @reactive.effect\n"
            f"  @otel.{name}\n"
            f"  def my_effect(): ..."
        )

    if isinstance(func, Renderer):
        raise TypeError(
            f"otel.{name} cannot be used on render objects. "
            f"Apply @otel.{name} before the @render.func decorator:\n"
            f"  @render.text\n"
            f"  @otel.{name}\n"
            f"  def my_output(): ..."
        )

    if not callable(func):
        raise TypeError(
            f"otel.{name} received a non-callable argument: {type(func).__name__!r}. "
            f"Use @otel.{name} (no parens) as a decorator, "
            f"or otel.{name}() (with parens) as a context manager."
        )

    set_otel_collect_level_on_func(func, level)
    return func


@overload
def suppress(func: T) -> T: ...  # @otel.suppress


@overload
def suppress() -> _OtelContext: ...  # with otel.suppress():


def suppress(func: Any = None) -> Any:
    """
    Disable Shiny's internal OTel instrumentation for a function or block.

    Serves a dual purpose depending on how it is called:

    - **As a no-parens decorator** (``@otel.suppress``): Stamps the plain function
      with ``OtelCollectLevel.NONE`` at definition time. Reactive objects created
      from the function will not emit Shiny internal spans or logs.
    - **As a context manager** (``with otel.suppress():``): Sets the collection
      level to ``NONE`` for the duration of the block. Reactive objects *created*
      inside the block capture ``NONE`` as their level.

    Parameters
    ----------
    func
        The plain function to suppress. Only provided when used as a decorator
        (``@otel.suppress``, no parens). Must be a plain callable — passing a
        ``reactive.calc``, ``reactive.effect``, or renderer object raises
        ``TypeError`` with instructions for the correct decorator ordering.

    Returns
    -------
    :
        When used as a decorator: the original function, unchanged except for
        the ``_shiny_otel_collect_level`` attribute being set.
        When used as a context manager: an ``_OtelContext`` instance whose
        ``__exit__`` restores the previous level via ``ContextVar.reset``.

    Raises
    ------
    TypeError
        If applied to a ``reactive.calc``, ``reactive.effect``, or renderer
        object (``@otel.suppress`` must come before those decorators), or to
        any non-callable.

    Note
    ----
    Only affects spans and logs created by Shiny itself (reactive calculations and value
    updates). User-defined OpenTelemetry spans are unaffected.

    Collection level is captured at **initialization time** for reactive
    objects — when ``reactive.calc``, ``reactive.effect``, or
    ``reactive.value`` is instantiated. Changing the context variable after
    initialization has no effect on already-created reactive objects.

    Both ``otel.suppress`` and ``otel.collect`` are backed by a
    ``ContextVar`` and are async-safe: concurrent tasks each see their own
    level independently.

    Examples
    --------
    **Decorator (no parens):**

    ```python
    from shiny import reactive, otel

    @reactive.calc
    @otel.suppress
    def sensitive_calc():
        return load_api_key()
    ```

    **Context manager (parens required):**

    ```python
    from shiny import reactive, otel

    with otel.suppress():
        private_counter = reactive.value(0)

        @reactive.calc
        def private_calc():
            return private_counter() * 2
    ```

    **Nested with** ``otel.collect`` **to re-enable for one object:**

    ```python
    from shiny import reactive, otel

    with otel.suppress():
        @reactive.calc
        def private_calc():  # suppressed
            return load_private_data()

        with otel.collect():
            @reactive.calc
            def public_calc():  # re-enabled
                return load_public_data()
    ```

    See Also
    --------
    * :func:`~shiny.otel.collect` - Re-enable Shiny's internal telemetry when the default has been lowered
    * :func:`~shiny.otel.get_level` - Inspect the current collection level
    """
    if func is None:
        return _OtelContext(OtelCollectLevel.NONE)
    return _stamp_or_raise(func, OtelCollectLevel.NONE, "suppress")


@overload
def collect(func: T) -> T: ...  # @otel.collect


@overload
def collect() -> _OtelContext: ...  # with otel.collect():


def collect(func: Any = None) -> Any:
    """
    Enable Shiny's internal OTel instrumentation for a function or block.

    Counterpart to :func:`~shiny.otel.suppress`. Useful when the global default
    has been lowered via ``SHINY_OTEL_COLLECT`` or when inside a
    ``with otel.suppress():`` block and a specific reactive object needs
    telemetry re-enabled.

    Serves a dual purpose depending on how it is called:

    - **As a no-parens decorator** (``@otel.collect``): Stamps the plain
      function with ``OtelCollectLevel.ALL`` at definition time. Reactive
      objects created from the function will emit Shiny internal spans and
      logs regardless of the surrounding context.
    - **As a context manager** (``with otel.collect():``): Sets the
      collection level to ``ALL`` for the duration of the block. Reactive
      objects *created* inside the block capture ``ALL`` as their level.

    Parameters
    ----------
    func
        The plain function to enable collection for. Only provided when used
        as a decorator (``@otel.collect``, no parens). Must be a plain
        callable — passing a ``reactive.calc``, ``reactive.effect``, or
        renderer object raises ``TypeError`` with instructions for the
        correct decorator ordering.

    Returns
    -------
    :
        When used as a decorator: the original function, unchanged except for
        the ``_shiny_otel_collect_level`` attribute being set.
        When used as a context manager: an ``_OtelContext`` instance whose
        ``__exit__`` restores the previous level via ``ContextVar.reset``.

    Raises
    ------
    TypeError
        If applied to a ``reactive.calc``, ``reactive.effect``, or renderer
        object (``@otel.collect`` must come before those decorators), or to
        any non-callable.

    Note
    ----
    Only affects spans and logs created by Shiny itself. User-defined
    OpenTelemetry spans are unaffected.

    Collection level is captured at **initialization time** for reactive
    objects. ``otel.collect`` overrides the surrounding context level —
    including a ``SHINY_OTEL_COLLECT=none`` environment variable — for
    reactive objects created within its scope.

    Both ``otel.collect`` and ``otel.suppress`` are backed by a
    ``ContextVar`` and are async-safe: concurrent tasks each see their own
    level independently.

    Examples
    --------
    **Decorator (no parens) — override a low global default:**

    ```python
    from shiny import reactive, otel

    # Even with SHINY_OTEL_COLLECT=none, this calc is always instrumented
    @reactive.calc
    @otel.collect
    def public_calc():
        return load_public_data()
    ```

    **Context manager — re-enable within a suppress block:**

    ```python
    from shiny import reactive, otel

    with otel.suppress():
        @reactive.calc
        def private_calc():
            return load_private_data()   # suppressed

        with otel.collect():
            @reactive.calc
            def public_calc():
                return load_public_data()  # re-enabled
    ```

    See Also
    --------
    * :func:`~shiny.otel.suppress` - Disable Shiny's internal telemetry for sensitive operations
    * :func:`~shiny.otel.get_level` - Inspect the current collection level
    """
    if func is None:
        return _OtelContext(OtelCollectLevel.ALL)
    return _stamp_or_raise(func, OtelCollectLevel.ALL, "collect")
