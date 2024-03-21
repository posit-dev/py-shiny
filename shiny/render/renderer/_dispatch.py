from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Literal,
    Protocol,
    TypeGuard,
    TypeVar,
    runtime_checkable,
)

from ...types import Jsonifiable

if TYPE_CHECKING:
    from ...session._session import Session


__all__ = (
    "output_binding_request_handler",
    "RendererHasSession",
    "OutputBindingRequestHandler",
    # "is_output_binding_request_handler",
)


@runtime_checkable
class RendererHasSession(Protocol):
    _session: Session


@runtime_checkable
class OutputBindingRequestHandler(Protocol):
    _outputBindingRequestHandler: Literal[True]

    async def __call__(self, arg: Any) -> Jsonifiable: ...


def is_output_binding_request_handler(x: Any) -> TypeGuard[OutputBindingRequestHandler]:
    return callable(x) and (getattr(x, "_outputBindingRequestHandler", False) == True)


# Cast value for within `output_binding_request_handler` dispatching
# Do not include `Renderer` as `self` can not be inspected
OutputBindingRequestHandlerBoundType = Callable[[Any], Awaitable[Jsonifiable]]
OutputBindingRequestHandlerClassType = Callable[[Any, Any], Awaitable[Jsonifiable]]
OutputBindingRequestHandlerT = TypeVar(
    "OutputBindingRequestHandlerT",
    bound=OutputBindingRequestHandlerClassType,
)


def output_binding_request_handler(
    fn: OutputBindingRequestHandlerT,
) -> OutputBindingRequestHandlerT:
    """
    Opt in to browser output binding requests.

    Decorator that marks an renderer method as a method that can handle a output binding
    request from the browser. NOTE: All arguments supplied to `fn` must be validated and
    handled as if the calling user has malicious intent.

    The method must take a single argument, and return a JSON-serializable object as the
    value is sent back to the browser.

    By making the renderer method of type `output_binding_request_handler`, the method
    may be invoked from the browser.

    All handler methods must be named as `_handle_{NAME}` to give context and not invite
    app authors to execute the method directly.
    """

    # Set attr on function to mark it as a output binding request handler
    fn._outputBindingRequestHandler = (  # pyright: ignore[reportFunctionMemberAccess]
        True
    )
    return fn
