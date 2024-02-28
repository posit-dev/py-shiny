from __future__ import annotations

__all__ = ("Progress",)

from types import TracebackType
from typing import TYPE_CHECKING, Optional, Type
from warnings import warn

from .._docstring import add_example
from .._utils import rand_hex
from ..session import require_active_session
from ..session._session import UpdateProgressMessage

if TYPE_CHECKING:
    from .. import Session


@add_example()
class Progress:
    """
    Initialize a progress bar.

    `Progress` creates a computation manager that can be used with `with` to
    run a block of code. Shiny will display a progress bar while the code runs, which
    you can update by calling the `set()` and `message()` methods of the computation
    manager at strategic points in the code block.

    Parameters
    ----------
    min
        The value that represents the starting point of the progress bar. Must be less
        than ``max``.
    max
        The value that represents the end of the progress bar. Must be greater than
        ``min``.
    session
        The :class:`~shiny.Session` instance that the progress bar should appear in. If not
        provided, the session is inferred via :func:`~shiny.session.get_current_session`.
    """

    _style = "notification"

    min: int
    max: int
    value: float | None

    def __init__(
        self, min: int = 0, max: int = 1, session: Optional[Session] = None
    ) -> None:
        self.min = min
        self.max = max
        self.value = None
        self._closed = False
        self._session = require_active_session(session)
        self._id = self._session.ns(rand_hex(8))

        self._session._send_progress("open", {"id": self._id, "style": self._style})

    def __enter__(self) -> "Progress":
        return self

    def __exit__(
        self,
        exctype: Optional[Type[BaseException]],
        excinst: Optional[BaseException],
        exctb: Optional[TracebackType],
    ) -> None:
        self.close()

    def set(
        self,
        value: Optional[float] = None,
        message: Optional[str] = None,
        detail: Optional[str] = None,
    ) -> None:
        """
        Opens and updates the progress panel.

        When called the first time, the progress panel is displayed.

        Parameters
        ----------
        self
            The object instance
        value
            The value at which to set the progress bar, relative to ``min`` and ``max``.
            ``None`` hides the progress bar, if it is currently visible.
        message
            The message to be displayed to the user or ``None`` to hide the current
            message (if any).
        detail
            The detail message to be displayed to the user or ``None`` to hide the
            current detail message (if any). The detail message will be shown with a
            de-emphasized appearance relative to message.
        """

        if self._closed:
            warn("Attempting to set progress, but progress already closed.")
            return None

        self.value = value
        if value:
            # Normalize value to number between 0 and 1
            value = min(1, max(0, (value - self.min) / (self.max - self.min)))

        msg: UpdateProgressMessage = {
            "id": self._id,
            "style": self._style,
        }
        if message is not None:
            msg["message"] = message
        if detail is not None:
            msg["detail"] = detail
        if value is not None:
            msg["value"] = value

        self._session._send_progress("update", msg)

    def inc(
        self,
        amount: float = 0.1,
        message: Optional[str] = None,
        detail: Optional[str] = None,
    ) -> None:
        """
        Increment the progress bar.

        Like ``set``, this updates the progress panel. The difference is that ``inc``
        increases the progress bar by amount, instead of setting it to a specific value.

        Parameters
        ----------
        self
            The object instance
        amount
            The amount to increment in progress.
        message
            The message to be displayed to the user or ``None`` to hide the current
            message (if any).
        detail
            The detail message to be displayed to the user or ``None`` to hide the current
            detail message (if any). The detail message will be shown with a
            de-emphasized appearance relative to message.
        """

        if self.value is None:
            self.value = self.min

        value = min(self.value + amount, self.max)
        self.set(value, message, detail)

    def close(self) -> None:
        """
        Close the progress bar. You can also use the Progress object as a context
        manager, which will cause the progress bar to close on exit.

        Parameters
        ----------
        self
            The object instance

        Note
        ----
        Removes the progress panel. Future calls to set and close will be ignored.
        """
        if self._closed:
            warn("Attempting to close progress, but progress already closed.")
            return None

        self._session._send_progress("close", {"id": self._id, "style": self._style})
        self._closed = True
