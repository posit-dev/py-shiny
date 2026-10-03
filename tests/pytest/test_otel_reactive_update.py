"""
`reactive_update` spans follow each session's cycle, as in Shiny for R.

A session's `reactive_update` span starts when the session turns busy and ends when
all of its effects have finished. It carries the session's `session.id`, and the
session's effect, output, and calc spans are its children. (A reactive flush is
global and can serve several sessions, so it can't carry a single `session.id`.)
"""

from __future__ import annotations

import asyncio
import json
import os
from typing import Callable, Iterator, Sequence, Tuple
from unittest.mock import patch

import pytest
from opentelemetry.sdk.trace import ReadableSpan, TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from shiny._connection import MockConnection
from shiny.otel._constants import ATTR_SESSION_ID

from .otel_helpers import get_exported_spans, patch_otel_tracing_state

TIMEOUT = 1.0
Spans = Tuple[TracerProvider, InMemorySpanExporter]


async def wait_until(cond: Callable[[], bool], timeout: float = TIMEOUT) -> bool:
    async def poll() -> None:
        while not cond():
            await asyncio.sleep(0.01)

    try:
        await asyncio.wait_for(poll(), timeout)
    except asyncio.TimeoutError:
        return False
    return True


class Client:
    def __init__(self, server: Callable[[Inputs, Outputs, Session], None]) -> None:
        self.conn = MockConnection()
        self.session = App(ui.TagList(), server)._create_session(self.conn)
        self.task = asyncio.create_task(self.session._run())

    def send(self, msg: dict[str, object]) -> None:
        self.conn.cause_receive(json.dumps(msg))

    async def idle(self) -> None:
        assert await wait_until(lambda: self.session._flush_enabled)
        assert await wait_until(lambda: self.session._busy_count == 0)

    async def close(self) -> None:
        self.conn.cause_disconnect()
        await asyncio.wait_for(self.task, TIMEOUT)


@pytest.fixture
def collect_all() -> Iterator[None]:
    with patch_otel_tracing_state(tracing_enabled=True):
        with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": "all"}):
            yield


def of_sessions(spans: Sequence[ReadableSpan], *clients: Client) -> list[ReadableSpan]:
    """Spans of these clients' sessions (other tests' sessions may still export)."""
    ids = {c.session.id for c in clients}
    return [
        s for s in spans if s.attributes and s.attributes.get(ATTR_SESSION_ID) in ids
    ]


def named(spans: Sequence[ReadableSpan], name: str) -> list[ReadableSpan]:
    return [s for s in spans if s.name == name]


def parent_of(span: ReadableSpan, spans: Sequence[ReadableSpan]) -> ReadableSpan | None:
    parent = span.parent
    if parent is None:
        return None
    return next(
        s
        for s in spans
        if s.context is not None and s.context.span_id == parent.span_id
    )


@pytest.mark.asyncio
async def test_effect_spans_are_children_of_their_sessions_reactive_update(
    otel_tracer_provider: Spans, collect_all: None
):
    provider, exporter = otel_tracer_provider

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        @reactive.calc
        def doubled():
            return input.x() * 2

        @reactive.effect
        def _show():
            _ = doubled()

    c = Client(server)
    c.send({"method": "init", "data": {"x": 1}})
    await c.idle()
    await c.close()

    spans = of_sessions(get_exported_spans(provider, exporter), c)
    (update,) = named(spans, "reactive_update")
    assert update.attributes is not None
    assert update.attributes[ATTR_SESSION_ID] == c.session.id
    (effect,) = [s for s in spans if s.name.startswith("reactive.effect")]
    assert parent_of(effect, spans) is update
    (calc,) = [s for s in spans if s.name.startswith("reactive.calc")]
    assert parent_of(calc, spans) is effect
    # The first cycle starts while the server function runs, in `session_start`.
    (start,) = named(spans, "session_start")
    assert parent_of(update, spans) is start


@pytest.mark.asyncio
async def test_each_session_gets_its_own_reactive_update_in_a_shared_flush(
    otel_tracer_provider: Spans, collect_all: None
):
    provider, exporter = otel_tracer_provider
    shared = reactive.value(0)

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        @reactive.effect
        @reactive.event(shared, ignore_init=True)
        def _react():
            pass

    a, b = Client(server), Client(server)
    for c in (a, b):
        c.send({"method": "init", "data": {}})
        await c.idle()
    exporter.clear()

    shared.set(1)  # one flush runs both sessions' effects
    await asyncio.wait_for(reactive.flush(), TIMEOUT)
    await a.close()
    await b.close()

    spans = of_sessions(get_exported_spans(provider, exporter), a, b)
    updates = named(spans, "reactive_update")
    session_ids = {(u.attributes or {}).get(ATTR_SESSION_ID) for u in updates}
    assert session_ids == {a.session.id, b.session.id}
    effects = [s for s in spans if s.name.startswith("reactive.effect")]
    assert len(effects) == 2
    assert {parent_of(e, spans) for e in effects} == set(updates)


@pytest.mark.asyncio
async def test_reactive_update_lasts_until_the_sessions_async_effects_finish(
    otel_tracer_provider: Spans, collect_all: None
):
    provider, exporter = otel_tracer_provider
    release = asyncio.Event()

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        @reactive.effect
        async def _slow():
            await release.wait()

    c = Client(server)
    c.send({"method": "init", "data": {}})
    assert await wait_until(lambda: c.session._busy_count == 1)
    await asyncio.sleep(0.02)
    assert (
        named(of_sessions(get_exported_spans(provider, exporter), c), "reactive_update")
        == []
    )
    release.set()
    await c.idle()

    spans = of_sessions(get_exported_spans(provider, exporter), c)
    (update,) = named(spans, "reactive_update")
    (effect,) = [s for s in spans if s.name.startswith("reactive.effect")]
    assert parent_of(effect, spans) is update
    assert update.end_time is not None and effect.end_time is not None
    assert update.end_time >= effect.end_time
    await c.close()


@pytest.mark.asyncio
async def test_one_reactive_update_per_cycle(
    otel_tracer_provider: Spans, collect_all: None
):
    provider, exporter = otel_tracer_provider

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        @render.text
        def out():
            return str(input.x())

    c = Client(server)
    c.send({"method": "init", "data": {"x": 0, ".clientdata_output_out_hidden": False}})
    await c.idle()
    for x in (1, 2):
        c.send({"method": "update", "data": {"x": x}})
        assert await wait_until(
            lambda x=x: len(
                named(
                    of_sessions(get_exported_spans(provider, exporter), c), "output out"
                )
            )
            == x + 1
        )
        await c.idle()
    await c.close()

    spans = of_sessions(get_exported_spans(provider, exporter), c)
    updates = named(spans, "reactive_update")
    outputs = named(spans, "output out")
    assert len(outputs) == 3
    # One cycle each: the first, then one per input update, in their own traces.
    assert {parent_of(o, spans) for o in outputs} == set(updates)
    assert len(updates) == 3
    assert all(parent_of(u, spans) is None for u in updates[1:])


@pytest.mark.asyncio
async def test_effect_without_a_session_has_no_reactive_update(
    otel_tracer_provider: Spans, collect_all: None
):
    provider, exporter = otel_tracer_provider

    @reactive.effect
    def _no_session():
        pass

    await asyncio.wait_for(reactive.flush(), TIMEOUT)
    _no_session.destroy()

    spans = get_exported_spans(provider, exporter)
    (effect,) = [s for s in spans if s.name == "reactive.effect _no_session"]
    assert effect.parent is None  # a root span, not under any reactive_update


@pytest.mark.asyncio
async def test_session_ending_mid_cycle_ends_its_reactive_update(
    otel_tracer_provider: Spans, collect_all: None
):
    provider, exporter = otel_tracer_provider
    release = asyncio.Event()

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        @reactive.effect
        async def _slow():
            await release.wait()

    c = Client(server)
    c.send({"method": "init", "data": {}})
    assert await wait_until(lambda: c.session._busy_count == 1)
    await c.close()
    release.set()

    assert await wait_until(
        lambda: len(
            named(
                of_sessions(get_exported_spans(provider, exporter), c),
                "reactive_update",
            )
        )
        == 1
    )


@pytest.mark.parametrize(
    "level, expect_update, expect_effect",
    [("session", False, False), ("reactive_update", True, False), ("all", True, True)],
)
@pytest.mark.asyncio
async def test_reactive_update_follows_the_collection_level(
    otel_tracer_provider: Spans, level: str, expect_update: bool, expect_effect: bool
):
    provider, exporter = otel_tracer_provider

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        @reactive.effect
        def _e():
            pass

    with patch_otel_tracing_state(tracing_enabled=True):
        with patch.dict(os.environ, {"SHINY_OTEL_COLLECT": level}):
            c = Client(server)
            c.send({"method": "init", "data": {}})
            await c.idle()
            await c.close()

    spans = of_sessions(get_exported_spans(provider, exporter), c)
    assert bool(named(spans, "reactive_update")) is expect_update
    assert any(s.name.startswith("reactive.effect") for s in spans) is expect_effect
