"""
Private reactive tracer hooks.

Subclass `ReactiveTracer`, override the hooks you need, and register it with
`add_tracer()`. A hook that is not overridden costs nothing: each chokepoint in the
reactive core checks `if hooks.<kind>:` (an empty tuple) before building an event.

Tracers see every session in the process and must filter on `event.session_id`
themselves. Tracers must not hold strong references to event nodes or values.

TODO(trace): events not yet emitted (each is a new no-op hook, so adding one is
non-breaking):
- thaw (shiny has no thaw today; the next `Value.set()` acts as one)
- effect suspend / resume
- async start / stop
- scheduling (`Context.add_pending_flush`)
- node destroy
"""

from __future__ import annotations

import contextlib
import itertools
import time
import warnings
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Callable, ContextManager, Generator, Literal, Optional, Protocol

NodeKind = Literal["value", "calc", "effect", "output"]


class ReactiveTracerWarning(RuntimeWarning):
    """Warning emitted when a tracer hook raises; the app keeps running."""


class ReactiveNode(Protocol):
    """A reactive object (Value, Calc, Effect) as seen by tracers."""

    @property
    def _node_id(self) -> int: ...

    @property
    def _node_kind(self) -> NodeKind: ...

    @property
    def _node_label(self) -> str: ...

    @property
    def _node_fn(self) -> Callable[..., object] | None: ...


@dataclass(frozen=True, slots=True)
class _Event:
    session_id: str | None
    time: float


@dataclass(frozen=True, slots=True)
class NodeDefined(_Event):
    node: ReactiveNode


@dataclass(frozen=True, slots=True)
class DependencyAdded(_Event):
    reader: ReactiveNode
    target: ReactiveNode
    ctx_id: int
    isolated: bool


@dataclass(frozen=True, slots=True)
class DependencyRemoved(_Event):
    reader: ReactiveNode
    target: ReactiveNode
    ctx_id: int
    isolated: bool


@dataclass(frozen=True, slots=True)
class NodeInvalidated(_Event):
    node: ReactiveNode
    ctx_id: int


@dataclass(frozen=True, slots=True)
class ValueChanged(_Event):
    node: ReactiveNode
    value: object


@dataclass(frozen=True, slots=True)
class ValueFrozen(_Event):
    node: ReactiveNode


@dataclass(frozen=True, slots=True)
class IsolateEvent(_Event):
    reader: Optional[ReactiveNode]
    ctx_id: int


@dataclass(frozen=True, slots=True)
class ExecuteEvent(_Event):
    node: ReactiveNode
    ctx_id: int


@dataclass(frozen=True, slots=True)
class FlushEvent(_Event):
    pass


NULL_CM: ContextManager[None] = contextlib.nullcontext()
"""Shared no-op context manager used when no tracer listens to a span kind."""


class ReactiveTracer:
    """
    Base class for reactive tracers. Every hook is a no-op; override the ones you
    need. Span hooks (`on_isolate`, `on_execute`, `on_flush`) return a context
    manager wrapping the operation; its `__exit__` sees any exception raised by the
    operation but can never suppress it.
    """

    def on_define_node(self, event: NodeDefined) -> None:
        pass

    def on_add_dependency(self, event: DependencyAdded) -> None:
        pass

    def on_remove_dependency(self, event: DependencyRemoved) -> None:
        pass

    def on_invalidate(self, event: NodeInvalidated) -> None:
        pass

    def on_value_change(self, event: ValueChanged) -> None:
        pass

    def on_freeze_value(self, event: ValueFrozen) -> None:
        pass

    def on_isolate(self, event: IsolateEvent) -> ContextManager[None]:
        return NULL_CM

    def on_execute(self, event: ExecuteEvent) -> ContextManager[None]:
        return NULL_CM

    def on_flush(self, event: FlushEvent) -> ContextManager[None]:
        return NULL_CM


_KINDS = (
    "define_node",
    "add_dependency",
    "remove_dependency",
    "invalidate",
    "value_change",
    "freeze_value",
    "isolate",
    "execute",
    "flush",
)


class _Hooks:
    """Per-kind tuples of bound tracer hooks. Empty tuple means nobody listens."""

    __slots__ = _KINDS

    def __init__(self) -> None:
        for kind in _KINDS:
            setattr(self, kind, ())

    define_node: tuple[Callable[[NodeDefined], None], ...]
    add_dependency: tuple[Callable[[DependencyAdded], None], ...]
    remove_dependency: tuple[Callable[[DependencyRemoved], None], ...]
    invalidate: tuple[Callable[[NodeInvalidated], None], ...]
    value_change: tuple[Callable[[ValueChanged], None], ...]
    freeze_value: tuple[Callable[[ValueFrozen], None], ...]
    isolate: tuple[Callable[[IsolateEvent], ContextManager[None]], ...]
    execute: tuple[Callable[[ExecuteEvent], ContextManager[None]], ...]
    flush: tuple[Callable[[FlushEvent], ContextManager[None]], ...]


hooks = _Hooks()
_tracers: list[ReactiveTracer] = []
_node_ids = itertools.count()


def next_node_id() -> int:
    return next(_node_ids)


def add_tracer(tracer: ReactiveTracer) -> Callable[[], None]:
    """Register `tracer`; returns a function that removes it (safe to call twice)."""
    _tracers.append(tracer)
    _rebuild_hooks()

    def remove() -> None:
        if tracer in _tracers:
            _tracers.remove(tracer)
            _rebuild_hooks()

    return remove


def _rebuild_hooks() -> None:
    for kind in _KINDS:
        name = f"on_{kind}"
        base = getattr(ReactiveTracer, name)
        setattr(
            hooks,
            kind,
            tuple(
                getattr(t, name) for t in _tracers if getattr(type(t), name) is not base
            ),
        )


# ------------------------------------------------------------------------------
# Session attribution
# ------------------------------------------------------------------------------

_session_id_override: ContextVar[Optional[str]] = ContextVar(
    "shiny_trace_session_id", default=None
)


@contextlib.contextmanager
def attribute_to_session(session_id: str) -> Generator[None, None, None]:
    """
    Attribute events emitted inside this block to `session_id`. Used where shiny
    deliberately runs session code outside `session_context` (initial inputs).
    """
    token = _session_id_override.set(session_id)
    try:
        yield
    finally:
        _session_id_override.reset(token)


def _current_session_id() -> str | None:
    session_id = _session_id_override.get()
    if session_id is not None:
        return session_id
    # Imported here: shiny.session imports shiny.reactive (circular import).
    from ..session._utils import get_current_session

    session = get_current_session()
    return None if session is None else session.id


# ------------------------------------------------------------------------------
# Emitting
# ------------------------------------------------------------------------------


def _warn(hook: object, err: Exception) -> None:
    warnings.warn(
        f"Reactive tracer hook {hook!r} raised {err!r}",
        ReactiveTracerWarning,
        stacklevel=3,
    )


def _call_point(callbacks: tuple[Callable[..., None], ...], event: _Event) -> None:
    for cb in callbacks:
        try:
            cb(event)
        # Broad on purpose: a broken tracer must never break app reactivity.
        except Exception as err:
            _warn(cb, err)


@contextlib.contextmanager
def _span(
    callbacks: tuple[Callable[..., ContextManager[None]], ...], event: _Event
) -> Generator[None, None, None]:
    entered: list[ContextManager[None]] = []
    for cb in callbacks:
        try:
            cm = cb(event)
            cm.__enter__()
            entered.append(cm)
        # Broad on purpose: a broken tracer must never break app reactivity.
        except Exception as err:
            _warn(cb, err)
    try:
        yield
    except BaseException as exc:
        _exit_all(entered, exc)
        raise
    else:
        _exit_all(entered, None)


def _exit_all(entered: list[ContextManager[None]], exc: BaseException | None) -> None:
    for cm in reversed(entered):
        try:
            # The return value is ignored: tracers cannot suppress app exceptions.
            cm.__exit__(
                None if exc is None else type(exc),
                exc,
                None if exc is None else exc.__traceback__,
            )
        # Broad on purpose: a broken tracer must never break app reactivity.
        except Exception as err:
            _warn(cm, err)


def emit_define_node(node: ReactiveNode) -> None:
    _call_point(
        hooks.define_node,
        NodeDefined(session_id=_current_session_id(), time=time.time(), node=node),
    )


def emit_add_dependency(
    *, reader: ReactiveNode, target: ReactiveNode, ctx_id: int, isolated: bool
) -> None:
    _call_point(
        hooks.add_dependency,
        DependencyAdded(
            session_id=_current_session_id(),
            time=time.time(),
            reader=reader,
            target=target,
            ctx_id=ctx_id,
            isolated=isolated,
        ),
    )


def emit_remove_dependency(
    *, reader: ReactiveNode, target: ReactiveNode, ctx_id: int, isolated: bool
) -> None:
    _call_point(
        hooks.remove_dependency,
        DependencyRemoved(
            session_id=_current_session_id(),
            time=time.time(),
            reader=reader,
            target=target,
            ctx_id=ctx_id,
            isolated=isolated,
        ),
    )


def emit_invalidate(node: ReactiveNode, *, ctx_id: int) -> None:
    _call_point(
        hooks.invalidate,
        NodeInvalidated(
            session_id=_current_session_id(), time=time.time(), node=node, ctx_id=ctx_id
        ),
    )


def emit_value_change(node: ReactiveNode, *, value: object) -> None:
    _call_point(
        hooks.value_change,
        ValueChanged(
            session_id=_current_session_id(), time=time.time(), node=node, value=value
        ),
    )


def emit_freeze_value(node: ReactiveNode) -> None:
    _call_point(
        hooks.freeze_value,
        ValueFrozen(session_id=_current_session_id(), time=time.time(), node=node),
    )


def isolate_span(reader: ReactiveNode | None, *, ctx_id: int) -> ContextManager[None]:
    return _span(
        hooks.isolate,
        IsolateEvent(
            session_id=_current_session_id(),
            time=time.time(),
            reader=reader,
            ctx_id=ctx_id,
        ),
    )


def execute_span(node: ReactiveNode, *, ctx_id: int) -> ContextManager[None]:
    return _span(
        hooks.execute,
        ExecuteEvent(
            session_id=_current_session_id(), time=time.time(), node=node, ctx_id=ctx_id
        ),
    )


def flush_span() -> ContextManager[None]:
    return _span(
        hooks.flush, FlushEvent(session_id=_current_session_id(), time=time.time())
    )
