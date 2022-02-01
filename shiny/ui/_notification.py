__all__ = ("notification_show", "notification_remove")

import sys
from typing import Dict, Union, Optional, Any

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

from htmltools import TagList, TagChildArg

from .._docstring import doc
from .._utils import run_coro_sync, rand_hex
from ..session import Session, require_active_session


@doc(
    "Show a notification to the user.",
    parameters={
        "ui": "Content of message.",
        "action": """
        Message content that represents an action. For example, this could be a link
        that the user can click on. This is separate from ui so customized layouts can
        handle the main notification content separately from action content.
        """,
        "duration": """
        Number of seconds to display the message before it disappears. Use ``None`` to
        make the message not automatically disappear.
        """,
        "close_button": """
        If ``True``, display a button which will make the notification disappear when
        clicked. If ``False`` do not display.
        """,
        "id": """
        An optional unique identifier for the notification. If supplied, any existing
        notification with the same ``id`` will be replaced with this one (otherwise, a
        new notification is created).
        """,
        "type": """
        A string which controls the color of the notification. One of "default" (gray),
        "message" (blue), "warning" (yellow), or "error" (red).
        """,
    },
    returns="The notification's ``id``.",
    see_also=[":func:`~shiny.ui.notification_remove`", ":func:`~shiny.ui.modal`"],
)
def notification_show(
    ui: TagChildArg,
    action: Optional[TagList] = None,
    duration: Optional[Union[int, float]] = 5,
    close_button: bool = True,
    id: Optional[str] = None,
    type: Literal["default", "message", "warning", "error"] = "default",
    session: Optional[Session] = None,
) -> str:
    session = require_active_session(session)

    ui_ = session.process_ui(ui)
    action_ = session.process_ui(action)

    id = id if id else rand_hex(8)

    payload: Dict[str, Any] = {
        "html": ui_["html"],
        "action": action_["html"],
        "deps": ui_["deps"] + action_["deps"],
        "closeButton": close_button,
        "id": id,
        "type": type,
    }

    if duration:
        payload.update({"duration": duration * 1000})

    run_coro_sync(
        session.send_message({"notification": {"type": "show", "message": payload}})
    )

    return id


@doc(
    "Remove a notification.",
    parameters={"id": "A notification ``id``."},
    returns="The notification's ``id``.",
    note="See :func:`~shiny.ui.notification_show` for an example.",
    see_also=[":func:`~shiny.ui.notification_show`", ":func:`~shiny.ui.modal`"],
)
def notification_remove(id: str, session: Optional[Session] = None) -> str:
    session = require_active_session(session)
    run_coro_sync(
        session.send_message({"notification": {"type": "remove", "message": id}})
    )
    return id
