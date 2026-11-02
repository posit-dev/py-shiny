"""Record a live reactlog from reactive tracer events, per session."""

from __future__ import annotations

import contextlib
import reprlib
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Generator, Mapping
from urllib.parse import urlencode

from htmltools import tags

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
# ponytail: fixed cap on ended sessions kept for viewing; oldest are dropped first.
_MAX_ENDED_SESSIONS = 20

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


@dataclass
class SessionInfo:
    id: str
    start: float
    end: float | None = None
    marks: list[dict[str, Any]] = field(default_factory=list[dict[str, Any]])


class ReactlogRecorder(ReactiveTracer):
    """
    Stores R-reactlog-format entries per session. Events without a session
    (app-level nodes) go to a shared log included in every session's export.
    Ended sessions stay viewable until more than `_MAX_ENDED_SESSIONS` have ended.
    """

    def __init__(self, owns_session: Callable[[str], bool]) -> None:
        self._owns_session = owns_session
        self._logs: dict[str | None, _SessionLog] = {}
        self._sessions: dict[str, SessionInfo] = {}

    def start_session(self, session_id: str) -> None:
        self._sessions.setdefault(
            session_id, SessionInfo(id=session_id, start=time.time())
        )

    def end_session(self, session_id: str, *, marks: list[dict[str, Any]]) -> None:
        info = self._sessions.get(session_id)
        if info is None:
            # Reactlog was enabled after this session started and it logged nothing.
            self.drop_session(session_id)
            return
        info.end = time.time()
        info.marks = list(marks)
        ended = [s for s in self._sessions.values() if s.end is not None]
        ended.sort(key=lambda s: s.end or 0)
        for old in ended[: max(0, len(ended) - _MAX_ENDED_SESSIONS)]:
            self.drop_session(old.id)

    def sessions(self) -> list[SessionInfo]:
        """Known sessions, newest first."""
        return sorted(self._sessions.values(), key=lambda s: s.start, reverse=True)

    def session(self, session_id: str) -> SessionInfo | None:
        return self._sessions.get(session_id)

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
        self._sessions.pop(session_id, None)

    # -- recording ----------------------------------------------------------------

    def _log_for(self, session_id: str | None) -> _SessionLog | None:
        if session_id is not None:
            if not self._owns_session(session_id):
                return None
            # Sessions that started before reactlog was enabled.
            self.start_session(session_id)
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


def _format_time(t: float | None) -> str:
    if t is None:
        return "Active"
    return datetime.fromtimestamp(t).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def session_picker_html(
    sessions: list[SessionInfo], *, query: Mapping[str, str], notice: str | None
) -> str:
    """A page listing recorded sessions; each row links to that session's reactlog."""

    def href(session_id: str) -> str:
        return "?" + urlencode({**query, "session_id": session_id})

    if sessions:
        body = tags.table(
            tags.thead(
                tags.tr(tags.th("Session"), tags.th("Started"), tags.th("Ended"))
            ),
            tags.tbody(
                *(
                    tags.tr(
                        tags.td(tags.a(tags.code(s.id), href=href(s.id))),
                        tags.td(_format_time(s.start)),
                        tags.td(_format_time(s.end)),
                    )
                    for s in sessions
                )
            ),
        )
    else:
        body = tags.p("No sessions recorded yet. Open the app, then refresh this page.")

    page = tags.html(
        tags.head(
            tags.meta(charset="utf-8"),
            tags.title("Reactlog: choose a session"),
            tags.style(
                "body{font-family:system-ui,sans-serif;margin:2rem;}"
                "table{border-collapse:collapse;}"
                "th,td{text-align:left;padding:.4rem .8rem;border-bottom:1px solid #ddd;}"
                "code{font-size:.85em;}"
                ".notice{color:#a33;}"
            ),
        ),
        tags.body(
            tags.h1("Reactlog: choose a session"),
            tags.p(notice, class_="notice") if notice else None,
            body,
        ),
    )
    return "<!DOCTYPE html>\n" + str(page)
