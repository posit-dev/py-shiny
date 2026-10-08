"""Concurrency behavior of async effects across and within sessions.

Target model (R Shiny's): a flush starts effects and never waits for their async parts.
A session's busy count defines its cycle; input updates wait until the session is idle,
while the receive loop and other sessions keep going.
"""

from __future__ import annotations

import asyncio
import gc
import json
import threading
from typing import AsyncIterable, Callable, Iterator

import pytest
from starlette.requests import Request

from shiny import App, Inputs, Outputs, Session, module, reactive, render, ui
from shiny._connection import MockConnection
from shiny.bookmark._bookmark import BookmarkApp
from shiny.bookmark._restore_state import RestoreContext
from shiny.reactive._core import (
    ReactiveEnvironment,
    ReactiveWarning,
    _reactive_environment,
)
from shiny.session import get_current_session, session_context

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
    first = asyncio.create_task(session._output_flush())
    await asyncio.sleep(0)  # `first` is now awaiting the send
    omq.set_value("y", 2)
    await first
    await session._output_flush()

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
    # re-running rounds and never return.
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
        await asyncio.sleep(0.002)  # the requested round is now mid-callback
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
        self.session: "Session | None" = None
        # The session's busy count each time an output message was sent.
        self.busy_at_output_send: list[int] = []

    async def send(self, message: str) -> None:
        msg = json.loads(message)
        if "values" in msg and self.session is not None:
            self.busy_at_output_send.append(self.session._busy_count)  # type: ignore
        self.sent.append(msg)


class RecordingClient(Client):
    def __init__(self, server: Callable[[Inputs, Outputs, Session], None]) -> None:
        self.recording = RecordingConnection()
        self.conn = self.recording
        self.session = App(ui.TagList(), server)._create_session(self.conn)
        self.recording.session = self.session
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

        await asyncio.sleep(0.05)
        start = len(c.sent)
        c.update(x=1)

        def cycle_end_message() -> "dict[str, object] | None":
            after = c.sent[start:]
            if {"busy": "idle"} not in after:
                return None
            idle = after.index({"busy": "idle"})
            return next((m for m in after[idle:] if "values" in m), None)

        assert await wait_until(lambda: cycle_end_message() is not None)
        assert cycle_end_message() == {"values": {}, "inputMessages": [], "errors": {}}
    finally:
        await c.close()


@pytest.mark.asyncio
async def test_queued_actions_dropped_when_session_ends():
    ran: list[bool] = []
    c = Client(lambda input, output, session: None)
    c.send({"method": "init", "data": {}})
    assert await wait_until(lambda: c.session._output_flush_enabled)
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


def download_request() -> Request:
    return Request({"type": "http", "method": "GET", "path": "/", "headers": []})


@pytest.mark.parametrize("kind", ["async", "sync"])
@pytest.mark.asyncio
async def test_value_set_in_download_handler_updates_outputs_and_effects(kind: str):
    # https://github.com/posit-dev/py-shiny/issues/1785: a download is a plain HTTP
    # request, so on main nothing flushed after its handler set a value.
    notes: list[int] = []

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        count = reactive.value(0)

        if kind == "async":

            @render.download_button(filename="f.txt")
            async def dl() -> AsyncIterable[str]:
                count.set(count.get() + 1)
                yield "data"

        else:

            @render.download_button(filename="f.txt")
            def dl() -> Iterator[str]:
                count.set(count.get() + 1)
                yield "data"

        @render.text
        def n():
            return str(count())

        @reactive.effect
        @reactive.event(count, ignore_init=True)
        def _():
            notes.append(count())

    def n_values() -> list[object]:
        return [m["values"]["n"] for m in c.sent if "n" in m.get("values", {})]  # type: ignore

    c = RecordingClient(server)
    try:
        c.send({"method": "init", "data": {".clientdata_output_n_hidden": False}})
        assert await wait_until(lambda: n_values()[-1:] == ["0"])
        for i in (1, 2):
            response = await c.session._handle_request(
                download_request(), "download", "dl"
            )
            async for _chunk in response.body_iterator:  # type: ignore
                pass
            # No client message needed for the output and effect to update.
            assert await wait_until(lambda i=i: n_values()[-1:] == [str(i)])
            assert notes == list(range(1, i + 1))
    finally:
        await c.close()


@pytest.mark.parametrize("kind", ["async", "sync"])
@pytest.mark.asyncio
async def test_values_set_mid_stream_are_sent_before_the_stream_ends(kind: str):
    def server(input: Inputs, output: Outputs, session: Session) -> None:
        progress = reactive.value(0)

        if kind == "async":

            @render.download_button(filename="f.txt")
            async def dl() -> AsyncIterable[str]:
                for i in (1, 2, 3):
                    progress.set(i)
                    yield f"chunk{i}"

        else:

            @render.download_button(filename="f.txt")
            def dl() -> Iterator[str]:
                for i in (1, 2, 3):
                    progress.set(i)
                    yield f"chunk{i}"

        @render.text
        def n():
            return str(progress())

    def n_values() -> list[object]:
        return [m["values"]["n"] for m in c.sent if "n" in m.get("values", {})]  # type: ignore

    c = RecordingClient(server)
    try:
        c.send({"method": "init", "data": {".clientdata_output_n_hidden": False}})
        assert await wait_until(lambda: n_values()[-1:] == ["0"])
        response = await c.session._handle_request(download_request(), "download", "dl")
        chunks = response.body_iterator.__aiter__()  # type: ignore
        for i in (1, 2, 3):
            assert await chunks.__anext__() == f"chunk{i}".encode()
            # The next chunk isn't read yet, so the stream is still open.
            assert await wait_until(lambda i=i: n_values()[-1:] == [str(i)])
        with pytest.raises(StopAsyncIteration):
            await chunks.__anext__()
    finally:
        await c.close()


@pytest.mark.asyncio
async def test_session_handles_input_while_a_download_streams():
    def server(input: Inputs, output: Outputs, session: Session) -> None:
        release = asyncio.Event()

        @reactive.effect
        @reactive.event(input.release, ignore_init=True)
        def _():
            release.set()

        @render.download_button(filename="f.txt")
        async def dl() -> AsyncIterable[str]:
            yield "a"
            await release.wait()
            yield "b"

    c = RecordingClient(server)
    try:
        c.send({"method": "init", "data": {"release": 0}})
        assert await wait_until(lambda: c.session._output_flush_enabled)
        response = await c.session._handle_request(download_request(), "download", "dl")

        async def read_body() -> bytes:
            return b"".join([chunk async for chunk in response.body_iterator])  # type: ignore

        body = asyncio.create_task(read_body())
        await asyncio.sleep(0.05)
        assert not body.done()
        # The stream finishes only once the session has handled this input.
        c.update(release=1)
        assert await asyncio.wait_for(body, TIMEOUT) == b"ab"
    finally:
        await c.close()


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
async def test_many_invalidations_in_one_tick_share_one_round():
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
async def test_no_output_flush_requests_after_session_ends():
    c = Client(lambda input, output, session: None)
    c.send({"method": "init", "data": {}})
    assert await wait_until(lambda: c.session._output_flush_enabled)
    await c.close()
    c.session.send_input_message("t", {"value": 1})
    assert c.session.id not in c.session.app._sessions_needing_output_flush


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
    # Session end cancels the run, so the busy period ends without `release`.
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


# ----------------------------------------------------------------------------
# Review round 2
# ----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_flush_through_child_task_of_flush_callback_returns():
    # `asyncio.gather()` (and `asyncio.wait_for()` before Python 3.12) awaits in a
    # child task, which used to wait for a flush that couldn't start until the
    # current one finished.
    done: list[bool] = []

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        async def on_flush() -> None:
            await asyncio.gather(reactive.flush())
            await asyncio.ensure_future(reactive.flush())
            done.append(True)

        session.on_flush(on_flush, once=True)

    c = Client(server)
    try:
        c.send({"method": "init", "data": {}})
        assert await wait_until(lambda: done == [True])
        assert await wait_until(lambda: not _reactive_environment._round_running)
    finally:
        await c.close()


@pytest.mark.asyncio
async def test_flush_through_child_task_of_effect_returns():
    # The effect queues its own re-run, then flushes via a child task: the child
    # must not wait for the re-run, which waits for the effect.
    v = reactive.value(0)
    log: list[str] = []

    @reactive.effect
    async def e():
        n = v()
        log.append(f"start {n}")
        if n == 0:
            v.set(1)
            await asyncio.gather(reactive.flush())
        log.append(f"end {n}")

    await asyncio.wait_for(reactive.flush(), TIMEOUT)
    assert log == ["start 0", "end 0", "start 1", "end 1"]
    e.destroy()


@pytest.mark.asyncio
async def test_async_calc_invalidated_mid_run_does_not_cache_stale_value():
    # The stale run is the slower one, so it finishes after the fresh run.
    v = reactive.value(1)
    trigger = reactive.value(0)
    seen: list[tuple[str, int]] = []

    @reactive.calc
    async def data():
        x = v()
        await asyncio.sleep(0.1 if x == 1 else 0.01)
        return x * 10

    @reactive.effect
    async def e1():
        seen.append(("e1", await data()))

    @reactive.effect
    async def e2():
        if trigger() == 0:
            return
        seen.append(("e2", await data()))

    async def poke() -> None:
        await asyncio.sleep(0.03)  # data()'s first run is mid-await
        v.set(2)
        trigger.set(1)

    poker = asyncio.create_task(poke())
    await reactive.flush()
    await poker
    await asyncio.sleep(0.15)
    await reactive.flush()

    with reactive.isolate():
        assert await data() == 20
    assert ("e2", 20) in seen and seen[-1] == ("e1", 20)
    e1.destroy()
    e2.destroy()


# ----------------------------------------------------------------------------
# One test per fix that other tests only cover jointly
# ----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_async_calc_reader_waits_for_the_latest_run():
    # Run A (x=1) is invalidated mid-run; run B (x=2) starts; a third reader waits
    # on B. A finishing first must not wake that reader with A's value.
    v = reactive.value(1)

    @reactive.calc
    async def data():
        x = v()
        await asyncio.sleep(0.05 if x == 1 else 0.15)
        return x * 10

    async def read() -> int:
        with reactive.isolate():
            return await data()

    first = asyncio.create_task(read())
    await asyncio.sleep(0.01)
    v.set(2)
    second = asyncio.create_task(read())
    await asyncio.sleep(0.01)
    third = asyncio.create_task(read())
    assert await asyncio.wait_for(third, TIMEOUT) == 20
    assert await asyncio.wait_for(second, TIMEOUT) == 20
    # A's own caller gets A's result; its context was invalidated anyway.
    assert await asyncio.wait_for(first, TIMEOUT) == 10


@pytest.mark.asyncio
async def test_cancelled_effect_run_ends_busy_period():
    release = asyncio.Event()
    running: list[asyncio.Task[object]] = []

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        @reactive.effect
        @reactive.event(input.go, ignore_init=True)
        async def _slow():
            task = asyncio.current_task()
            assert task is not None
            running.append(task)
            await release.wait()

    c = Client(server)
    try:
        c.send({"method": "init", "data": {"go": 0}})
        c.update(go=1)
        assert await wait_until(lambda: len(running) == 1)
        assert c.session._busy_count == 1
        running[0].cancel()
        assert await wait_until(lambda: c.session._busy_count == 0)
    finally:
        release.set()
        await c.close()


@pytest.mark.asyncio
async def test_concurrent_rounds_do_not_overlap():
    active = 0
    most_active = 0

    async def slow_flushed() -> None:
        nonlocal active, most_active
        active += 1
        most_active = max(most_active, active)
        await asyncio.sleep(0.02)
        active -= 1

    unregister = reactive.on_flushed(slow_flushed)
    try:
        await asyncio.wait_for(
            asyncio.gather(
                _reactive_environment.start_round(),
                _reactive_environment.start_round(),
                _reactive_environment.start_round(),
            ),
            TIMEOUT,
        )
        await asyncio.wait_for(reactive.flush(), TIMEOUT)
        assert most_active == 1
    finally:
        unregister()


@pytest.mark.asyncio
async def test_requested_flush_does_not_inherit_the_requesters_session():
    seen: list[object] = []

    async def record() -> None:
        seen.append(get_current_session())

    unregister = reactive.on_flushed(record)
    try:
        session = App(ui.TagList(), None)._create_session(MockConnection())
        v = reactive.value(0)

        @reactive.effect
        def _e():
            v()

        await reactive.flush()
        seen.clear()
        with session_context(session):
            v.set(1)  # the flush is requested under this session's context
        assert await wait_until(lambda: len(seen) > 0)
        assert seen[0] is None
        _e.destroy()
    finally:
        unregister()


@pytest.mark.asyncio
async def test_on_flush_registered_outside_a_cycle_runs():
    c = Client(lambda input, output, session: None)
    try:
        c.send({"method": "init", "data": {}})
        assert await wait_until(lambda: c.session._output_flush_enabled)
        await asyncio.sleep(0.02)

        ran: list[bool] = []
        c.session.on_flush(lambda: ran.append(True))
        await asyncio.wait_for(reactive.flush(), TIMEOUT)
        assert await wait_until(lambda: ran == [True])
    finally:
        await c.close()


@pytest.mark.asyncio
async def test_slow_message_handler_does_not_block_other_messages():
    gate = asyncio.Event()
    fast_done = asyncio.Event()

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        async def slow() -> None:
            await gate.wait()

        session.set_message_handler("slow", slow)
        session.set_message_handler("fast", lambda: fast_done.set())

    c = Client(server)
    try:
        c.send({"method": "init", "data": {}})
        c.send({"method": "slow", "tag": 1, "args": []})
        c.send({"method": "fast", "tag": 2, "args": []})
        assert await wait_until(fast_done.is_set)
    finally:
        gate.set()
        await c.close()


@pytest.mark.asyncio
async def test_flush_callbacks_wait_while_session_is_busy():
    release = asyncio.Event()
    busy_when_called: list[int] = []

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        session.on_flush(
            lambda: busy_when_called.append(session._busy_count),  # type: ignore
            once=False,
        )

        @reactive.effect
        @reactive.event(input.go, ignore_init=True)
        async def _slow():
            await release.wait()

    c = Client(server)
    try:
        c.send({"method": "init", "data": {"go": 0}})
        c.update(go=1)
        assert await wait_until(lambda: c.session._busy_count == 1)
        # Ask for flushes while busy.
        for _ in range(3):
            c.session.send_input_message("t", {"value": 1})
            await asyncio.sleep(0.01)
        release.set()
        assert await wait_until(lambda: c.session._busy_count == 0)
        await asyncio.sleep(0.02)
        assert busy_when_called and all(b == 0 for b in busy_when_called)
    finally:
        release.set()
        await c.close()


@pytest.mark.asyncio
async def test_no_output_message_while_busy_after_async_flush_callback():
    # The session becomes busy while an async on_flush callback awaits; the output
    # message must then wait for the idle transition.
    shared = reactive.value(0)
    release = asyncio.Event()

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        async def on_flush() -> None:
            await asyncio.sleep(0.02)

        session.on_flush(on_flush, once=False)

        @reactive.effect
        @reactive.event(shared, ignore_init=True)
        async def _slow():
            await release.wait()

    c = RecordingClient(server)
    try:
        c.send({"method": "init", "data": {}})
        assert await wait_until(lambda: len(c.recording.busy_at_output_send) == 1)
        c.session.send_input_message("t", {"value": 1})
        await asyncio.sleep(0.005)  # the on_flush callback is now awaiting
        shared.set(1)
        assert await wait_until(lambda: c.session._busy_count == 1)
        await asyncio.sleep(0.05)
        release.set()
        assert await wait_until(lambda: len(c.input_messages()) == 1)
        assert all(b == 0 for b in c.recording.busy_at_output_send)
    finally:
        release.set()
        await c.close()


@pytest.mark.asyncio
async def test_queued_update_waits_if_session_turns_busy_during_flushed_callbacks():
    shared = reactive.value(0)
    release = asyncio.Event()
    x_seen: list[object] = []
    # Once armed, the on_flushed callback signals that it's running, then waits
    # for the test, so the session can turn busy while it awaits.
    armed = asyncio.Event()
    in_callback = asyncio.Event()
    proceed = asyncio.Event()

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        async def on_flushed() -> None:
            if armed.is_set():
                in_callback.set()
                await proceed.wait()

        session.on_flushed(on_flushed, once=False)

        @reactive.effect
        def _x():
            x_seen.append(input.x())

        @reactive.effect
        @reactive.event(shared, ignore_init=True)
        async def _slow():
            await release.wait()

    c = Client(server)
    try:
        c.send({"method": "init", "data": {"x": 0}})
        assert await wait_until(lambda: x_seen == [0])
        await asyncio.sleep(0.05)
        session = c.session
        # Something to send plus a queued update: the flush sends, runs its flushed
        # callbacks, then starts the update.
        armed.set()
        session.send_input_message("t", {"value": 1})
        session.run_once_when_idle(lambda: session._manage_inputs({"x": 1}))
        await asyncio.wait_for(in_callback.wait(), TIMEOUT)
        shared.set(1)  # the session turns busy while the callback awaits
        await asyncio.sleep(0.01)
        proceed.set()
        await asyncio.sleep(0.05)
        assert x_seen == [0]
        release.set()
        assert await wait_until(lambda: x_seen == [0, 1])
    finally:
        proceed.set()
        release.set()
        await c.close()


@pytest.mark.asyncio
async def test_cycle_not_started_by_an_input_still_ends_with_a_message():
    # A cycle started by a shared value (not a queued action) that queues an
    # update while busy: its (empty) message must go out before the update runs.
    shared = reactive.value(0)
    release = asyncio.Event()

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        @reactive.effect
        def _x():
            input.x()

        @reactive.effect
        @reactive.event(shared, ignore_init=True)
        async def _slow():
            await release.wait()

    c = RecordingClient(server)
    try:
        c.send({"method": "init", "data": {"x": 0}})

        await asyncio.sleep(0.05)
        shared.set(1)
        assert await wait_until(lambda: c.session._busy_count == 1)
        c.update(x=1)
        await asyncio.sleep(0.02)
        start = len(c.sent)
        release.set()
        assert await wait_until(lambda: {"busy": "busy"} in c.sent[start:])
        after = c.sent[start:]
        # Between this cycle going idle and the update's cycle starting, the
        # cycle's message goes out.
        idle = after.index({"busy": "idle"})
        busy = after.index({"busy": "busy"})
        assert any("values" in m for m in after[idle:busy])
    finally:
        release.set()
        await c.close()


# ----------------------------------------------------------------------------
# Each session sends its outputs in its own task
# ----------------------------------------------------------------------------


class GatedConnection(RecordingConnection):
    """
    A connection whose output-message sends can be held open (a slow client) or
    fail. Other messages (e.g. busy/idle status) go straight through.
    """

    def __init__(self) -> None:
        super().__init__()
        self.gate = asyncio.Event()
        self.gate.set()
        self.fail = False
        self.sending = 0
        self.most_sending = 0

    async def send(self, message: str) -> None:
        if '"values"' not in message:
            await super().send(message)
            return
        self.sending += 1
        self.most_sending = max(self.most_sending, self.sending)
        try:
            await self.gate.wait()
            if self.fail:
                raise RuntimeError("send failed")
            await super().send(message)
        finally:
            self.sending -= 1


class GatedClient(RecordingClient):
    def __init__(self, server: Callable[[Inputs, Outputs, Session], None]) -> None:
        self.gated = GatedConnection()
        self.recording = self.gated
        self.conn = self.gated
        self.session = App(ui.TagList(), server)._create_session(self.conn)
        self.recording.session = self.session
        self.task = asyncio.create_task(self.session._run())


def update_on(x_name: str = "x"):
    """A server that sends an input message for every change of input `x_name`."""

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        @reactive.effect
        def _():
            ui.update_text("t", value=str(input[x_name]()))

    return server


async def started(*clients: RecordingClient) -> None:
    for c in clients:
        c.send({"method": "init", "data": {"x": 0}})
    for c in clients:
        assert await wait_until(lambda c=c: len(c.input_messages()) == 1)


def texts(c: RecordingClient) -> list[object]:
    return [m["message"]["value"] for m in c.input_messages()]  # type: ignore


@pytest.mark.asyncio
async def test_slow_client_does_not_delay_other_sessions_output():
    a, b = GatedClient(update_on()), GatedClient(update_on())
    try:
        await started(a, b)
        a.gated.gate.clear()  # A's client stops reading
        a.update(x=1)
        b.update(x=1)
        assert await wait_until(lambda: texts(b) == ["0", "1"])
        assert texts(a) == ["0"]
        a.gated.gate.set()
        assert await wait_until(lambda: texts(a) == ["0", "1"])
    finally:
        a.gated.gate.set()
        await a.close()
        await b.close()


@pytest.mark.asyncio
async def test_slow_client_does_not_block_the_next_reactive_flush():
    shared = reactive.value(0)
    seen: list[int] = []

    @reactive.effect
    def _no_session():
        seen.append(shared())

    a = GatedClient(update_on())
    try:
        await started(a)
        await reactive.flush()
        a.gated.gate.clear()
        a.update(x=1)
        assert await wait_until(lambda: a.gated.sending == 1)
        # A's send is stuck; unrelated reactive work still runs.
        shared.set(1)
        assert await wait_until(lambda: seen[-1] == 1)
    finally:
        a.gated.gate.set()
        _no_session.destroy()
        await a.close()


@pytest.mark.asyncio
async def test_slow_on_flush_callback_delays_only_its_session():
    gate = asyncio.Event()

    def slow_server(input: Inputs, output: Outputs, session: Session) -> None:
        update_on()(input, output, session)

        async def slow() -> None:
            await gate.wait()

        session.on_flush(slow, once=False)

    a, b = RecordingClient(slow_server), RecordingClient(update_on())
    try:
        a.send({"method": "init", "data": {"x": 0}})
        b.send({"method": "init", "data": {"x": 0}})
        assert await wait_until(lambda: len(b.input_messages()) == 1)
        b.update(x=1)
        assert await wait_until(lambda: texts(b) == ["0", "1"])
        assert texts(a) == []
        gate.set()
        assert await wait_until(lambda: texts(a) == ["0"])
    finally:
        gate.set()
        await a.close()
        await b.close()


@pytest.mark.asyncio
async def test_a_sessions_sends_never_overlap_and_stay_in_order():
    a = GatedClient(update_on())
    try:
        await started(a)
        a.gated.gate.clear()
        a.update(x=1)
        assert await wait_until(lambda: a.gated.sending == 1)
        # More output queued while the first send is stuck.
        for i in range(2, 5):
            a.session.send_input_message("t", {"value": str(i)})
            await asyncio.sleep(0.01)
        a.gated.gate.set()
        assert await wait_until(lambda: texts(a) == ["0", "1", "2", "3", "4"])
        assert a.gated.most_sending == 1
        # The requests made while blocked were merged into one more output flush.
        assert sum("values" in m for m in a.sent[-3:]) <= 2
    finally:
        a.gated.gate.set()
        await a.close()


@pytest.mark.asyncio
async def test_reactive_flush_waits_for_pending_sends():
    a = GatedClient(update_on())
    try:
        await started(a)
        a.gated.gate.clear()
        a.session.send_input_message("t", {"value": "hi"})
        flush = asyncio.create_task(reactive.flush())
        assert await wait_until(lambda: a.gated.sending == 1)
        await asyncio.sleep(0.05)
        assert not flush.done()
        a.gated.gate.set()
        await asyncio.wait_for(flush, TIMEOUT)
        assert texts(a)[-1] == "hi"
    finally:
        a.gated.gate.set()
        await a.close()


@pytest.mark.asyncio
async def test_flush_callbacks_in_two_sessions_calling_reactive_flush_return():
    # Both sessions flush at once, and each callback awaits reactive.flush(): they
    # must not wait on each other's flush task.
    done: list[str] = []
    a, b = Client(lambda i, o, s: None), Client(lambda i, o, s: None)
    try:
        a.send({"method": "init", "data": {}})
        b.send({"method": "init", "data": {}})
        assert await wait_until(
            lambda: a.session._output_flush_enabled and b.session._output_flush_enabled
        )
        await asyncio.sleep(0.02)

        def callback(name: str):
            async def cb() -> None:
                await reactive.flush()
                done.append(name)

            return cb

        for name, c in (("a", a), ("b", b)):
            c.session.on_flush(callback(name), once=True)
        assert await wait_until(lambda: sorted(done) == ["a", "b"])
    finally:
        await a.close()
        await b.close()


@pytest.mark.asyncio
async def test_session_closed_while_its_send_is_stuck():
    a = GatedClient(update_on())
    await started(a)
    a.gated.gate.clear()
    a.update(x=1)
    assert await wait_until(lambda: a.gated.sending == 1)
    # Queued while the send is stuck, so a re-run is pending when the session ends.
    a.session.send_input_message("t", {"value": "queued"})
    a.conn.cause_disconnect()
    assert await wait_until(lambda: not a.session._output_flush_enabled)
    flush_task = a.session._output_flush_task
    a.gated.gate.set()
    assert flush_task is not None
    await asyncio.wait_for(flush_task, TIMEOUT)
    # The session is gone: the pending re-run doesn't send.
    assert "queued" not in texts(a)
    # ...and later requests don't start an output flush at all.
    a.session.send_input_message("t", {"value": "late"})
    await asyncio.sleep(0.02)
    assert "late" not in texts(a)


@pytest.mark.asyncio
async def test_failed_send_closes_only_that_session():
    a, b = GatedClient(update_on()), GatedClient(update_on())
    try:
        await started(a, b)
        a.gated.fail = True
        a.update(x=1)
        assert await wait_until(lambda: a.session._has_run_session_ended_tasks)
        b.update(x=1)
        assert await wait_until(lambda: texts(b) == ["0", "1"])
        assert not b.session._has_run_session_ended_tasks
    finally:
        await a.close()
        await b.close()


@pytest.mark.asyncio
async def test_outputs_stay_in_order_across_cycles_with_a_slow_client():
    class SlowConnection(GatedConnection):
        async def send(self, message: str) -> None:
            if '"values"' in message:
                await asyncio.sleep(0.005)
            await super().send(message)

    a = GatedClient(update_on())
    a.gated.__class__ = SlowConnection
    try:
        await started(a)
        for i in range(1, 6):
            a.update(x=i)
        assert await wait_until(lambda: texts(a)[-1:] == ["5"])
        assert texts(a) == [str(i) for i in range(6)]
        assert a.gated.most_sending == 1
    finally:
        await a.close()


# ----------------------------------------------------------------------------
# Flush requests from other threads
# ----------------------------------------------------------------------------


def in_thread(fn: Callable[[], object]) -> None:
    t = threading.Thread(target=fn)
    t.start()
    t.join(TIMEOUT)


@pytest.mark.asyncio
async def test_value_set_from_another_thread_updates_session_output():
    shared = reactive.value(0)

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        @reactive.effect
        def _():
            ui.update_text("t", value=str(shared()))

    c = RecordingClient(server)
    try:
        c.send({"method": "init", "data": {}})
        assert await wait_until(lambda: texts(c) == ["0"])
        loop = asyncio.get_running_loop()
        # Changing reactive state isn't thread-safe; hand the set() to the loop.
        in_thread(lambda: loop.call_soon_threadsafe(shared.set, 1))
        assert await wait_until(lambda: texts(c) == ["0", "1"])
    finally:
        await c.close()


@pytest.mark.asyncio
async def test_value_set_from_another_thread_runs_sessionless_effect():
    # Not the recommended pattern (see `Value.set()`), but with no session involved
    # it works, and the flush it requests must reach Shiny's loop.
    v = reactive.value(0)
    seen: list[int] = []

    @reactive.effect
    def _e():
        seen.append(v())

    await reactive.flush()
    in_thread(lambda: v.set(1))
    assert await wait_until(lambda: seen == [0, 1])
    _e.destroy()


@pytest.mark.asyncio
async def test_call_soon_threadsafe_set_from_another_thread():
    # The documented thread-safe pattern.
    v = reactive.value(0)
    seen: list[int] = []
    loop = asyncio.get_running_loop()

    @reactive.effect
    def _e():
        seen.append(v())

    await reactive.flush()
    in_thread(lambda: loop.call_soon_threadsafe(v.set, 1))
    assert await wait_until(lambda: seen == [0, 1])
    _e.destroy()


@pytest.mark.asyncio
async def test_round_request_from_a_thread_with_its_own_loop_goes_to_shinys_loop():
    main_loop = asyncio.get_running_loop()
    loops: list[object] = []
    v = reactive.value(0)

    @reactive.effect
    def _e():
        v()
        loops.append(asyncio.get_running_loop())

    await reactive.flush()

    async def other_loop() -> None:
        v.set(1)

    in_thread(lambda: asyncio.run(other_loop()))
    assert await wait_until(lambda: len(loops) == 2)
    assert loops[1] is main_loop
    _e.destroy()


@pytest.mark.asyncio
async def test_many_round_requests_from_threads_are_merged():
    flushes = 0

    async def count() -> None:
        nonlocal flushes
        flushes += 1

    await reactive.flush()
    unregister = reactive.on_flushed(count)
    try:
        threads = [
            threading.Thread(target=_reactive_environment.request_round)
            for _ in range(20)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join(TIMEOUT)
        assert await wait_until(lambda: flushes >= 1)
        await asyncio.sleep(0.05)
        assert flushes <= 3
    finally:
        unregister()


def test_round_request_from_a_thread_with_no_loop_yet_is_ignored():
    env = ReactiveEnvironment()
    in_thread(env.request_round)
    assert env._loop is None and not env._round_requested


def test_round_request_on_a_new_loop_after_the_old_one_closed():
    # E.g. `asyncio.run()` twice: the new loop takes over.
    env = ReactiveEnvironment()
    flushed: list[bool] = []

    async def mark() -> None:
        flushed.append(True)

    env.on_round_finished(mark)

    async def use() -> None:
        env.request_round()
        await asyncio.sleep(0.01)

    asyncio.run(use())
    flushed.clear()
    asyncio.run(use())
    assert flushed == [True]


def test_round_request_after_the_loop_closed_is_ignored():
    env = ReactiveEnvironment()

    async def use() -> None:
        env.request_round()
        await asyncio.sleep(0.01)

    asyncio.run(use())  # env now remembers a loop that is closed
    assert env._loop is not None and env._loop.is_closed()
    errors: list[Exception] = []

    def call() -> None:
        try:
            env.request_round()
        except Exception as e:  # pragma: no cover
            errors.append(e)

    in_thread(call)
    assert errors == []


@pytest.mark.asyncio
async def test_one_output_message_per_input_update():
    # No extra empty message when a flush finds nothing to send and no cycle ended.
    c = RecordingClient(update_on())
    try:
        await started(c)
        await asyncio.sleep(0.05)
        start = len(c.sent)
        for i in range(1, 4):
            c.update(x=i)
            assert await wait_until(lambda i=i: texts(c)[-1:] == [str(i)])
            await asyncio.sleep(0.02)
        assert sum("values" in m for m in c.sent[start:]) == 3
    finally:
        await c.close()


@pytest.mark.asyncio
async def test_on_flush_outside_a_cycle_runs_without_sending_an_empty_message():
    c = RecordingClient(lambda input, output, session: None)
    try:
        c.send({"method": "init", "data": {}})
        assert await wait_until(lambda: c.session._output_flush_enabled)
        await asyncio.sleep(0.05)
        start = len(c.sent)
        ran: list[bool] = []
        c.session.on_flush(lambda: ran.append(True))
        await reactive.flush()
        assert ran == [True]
        assert not any("values" in m for m in c.sent[start:])
    finally:
        await c.close()


def test_round_state_from_a_dead_event_loop_is_discarded():
    # A round stranded on an event loop that has stopped (e.g. a previous
    # `test_server()` run, or a test whose loop closed mid-round) used to leave the
    # environment "in a round" forever: later rounds returned without running, and
    # `run_next_round()` (used by ExtendedTask) waited forever.
    env = ReactiveEnvironment()
    stuck = asyncio.Event()

    async def wait_forever() -> None:
        await stuck.wait()

    finalized: list[bool] = []

    async def stranded_run() -> None:
        try:
            # Nothing else references this future, so only the environment keeps
            # the task alive.
            await asyncio.get_running_loop().create_future()
        finally:
            # Runs if the task is garbage-collected: in an effect, in the wrong
            # context, which raised (and failed whichever test was running).
            finalized.append(True)

    async def strand_a_round() -> None:
        env._round_finished_callbacks.register(wait_forever)
        env._spawn(stranded_run())
        env._spawn(env.start_round())
        await asyncio.sleep(0.01)  # the round is now waiting on `stuck`
        assert env._round_running
        env.request_round()  # also leaves a request pending

    old = asyncio.new_event_loop()
    old.run_until_complete(strand_a_round())
    old.close()  # without letting the round finish
    env._round_finished_callbacks = type(env._round_finished_callbacks)()

    ran: list[bool] = []

    async def record() -> None:
        ran.append(True)

    async def use_a_new_loop() -> None:
        env._round_finished_callbacks.register(record)
        await asyncio.wait_for(env.run_next_round(), TIMEOUT)
        assert ran == [True]
        env.request_round()
        # The dead loop's tasks no longer count as running. (Wait for the round
        # task's done callback; a timed sleep may not cover it on Windows.)
        assert await wait_until(lambda: ran == [True, True] and not env._tasks)

    asyncio.run(use_a_new_loop())
    gc.collect()
    assert finalized == []  # ...but they're kept, so they're never finalized


# ----------------------------------------------------------------------------
# Destroying an effect cancels its in-progress runs (session end, scope destroy)
# ----------------------------------------------------------------------------


def slow_effect(log: list[str], release: asyncio.Event, name: str = "e"):
    """An effect body that logs its progress and waits on `release`."""

    async def body() -> None:
        try:
            log.append(f"{name} start")
            await release.wait()
            log.append(f"{name} end")
        finally:
            log.append(f"{name} finally")

    return body


@pytest.mark.asyncio
async def test_destroy_cancels_effect_run_in_progress():
    log: list[str] = []
    release = asyncio.Event()
    e = reactive.effect(slow_effect(log, release))

    flush = asyncio.create_task(reactive.flush())
    assert await wait_until(lambda: log == ["e start"])
    e.destroy()
    await asyncio.wait_for(flush, TIMEOUT)
    assert log == ["e start", "e finally"]
    release.set()
    await asyncio.sleep(0.01)
    assert log == ["e start", "e finally"]


@pytest.mark.asyncio
async def test_destroy_cancels_queued_rerun_waiting_on_previous_run():
    v = reactive.value(0)
    release = asyncio.Event()
    runs: list[int] = []

    @reactive.effect
    async def e():
        runs.append(v())
        await release.wait()

    flush = asyncio.create_task(reactive.flush())
    assert await wait_until(lambda: runs == [0])
    v.set(1)  # the re-run waits for the run in progress
    assert await wait_until(lambda: len(e._run_tasks) == 2)
    e.destroy()
    await asyncio.wait_for(flush, TIMEOUT)
    assert runs == [0]
    assert e._run_tasks == set()


@pytest.mark.asyncio
async def test_destroy_does_not_cancel_finished_or_other_effects():
    log: list[str] = []
    release = asyncio.Event()
    other = reactive.effect(slow_effect(log, release, "other"))

    @reactive.effect
    async def done():
        log.append("done ran")

    flush = asyncio.create_task(reactive.flush())
    assert await wait_until(lambda: "other start" in log and "done ran" in log)
    done.destroy()
    release.set()
    await asyncio.wait_for(flush, TIMEOUT)
    assert log.count("other end") == 1
    other.destroy()


@pytest.mark.asyncio
async def test_effect_that_destroys_itself_keeps_running():
    log: list[str] = []
    holder: list[reactive.Effect_] = []

    @reactive.effect
    async def e():
        holder[0].destroy()
        await asyncio.sleep(0)
        log.append("after destroy")

    holder.append(e)
    await asyncio.wait_for(reactive.flush(), TIMEOUT)
    assert log == ["after destroy"]


@pytest.mark.asyncio
async def test_effect_that_destroys_itself_from_a_child_task_keeps_running():
    # `asyncio.gather()` runs its argument in a child task of the effect's run.
    log: list[str] = []
    holder: list[reactive.Effect_] = []

    async def destroy_self() -> None:
        holder[0].destroy()
        await asyncio.sleep(0)
        log.append("child after destroy")

    @reactive.effect
    async def e():
        await asyncio.gather(destroy_self())
        log.append("after gather")

    holder.append(e)
    await asyncio.wait_for(reactive.flush(), TIMEOUT)
    assert log == ["child after destroy", "after gather"]


@pytest.mark.asyncio
async def test_session_end_cancels_running_effects():
    log: list[str] = []
    release = asyncio.Event()

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        reactive.effect(slow_effect(log, release))

    c = Client(server)
    c.send({"method": "init", "data": {}})
    assert await wait_until(lambda: log == ["e start"])
    await c.close()
    assert await wait_until(lambda: log == ["e start", "e finally"])
    assert c.session._busy_count == 0
    release.set()
    await asyncio.sleep(0.01)
    assert "e end" not in log


@pytest.mark.asyncio
async def test_session_end_cancels_running_render_output():
    log: list[str] = []
    release = asyncio.Event()

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        @render.text
        async def out():
            await slow_effect(log, release, "out")()
            return "done"

    c = RecordingClient(server)
    c.send({"method": "init", "data": {}})
    c.send({"method": "update", "data": {".clientdata_output_out_hidden": False}})
    assert await wait_until(lambda: log == ["out start"])
    await c.close()
    assert await wait_until(lambda: log == ["out start", "out finally"])
    assert c.session._busy_count == 0


@pytest.mark.asyncio
async def test_session_end_does_not_cancel_other_sessions_effects():
    log: list[str] = []
    release = asyncio.Event()
    names = iter(["a", "b"])

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        reactive.effect(slow_effect(log, release, next(names)))

    a = Client(server)
    a.send({"method": "init", "data": {}})
    assert await wait_until(lambda: log == ["a start"])
    b = Client(server)
    try:
        b.send({"method": "init", "data": {}})
        assert await wait_until(lambda: "b start" in log)
        await a.close()
        assert await wait_until(lambda: "a finally" in log)
        release.set()
        assert await wait_until(lambda: "b end" in log)
    finally:
        release.set()
        await b.close()


@pytest.mark.asyncio
async def test_effect_error_closes_session_and_cancels_sibling_effects():
    log: list[str] = []
    release = asyncio.Event()

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        reactive.effect(slow_effect(log, release, "sibling"))

        @reactive.effect
        async def _boom():
            await asyncio.sleep(0.01)
            raise RuntimeError("boom")

        session.on_ended(lambda: log.append("on_ended"))

    c = Client(server)
    try:
        c.send({"method": "init", "data": {}})
        with pytest.warns(ReactiveWarning):
            assert await wait_until(lambda: c.session._has_run_session_ended_tasks)
            assert await wait_until(lambda: "sibling finally" in log)
        assert "sibling end" not in log
        assert await wait_until(lambda: "on_ended" in log)
        assert c.session.id not in c.session.app._sessions
        assert await wait_until(lambda: c.session._busy_count == 0)
    finally:
        await c.close()


@pytest.mark.parametrize("via_child_task", [False, True])
@pytest.mark.asyncio
async def test_effect_that_closes_its_session_finishes_teardown(via_child_task: bool):
    log: list[str] = []
    release = asyncio.Event()

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        reactive.effect(slow_effect(log, release, "sibling"))

        @reactive.effect
        async def _closer():
            await asyncio.sleep(0.01)
            if via_child_task:
                await asyncio.gather(session.close())
            else:
                await session.close()
            await asyncio.sleep(0)
            log.append("closer after close")

        # Registered after both effects, so it runs after they're destroyed.
        session.on_ended(lambda: log.append("on_ended"))

    c = Client(server)
    try:
        c.send({"method": "init", "data": {}})
        assert await wait_until(lambda: "closer after close" in log)
        assert "on_ended" in log
        assert "sibling finally" in log and "sibling end" not in log
        assert c.session.id not in c.session.app._sessions
        assert await wait_until(lambda: c.session._busy_count == 0)
    finally:
        await c.close()


@pytest.mark.asyncio
async def test_destroying_a_scope_cancels_its_effects_before_its_values_go():
    # Without cancelling, the module's effect wakes up, reads its destroyed value,
    # and the DestroyedReactiveError closes the whole session.
    log: list[str] = []
    release = asyncio.Event()

    @module.server
    def mod(input: Inputs, output: Outputs, session: Session) -> None:
        x = reactive.value(1)  # destroyed along with the module's scope

        @reactive.effect
        async def _():
            try:
                log.append("mod start")
                await release.wait()
                log.append(f"mod read {x()}")
            finally:
                log.append("mod finally")

    # An input update would wait for the busy session to go idle, so the removal
    # is triggered from within the server instead.
    remove = asyncio.Event()

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        mod("mod")

        @reactive.effect
        async def _remove():
            await remove.wait()
            await session.destroy("mod")
            release.set()
            log.append("removed")

    c = Client(server)
    try:
        c.send({"method": "init", "data": {}})
        assert await wait_until(lambda: log == ["mod start"])
        remove.set()
        assert await wait_until(lambda: "removed" in log)
        assert await wait_until(lambda: "mod finally" in log)
        await asyncio.sleep(0.02)
        assert sorted(log) == ["mod finally", "mod start", "removed"]
        assert not c.session._has_run_session_ended_tasks
        assert await wait_until(lambda: c.session._busy_count == 0)
    finally:
        await c.close()


@pytest.mark.asyncio
async def test_destroying_a_scope_leaves_other_scopes_running():
    log: list[str] = []
    release = asyncio.Event()

    @module.server
    def mod(input: Inputs, output: Outputs, session: Session, name: str) -> None:
        reactive.effect(slow_effect(log, release, name))
        if name == "a":
            mod("child", "a-child")  # nested, so destroyed along with "a"

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        mod("a", "a")
        mod("ab", "ab")  # shares a prefix with "a" but isn't inside it

        @reactive.effect
        async def _remove():
            await remove.wait()
            await session.destroy("a")

    remove = asyncio.Event()
    c = Client(server)
    try:
        c.send({"method": "init", "data": {}})
        assert await wait_until(lambda: len(log) == 3)
        remove.set()
        assert await wait_until(lambda: "a finally" in log and "a-child finally" in log)
        assert "ab finally" not in log
        release.set()
        assert await wait_until(lambda: "ab end" in log)
    finally:
        release.set()
        await c.close()


@pytest.mark.asyncio
async def test_calc_waiter_recomputes_when_the_run_it_shares_is_cancelled():
    gate = asyncio.Event()
    calc_runs: list[int] = []
    results: list[tuple[str, int]] = []

    @reactive.calc
    async def c():
        calc_runs.append(1)
        await gate.wait()
        return 42

    @reactive.effect
    async def a():
        results.append(("a", await c()))

    @reactive.effect
    async def b():
        results.append(("b", await c()))

    flush = asyncio.create_task(reactive.flush())
    assert await wait_until(lambda: len(calc_runs) == 1)
    await asyncio.sleep(0.01)  # b is now waiting on a's run of the calc
    a.destroy()
    assert await wait_until(lambda: len(calc_runs) == 2)
    gate.set()
    await asyncio.wait_for(flush, TIMEOUT)
    assert results == [("b", 42)]
    b.destroy()


@pytest.mark.asyncio
async def test_calc_recomputes_after_its_run_is_cancelled():
    gate = asyncio.Event()
    calc_runs: list[int] = []

    @reactive.calc
    async def c():
        calc_runs.append(1)
        await gate.wait()
        return 42

    async def read() -> int:
        with reactive.isolate():
            return await c()

    task = asyncio.create_task(read())
    assert await wait_until(lambda: len(calc_runs) == 1)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    gate.set()
    assert await asyncio.wait_for(read(), TIMEOUT) == 42
    assert len(calc_runs) == 2


@pytest.mark.parametrize("cleanup", ["finally", "except_cancelled", "self_destroy"])
@pytest.mark.asyncio
async def test_cleanup_reading_destroyed_scope_values_keeps_session_open(
    cleanup: str,
):
    # A cancelled effect's cleanup runs after the scope's values are destroyed, so
    # reading one raises DestroyedReactiveError. An effect that has been destroyed
    # has no session to protect: the error is logged, not sent to the session.
    log: list[str] = []
    release = asyncio.Event()
    remove = asyncio.Event()

    @module.server
    def mod(input: Inputs, output: Outputs, session: Session) -> None:
        x = reactive.value(1)

        @reactive.effect
        async def _():
            if cleanup == "self_destroy":
                await remove.wait()
                await session.destroy()  # this run isn't cancelled
                log.append(f"after {x()}")
            elif cleanup == "finally":
                try:
                    await release.wait()
                finally:
                    log.append(f"stopped at {x()}")
            else:
                try:
                    await release.wait()
                except asyncio.CancelledError:
                    log.append(f"stopped at {x()}")
                    raise

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        mod("mod")

        @reactive.effect
        async def _remove():
            await remove.wait()
            if cleanup != "self_destroy":
                await session.destroy("mod")
            log.append("removed")

    c = Client(server)
    try:
        c.send({"method": "init", "data": {}})
        await asyncio.sleep(0.02)
        with pytest.warns(ReactiveWarning, match="has been destroyed"):
            remove.set()
            assert await wait_until(lambda: "removed" in log)
            await asyncio.sleep(0.05)
        assert not c.session._has_run_session_ended_tasks
        assert await wait_until(lambda: c.session._busy_count == 0)
    finally:
        release.set()
        await c.close()


@pytest.mark.asyncio
async def test_cancelled_calc_run_does_not_react_to_sources_only_it_read():
    use_a = [True]  # not reactive: run 1 reads `a`, run 2 reads only `b`
    a = reactive.value(0)
    b = reactive.value(0)
    gate = asyncio.Event()
    calc_runs: list[int] = []
    effect_runs: list[int] = []

    @reactive.calc
    async def c() -> int:
        calc_runs.append(1)
        if use_a[0]:
            a()
            await gate.wait()
        else:
            b()
        return 1

    async def read() -> int:
        with reactive.isolate():
            return await c()

    task = asyncio.create_task(read())
    assert await wait_until(lambda: len(calc_runs) == 1)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    use_a[0] = False

    @reactive.effect
    async def e():
        effect_runs.append(await c())

    await asyncio.wait_for(reactive.flush(), TIMEOUT)
    assert (len(calc_runs), effect_runs) == (2, [1])

    a.set(1)  # only the cancelled run read `a`
    await asyncio.wait_for(reactive.flush(), TIMEOUT)
    assert (len(calc_runs), effect_runs) == (2, [1])

    b.set(1)  # the current run read `b`
    await asyncio.wait_for(reactive.flush(), TIMEOUT)
    assert (len(calc_runs), effect_runs) == (3, [1, 1])
    e.destroy()


# ----------------------------------------------------------------------------
# session.run_once_when_idle()
# ----------------------------------------------------------------------------


async def started_client(server: Callable[[Inputs, Outputs, Session], None]) -> Client:
    c = Client(server)
    c.send({"method": "init", "data": {}})
    assert await wait_until(lambda: c.session._output_flush_enabled)
    assert await wait_until(lambda: c.session._busy_count == 0)
    return c


@pytest.mark.asyncio
async def test_run_once_when_idle_runs_on_next_loop_pass_with_session_current():
    c = await started_client(lambda input, output, session: None)
    try:
        ran: list[object] = []
        c.session.run_once_when_idle(lambda: ran.append(get_current_session()))
        assert ran == []  # never synchronously, even when idle
        assert await wait_until(lambda: ran == [c.session])
        await asyncio.sleep(0.02)
        assert len(ran) == 1  # once
    finally:
        await c.close()


@pytest.mark.asyncio
async def test_run_once_when_idle_waits_for_running_effects():
    v = reactive.value(0)
    release = asyncio.Event()
    seen: list[tuple[int, int]] = []

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        @reactive.effect
        @reactive.event(input.go, ignore_init=True)
        async def _slow():
            before = v()
            await release.wait()
            seen.append((before, v()))

    c = Client(server)
    try:
        c.send({"method": "init", "data": {"go": 0}})
        c.update(go=1)
        assert await wait_until(lambda: c.session._busy_count == 1)
        c.session.run_once_when_idle(lambda: v.set(1))
        await asyncio.sleep(0.05)
        assert v._value == 0  # held while the effect runs
        release.set()
        assert await wait_until(lambda: v._value == 1)
        assert seen == [(0, 0)]  # the effect saw a stable value
    finally:
        await c.close()


@pytest.mark.asyncio
async def test_run_once_when_idle_runs_queued_functions_one_cycle_each():
    v = reactive.value(0)
    log: list[str] = []

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        @reactive.effect
        async def _slow():
            n = v()
            log.append(f"effect {n} start")
            await asyncio.sleep(0.02)
            log.append(f"effect {n} end")

    c = await started_client(server)
    try:
        log.clear()

        def set_to(n: int) -> Callable[[], None]:
            def fn() -> None:
                log.append(f"set {n}")
                v.set(n)

            return fn

        c.session.run_once_when_idle(set_to(1))
        c.session.run_once_when_idle(set_to(2))
        assert await wait_until(lambda: "effect 2 end" in log)
        assert log == [
            "set 1",
            "effect 1 start",
            "effect 1 end",
            "set 2",
            "effect 2 start",
            "effect 2 end",
        ]
    finally:
        await c.close()


@pytest.mark.asyncio
async def test_run_once_when_idle_from_a_module_runs_in_the_module_session():
    sessions: dict[str, Session] = {}
    ran: list[object] = []

    @module.server
    def mod(input: Inputs, output: Outputs, session: Session) -> None:
        sessions["mod"] = session
        session.run_once_when_idle(lambda: ran.append(get_current_session()))

    c = await started_client(lambda input, output, session: mod("mod"))
    try:
        assert await wait_until(lambda: len(ran) == 1)
        assert ran == [sessions["mod"]]
        assert sessions["mod"].ns == "mod"
    finally:
        await c.close()


@pytest.mark.asyncio
async def test_run_once_when_idle_rejects_async_functions():
    c = await started_client(lambda input, output, session: None)
    try:

        async def fn() -> None:
            pass

        with pytest.raises(TypeError, match="synchronous"):
            c.session.run_once_when_idle(fn)  # type: ignore[arg-type]
        with pytest.raises(TypeError, match="synchronous"):
            c.session.make_scope("mod").run_once_when_idle(fn)  # type: ignore
    finally:
        await c.close()


@pytest.mark.asyncio
async def test_run_once_when_idle_is_dropped_if_the_session_ends_first():
    release = asyncio.Event()

    def server(input: Inputs, output: Outputs, session: Session) -> None:
        @reactive.effect
        async def _slow():
            await release.wait()

    c = Client(server)
    c.send({"method": "init", "data": {}})
    assert await wait_until(lambda: c.session._busy_count == 1)
    ran: list[bool] = []
    c.session.run_once_when_idle(lambda: ran.append(True))
    await c.close()
    release.set()
    await asyncio.sleep(0.05)
    assert ran == []


@pytest.mark.asyncio
async def test_run_once_when_idle_error_closes_the_session():
    c = await started_client(lambda input, output, session: None)
    try:

        def boom() -> None:
            raise RuntimeError("boom")

        c.session.run_once_when_idle(boom)
        assert await wait_until(lambda: c.session._has_run_session_ended_tasks)
    finally:
        await c.close()
