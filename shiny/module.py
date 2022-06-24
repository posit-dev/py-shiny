__all__ = ("resolve_id", "ui", "server")

import sys
from typing import Callable, TypeVar

if sys.version_info < (3, 10):
    from typing_extensions import ParamSpec, Concatenate
else:
    from typing import ParamSpec, Concatenate

from ._namespaces import resolve_id, namespace_context, Id
from .session import Inputs, Outputs, Session, require_active_session, session_context

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
    def wrapper(id: Id, *args: P.args, **kwargs: P.kwargs) -> R:
        sess = require_active_session(None)
        child_sess = sess.make_scope(id)
        with session_context(child_sess):
            return fn(child_sess.input, child_sess.output, child_sess, *args, **kwargs)

    return wrapper
