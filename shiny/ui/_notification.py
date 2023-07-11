from __future__ import annotations

__all__ = ("notification_show", "notification_remove")

from typing import Any, Literal, Optional

from htmltools import TagChild

from .._docstring import add_example
from .._utils import rand_hex
from ..session import Session, require_active_session


@add_example()
def notification_show(
    ui: TagChild,
    *,
    action: Optional[TagChild] = None,
    duration: Optional[int | float] = 5,
    close_button: bool = True,
    id: Optional[str] = None,
    type: Literal["default", "message", "warning", "error"] = "default",
    session: Optional[Session] = None,
) -> str:
    """
    Show a notification to the user.

    Parameters
    ----------
    ui
        Content of message.
    action
        Message content that represents an action. For example, this could be a link
        that the user can click on. This is separate from ui so customized layouts can
        handle the main notification content separately from action content.
    duration
        Number of seconds to display the message before it disappears. Use ``None`` to
        make the message not automatically disappear.
    close_button
        If ``True``, display a button which will make the notification disappear when
        clicked. If ``False`` do not display.
    id
        An optional unique identifier for the notification. If supplied, any existing
        notification with the same ``id`` will be replaced with this one (otherwise, a
        new notification is created).
    type
        A string which controls the color of the notification. One of "default" (gray),
        "message" (blue), "warning" (yellow), or "error" (red).
    session
        A :class:`~shiny.Session` instance. If not provided, it is inferred via
        :func:`~shiny.session.get_current_session`.

    Returns
    -------
    :
        The notification's ``id``.

    See Also
    -------
    ~shiny.ui.notification_remove
    ~shiny.ui.modal
    """

    session = require_active_session(session)

    ui_ = session._process_ui(ui)
    action_ = session._process_ui(action)

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

    session._send_message_sync({"notification": {"type": "show", "message": payload}})

    return id


def notification_remove(id: str, *, session: Optional[Session] = None) -> str:
    """
    Remove a notification.

    Parameters
    ----------
    id
        A notification ``id``.
    session
        A :class:`~shiny.Session` instance. If not provided, it is inferred via
        :func:`~shiny.session.get_current_session`.

    Returns
    -------
    :
        The notification's ``id``.

    See Also
    -------
    ~shiny.ui.notification_show
    ~shiny.ui.modal

    Example
    -------
    See :func:`notification_show`.
    """
    session = require_active_session(session)
    session._send_message_sync({"notification": {"type": "remove", "message": id}})
    return id
