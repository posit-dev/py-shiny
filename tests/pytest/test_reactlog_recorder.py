from __future__ import annotations

import asyncio
from typing import Any, Callable, Iterator

import pytest

from shiny import App, Inputs, Outputs, Session, _reactlog, ui
from shiny._connection import MockConnection
from shiny._inspect import load_reactlog_json
from shiny._reactlog import ReactlogRecorder
from shiny.reactive import Value, calc, effect, flush, isolate
from shiny.reactive._trace import NodeKind, ValueChanged, add_tracer


class FakeNode:
    def __init__(self, node_id: int, label: str, kind: NodeKind = "value") -> None:
        self._node_id = node_id
        self._node_kind: NodeKind = kind
        self._node_label = label
        self._node_fn: Callable[..., object] | None = None
        self._node_session_id: str | None = None


def _change(
    recorder: ReactlogRecorder, sid: str | None, node: FakeNode, value: Any
) -> None:
    recorder.on_value_change(
        ValueChanged(session_id=sid, time=1.0, node=node, value=value)
    )


@pytest.fixture
def recorder() -> Iterator[ReactlogRecorder]:
    r = ReactlogRecorder(owns_session=lambda sid: True)
    remove = add_tracer(r)
    yield r
    remove()


@pytest.mark.asyncio
async def test_recorder_export_round_trips(recorder: ReactlogRecorder) -> None:
    a = Value(1, name="a")
    b = Value(2, name="b")

    @calc
    def c() -> int:
        with isolate():
            b()
        return a()

    @effect
    def e() -> None:
        c()

    await flush()
    data = load_reactlog_json(recorder.export("any-session"))
    labels = {n["label"] for n in data["nodes"]}
    assert {"a", "b", "reactive.calc c", "reactive.effect e"} <= labels

    def rid(node: Any) -> str:
        return f"r{node._node_id}"

    edges = {(x["from"], x["to"], x.get("isolated", False)) for x in data["edges"]}
    assert (rid(a), rid(c), False) in edges
    assert (rid(b), rid(c), True) in edges
    assert (rid(c), rid(e), False) in edges
    assert all(ev["provenance"] == "observed" for ev in data["events"])


def test_recorder_separates_and_drops_sessions() -> None:
    r = ReactlogRecorder(owns_session=lambda sid: True)
    node = FakeNode(1, "input.x")
    _change(r, "s1", node, 1)
    assert any(x["action"] == "valueChange" for x in r.export("s1")["log"])
    assert not any(x["action"] == "valueChange" for x in r.export("s2")["log"])
    r.drop_session("s1")
    assert r.export("s1")["log"] == []


def test_recorder_ignores_foreign_sessions() -> None:
    r = ReactlogRecorder(owns_session=lambda sid: sid == "mine")
    _change(r, "stub-or-other-app", FakeNode(1, "v"), 1)
    assert r.export("stub-or-other-app")["log"] == []
    assert r.export("mine")["log"] == []


def test_recorder_caps_events_but_keeps_nodes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(_reactlog, "_MAX_EVENTS_PER_SESSION", 3)
    r = ReactlogRecorder(owns_session=lambda sid: True)
    node = FakeNode(1, "input.x")
    for i in range(5):
        _change(r, "s1", node, i)
    log = r.export("s1")["log"]
    assert [x["value"] for x in log if x["action"] == "valueChange"] == ["2", "3", "4"]
    assert [x["reactId"] for x in log if x["action"] == "define"] == ["r1"]


def test_recorder_defines_unknown_nodes_lazily_and_refreshes_labels() -> None:
    r = ReactlogRecorder(owns_session=lambda sid: True)
    node = FakeNode(7, "value7")
    _change(r, "s1", node, 1)  # never saw a define event
    node._node_label = "input.renamed"
    _change(r, "s1", node, 2)
    defines = [x for x in r.export("s1")["log"] if x["action"] == "define"]
    assert defines == [
        {
            "action": "define",
            "reactId": "r7",
            "label": "input.renamed",
            "type": "input",
            "session": "s1",
            "time": 1.0,
            "provenance": "observed",
        }
    ]


def test_recorder_value_repr_is_safe() -> None:
    class Boom:
        def __repr__(self) -> str:
            raise RuntimeError("no repr")

    r = ReactlogRecorder(owns_session=lambda sid: True)
    node = FakeNode(1, "v")
    _change(r, "s1", node, "x" * 10_000)
    _change(r, "s1", node, Boom())
    _change(r, "s1", node, list(range(1_000_000)))
    values = [x["value"] for x in r.export("s1")["log"] if x["action"] == "valueChange"]
    assert len(values[0]) <= 210
    assert "Boom" in values[1]
    assert len(values[2]) <= 210


@pytest.mark.asyncio
async def test_cross_session_invalidation_lands_in_reader_session(
    recorder: ReactlogRecorder,
) -> None:
    shared = Value(0, name="shared")
    runs: list[int] = []
    a_ran = asyncio.Event()
    a_reran = asyncio.Event()

    def server_a(input: Inputs, output: Outputs, session: Session) -> None:
        @effect
        def watcher() -> None:
            runs.append(shared())
            (a_reran if len(runs) > 1 else a_ran).set()

    def server_b(input: Inputs, output: Outputs, session: Session) -> None:
        @effect
        def setter() -> None:
            shared.set(input.go())

    conn_a, conn_b = MockConnection(), MockConnection()
    sess_a = App(ui.TagList(), server_a)._create_session(conn_a)
    sess_b = App(ui.TagList(), server_b)._create_session(conn_b)

    async def client() -> None:
        conn_a.cause_receive('{"method":"init","data":{}}')
        await a_ran.wait()
        conn_b.cause_receive('{"method":"init","data":{"go":1}}')
        await a_reran.wait()
        conn_b.cause_disconnect()
        conn_a.cause_disconnect()

    await asyncio.wait_for(
        asyncio.gather(client(), sess_a._run(), sess_b._run()), timeout=5
    )
    assert runs == [0, 1]

    watcher = "reactive.effect watcher"
    log_a = recorder.export(sess_a.id)["log"]
    log_b = recorder.export(sess_b.id)["log"]
    assert any(
        x["action"] == "invalidateStart" and x["label"] == watcher for x in log_a
    )
    assert not [x for x in log_b if x.get("label") == watcher]
