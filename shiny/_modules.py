__all__ = ("namespaced_id", "module_ui", "module_server")

import sys
from typing import Callable, TypeVar

if sys.version_info < (3, 10):
    from typing_extensions import ParamSpec, Concatenate
else:
    from typing import ParamSpec, Concatenate

from ._namespaces import namespaced_id, namespace_context, get_current_namespaces
from .session import Inputs, Outputs, Session, require_active_session, session_context

P = ParamSpec("P")
R = TypeVar("R")


def module_ui(fn: Callable[P, R]) -> Callable[Concatenate[str, P], R]:
    def wrapper(ns: str, *args: P.args, **kwargs: P.kwargs) -> R:
        with namespace_context(get_current_namespaces() + [ns]):
            return fn(*args, **kwargs)

    return wrapper


def module_server(
    fn: Callable[Concatenate[Inputs, Outputs, Session, P], R]
) -> Callable[Concatenate[str, P], R]:
    def wrapper(ns: str, *args: P.args, **kwargs: P.kwargs) -> R:
        sess = require_active_session(None)
        child_sess = sess.make_scope(ns)
        with session_context(child_sess):
            return fn(child_sess.input, child_sess.output, child_sess, *args, **kwargs)

    return wrapper
