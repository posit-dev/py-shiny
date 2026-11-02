"""Tests for reactive.debounce() and reactive.throttle()."""

from typing import Any, Callable, Tuple

import pytest
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from shiny import otel
from shiny.reactive import (
    Calc_,
    Value,
    calc,
    debounce,
    effect,
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

            @debounce(0.5)
            @calc
            def d() -> int:
                return a()

            @throttle(0.5)
            @calc
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

        @limit(1)
        @calc
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
async def test_async_and_plain_functions(limit: Callable[..., Any]):
    async with OnEndedSessionCallbacks():
        mock_time = MockTime()
        with mock_time():
            a = Value(0)

            @limit(1)
            async def r_async() -> int:
                return a()

            @limit(1)
            def r_plain() -> int:
                return a()

            assert isinstance(r_async, Calc_)
            assert isinstance(r_plain, Calc_)

            seen: list[Tuple[int, int]] = []

            @effect()
            async def _():
                seen.append((await r_async(), r_plain()))

            await flush()
            with isolate():
                a.set(1)
            await flush()
            await mock_time.advance_time(1.1)
            await flush()
            assert seen[0] == (0, 0)
            assert seen[-1] == (1, 1)


@pytest.mark.asyncio
async def test_delay_can_be_a_function():
    async with OnEndedSessionCallbacks():
        mock_time = MockTime()
        with mock_time():
            a = Value(0)
            delay = Value(1.0)

            @debounce(delay)
            @calc
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
async def test_otel_only_the_result_calc_records_a_span(
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

            @limit(1)
            @calc
            def source_calc() -> int:
                return a()

            @limit(1)
            def plain_fn() -> int:
                return a()

            @limit(1)
            @calc
            @otel.suppress
            def quiet_calc() -> int:
                return a()

            assert isinstance(source_calc, Calc_)
            assert source_calc._otel_label == f"reactive.calc {kind} source_calc"

            @effect()
            def reader():
                source_calc()
                plain_fn()
                quiet_calc()

            await flush()

    names = sorted(span.name for span in get_exported_spans(provider, exporter))
    # The user's own calc keeps its span; the hidden calc around a plain function,
    # the internal effects, and anything marked @otel.suppress record none.
    assert names == sorted(
        [
            "reactive.calc source_calc",
            f"reactive.calc {kind} source_calc",
            f"reactive.calc {kind} plain_fn",
            "reactive.effect reader",
        ]
    )
