from __future__ import annotations

from typing import Literal, Optional

from .. import Session
from .._utils import drop_none
from ..module import resolve_id
from ..session import require_active_session
from ._utils import _session_on_flush_send_msg


def toggle_popover(
    id: str,
    show: Optional[bool] = None,
    session: Optional[Session] = None,
) -> None:
    """
    Programmatically show/hide a popover.

    Parameters
    ----------
    id
        The id of the popover DOM element to update.
    show
        Whether to show (`True`) or hide (`False`) the popover. The default
        (`None`) will show if currently hidden and hide if currently shown.
        Note that a popover will not be shown if the trigger is not visible
        (e.g., it is hidden behind a tab).
    session
        A Shiny session object (the default should almost always be used).

    See Also
    --------
    * :func:`~shiny.ui.popover`
    * :func:`~shiny.ui.update_popover`
    """
    session = require_active_session(session)

    _session_on_flush_send_msg(
        id,
        session,
        {
            "method": "toggle",
            "value": _normalize_show_value(show),
        },
    )


def toggle_tooltip(
    id: str, show: Optional[bool] = None, session: Optional[Session] = None
) -> None:
    """
    Programmatically show/hide a tooltip

    Parameters
    ----------
    id
        A character string that matches an existing tooltip id.
    show
        Whether to show (`True`) or hide (`False`) the tooltip. The default (`None`)
        will show if currently hidden and hide if currently shown. Note that a tooltip
        will not be shown if the trigger is not visible (e.g., it's hidden behind a
        tab).
    session
        A Shiny session object (the default should almost always be used).
    """
    _session_on_flush_send_msg(
        id,
        session,
        {
            "method": "toggle",
            "value": _normalize_show_value(show),
        },
    )


def _normalize_show_value(show: bool | None) -> Literal["toggle", "show", "hide"]:
    if show is None:
        return "toggle"
    return "show" if show else "hide"


def toggle_switch(
    id: str, value: Optional[bool] = None, session: Optional[Session] = None
):
    """
    Toggle a switch input.

    Parameters
    ----------
    id
        The id of the switch input.
    value
        The new value of the switch input. If `NULL`, the value will be toggled.
    session
        The session object passed to `server()`.
    """

    if value is not None and not isinstance(value, bool):
        raise TypeError("`value` must be `None` or a single boolean value.")

    msg = drop_none({"id": resolve_id(id), "value": value})
    session = require_active_session(session)

    async def callback():
        await session.send_custom_message("bslib.toggle-input-binary", msg)

    session.on_flush(callback, once=True)
