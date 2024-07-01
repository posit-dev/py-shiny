from __future__ import annotations

__all__ = ("notification_show", "notification_remove")

from typing import Any, Literal, Optional

from htmltools import TagChild

from .._deprecated import _session_param_docs as _session_param
from .._docstring import add_example, doc_format, no_example
from .._utils import rand_hex
from ..session import require_active_session
from ..types import MISSING, MISSING_TYPE


@add_example()
@doc_format(session_param=_session_param)
def notification_show(
    ui: TagChild,
    *,
    action: Optional[TagChild] = None,
    duration: Optional[int | float] = 5,
    close_button: bool = True,
    id: Optional[str] = None,
    type: Literal["default", "message", "warning", "error"] = "default",
    session: MISSING_TYPE = MISSING,
) -> str:
    """
    Show a notification to the user.

    A notification is a message that appears near the bottom corner of the app.
    Notifications normally disappear after a short period of time, and should multiple
    notifications appear together, they will stack on top of one another.

    Parameters
    ----------
    ui
        Contents of the notification message.
    action
        Message content that represents an action. For example, this could be a link
        that the user can click on. This is separate from ui so customized layouts can
        handle the main notification content separately from the action content.
    duration
        Number of seconds to display the message before it disappears. Use ``None`` to
        prevent the message from disappearing automatically. The user will need to click
        the corner of the notification to close it.
    close_button
        If ``True``, display a button which will make the notification disappear when
        clicked. If ``False`` do not display.
    id
        An optional unique identifier for the notification. If supplied, any existing
        notification with the same ``id`` will be replaced with this one (otherwise, a
        new notification is created).
    type
        A string which controls the color of the notification. This should be one of
        "default" (gray), "message" (blue), "warning" (yellow), or "error" (red).
    {session_param}

    Returns
    -------
    :
        The notification's ``id``.

    See Also
    --------
    * :func:`~shiny.ui.notification_remove`
    * :func:`~shiny.ui.modal`
    """

    active_session = require_active_session(session)

    ui_ = active_session._process_ui(ui)
    action_ = active_session._process_ui(action)

    id = id if id else rand_hex(8)

    payload: dict[str, Any] = {
        "html": ui_["html"],
        "action": action_["html"],
        "deps": ui_["deps"] + action_["deps"],
        "closeButton": close_button,
        "id": id,
        "type": type,
    }

    if duration:
        payload.update({"duration": duration * 1000})

    active_session._send_message_sync(
        {"notification": {"type": "show", "message": payload}}
    )

    return id


@no_example()
@doc_format(session_param=_session_param)
def notification_remove(
    id: str,
    *,
    session: MISSING_TYPE = MISSING,
) -> str:
    """
    Remove a notification.

    :func:`~shiny.ui.notification_remove` provides a way to remove a notification programmatically.
    Notifications can also be removed manually by the user, or automatically after a
    specififed amont of time passes.

    Parameters
    ----------
    id
        The ``id`` of the notification to remove.
    {session_param}

    Returns
    -------
    :
        The notification's ``id``.

    See Also
    --------
    * :func:`~shiny.ui.notification_show`
    * :func:`~shiny.ui.modal`

    Example
    -------
    See :func:`shiny.ui.notification_show`.
    """
    active_session = require_active_session(session)
    active_session._send_message_sync(
        {"notification": {"type": "remove", "message": id}}
    )
    return id
