"""Concurrency behavior of async effects across and within sessions.

Target model (R Shiny's): a flush starts effects and never waits for their async parts.
A session's busy count defines its cycle; input updates wait until the session is idle,
while the receive loop and other sessions keep going.
"""

from __future__ import annotations

import asyncio
import json
from typing import Callable

import pytest

from shiny import App, Inputs, Outputs, Session, reactive, ui
from shiny._connection import MockConnection
from shiny.bookmark._bookmark import BookmarkApp
from shiny.bookmark._restore_state import RestoreContext

TIMEOUT = 1.0


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
    """Drives one in-process session over a MockConnection."""

    def __init__(self, server: Callable[[Inputs, Outputs, Session], None]) -> None:
        self.conn = MockConnection()
        self.session = App(ui.TagList(), server)._create_session(self.conn)
        self.task = asyncio.create_task(self.session._run())

    def send(self, msg: dict[str, object]) -> None:
        self.conn.cause_receive(json.dumps(msg))

    def update(self, **data: object) -> None:
        self.send({"method": "update", "data": data})

    async def close(self) -> None:
        self.conn.cause_disconnect()
        await asyncio.wait_for(self.task, TIMEOUT)


@pytest.mark.asyncio
async def test_slow_effect_does_not_block_other_session():
    gate = asyncio.Event()
    a_started = asyncio.Event()
    b_seen: list[object] = []

    def server_a(input: Inputs, output: Outputs, session: Session) -> None:
        @reactive.effect
        @reactive.event(input.go, ignore_init=True)
        async def _slow():
            a_started.set()
            await gate.wait()

    def server_b(input: Inputs, output: Outputs, session: Session) -> None:
        @reactive.effect
        def _x():
            b_seen.append(input.x())

    a, b = Client(server_a), Client(server_b)
    try:
        a.send({"method": "init", "data": {"go": 0}})
        b.send({"method": "init", "data": {"x": 0}})
        assert await wait_until(lambda: b_seen == [0])

        a.update(go=1)
        await asyncio.wait_for(a_started.wait(), TIMEOUT)

        b.update(x=1)
        assert await wait_until(
            lambda: b_seen == [0, 1]
        ), "session B stalled behind session A's slow async effect"
    finally:
        gate.set()
        await a.close()
        await b.close()


@pytest.mark.asyncio
async def test_other_sessions_slow_effect_does_not_block_flush():
    # A sets a value shared across sessions, which invalidates B's slow effect in the
    # middle of A's flush. A's flush must not wait for B's effect to finish.
    shared = reactive.value(0)
    gate = asyncio.Event()
    b_started = asyncio.Event()
    a_seen: list[object] = []

    def server_a(input: Inputs, output: Outputs, session: Session) -> None:
        @reactive.effect
        @reactive.event(input.go, ignore_init=True)
        def _bump():
            shared.set(shared() + 1)

        @reactive.effect
        def _x():
            a_seen.append(input.x())

    def server_b(input: Inputs, output: Outputs, session: Session) -> None:
        @reactive.effect
        @reactive.event(shared, ignore_init=True)
        async def _slow():
            b_started.set()
            await gate.wait()

    a, b = Client(server_a), Client(server_b)
    try:
        b.send({"method": "init", "data": {}})
        a.send({"method": "init", "data": {"go": 0, "x": 0}})
        assert await wait_until(lambda: a_seen == [0])

        a.update(go=1)
        await asyncio.wait_for(b_started.wait(), TIMEOUT)

        a.update(x=1)
        assert await wait_until(
            lambda: a_seen == [0, 1]
        ), "session A stalled behind session B's slow async effect"
    finally:
        gate.set()
        await a.close()
        await b.close()


@pytest.mark.asyncio
async def test_update_while_busy():
    gate = asyncio.Event()
    started = asyncio.Event()
    pinged = asyncio.Event()
    slow_seen: list[object] = []
    x_seen: list[object] = []

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        @reactive.effect
        @reactive.event(input.go, ignore_init=True)
        async def _slow():
            slow_seen.append(input.x())
            started.set()
            await gate.wait()
            slow_seen.append(input.x())

        @reactive.effect
        def _x():
            x_seen.append(input.x())

        session.set_message_handler("ping", lambda: pinged.set())

    c = Client(server)
    try:
        c.send({"method": "init", "data": {"go": 0, "x": 0}})
        assert await wait_until(lambda: x_seen == [0])

        c.update(go=1)
        await asyncio.wait_for(started.wait(), TIMEOUT)

        # The session keeps handling messages while an effect is busy.
        c.send({"method": "ping", "tag": 1, "args": []})
        assert await wait_until(
            pinged.is_set
        ), "receive loop blocked while an effect was busy"

        # An input update that arrives while busy waits until the session is idle...
        c.update(x=1)
        await asyncio.sleep(0.05)
        assert x_seen == [0]

        # ...so the busy effect sees stable inputs, and the update then applies.
        gate.set()
        assert await wait_until(lambda: x_seen == [0, 1])
        assert slow_seen == [0, 0]
    finally:
        gate.set()
        await c.close()


class SlowSendConnection(MockConnection):
    def __init__(self) -> None:
        super().__init__()
        self.sent: list[dict[str, object]] = []

    async def send(self, message: str) -> None:
        await asyncio.sleep(0)  # transport backpressure
        self.sent.append(json.loads(message))


@pytest.mark.asyncio
async def test_output_set_during_send_is_kept():
    conn = SlowSendConnection()
    session = App(ui.TagList(), None)._create_session(conn)
    assert isinstance(session.bookmark, BookmarkApp)
    session.bookmark._set_restore_context(RestoreContext())
    omq = session._outbound_message_queues

    omq.set_value("x", 1)
    first = asyncio.create_task(session._flush())
    await asyncio.sleep(0)  # `first` is now awaiting the send
    omq.set_value("y", 2)
    await first
    await session._flush()

    assert [m["values"] for m in conn.sent if "values" in m] == [{"x": 1}, {"y": 2}]


@pytest.mark.asyncio
async def test_timer_with_queued_update_does_not_hang():
    # #2182 hang: when the timer fired during the tick between the session going
    # idle and its queued update running, the timer ran that update inline, then
    # cancelled itself mid-update, leaving busy_count stuck at 1.
    seen: list[object] = []

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        @reactive.effect
        def _tick():
            seen.append(input.x())
            reactive.invalidate_later(0.05)

    c = Client(server)
    try:
        c.send({"method": "init", "data": {"x": 0}})
        assert await wait_until(lambda: seen == [0])
        session = c.session
        assert session._busy_count == 0

        # Put the session in that one-tick state by hand: idle, with an update queued.
        session._cycle_start_action_queue.append(
            lambda: session._manage_inputs({"x": 1})
        )
        await asyncio.sleep(0.1)  # the timer fires

        assert await wait_until(lambda: 1 in seen)
        n = len(seen)
        assert await wait_until(lambda: len(seen) > n), "timer effect stopped"
        c.update(x=2)
        assert await wait_until(lambda: 2 in seen), "session stopped taking updates"
    finally:
        await c.close()
