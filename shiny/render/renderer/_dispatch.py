from __future__ import annotations

from typing import Awaitable, Callable, Generic, TypeVar

from ._renderer import Jsonifiable, RendererT

__all__ = ("output_dispatch_handler",)


ObjectT = TypeVar("ObjectT", bound=object)
JsonifiableT = TypeVar("JsonifiableT", bound=Jsonifiable)


class output_dispatch_handler(Generic[RendererT, ObjectT, JsonifiableT]):
    """
    Decorator that marks an renderer method as an output handler.

    The method must take a single argument, and return a JSON-serializable object as the value is sent to the browser.

    By making the renderer method of type `output_dispatch_handler`, the method may be invoked from the browser.

    All handler methods must be named as `_handle_{NAME}` to give context and not invite app authors to execute the method directly.
    """

    def __init__(
        self, fn: Callable[[RendererT, ObjectT], Awaitable[JsonifiableT]]
    ) -> None:
        self.fn = fn

    async def __call__(self, this: RendererT, msg: ObjectT) -> JsonifiableT:
        return await self.fn(this, msg)
