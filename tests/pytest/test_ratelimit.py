"""Tests for reactive.debounce() and reactive.throttle()."""

import warnings
from typing import Any, Callable, Tuple

import pytest
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from shiny import otel, render
from shiny.reactive import (
    Calc_,
    Value,
    calc,
    debounce,
    effect,
    event,
    flush,
    invalidate_later,
    isolate,
    throttle,
)

from .mocktime import MockTime
from .otel_helpers import get_exported_spans, patch_otel_tracing_state
from .test_poll import OnEndedSessionCallbacks


class RecordingSession(OnEndedSessionCallbacks):
    """Records the errors that would close a real session."""

    def __init__(self):
        super().__init__()
        self.unhandled_errors: list[Exception] = []

    async def _unhandled_error(self, e: Exception) -> None:
        self.unhandled_errors.append(e)


@pytest.mark.asyncio
@pytest.mark.parametrize("do_priming", [True, False])
async def test_debounce_and_throttle_timing(do_priming: bool):
    async with OnEndedSessionCallbacks():
        mock_time = MockTime()
        with mock_time():
            # The chatty source: changes every 0.3 seconds
            a = Value(0)

            @effect()
            def src():
                invalidate_later(0.3)
                with isolate():
                    a.set(a() + 1)

            @calc
            @debounce(0.5)
            def d() -> int:
                return a()

            @calc
            @throttle(0.5)
            def t() -> int:
                return a()

            d_fired = 0
            t_fired = 0

            @effect()
            def _():
                d()
                nonlocal d_fired
                d_fired += 1

            @effect()
            def _():
                t()
                nonlocal t_fired
                t_fired += 1

            # Reading the values before the first flush must not change the outcome
            if do_priming:
                with isolate():
                    assert d() == 0
                    assert t() == 0

            await flush()
            await mock_time.advance_time(1.3)
            await flush()

            # The source never paused long enough for the debounce to fire
            with isolate():
                assert a() == 5
                assert d_fired == 1
                assert d() == 0
            # The throttle fired at most once per 0.5 seconds
            with isolate():
                assert t_fired == 3
                assert t() == 4

            # Let the source go quiet
            src.destroy()
            await mock_time.advance_time(1)
            await flush()

            with isolate():
                assert d_fired == 2
                assert d() == a()
                assert t() == a()


@pytest.mark.asyncio
@pytest.mark.parametrize("limit", [debounce, throttle])
async def test_errors_reach_readers_only(limit: Callable[..., Any]):
    # An error in the source must not break the internal effects (which would close
    # the session); readers get it instead.
    session = RecordingSession()
    async with session:

        @calc
        @limit(1)
        def r() -> int:
            raise ValueError("boom")

        errors: list[Exception] = []

        @effect()
        def _():
            try:
                r()
            except ValueError as e:
                errors.append(e)

        await flush()
        assert [str(e) for e in errors] == ["boom"]
        assert session.unhandled_errors == []


@pytest.mark.asyncio
@pytest.mark.parametrize("limit", [debounce, throttle])
async def test_async_functions_and_effects(limit: Callable[..., Any]):
    async with OnEndedSessionCallbacks():
        mock_time = MockTime()
        with mock_time():
            a = Value(0)

            @calc
            @limit(1)
            async def r_async() -> int:
                return a()

            seen: list[int] = []

            # Like @reactive.event, it also works right under an effect
            @effect()
            @limit(1)
            async def _():
                seen.append(await r_async())

            await flush()
            with isolate():
                a.set(1)
            await flush()
            await mock_time.advance_time(1.1)
            await flush()
            assert seen[0] == 0
            assert seen[-1] == 1


@pytest.mark.parametrize("limit", [debounce, throttle])
def test_must_be_below_other_decorators(limit: Callable[..., Any]):
    name = limit.__name__

    with pytest.raises(
        TypeError, match=f"`@reactive.calc` must be above `@reactive.{name}"
    ):

        @limit(1)
        @calc
        def _():
            return 1

    with pytest.raises(
        TypeError, match=f"`@render.xx` must be above `@reactive.{name}"
    ):

        @limit(1)
        @render.text
        def _():
            return "x"

    with pytest.raises(
        TypeError, match=f"`@reactive.effect` must be above `@reactive.{name}"
    ):

        @limit(1)
        @effect
        def _():
            pass

    with pytest.raises(
        TypeError, match=f"`@reactive.{name}\\(\\)` must be applied to a function"
    ):
        limit(1)(1)

    with pytest.raises(TypeError, match=f"@reactive.{name} expected a function"):

        @limit(1)
        def _(x: int):
            return x


@pytest.mark.parametrize("limit", [debounce, throttle])
def test_default_params_warn_once_at_caller(limit: Callable[..., Any]):
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        @limit(1)
        def _(x: int = 1):
            return x

    assert len(w) == 1
    assert w[0].filename == __file__
    assert f"reactive.{limit.__name__}" in str(w[0].message)


@pytest.mark.asyncio
async def test_delay_can_be_a_function():
    async with OnEndedSessionCallbacks():
        mock_time = MockTime()
        with mock_time():
            a = Value(0)
            delay = Value(1.0)

            @calc
            @debounce(delay)
            def d() -> int:
                return a()

            @effect()
            def _():
                d()

            await flush()
            with isolate():
                delay.set(5.0)
                a.set(1)
            await flush()
            await mock_time.advance_time(1.1)
            with isolate():
                assert d() == 0
            await mock_time.advance_time(4)
            with isolate():
                assert d() == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", ["debounce", "throttle"])
async def test_otel_only_the_users_reactives_record_spans(
    kind: str,
    otel_tracer_provider: Tuple[TracerProvider, InMemorySpanExporter],
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv("SHINY_OTEL_COLLECT", "all")
    provider, exporter = otel_tracer_provider
    limit = debounce if kind == "debounce" else throttle

    with patch_otel_tracing_state(tracing_enabled=True):
        async with OnEndedSessionCallbacks():
            a = Value(0)

            @calc
            @limit(1)
            def limited() -> int:
                return a()

            @calc
            @limit(1)
            @event(a)
            def limited_event() -> int:
                return a()

            @calc
            @limit(1)
            @otel.suppress
            def quiet() -> int:
                return a()

            assert isinstance(limited, Calc_)
            assert limited._otel_label == f"reactive.calc {kind} limited"
            assert (
                limited_event._otel_label == f"reactive.calc {kind} event limited_event"
            )

            @effect()
            def reader():
                limited()
                limited_event()
                quiet()

            await flush()

    names = sorted(span.name for span in get_exported_spans(provider, exporter))
    # The hidden calcs and effects, and anything marked @otel.suppress, record none
    assert names == sorted(
        [
            f"reactive.calc {kind} limited",
            f"reactive.calc {kind} event limited_event",
            "reactive.effect reader",
        ]
    )
