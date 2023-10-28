from __future__ import annotations

from typing import Literal, Optional

from .._docstring import add_example
from ..session import Session, require_active_session
from ._utils import _session_on_flush_send_msg


@add_example()
# TODO-barret-API; Should toggle methods exist? You should know (or can retrieve) the current state and where you are wanting to go.
def toggle_popover(  # TODO-barret-API; Move into update popover method
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


@add_example()
# TODO-barret-API; Should toggle methods exist? You should know (or can retrieve) the current state and where you are wanting to go.
def toggle_tooltip(  # TODO-barret-API; Move into update tooltip method
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
