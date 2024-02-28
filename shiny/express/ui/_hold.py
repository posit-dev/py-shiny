from __future__ import annotations

import sys
from types import TracebackType
from typing import Callable, Optional, Type, TypeVar

from htmltools import wrap_displayhook_handler

from ..._docstring import no_example
from ..._typing_extensions import ParamSpec

__all__ = ("hold",)

P = ParamSpec("P")
R = TypeVar("R")
CallableT = TypeVar("CallableT", bound=Callable[..., object])


@no_example()
def hold() -> HoldContextManager:
    """Prevent the display of UI elements in various ways.

    This is used as a context manager, as in `with hold():`. It prevents the display of
    all UI elements within the context block. (This is useful when you want to
    temporarily prevent the display of a large number of UI elements, or when you want
    to prevent the display of UI elements that are not directly under your control.)

    It can also be used as `with hold() as content:` to capture the UI elements that
    would be displayed within the context block. Then, later, you can put `content` on a
    line by itself to display the captured UI elements.

    Returns
    -------
    :
        A context manager that prevents the display of UI elements within the context
        block.

    See Also
    --------
    * ~shiny.render.express
    * ~shiny.express.expressify
    """

    return HoldContextManager()


class HoldContextManager:
    def __init__(self):
        self.content: list[object] = list()

    def __enter__(self) -> list[object]:
        self.prev_displayhook = sys.displayhook
        sys.displayhook = wrap_displayhook_handler(
            self.content.append  # pyright: ignore[reportArgumentType]
        )
        return self.content

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> bool:
        sys.displayhook = self.prev_displayhook
        return False
