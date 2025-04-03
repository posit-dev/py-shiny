from __future__ import annotations

import functools
from typing import Awaitable, Callable, TypeVar, overload

from .._docstring import add_example
from .._typing_extensions import Concatenate, ParamSpec
from .._utils import is_async_callable, not_is_async_callable
from ..module import Id
from ..session._session import Inputs, Outputs, Session
from ..session._utils import require_active_session, session_context
from .expressify_decorator import expressify

T = TypeVar("T")
P = ParamSpec("P")
R = TypeVar("R")

__all__ = ("module",)


@add_example(ex_dir="../api-examples/express_module")
# Use overloads so the function type stays the same for when the user calls it
@overload
def module(
    fn: Callable[Concatenate[Inputs, Outputs, Session, P], Awaitable[R]],
) -> Callable[Concatenate[Id, P], Awaitable[R]]: ...
@overload
def module(
    fn: Callable[Concatenate[Inputs, Outputs, Session, P], R],
) -> Callable[Concatenate[Id, P], R]: ...
def module(
    fn: (
        Callable[Concatenate[Inputs, Outputs, Session, P], R]
        | Callable[Concatenate[Inputs, Outputs, Session, P], Awaitable[R]]
    ),
) -> Callable[Concatenate[Id, P], R] | Callable[Concatenate[Id, P], Awaitable[R]]:
    """
    Create a Shiny module using Shiny Express syntax

    This function is used to create a Shiny module, where the code inside the function
    uses Shiny Express syntax. This is in contrast to the pair of functions
    :func:`~shiny.module.ui()` and :func:`~shiny.module.server()`, which are used to
    create Shiny modules with Core syntax.

    Parameters
    ----------
    fn
        The function that defines the module. The first three parameters of this
        function must be `input`, `output`, and `session`. Any additional parameters can
        used to pass information to the module.

    See Also
    --------
    * ~shiny.module.ui
    * ~shiny.module.server
    * ~shiny.express.expressify
    """
    fn = expressify(fn)

    if is_async_callable(fn):
        # If the function is async, we need to wrap it in an async wrapper
        @functools.wraps(fn)
        async def async_wrapper(id: Id, *args: P.args, **kwargs: P.kwargs) -> R:
            parent_session = require_active_session(None)
            module_session = parent_session.make_scope(id)

            with session_context(module_session):
                return await fn(
                    module_session.input,
                    module_session.output,
                    module_session,
                    *args,
                    **kwargs,
                )

        return async_wrapper

    # Required for type narrowing. `TypeIs` did not seem to work as expected here.
    if not_is_async_callable(fn):

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
                    **kwargs,
                )

        return wrapper

    raise RuntimeError(
        "The provided function must be either synchronous or asynchronous."
    )
