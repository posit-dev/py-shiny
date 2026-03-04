"""
User-facing decorator and context manager for OpenTelemetry collection suppression.
"""

from __future__ import annotations

from contextvars import Token
from typing import Any, Callable, TypeVar, overload

from ._collect import OtelCollectLevel, _current_collect_level
from ._function_attrs import set_otel_collect_level_on_func

__all__ = ("suppress",)

T = TypeVar("T", bound=Callable[..., Any])


class _SuppressContext:
    """Per-use context manager returned by suppress(). Owns its own Token."""

    def __init__(self) -> None:
        self._token: Token[OtelCollectLevel | None] | None = None

    def __enter__(self) -> None:
        self._token = _current_collect_level.set(OtelCollectLevel.NONE)
        return None

    def __exit__(self, *_: object) -> None:
        if self._token is not None:
            _current_collect_level.reset(self._token)
            self._token = None


class _Suppress:
    """
    Singleton that suppresses Shiny's internal OTel instrumentation.

    Use as a no-parens decorator or a parens context manager:

        @reactive.calc
        @otel.suppress
        def sensitive_calc(): ...

        with otel.suppress():
            @reactive.effect
            def my_effect(): ...
    """

    @overload
    def __call__(self, func: T) -> T: ...  # @otel.suppress

    @overload
    def __call__(self) -> _SuppressContext: ...  # with otel.suppress():

    def __call__(self, func: Any = None) -> Any:
        if func is None:
            return _SuppressContext()

        # Reject reactive objects — suppress must wrap the plain function.
        # These checks must come before the callable() check because some
        # reactive objects (e.g., Effect_) are not callable.
        from shiny.reactive._reactives import Calc_, Effect_
        from shiny.render.renderer import Renderer

        if isinstance(func, Calc_):
            raise TypeError(
                "otel.suppress cannot be used on @reactive.calc objects. "
                "Apply @otel.suppress before @reactive.calc:\n"
                "  @reactive.calc\n"
                "  @otel.suppress\n"
                "  def my_calc(): ..."
            )

        if isinstance(func, Effect_):
            raise TypeError(
                "otel.suppress cannot be used on @reactive.effect objects. "
                "Apply @otel.suppress before @reactive.effect:\n"
                "  @reactive.effect\n"
                "  @otel.suppress\n"
                "  def my_effect(): ..."
            )

        if isinstance(func, Renderer):
            raise TypeError(
                "otel.suppress cannot be used on render objects. "
                "Apply @otel.suppress before the @render.func decorator:\n"
                "  @render.text\n"
                "  @otel.suppress\n"
                "  def my_output(): ..."
            )

        if not callable(func):
            raise TypeError(
                f"otel.suppress received a non-callable argument: {type(func).__name__!r}. "
                f"Use @otel.suppress (no parens) as a decorator, "
                f"or otel.suppress() (with parens) as a context manager."
            )

        set_otel_collect_level_on_func(func, OtelCollectLevel.NONE)
        return func


suppress = _Suppress()
"""
Suppress Shiny's internal OTel instrumentation for a function or block.

Use as a no-parens decorator:

    @reactive.calc
    @otel.suppress
    def sensitive_calc(): ...

Use as a context manager (parens required):

    with otel.suppress():
        @reactive.effect
        def my_effect(): ...

Note: This only affects spans created by Shiny itself. Your own custom
OpenTelemetry spans are unaffected.
"""


def _no_collect() -> _SuppressContext:
    """Internal helper used by Shiny's own reactive objects. Not public API."""
    return _SuppressContext()
