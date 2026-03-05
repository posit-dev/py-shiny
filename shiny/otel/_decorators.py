"""
User-facing decorator and context manager for OpenTelemetry collection control.
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

    Use as a no-parens decorator:

        @reactive.calc
        @otel.suppress
        def sensitive_calc(): ...

    Use as a context manager (parens required):

        with otel.suppress():
            @reactive.effect
            def my_effect(): ...

    Note: This only affects spans and logs created by Shiny itself. Your own custom
    OpenTelemetry spans and logs are unaffected.
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

    Use as a no-parens decorator:

        @reactive.calc
        @otel.collect
        def instrumented_calc(): ...

    Use as a context manager (parens required):

        with otel.collect():
            @reactive.effect
            def my_effect(): ...

    Note: This only affects Shiny's internal spans and logs. Your own custom
    OpenTelemetry spans and logs are unaffected.
    """
    if func is None:
        return _OtelContext(OtelCollectLevel.ALL)
    return _stamp_or_raise(func, OtelCollectLevel.ALL, "collect")
