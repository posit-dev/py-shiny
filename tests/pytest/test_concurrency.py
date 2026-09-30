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
            reactive.invalidate_later(0.3)

    c = Client(server)
    try:
        c.send({"method": "init", "data": {"x": 0}})
        session = c.session
        # Idle between timer runs (the long timer leaves plenty of room).
        assert await wait_until(lambda: seen == [0] and session._busy_count == 0)

        # Put the session in that one-tick state by hand: idle, with an update queued.
        session._cycle_start_action_queue.append(
            lambda: session._manage_inputs({"x": 1})
        )
        await asyncio.sleep(0.35)  # the timer fires

        assert await wait_until(lambda: 1 in seen)
        n = len(seen)
        assert await wait_until(lambda: len(seen) > n), "timer effect stopped"
        c.update(x=2)
        assert await wait_until(lambda: 2 in seen), "session stopped taking updates"
    finally:
        await c.close()


# ----------------------------------------------------------------------------
# Effects and calcs that overlap now that a flush doesn't wait for them
# ----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_async_calc_read_by_two_effects_runs_once():
    runs = 0
    src = reactive.value(1)

    @reactive.calc
    async def data():
        nonlocal runs
        runs += 1
        v = src()
        await asyncio.sleep(0.02)
        return v * 10

    seen: list[int] = []

    @reactive.effect
    async def _e1():
        seen.append(await data())

    @reactive.effect
    async def _e2():
        seen.append(await data())

    await reactive.flush()
    assert (runs, seen) == (1, [10, 10])

    # The cache still works afterwards.
    with reactive.isolate():
        for _ in range(3):
            assert await data() == 10
    assert runs == 1

    _e1.destroy()
    _e2.destroy()


@pytest.mark.asyncio
async def test_effect_runs_do_not_overlap():
    # A re-run waits for the previous run, so a slower, older run can't finish last.
    v = reactive.value(1)
    log: list[tuple[str, int]] = []

    @reactive.effect
    async def _setter():
        await asyncio.sleep(0.01)
        v.set(2)

    @reactive.effect
    async def _slow_for_old_values():
        x = v()
        log.append(("start", x))
        await asyncio.sleep(0.1 if x == 1 else 0.01)
        log.append(("end", x))

    await reactive.flush()
    assert log == [("start", 1), ("end", 1), ("start", 2), ("end", 2)]

    _setter.destroy()
    _slow_for_old_values.destroy()


# ----------------------------------------------------------------------------
# reactive.flush()
# ----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_flush_from_effect_returns_right_away():
    # Called from inside an effect run, waiting would wait on itself.
    done: list[bool] = []

    @reactive.effect
    async def _e():
        await asyncio.wait_for(reactive.flush(), TIMEOUT)
        done.append(True)

    await asyncio.wait_for(reactive.flush(), TIMEOUT)
    assert done == [True]
    _e.destroy()


@pytest.mark.asyncio
async def test_flush_from_task_started_by_effect_waits_for_dependents():
    log: list[str] = []
    v = reactive.value(0)
    trigger = reactive.value(0)
    bg_tasks: list[asyncio.Task[None]] = []

    @reactive.effect
    def _dep():
        log.append(f"dep saw {v()}")

    @reactive.effect
    def _starter():
        async def bg():
            await asyncio.sleep(0.01)
            v.set(1)
            await reactive.flush()
            log.append("bg after flush")

        if trigger() == 1:
            bg_tasks.append(asyncio.create_task(bg()))

    await reactive.flush()
    trigger.set(1)
    await reactive.flush()
    await asyncio.wait_for(bg_tasks[0], TIMEOUT)
    assert log == ["dep saw 0", "dep saw 1", "bg after flush"]

    _dep.destroy()
    _starter.destroy()


@pytest.mark.asyncio
async def test_flush_during_active_flush_returns():
    # With a flushed callback that keeps yielding, reactive.flush() used to keep
    # re-running flushes and never return.
    flushes = 0

    async def slow_flushed() -> None:
        nonlocal flushes
        flushes += 1
        await asyncio.sleep(0.01)

    unregister = reactive.on_flushed(slow_flushed)
    try:
        v = reactive.value(0)

        @reactive.effect
        def _e():
            v()

        await reactive.flush()
        v.set(1)
        await asyncio.sleep(0.002)  # the requested flush is now mid-callback
        await asyncio.wait_for(reactive.flush(), TIMEOUT)
        assert flushes < 10
        _e.destroy()
    finally:
        unregister()


@pytest.mark.asyncio
async def test_extended_task_dependents_see_every_queued_result():
    async def slow_flushed() -> None:
        await asyncio.sleep(0.05)

    unregister = reactive.on_flushed(slow_flushed)
    try:

        @reactive.extended_task
        async def task(n: int) -> int:
            await asyncio.sleep(0.02)
            return n

        seen: list[int] = []

        @reactive.effect
        def _e():
            if task.status() == "success":
                seen.append(task.value())

        task.invoke(1)
        task.invoke(2)  # queued behind the first
        await reactive.flush()
        assert await wait_until(lambda: len(seen) == 2)
        assert seen == [1, 2]
        _e.destroy()
    finally:
        unregister()


# ----------------------------------------------------------------------------
# Per-session flush requests
# ----------------------------------------------------------------------------


class RecordingConnection(MockConnection):
    def __init__(self) -> None:
        super().__init__()
        self.sent: list[dict[str, object]] = []

    async def send(self, message: str) -> None:
        self.sent.append(json.loads(message))


class RecordingClient(Client):
    def __init__(self, server: Callable[[Inputs, Outputs, Session], None]) -> None:
        self.recording = RecordingConnection()
        self.conn = self.recording
        self.session = App(ui.TagList(), server)._create_session(self.conn)
        self.task = asyncio.create_task(self.session._run())

    @property
    def sent(self) -> list[dict[str, object]]:
        return self.recording.sent

    def input_messages(self) -> list[object]:
        return [m for s in self.sent for m in s.get("inputMessages", [])]  # type: ignore


@pytest.mark.asyncio
async def test_input_update_from_background_task_is_sent():
    c = RecordingClient(lambda input, output, session: None)
    try:
        c.send({"method": "init", "data": {}})
        assert await wait_until(lambda: len(c.sent) > 1)

        async def background() -> None:
            ui.update_text("t", value="hi", session=c.session)
            await reactive.flush()

        await asyncio.create_task(background())
        assert await wait_until(lambda: len(c.input_messages()) == 1)
    finally:
        await c.close()


@pytest.mark.asyncio
async def test_message_handler_update_after_await_is_sent():
    def server(input: Inputs, output: Outputs, session: Session) -> None:
        async def handler() -> None:
            await asyncio.sleep(0.01)
            ui.update_text("t", value="hi")

        session.set_message_handler("h", handler)

    c = RecordingClient(server)
    try:
        c.send({"method": "init", "data": {}})
        c.send({"method": "h", "tag": 1, "args": []})
        assert await wait_until(lambda: len(c.input_messages()) == 1)
    finally:
        await c.close()


@pytest.mark.asyncio
async def test_message_handlers_awaiting_flush_do_not_deadlock():
    v = reactive.value(0)

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        async def handler() -> int:
            v.set(v() + 1)
            await reactive.flush()
            return 1

        session.set_message_handler("h", handler)

    c = RecordingClient(server)
    try:
        c.send({"method": "init", "data": {}})
        c.send({"method": "h", "tag": 1, "args": []})
        c.send({"method": "h", "tag": 2, "args": []})

        def tags() -> list[object]:
            return [m["response"]["tag"] for m in c.sent if "response" in m]  # type: ignore

        assert await wait_until(lambda: sorted(tags()) == [1, 2])  # type: ignore
    finally:
        await c.close()


@pytest.mark.asyncio
async def test_one_sessions_flush_error_does_not_stop_others():
    def server_a(input: Inputs, output: Outputs, session: Session) -> None:
        calls = 0

        def bad() -> None:
            # Past the init flush, so the error is raised from a shared flush.
            nonlocal calls
            calls += 1
            if calls > 1:
                raise RuntimeError("on_flush boom")

        session.on_flush(bad, once=False)

        @reactive.effect
        def _():
            input.x()

    def server_b(input: Inputs, output: Outputs, session: Session) -> None:
        @reactive.effect
        def _():
            ui.update_text("t", value=str(input.x()))

    a, b = RecordingClient(server_a), RecordingClient(server_b)
    try:
        a.send({"method": "init", "data": {"x": 0}})
        b.send({"method": "init", "data": {"x": 0}})
        assert await wait_until(lambda: len(b.input_messages()) == 1)
        a.update(x=1)
        # A's error closes A only.
        assert await wait_until(lambda: a.session._has_run_session_ended_tasks)
        for i in range(1, 4):
            b.update(x=i)
        assert await wait_until(lambda: len(b.input_messages()) == 4)
        assert not b.session._has_run_session_ended_tasks
    finally:
        await a.close()
        await b.close()


@pytest.mark.asyncio
async def test_every_cycle_ends_with_a_message_even_when_empty():
    # The client settles output progress (e.g. after `req(False,
    # cancel_output=True)`) on this message, so it's sent with nothing in it.
    def server(input: Inputs, output: Outputs, session: Session) -> None:
        @reactive.effect
        def _():
            input.x()

    c = RecordingClient(server)
    try:
        c.send({"method": "init", "data": {"x": 0}})

        def value_messages() -> int:
            return sum("values" in m for m in c.sent)

        assert await wait_until(lambda: value_messages() == 1)
        c.update(x=1)
        assert await wait_until(lambda: value_messages() == 2)
        assert c.sent[-1] == {"values": {}, "inputMessages": [], "errors": {}}
    finally:
        await c.close()


@pytest.mark.asyncio
async def test_queued_actions_dropped_when_session_ends():
    ran: list[bool] = []
    c = Client(lambda input, output, session: None)
    c.send({"method": "init", "data": {}})
    assert await wait_until(lambda: c.session._flush_enabled)
    await c.close()

    c.session._cycle_start_action_queue.append(lambda: ran.append(True))
    c.session._start_cycle()
    assert ran == []
    assert c.session._cycle_start_action_queue == []


@pytest.mark.asyncio
async def test_only_downloads_make_the_session_busy():
    session = App(ui.TagList(), None)._create_session(MockConnection())
    busy: list[int] = []

    async def record(*args: object) -> None:
        busy.append(session._busy_count)

    session._handle_request_impl = record  # type: ignore
    for action in ("upload", "dynamic_route", "download"):
        await session._handle_request(None, action, None)  # type: ignore
    assert busy == [0, 0, 1]


# ----------------------------------------------------------------------------
# More edge cases
# ----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_async_calc_invalidated_mid_run_recomputes_for_waiting_reader():
    src = reactive.value(1)
    started = asyncio.Event()
    release = asyncio.Event()

    @reactive.calc
    async def data():
        v = src()
        started.set()
        await release.wait()
        return v * 10

    async def read() -> int:
        with reactive.isolate():
            return await data()

    first = asyncio.create_task(read())
    await started.wait()
    second = asyncio.create_task(read())  # waits on the run in flight
    await asyncio.sleep(0)
    src.set(2)  # invalidates the run the second reader is waiting on
    release.set()
    assert await asyncio.wait_for(first, TIMEOUT) == 10
    assert await asyncio.wait_for(second, TIMEOUT) == 20


@pytest.mark.asyncio
async def test_async_calc_error_is_shared_by_concurrent_readers():
    runs = 0

    @reactive.calc
    async def data():
        nonlocal runs
        runs += 1
        await asyncio.sleep(0.01)
        raise ValueError("boom")

    async def read() -> str:
        with reactive.isolate():
            try:
                await data()
            except ValueError as e:
                return str(e)
            return "no error"

    results = await asyncio.wait_for(asyncio.gather(read(), read()), TIMEOUT)
    assert results == ["boom", "boom"]
    assert runs == 1


@pytest.mark.asyncio
async def test_rerun_of_destroyed_effect_is_skipped():
    v = reactive.value(0)
    release = asyncio.Event()
    runs: list[int] = []

    @reactive.effect
    async def e():
        runs.append(v())
        await release.wait()

    flush_task = asyncio.create_task(reactive.flush())
    assert await wait_until(lambda: runs == [0])
    v.set(1)  # queues a re-run behind the one in progress
    await asyncio.sleep(0.01)
    e.destroy()
    release.set()
    await asyncio.wait_for(flush_task, TIMEOUT)
    await asyncio.wait_for(reactive.flush(), TIMEOUT)
    assert runs == [0]


@pytest.mark.asyncio
async def test_priority_orders_effect_starts():
    order: list[str] = []
    v = reactive.value(0)

    @reactive.effect(priority=1)
    async def _low():
        v()
        order.append("low start")
        await asyncio.sleep(0.02)
        order.append("low end")

    @reactive.effect(priority=10)
    async def _high():
        v()
        order.append("high start")
        await asyncio.sleep(0.04)
        order.append("high end")

    await reactive.flush()
    # Starts follow priority; a lower-priority effect can finish first.
    assert order == ["high start", "low start", "low end", "high end"]
    _low.destroy()
    _high.destroy()


@pytest.mark.asyncio
async def test_many_invalidations_in_one_tick_share_one_flush():
    flushes = 0

    async def count() -> None:
        nonlocal flushes
        flushes += 1

    unregister = reactive.on_flushed(count)
    try:
        v = reactive.value(0)
        runs: list[int] = []

        @reactive.effect
        def _e():
            runs.append(v())

        await reactive.flush()
        flushes = 0
        for i in range(1, 6):
            v.set(i)
        assert await wait_until(lambda: runs[-1] == 5)
        await asyncio.sleep(0.02)
        assert runs == [0, 5]
        assert flushes == 1
        _e.destroy()
    finally:
        unregister()


@pytest.mark.asyncio
async def test_flush_from_session_on_flush_callback_returns_right_away():
    called: list[bool] = []

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        async def on_flush() -> None:
            await asyncio.wait_for(reactive.flush(), TIMEOUT)
            called.append(True)

        session.on_flush(on_flush, once=True)

    c = RecordingClient(server)
    try:
        c.send({"method": "init", "data": {}})
        assert await wait_until(lambda: called == [True])
    finally:
        await c.close()


@pytest.mark.asyncio
async def test_input_message_from_on_flush_callback_does_not_loop():
    # #2449 measured 999 flushes when a repeating on_flush callback queued an input
    # message that requested another flush.
    count = 0

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        def on_flush() -> None:
            nonlocal count
            count += 1
            session.send_input_message("t", {"value": count})

        session.on_flush(on_flush, once=False)

    c = RecordingClient(server)
    try:
        c.send({"method": "init", "data": {}})
        await asyncio.sleep(0.2)
        assert count < 5
    finally:
        await c.close()


@pytest.mark.asyncio
async def test_outputs_are_sent_together_once_the_cycle_ends():
    release = asyncio.Event()

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        @reactive.effect
        @reactive.event(input.go, ignore_init=True)
        def _fast():
            ui.update_text("fast", value="done")

        @reactive.effect
        @reactive.event(input.go, ignore_init=True)
        async def _slow():
            await release.wait()
            ui.update_text("slow", value="done")

    c = RecordingClient(server)
    try:
        c.send({"method": "init", "data": {"go": 0}})
        assert await wait_until(lambda: any("values" in m for m in c.sent))
        c.update(go=1)
        await asyncio.sleep(0.05)
        # The fast effect finished, but its output waits for the slow one.
        assert c.input_messages() == []
        release.set()
        assert await wait_until(lambda: len(c.input_messages()) == 2)
        # ...and both arrive in the same message.
        batches = [m["inputMessages"] for m in c.sent if m.get("inputMessages")]
        assert len(batches) == 1
    finally:
        release.set()
        await c.close()


@pytest.mark.asyncio
async def test_timer_waits_while_session_is_busy():
    release = asyncio.Event()
    ticks: list[float] = []

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        @reactive.effect
        def _tick():
            ticks.append(asyncio.get_running_loop().time())
            reactive.invalidate_later(0.02)

        @reactive.effect
        @reactive.event(input.go, ignore_init=True)
        async def _slow():
            await release.wait()

    c = Client(server)
    try:
        c.send({"method": "init", "data": {"go": 0}})
        assert await wait_until(lambda: len(ticks) >= 2)
        c.update(go=1)
        assert await wait_until(lambda: c.session._busy_count > 0)
        n = len(ticks)
        await asyncio.sleep(0.15)
        # Timer invalidations wait for the busy cycle, like input changes.
        assert len(ticks) <= n + 1
        release.set()
        assert await wait_until(lambda: len(ticks) > n + 2)
    finally:
        release.set()
        await c.close()


@pytest.mark.asyncio
async def test_message_handler_error_returns_error_response():
    def server(input: Inputs, output: Outputs, session: Session) -> None:
        def handler() -> None:
            raise RuntimeError("handler boom")

        session.set_message_handler("h", handler)

    c = RecordingClient(server)
    try:
        c.send({"method": "init", "data": {}})
        c.send({"method": "h", "tag": 1, "args": []})
        assert await wait_until(lambda: any("response" in m for m in c.sent))
        response = next(m["response"] for m in c.sent if "response" in m)
        assert "handler boom" in str(response)
        assert not c.session._has_run_session_ended_tasks
    finally:
        await c.close()


@pytest.mark.asyncio
async def test_no_flush_requests_after_session_ends():
    c = Client(lambda input, output, session: None)
    c.send({"method": "init", "data": {}})
    assert await wait_until(lambda: c.session._flush_enabled)
    await c.close()
    c.session.send_input_message("t", {"value": 1})
    assert c.session.id not in c.session.app._sessions_needing_flush


@pytest.mark.asyncio
async def test_session_ending_mid_effect_settles_busy_count():
    release = asyncio.Event()

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        @reactive.effect
        @reactive.event(input.go, ignore_init=True)
        async def _slow():
            await release.wait()

    c = Client(server)
    c.send({"method": "init", "data": {"go": 0}})
    c.update(go=1)
    assert await wait_until(lambda: c.session._busy_count == 1)
    await c.close()
    release.set()
    assert await wait_until(lambda: c.session._busy_count == 0)


@pytest.mark.asyncio
async def test_flush_waits_for_slow_effects_in_other_sessions():
    # reactive.flush() means "settled": it also waits for other sessions' effects.
    release = asyncio.Event()
    done: list[bool] = []

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        @reactive.effect
        @reactive.event(input.go, ignore_init=True)
        async def _slow():
            await release.wait()
            done.append(True)

    c = Client(server)
    try:
        c.send({"method": "init", "data": {"go": 0}})
        c.update(go=1)
        assert await wait_until(lambda: c.session._busy_count == 1)
        flush = asyncio.create_task(reactive.flush())
        await asyncio.sleep(0.05)
        assert not flush.done()
        release.set()
        await asyncio.wait_for(flush, TIMEOUT)
        assert done == [True]
    finally:
        release.set()
        await c.close()
