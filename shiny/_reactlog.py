"""Record a live reactlog from reactive tracer events, per session."""

from __future__ import annotations

import contextlib
import reprlib
import time
from collections import deque
from typing import Any, Callable, Generator

from .reactive._trace import (
    DependencyAdded,
    DependencyRemoved,
    ExecuteEvent,
    FlushEvent,
    IsolateEvent,
    NodeDefined,
    NodeInvalidated,
    ReactiveNode,
    ReactiveTracer,
    ValueChanged,
    ValueFrozen,
)

# ponytail: fixed cap; make configurable if long sessions need more history.
_MAX_EVENTS_PER_SESSION = 50_000

_repr = reprlib.Repr()
_repr.maxstring = 200
_repr.maxother = 200


def _react_id(node: ReactiveNode) -> str:
    return f"r{node._node_id}"


def _react_type(node: ReactiveNode) -> str:
    kind = node._node_kind
    if kind == "value":
        return "input" if node._node_label.startswith("input.") else "reactiveVal"
    return {"calc": "calc", "effect": "observer", "output": "output"}[kind]


def _safe_repr(value: object) -> str:
    try:
        return _repr.repr(value)
    # reprlib already guards raising __repr__; last-resort guard so recording never breaks.
    except Exception:
        return f"<unrepresentable {type(value).__name__}>"


class _SessionLog:
    __slots__ = ("nodes", "events")

    def __init__(self) -> None:
        self.nodes: dict[str, dict[str, Any]] = {}
        self.events: deque[dict[str, Any]] = deque(maxlen=_MAX_EVENTS_PER_SESSION)


class ReactlogRecorder(ReactiveTracer):
    """
    Stores R-reactlog-format entries per session. Events without a session
    (app-level nodes) go to a shared log included in every session's export.
    """

    def __init__(self, owns_session: Callable[[str], bool]) -> None:
        self._owns_session = owns_session
        self._logs: dict[str | None, _SessionLog] = {}

    def export(self, session_id: str) -> dict[str, Any]:
        shared = self._logs.get(None) or _SessionLog()
        own = self._logs.get(session_id) or _SessionLog()
        nodes = {k: dict(v) for k, v in {**shared.nodes, **own.nodes}.items()}
        log = sorted(
            [*nodes.values(), *shared.events, *own.events], key=lambda x: x["time"]
        )
        return {"version": "1", "session": session_id, "log": log}

    def drop_session(self, session_id: str) -> None:
        self._logs.pop(session_id, None)

    # -- recording ----------------------------------------------------------------

    def _log_for(self, session_id: str | None) -> _SessionLog | None:
        if session_id is not None and not self._owns_session(session_id):
            return None
        log = self._logs.get(session_id)
        if log is None:
            log = self._logs[session_id] = _SessionLog()
        return log

    def _ensure_node(
        self, log: _SessionLog, node: ReactiveNode, session_id: str | None, t: float
    ) -> None:
        rid = _react_id(node)
        label = node._node_label
        rtype = _react_type(node)
        entry = log.nodes.get(rid)
        if entry is None:
            log.nodes[rid] = {
                "action": "define",
                "reactId": rid,
                "label": label,
                "type": rtype,
                "session": session_id,
                "time": t,
                "provenance": "observed",
            }
        else:
            # Inputs and outputs are renamed after they are defined.
            entry["label"] = label
            entry["type"] = rtype

    def _record(
        self,
        session_id: str | None,
        t: float,
        entry: dict[str, Any],
        node: ReactiveNode | None = None,
        other: ReactiveNode | None = None,
    ) -> None:
        log = self._log_for(session_id)
        if log is None:
            return
        for n in (node, other):
            if n is not None:
                self._ensure_node(log, n, session_id, t)
        if node is not None:
            entry.update(
                reactId=_react_id(node), label=node._node_label, type=_react_type(node)
            )
        entry.update(session=session_id, time=t, provenance="observed")
        log.events.append(entry)

    # -- hooks --------------------------------------------------------------------

    def on_define_node(self, event: NodeDefined) -> None:
        log = self._log_for(event.session_id)
        if log is not None:
            self._ensure_node(log, event.node, event.session_id, event.time)

    def on_add_dependency(self, event: DependencyAdded) -> None:
        self._record(
            event.session_id,
            event.time,
            {
                "action": "dependsOn",
                "depOnReactId": _react_id(event.target),
                "ctxId": event.ctx_id,
                "isolate": event.isolated,
            },
            event.reader,
            event.target,
        )

    def on_remove_dependency(self, event: DependencyRemoved) -> None:
        self._record(
            event.session_id,
            event.time,
            {
                "action": "dependsOnRemove",
                "depOnReactId": _react_id(event.target),
                "ctxId": event.ctx_id,
                "isolate": event.isolated,
            },
            event.reader,
            event.target,
        )

    def on_invalidate(self, event: NodeInvalidated) -> None:
        self._record(
            event.session_id,
            event.time,
            {"action": "invalidateStart", "ctxId": event.ctx_id},
            event.node,
        )

    def on_value_change(self, event: ValueChanged) -> None:
        self._record(
            event.session_id,
            event.time,
            {"action": "valueChange", "value": _safe_repr(event.value)},
            event.node,
        )

    def on_freeze_value(self, event: ValueFrozen) -> None:
        self._record(event.session_id, event.time, {"action": "freeze"}, event.node)

    @contextlib.contextmanager
    def on_isolate(self, event: IsolateEvent) -> Generator[None, None, None]:
        if event.reader is None:
            yield
            return
        entry = {"ctxId": event.ctx_id}
        self._record(
            event.session_id,
            event.time,
            {"action": "isolateEnter", **entry},
            event.reader,
        )
        try:
            yield
        finally:
            self._record(
                event.session_id,
                time.time(),
                {"action": "isolateExit", **entry},
                event.reader,
            )

    @contextlib.contextmanager
    def on_execute(self, event: ExecuteEvent) -> Generator[None, None, None]:
        self._record(
            event.session_id,
            event.time,
            {"action": "enter", "ctxId": event.ctx_id},
            event.node,
        )
        exit_entry: dict[str, Any] = {"action": "exit", "ctxId": event.ctx_id}
        try:
            yield
        except BaseException as exc:
            exit_entry["error"] = _safe_repr(exc)
            raise
        finally:
            self._record(event.session_id, time.time(), exit_entry, event.node)

    @contextlib.contextmanager
    def on_flush(self, event: FlushEvent) -> Generator[None, None, None]:
        try:
            yield
        finally:
            self._record(event.session_id, time.time(), {"action": "queueEmpty"})
