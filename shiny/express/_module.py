import functools
from typing import Callable, TypeVar

from .._typing_extensions import Concatenate, ParamSpec
from ..module import Id
from ..session._session import Inputs, Outputs, SessionABC
from ..session._utils import require_active_session, session_context
from .expressify_decorator import expressify

T = TypeVar("T")
P = ParamSpec("P")
R = TypeVar("R")

__all__ = ("module",)


def module(
    fn: Callable[Concatenate[Inputs, Outputs, SessionABC, P], R]
) -> Callable[Concatenate[Id, P], R]:
    fn = expressify(fn)

    @functools.wraps(fn)
    def wrapper(id: Id, *args: P.args, **kwargs: P.kwargs) -> R:
        parent_session = require_active_session(None)
        module_session = parent_session.make_scope(id)

        with session_context(module_session):
            return fn(
                module_session.input,
                module_session.output,
                module_session,
                *args,
                **kwargs
            )

    return wrapper
