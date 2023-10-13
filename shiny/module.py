from __future__ import annotations

__all__ = ("current_namespace", "resolve_id", "ui", "server")

from typing import TYPE_CHECKING, Callable, TypeVar

from ._namespaces import Id, current_namespace, namespace_context, resolve_id
from ._typing_extensions import Concatenate, ParamSpec

if TYPE_CHECKING:
    from .session import Inputs, Outputs, Session

P = ParamSpec("P")
R = TypeVar("R")


def ui(fn: Callable[P, R]) -> Callable[Concatenate[str, P], R]:
    def wrapper(id: Id, *args: P.args, **kwargs: P.kwargs) -> R:
        with namespace_context(id):
            return fn(*args, **kwargs)

    return wrapper


def server(
    fn: Callable[Concatenate[Inputs, Outputs, Session, P], R]
) -> Callable[Concatenate[str, P], R]:
    from .session import require_active_session, session_context

    def wrapper(id: Id, *args: P.args, **kwargs: P.kwargs) -> R:
        sess = require_active_session(None)
        child_sess = sess.make_scope(id)
        with session_context(child_sess):
            return fn(child_sess.input, child_sess.output, child_sess, *args, **kwargs)

    return wrapper
