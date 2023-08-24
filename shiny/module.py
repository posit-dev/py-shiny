__all__ = ("current_namespace", "resolve_id", "ui", "server")

from typing import Callable, TypeVar

from ._namespaces import Id, current_namespace, namespace_context, resolve_id
from ._typing_extensions import Concatenate, ParamSpec
from .session import Inputs, Outputs, Session, require_active_session, session_context

P = ParamSpec("P")
R = TypeVar("R")


def ui(fn: Callable[P, R]) -> Callable[Concatenate[str, P], R]:
    """Decorator for marking UI functions for Shiny modules.

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

    Parameters
    ----------
    fn
        The UI function to decorate.

    Returns
    -------
    :
        The decorated UI function. The function signature will have a new `id` parameter
        inserted at the beginning.

    See Also
    --------
    - ~shiny.module.server for the corresponding decorator for server functions
    - [Introduction to Shiny
      modules](https://shiny.posit.co/py/docs/workflow-modules.html)
    """

    def wrapper(id: Id, *args: P.args, **kwargs: P.kwargs) -> R:
        with namespace_context(id):
            return fn(*args, **kwargs)

    return wrapper


def server(
    fn: Callable[Concatenate[Inputs, Outputs, Session, P], R]
) -> Callable[Concatenate[str, P], R]:
    """Decorator for marking server functions for Shiny modules.

    A Shiny module is a reusable component that can be embedded within Shiny apps or
    other Shiny modules. Each module consists of a UI function and a server function.
    Use this decorator to mark the server function for a module.

    Every Shiny module server function must always begin with the same three arguments:
    `input`, `output`, and `session`, just like a Shiny app's server function.

    After `input`, `output`, and `session`, the server function may include additional
    parameters to be used in the server logic; for example, reactive data sources or
    file paths that need to be provided by the caller.

    This decorator modifies the signature of the decorated server function. The `input`,
    `output`, and `session` parameters are removed, and a new `id` parameter is
    prepended to the signature.

    Parameters
    ----------
    fn
        The server function to decorate. Must have `input`, `output`, and `session` as
        the first three parameters; other parameters may follow.

    Returns
    -------
    :
        The decorated server function. The function signature of `fn` will have been
        modified to remove `input`, `output`, and `session`, and to prepend a new `id`
        parameter.

    See Also
    --------
    - ~shiny.module.ui for the corresponding decorator for UI functions
    - [Introduction to Shiny
        modules](https://shiny.posit.co/py/docs/workflow-modules.html)
    """

    def wrapper(id: Id, *args: P.args, **kwargs: P.kwargs) -> R:
        sess = require_active_session(None)
        child_sess = sess.make_scope(id)
        with session_context(child_sess):
            return fn(child_sess.input, child_sess.output, child_sess, *args, **kwargs)

    return wrapper
