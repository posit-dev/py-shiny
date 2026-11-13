"""Tests for reactive.debounce() and reactive.throttle()."""

import warnings
from typing import Any, Callable, Tuple

import numpy as np
import pytest
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from shiny import otel, render
from shiny.reactive import (
    Calc_,
    CalcAsync_,
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
        @limit(delay_secs=1)
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

            # An effect reacts to a limited calc through @reactive.event
            @effect()
            @event(r_async)
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


@pytest.mark.asyncio
@pytest.mark.parametrize("limit", [debounce, throttle])
async def test_function_form_returns_a_calc(limit: Callable[..., Any]):
    async with OnEndedSessionCallbacks():
        mock_time = MockTime()
        with mock_time():
            a = Value(0)

            @calc
            def doubled() -> int:
                return a() * 2

            @calc
            async def doubled_async() -> int:
                return a() * 2

            # An existing calc, an async calc, and a value
            from_calc: Calc_[int] = limit(doubled, 1)
            from_async: CalcAsync_[int] = limit(doubled_async, 1)
            from_value: Calc_[int] = limit(a, 1)
            assert isinstance(from_calc, Calc_)
            assert isinstance(from_async, CalcAsync_)

            seen: list[Tuple[int, int, int]] = []

            @effect()
            async def _():
                seen.append((from_calc(), await from_async(), from_value()))

            await flush()
            with isolate():
                a.set(1)
            await flush()
            if limit is debounce:
                # Still waiting for the changes to stop
                assert seen == [(0, 0, 0)]
            await mock_time.advance_time(1.1)
            await flush()
            assert seen[-1] == (2, 2, 1)


@pytest.mark.parametrize("limit", [debounce, throttle])
def test_function_form_checks_fn(limit: Callable[..., Any]):
    with pytest.raises(TypeError, match="must be applied to a function"):
        limit(1, 1)
    with pytest.raises(TypeError, match="`@reactive.effect` cannot"):
        plain_effect = effect(lambda: None)
        try:
            limit(plain_effect, 1)
        finally:
            plain_effect.destroy()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        limit(lambda x=1: x, 1)
    assert len(w) == 1
    assert w[0].filename == __file__


@pytest.mark.parametrize("limit", [debounce, throttle])
def test_must_be_below_calc(limit: Callable[..., Any]):
    name = limit.__name__

    with pytest.raises(
        TypeError, match=f"`@reactive.calc` must be above `@reactive.{name}"
    ):

        @limit(1)
        @calc
        def _():
            return 1

    with pytest.raises(
        TypeError, match=f"`@reactive.{name}\\(\\)` must be applied to a function"
    ):
        limit(1)(1)

    with pytest.raises(TypeError, match=f"@reactive.{name} expected a function"):

        @limit(1)
        def _(x: int):
            return x


@pytest.mark.parametrize("limit", [debounce, throttle])
def test_effects_and_outputs_reject_it(limit: Callable[..., Any]):
    # Effects and outputs have no value for readers to wait on, in either order
    def limited():
        return limit(1)(lambda: 1)

    hint = "read that calc from"
    with pytest.raises(TypeError, match=f"(?s)`@reactive.effect` cannot .* {hint}"):
        effect(limited())
    with pytest.raises(TypeError, match=f"(?s)`@reactive.effect` cannot .* {hint}"):
        effect(event(lambda: 1)(limited()))
    with pytest.raises(TypeError, match=f"(?s)`@render.text` cannot .* {hint}"):
        render.text(limited())
    with pytest.raises(
        TypeError, match=f"(?s)`@render.download_button` cannot .* {hint}"
    ):
        render.download_button(limited())

    plain_effect = effect(lambda: None)
    with pytest.raises(TypeError, match=f"(?s)`@reactive.effect` cannot .* {hint}"):
        limit(1)(plain_effect)
    # Otherwise it would run (and record a span) in a later test's flush
    plain_effect.destroy()
    with pytest.raises(TypeError, match=f"(?s)`@render.xx` cannot .* {hint}"):
        limit(1)(render.text(lambda: "x"))


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


@pytest.mark.parametrize("limit", [debounce, throttle])
def test_bad_delay_is_rejected(limit: Callable[..., Any]):
    async def async_delay() -> float:
        return 1

    for bad in [None, "1", True, async_delay]:
        with pytest.raises(TypeError, match="delay_secs"):
            limit(bad)
    for bad in [-1, float("nan")]:
        with pytest.raises(ValueError, match="delay_secs"):
            limit(bad)
    # numpy numbers are fine
    limit(np.int64(1))
    limit(np.float32(0.5))


@pytest.mark.parametrize("limit", [debounce, throttle])
def test_missing_delay_is_reported(limit: Callable[..., Any]):
    hint = f"`@reactive.{limit.__name__}` must be given a delay"

    def f() -> int:
        return 1

    with pytest.raises(TypeError, match=hint):
        calc(limit(f))
    with pytest.raises(TypeError, match=hint):
        effect(limit(f))
    with pytest.raises(TypeError, match=hint):
        render.text(limit(f))


@pytest.mark.asyncio
@pytest.mark.parametrize("limit", [debounce, throttle])
@pytest.mark.parametrize("bad_delay", ["1", float("nan")])
async def test_bad_delay_function_value_is_reported(
    limit: Callable[..., Any], bad_delay: Any
):
    session = RecordingSession()
    async with session:
        a = Value(0)

        @calc
        @limit(lambda: bad_delay)
        def d() -> int:
            return a()

        @effect()
        def _():
            d()

        await flush()
        a.set(1)
        await flush()
        messages = [str(e) for e in session.unhandled_errors]
        assert any("delay_secs" in m for m in messages)


@pytest.mark.asyncio
@pytest.mark.parametrize("limit", [debounce, throttle])
async def test_delay_change_moves_an_open_window(limit: Callable[..., Any]):
    async with OnEndedSessionCallbacks():
        mock_time = MockTime()
        with mock_time():
            a = Value(0)
            delay = Value(1.0)

            @calc
            @limit(delay)
            def r() -> int:
                return a()

            @effect()
            def _():
                r()

            await flush()
            # Debounce: the timer starts. Throttle: it fired at creation, so the
            # change waits for the window to end.
            with isolate():
                a.set(1)
            await flush()
            await mock_time.advance_time(0.5)
            with isolate():
                delay.set(3.0)
            await flush()
            await mock_time.advance_time(0.6)
            with isolate():
                assert r() == 0
            await mock_time.advance_time(2.5)
            with isolate():
                assert r() == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("limit", [debounce, throttle])
async def test_session_end_stops_a_pending_timer(limit: Callable[..., Any]):
    mock_time = MockTime()
    with mock_time():
        async with OnEndedSessionCallbacks():
            a = Value(0)

            @calc
            @limit(1)
            def r() -> int:
                return a()

            @effect()
            def _():
                r()

            await flush()
            with isolate():
                a.set(1)
            await flush()

        # The session ended with the timer pending, so it must not fire
        await mock_time.advance_time(2)
        await flush()
        with isolate():
            assert r() == 0


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
