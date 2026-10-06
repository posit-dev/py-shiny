"""Tests for the private reactive tracer hooks (`shiny.reactive._trace`)."""

from __future__ import annotations

import asyncio
import contextlib
import warnings
from typing import Any, Callable, Generator

import pytest

from shiny import App, module, reactive, ui
from shiny._connection import MockConnection
from shiny.reactive import Value, _trace, calc, effect, flush, isolate
from shiny.reactive._trace import (
    ExecuteEvent,
    NodeKind,
    ReactiveTracer,
    ReactiveTracerWarning,
    ValueChanged,
    add_tracer,
    hooks,
)


class FakeNode:
    def __init__(self, node_id: int, label: str = "", kind: NodeKind = "calc") -> None:
        self._node_id = node_id
        self._node_kind: NodeKind = kind
        self._node_label = label or f"n{node_id}"
        self._node_fn: Callable[..., object] | None = None


def _subscribed(kind: str, tracer: ReactiveTracer) -> bool:
    return any(getattr(cb, "__self__", None) is tracer for cb in getattr(hooks, kind))


def test_dispatch_only_overridden_kinds() -> None:
    class OnlyExecute(ReactiveTracer):
        def on_execute(
            self, event: ExecuteEvent
        ) -> contextlib.AbstractContextManager[None]:
            return contextlib.nullcontext()

    tracer = OnlyExecute()
    remove = add_tracer(tracer)
    assert _subscribed("execute", tracer)
    assert not _subscribed("add_dependency", tracer)
    assert not _subscribed("define_node", tracer)
    remove()
    assert not _subscribed("execute", tracer)
    remove()  # idempotent


def test_point_hook_error_warns_and_continues() -> None:
    seen: list[Any] = []

    class Broken(ReactiveTracer):
        def on_value_change(self, event: ValueChanged) -> None:
            raise RuntimeError("tracer bug")

    class Good(ReactiveTracer):
        def on_value_change(self, event: ValueChanged) -> None:
            seen.append(event.value)

    removers = [add_tracer(Broken()), add_tracer(Good())]
    try:
        with pytest.warns(ReactiveTracerWarning, match="tracer bug"):
            _trace.emit_value_change(FakeNode(1), value=42)
    finally:
        for remove in removers:
            remove()
    assert seen == [42]


def test_span_enter_error_skips_that_tracers_exit() -> None:
    log: list[str] = []

    class BadEnter(ReactiveTracer):
        @contextlib.contextmanager
        def on_execute(self, event: ExecuteEvent) -> Generator[None, None, None]:
            raise RuntimeError("enter bug")
            yield  # pragma: no cover

    class Good(ReactiveTracer):
        @contextlib.contextmanager
        def on_execute(self, event: ExecuteEvent) -> Generator[None, None, None]:
            log.append("enter")
            yield
            log.append("exit")

    removers = [add_tracer(BadEnter()), add_tracer(Good())]
    try:
        with pytest.warns(ReactiveTracerWarning, match="enter bug"):
            with _trace.execute_span(FakeNode(1), ctx_id=1):
                log.append("body")
    finally:
        for remove in removers:
            remove()
    assert log == ["enter", "body", "exit"]


def test_span_exit_error_warns() -> None:
    class BadExit(ReactiveTracer):
        @contextlib.contextmanager
        def on_execute(self, event: ExecuteEvent) -> Generator[None, None, None]:
            yield
            raise RuntimeError("exit bug")

    remove = add_tracer(BadExit())
    try:
        with pytest.warns(ReactiveTracerWarning, match="exit bug"):
            with _trace.execute_span(FakeNode(1), ctx_id=1):
                pass
    finally:
        remove()


def test_span_cannot_swallow_app_exception() -> None:
    class SwallowCM:
        def __enter__(self) -> None:
            return None

        def __exit__(self, *args: object) -> bool:
            return True

    class Swallow(ReactiveTracer):
        def on_execute(
            self, event: ExecuteEvent
        ) -> contextlib.AbstractContextManager[None]:
            return SwallowCM()

    remove = add_tracer(Swallow())
    try:
        with pytest.raises(ValueError, match="app error"):
            with _trace.execute_span(FakeNode(1), ctx_id=1):
                raise ValueError("app error")
    finally:
        remove()


def test_span_passes_base_exceptions_through() -> None:
    seen: list[type[BaseException]] = []

    class Watch(ReactiveTracer):
        @contextlib.contextmanager
        def on_execute(self, event: ExecuteEvent) -> Generator[None, None, None]:
            try:
                yield
            except BaseException as exc:
                seen.append(type(exc))
                raise

    remove = add_tracer(Watch())
    try:
        with pytest.raises(asyncio.CancelledError):
            with _trace.execute_span(FakeNode(1), ctx_id=1):
                raise asyncio.CancelledError()
    finally:
        remove()
    assert seen == [asyncio.CancelledError]


def test_attribute_to_session_sets_session_id() -> None:
    events: list[ValueChanged] = []

    class Cap(ReactiveTracer):
        def on_value_change(self, event: ValueChanged) -> None:
            events.append(event)

    remove = add_tracer(Cap())
    try:
        _trace.emit_value_change(FakeNode(1), value=1)
        with _trace.attribute_to_session("sess-1"):
            _trace.emit_value_change(FakeNode(1), value=2)
    finally:
        remove()
    assert [e.session_id for e in events] == [None, "sess-1"]


def test_node_ids_are_unique() -> None:
    assert _trace.next_node_id() != _trace.next_node_id()


def test_span_completes_exits_before_warning_on_enter_error() -> None:
    """When enter fails and warning raises, already-entered tracers must still exit."""
    log: list[str] = []

    class GoodSpan(ReactiveTracer):
        @contextlib.contextmanager
        def on_execute(self, event: ExecuteEvent) -> Generator[None, None, None]:
            log.append("enter")
            try:
                yield
            finally:
                log.append("exit")

    class BadEnterSpan(ReactiveTracer):
        @contextlib.contextmanager
        def on_execute(self, event: ExecuteEvent) -> Generator[None, None, None]:
            raise RuntimeError("enter crash")
            yield  # pragma: no cover

    removers = [add_tracer(GoodSpan()), add_tracer(BadEnterSpan())]
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", ReactiveTracerWarning)
            with pytest.raises(ReactiveTracerWarning, match="enter crash"):
                with _trace.execute_span(FakeNode(1), ctx_id=1):
                    log.append("body")  # pragma: no cover
    finally:
        for remove in removers:
            remove()
    # GoodSpan's finally block must run even though warning was raised during error handling
    assert log == ["enter", "exit"]


def test_point_hook_calls_all_before_warning_error() -> None:
    """When a tracer raises and warning is configured as error, other tracers must still run."""
    seen: list[object] = []

    class BrokenHook(ReactiveTracer):
        def on_value_change(self, event: ValueChanged) -> None:
            raise RuntimeError("hook crash")

    class GoodHook(ReactiveTracer):
        def on_value_change(self, event: ValueChanged) -> None:
            seen.append(event.value)

    removers = [add_tracer(BrokenHook()), add_tracer(GoodHook())]
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", ReactiveTracerWarning)
            with pytest.raises(ReactiveTracerWarning, match="hook crash"):
                _trace.emit_value_change(FakeNode(1), value=42)
    finally:
        for remove in removers:
            remove()
    # GoodHook must run even though BrokenHook raised
    assert seen == [42]


class Recorder(ReactiveTracer):
    """Records hook calls as tuples keyed by node label."""

    def __init__(self) -> None:
        self.log: list[tuple[Any, ...]] = []

    def on_define_node(self, event: _trace.NodeDefined) -> None:
        self.log.append(("define", event.node._node_label))

    def on_add_dependency(self, event: _trace.DependencyAdded) -> None:
        self.log.append(
            ("add", event.reader._node_label, event.target._node_label, event.isolated)
        )

    def on_remove_dependency(self, event: _trace.DependencyRemoved) -> None:
        self.log.append(
            (
                "remove",
                event.reader._node_label,
                event.target._node_label,
                event.isolated,
            )
        )

    def on_invalidate(self, event: _trace.NodeInvalidated) -> None:
        self.log.append(("invalidate", event.node._node_label))

    def on_value_change(self, event: ValueChanged) -> None:
        self.log.append(("value", event.node._node_label, event.value))

    def on_freeze_value(self, event: _trace.ValueFrozen) -> None:
        self.log.append(("freeze", event.node._node_label))

    @contextlib.contextmanager
    def on_isolate(self, event: _trace.IsolateEvent) -> Generator[None, None, None]:
        reader = event.reader._node_label if event.reader else None
        self.log.append(("isolate_enter", reader))
        yield
        self.log.append(("isolate_exit", reader))

    @contextlib.contextmanager
    def on_execute(self, event: ExecuteEvent) -> Generator[None, None, None]:
        label = event.node._node_label
        self.log.append(("enter", label))
        try:
            yield
        except BaseException as exc:
            self.log.append(("exit", label, type(exc).__name__))
            raise
        self.log.append(("exit", label, None))

    @contextlib.contextmanager
    def on_flush(self, event: _trace.FlushEvent) -> Generator[None, None, None]:
        self.log.append(("flush_start",))
        yield
        self.log.append(("flush_end",))

    def of(self, kind: str) -> list[tuple[Any, ...]]:
        return [x for x in self.log if x[0] == kind]


@pytest.fixture
def rec() -> Generator[Recorder, None, None]:
    recorder = Recorder()
    remove = add_tracer(recorder)
    yield recorder
    remove()


@pytest.mark.asyncio
async def test_define_value_change_freeze(rec: Recorder) -> None:
    v = Value(1, name="v")

    @calc
    def c() -> int:
        return v()

    @effect
    def e() -> None:
        c()

    assert rec.of("define") == [
        ("define", "v"),
        ("define", "reactive.calc c"),
        ("define", "reactive.effect e"),
    ]
    assert len({v._node_id, c._node_id, e._node_id}) == 3
    assert (v._node_kind, c._node_kind, e._node_kind) == ("value", "calc", "effect")

    v.set(2)
    v.set(2)  # same object: no change event
    v.freeze()
    assert rec.of("value") == [("value", "v", 2)]
    assert rec.of("freeze") == [("freeze", "v")]


@pytest.mark.asyncio
async def test_edges_and_dynamic_dependencies(rec: Recorder) -> None:
    # Drain effects left pending by earlier tests so they don't add edges here.
    await flush()
    rec.log.clear()

    use_b = Value(False, name="use_b")
    a = Value(1, name="a")
    b = Value(2, name="b")

    @calc
    def c() -> int:
        return a()

    @effect
    def e() -> None:
        c()
        if use_b():
            b()

    await flush()
    assert rec.of("add") == [
        ("add", "reactive.effect e", "reactive.calc c", False),
        ("add", "reactive.calc c", "a", False),
        ("add", "reactive.effect e", "use_b", False),
    ]

    rec.log.clear()
    use_b.set(True)
    await flush()
    assert ("invalidate", "reactive.effect e") in rec.log
    assert ("remove", "reactive.effect e", "use_b", False) in rec.log
    assert ("remove", "reactive.effect e", "reactive.calc c", False) in rec.log
    assert ("add", "reactive.effect e", "b", False) in rec.log
    # The calc was not invalidated, so its edge to `a` is untouched.
    assert ("remove", "reactive.calc c", "a", False) not in rec.log


def test_value_not_kept_alive_by_dependents_closure() -> None:
    import gc
    import weakref

    from shiny.reactive._core import Context

    gc.disable()
    try:
        v = Value(1, name="v")
        ref = weakref.ref(v)
        ctx = Context()
        with ctx():
            v()
        del v
        assert ref() is None
    finally:
        gc.enable()


@pytest.mark.asyncio
async def test_output_effect_traces_as_output(rec: Recorder) -> None:
    from shiny import App, render, ui
    from shiny._connection import MockConnection

    def server(input: Any, output: Any, session: Any) -> None:
        @render.text
        def txt() -> str:
            return "hi"

    conn = MockConnection()
    sess = App(ui.TagList(), server)._create_session(conn)

    async def mock_client() -> None:
        # Outputs are suspended until the client reports them visible.
        conn.cause_receive(
            '{"method":"init","data":{".clientdata_output_txt_hidden":false}}'
        )
        # Let the output effect run before the session ends.
        await asyncio.sleep(0.1)
        conn.cause_disconnect()

    await asyncio.gather(mock_client(), sess._run())
    assert ("enter", "output txt") in rec.log


@pytest.mark.asyncio
async def test_execute_spans_nest(rec: Recorder) -> None:
    await flush()
    rec.log.clear()
    v = Value(1, name="v")

    @calc
    def c() -> int:
        return v()

    @effect
    def e() -> None:
        c()

    await flush()
    assert [x for x in rec.log if x[0] in ("enter", "exit")] == [
        ("enter", "reactive.effect e"),
        ("enter", "reactive.calc c"),
        ("exit", "reactive.calc c", None),
        ("exit", "reactive.effect e", None),
    ]


@pytest.mark.asyncio
async def test_calc_error_visible_to_tracer_and_still_cached(rec: Recorder) -> None:
    await flush()
    rec.log.clear()

    @calc
    def c() -> int:
        raise ValueError("boom")

    seen: list[int] = []

    @effect
    def e() -> None:
        for _ in range(2):
            try:
                c()
            except ValueError:
                seen.append(1)

    await flush()
    assert seen == [1, 1]
    assert [x for x in rec.of("exit") if x[1] == "reactive.calc c"] == [
        ("exit", "reactive.calc c", "ValueError")
    ]


@pytest.mark.asyncio
async def test_flush_span_encloses_on_flushed_callbacks() -> None:
    from shiny.reactive._core import on_flushed

    order: list[str] = []

    class FlushOrder(ReactiveTracer):
        @contextlib.contextmanager
        def on_flush(self, event: _trace.FlushEvent) -> Generator[None, None, None]:
            order.append("start")
            yield
            order.append("end")

    async def flushed() -> None:
        order.append("flushed")

    remove = add_tracer(FlushOrder())
    unregister = on_flushed(flushed, once=True)
    try:
        await flush()
    finally:
        remove()
        unregister()
    assert order == ["start", "flushed", "end"]


@pytest.mark.asyncio
async def test_isolated_reads_are_isolated_edges(rec: Recorder) -> None:
    await flush()
    rec.log.clear()
    a = Value(1, name="a")
    trig = Value(0, name="trig")

    @effect
    def e() -> None:
        trig()
        with isolate():
            a()

    await flush()
    assert ("add", "reactive.effect e", "a", True) in rec.log
    assert ("isolate_enter", "reactive.effect e") in rec.log

    rec.log.clear()
    trig.set(1)
    await flush()
    assert ("remove", "reactive.effect e", "a", True) in rec.log
    assert ("add", "reactive.effect e", "a", True) in rec.log
    assert ("invalidate", "reactive.effect e") in rec.log

    rec.log.clear()
    a.set(5)  # isolated: must not re-run the effect
    await flush()
    assert rec.of("enter") == []


def test_top_level_isolate_has_no_edges(rec: Recorder) -> None:
    a = Value(1, name="a")
    with isolate():
        a()
    assert rec.of("add") == []
    assert ("isolate_enter", None) in rec.log


async def _run_session(server: Any, *messages: str) -> Any:
    conn = MockConnection()
    sess = App(ui.TagList(), server)._create_session(conn)

    async def mock_client() -> None:
        for message in messages:
            conn.cause_receive(message)
        conn.cause_disconnect()

    await asyncio.gather(mock_client(), sess._run())
    return sess


@pytest.mark.asyncio
async def test_input_value_changes_attributed_to_session() -> None:
    events: list[ValueChanged] = []

    class Cap(ReactiveTracer):
        def on_value_change(self, event: ValueChanged) -> None:
            events.append(event)

    remove = add_tracer(Cap())
    try:
        sess = await _run_session(
            None,
            '{"method":"init","data":{"x":1}}',
            '{"method":"update","data":{"x":2}}',
        )
    finally:
        remove()
    assert [
        (e.node._node_label, e.value, e.session_id)
        for e in events
        if e.node._node_label == "input.x"
    ] == [("input.x", 1, sess.id), ("input.x", 2, sess.id)]


@pytest.mark.asyncio
async def test_module_nodes_use_root_session_id() -> None:
    defined: list[_trace.NodeDefined] = []

    class Cap(ReactiveTracer):
        def on_define_node(self, event: _trace.NodeDefined) -> None:
            defined.append(event)

    @module.server
    def mod_server(input: Any, output: Any, session: Any) -> None:
        @reactive.calc
        def inner() -> int:
            return 1

    def server(input: Any, output: Any, session: Any) -> None:
        mod_server("m")

    remove = add_tracer(Cap())
    try:
        sess = await _run_session(server, '{"method":"init","data":{}}')
    finally:
        remove()
    inner = [e for e in defined if e.node._node_label == "reactive.calc m:inner"]
    assert len(inner) == 1
    assert inner[0].session_id == sess.id
