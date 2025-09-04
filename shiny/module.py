from __future__ import annotations

__all__ = ("current_namespace", "resolve_id", "ui", "server", "ResolvedId")

from typing import TYPE_CHECKING, Callable, TypeVar

from ._docstring import add_example
from ._namespaces import (
    Id,
    ResolvedId,
    current_namespace,
    namespace_context,
    resolve_id,
)
from ._typing_extensions import Concatenate, ParamSpec

if TYPE_CHECKING:
    from .session import Inputs, Outputs, Session

P = ParamSpec("P")
R = TypeVar("R")

# Ensure that Id type is not stripped out from .pyi file when generating type stubs
_: Id  # type: ignore


@add_example(ex_dir="api-examples/Module")
def ui(fn: Callable[P, R]) -> Callable[Concatenate[str, P], R]:
    """
    Decorator for defining a Shiny module UI function.

    A Shiny module is a reusable component that can be embedded within Shiny apps or
    other Shiny modules. Each module consists of a UI function and a server function.
    Use this decorator to mark the UI function for a module.

    The UI function can take whatever parameters are required to create the UI; for
    example, a label or a default value. It can also take no parameters, if none are
    required.

    Whatever parameters the UI function takes, the `ui` decorator will prepend the
    signature with a new `id` argument. This argument will be an id string passed by the
    caller, that uniquely identifies the module instance within the calling scope.

    When the decorated function is called, any Shiny input or output elements created
    within the function will automatically have their `id` values prefixed with the
    module instance's `id`. This ensures that the input and output elements are uniquely
    namespaced and won't conflict with other elements in the same app.

    This enables reuse of UI components and consistent input/output handling
    when paired with a :func:`shiny.module.server` function.

    Parameters
    ----------
    fn
        A function that returns a Shiny UI element or layout (e.g., a `ui.panel_*` component).
        This function should **not** accept an `id` parameter itself; the decorator injects it.

    Returns
    -------
    :
        The decorated UI function. The function takes a `str` `id` as its first argument,
        followed by any additional parameters accepted by `fn`.
        When called, it returns UI elements with input/output
        IDs automatically namespaced using the provided module `id`.

    See Also
    --------
    * Shiny Modules documentation: <https://shiny.posit.co/py/docs/modules.html>
    * :func:`shiny.module.server`
    """

    def wrapper(id: Id, *args: P.args, **kwargs: P.kwargs) -> R:
        with namespace_context(id):
            return fn(*args, **kwargs)

    return wrapper


@add_example(ex_dir="api-examples/Module")
def server(
    fn: Callable[Concatenate[Inputs, Outputs, Session, P], R],
) -> Callable[Concatenate[str, P], R]:
    """
    Decorator for defining a Shiny module server function.

    A Shiny module is a reusable component that can be embedded within Shiny apps or
    other Shiny modules. Each module consists of a UI function and a server function.
    This decorator is used to encapsulate the server logic for a Shiny module.

    Every Shiny module server function must always begin with the same three arguments:
    `input`, `output`, and `session`, just like a Shiny app's server function.

    After `input`, `output`, and `session`, the server function may include additional
    parameters to be used in the server logic; for example, reactive data sources or
    file paths that need to be provided by the caller.

    This decorator modifies the signature of the decorated server function. The `input`,
    `output`, and `session` parameters are removed, and a new `id` parameter is
    prepended to the signature.

    This decorator is used to encapsulate the server logic for a Shiny module.
    It automatically creates a namespaced child `Session` using the provided module `id`,
    and passes the appropriate `input`, `output`, and `session` objects to your server function.

    This ensures that the server logic is scoped correctly for each module instance and
    allows for reuse of logic across multiple instances of the same module.

    Parameters
    ----------
    fn
        A server function that takes `input`, `output`, and `session` as its first
        three arguments, followed by any additional arguments defined by the user.

    Returns
    -------
    :
        The decorated server function.
        A function that takes a module `id` (as a string) as its first argument,
        followed by any arguments expected by `fn`. When called, it will register
        the module's server logic in a namespaced context.
        The function signature of `fn` will have been
        modified to remove `input`, `output`, and `session`, and to prepend a new `id`
        parameter.

    See Also
    --------
    * Shiny Modules documentation: <https://shiny.posit.co/py/docs/modules.html>
    * :func:`shiny.module.ui`
    """
    from .session import require_active_session, session_context

    def wrapper(id: Id, *args: P.args, **kwargs: P.kwargs) -> R:
        sess = require_active_session(None)
        child_sess = sess.make_scope(id)
        with session_context(child_sess):
            return fn(
                child_sess.input,
                child_sess.output,
                child_sess,
                *args,
                **kwargs,
            )

    return wrapper
