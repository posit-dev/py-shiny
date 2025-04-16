from __future__ import annotations

__all__ = ("current_namespace", "resolve_id", "ui", "server", "ResolvedId")

from typing import TYPE_CHECKING, Callable, TypeVar

from ._docstring import no_example
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


@add_example(ex_dir="../api-examples/Module")
def ui(fn: Callable[P, R]) -> Callable[Concatenate[str, P], R]:
    """Decorator for defining a Shiny module UI function.

    This decorator allows you to write the UI portion of a Shiny module.
    When your decorated `ui` function is called with an `id`,
    the UI elements defined within will automatically be namespaced using that `id`.
    This enables reuse of UI components and consistent input/output handling
    when paired with a `@module.server` function.

    Parameters
    ----------
    fn : Callable[..., R]
        A function that returns a Shiny UI element or layout (e.g., a `ui.panel_*` component).
        This function should **not** accept an `id` parameter itself; the decorator injects it.

    Returns
    -------
    Callable[[str, ...], R]
        A function that takes a `str` `id` as its first argument, followed by any additional
        parameters accepted by `fn`. When called, it returns UI elements with input/output
        IDs automatically namespaced using the provided module `id`.

    See Also
    --------
    * Shiny Modules documentation: https://shiny.posit.co/py/docs/modules.html
    * ~shiny.module.server
    """

    def wrapper(id: Id, *args: P.args, **kwargs: P.kwargs) -> R:
        with namespace_context(id):
            return fn(*args, **kwargs)

    return wrapper


@add_example(ex_dir="../api-examples/Module")
def server(
    fn: Callable[Concatenate[Inputs, Outputs, Session, P], R],
) -> Callable[Concatenate[str, P], R]:
    """Decorator for defining a Shiny module server function.

    This decorator is used to encapsulate the server logic for a Shiny module.
    It automatically creates a namespaced child `Session` using the provided module `id`,
    and passes the appropriate `input`, `output`, and `session` objects to your server function.

    This ensures that the server logic is scoped correctly for each module instance and
    allows for reuse of logic across multiple instances of the same module.

    Parameters
    ----------
    fn : Callable[[Inputs, Outputs, Session, ...], R]
        A server function that takes `input`, `output`, and `session` as its first
        three arguments, followed by any additional arguments defined by the user.

    Returns
    -------
    Callable[[str, ...], R]
        A function that takes a module `id` (as a string) as its first argument,
        followed by any arguments expected by `fn`. When called, it will register
        the module's server logic in a namespaced context.

    See Also
    --------
    * Shiny Modules documentation: https://shiny.posit.co/py/docs/modules.html
    * ~shiny.module.ui
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
