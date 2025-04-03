from __future__ import annotations

import functools
from typing import TYPE_CHECKING, Awaitable, Callable, TypeVar, overload

from ._docstring import no_example
from ._namespaces import (
    Id,
    ResolvedId,
    current_namespace,
    namespace_context,
    resolve_id,
)
from ._typing_extensions import Concatenate, ParamSpec
from ._utils import is_async_callable, not_is_async_callable

if TYPE_CHECKING:
    from .session import Inputs, Outputs, Session

__all__ = ("current_namespace", "resolve_id", "ui", "server", "ResolvedId")

P = ParamSpec("P")
R = TypeVar("R")

# Ensure that Id type is not stripped out from .pyi file when generating type stubs
_: Id  # type: ignore


@no_example()
def ui(fn: Callable[P, R]) -> Callable[Concatenate[str, P], R]:
    def wrapper(id: Id, *args: P.args, **kwargs: P.kwargs) -> R:
        with namespace_context(id):
            return fn(*args, **kwargs)

    return wrapper


@no_example()
# Use overloads so the function type stays the same for when the user calls it
@overload
def server(
    fn: Callable[Concatenate[Inputs, Outputs, Session, P], Awaitable[R]],
) -> Callable[Concatenate[str, P], Awaitable[R]]: ...
@overload
def server(
    fn: Callable[Concatenate[Inputs, Outputs, Session, P], R],
) -> Callable[Concatenate[str, P], R]: ...
def server(
    fn: (
        Callable[Concatenate[Inputs, Outputs, Session, P], R]
        | Callable[Concatenate[Inputs, Outputs, Session, P], Awaitable[R]]
    ),
) -> Callable[Concatenate[str, P], R] | Callable[Concatenate[str, P], Awaitable[R]]:
    from .session import require_active_session, session_context

    if is_async_callable(fn):

        @functools.wraps(fn)
        async def async_wrapper(id: Id, *args: P.args, **kwargs: P.kwargs) -> R:
            sess = require_active_session(None)
            child_sess = sess.make_scope(id)
            with session_context(child_sess):
                return await fn(
                    child_sess.input, child_sess.output, child_sess, *args, **kwargs
                )

        return async_wrapper

    # Required for type narrowing. `TypeIs` did not seem to work as expected here.
    if not_is_async_callable(fn):

        @functools.wraps(fn)
        def sync_wrapper(id: Id, *args: P.args, **kwargs: P.kwargs) -> R:
            sess = require_active_session(None)
            child_sess = sess.make_scope(id)
            with session_context(child_sess):
                return fn(
                    child_sess.input, child_sess.output, child_sess, *args, **kwargs
                )

        return sync_wrapper

    raise RuntimeError(
        "The provided function must be either synchronous or asynchronous."
    )
