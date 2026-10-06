"""Tests for the private reactive tracer hooks (`shiny.reactive._trace`)."""

from __future__ import annotations

import asyncio
import contextlib
from typing import Any, Callable, Generator

import pytest

from shiny.reactive import _trace
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
