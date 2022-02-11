__all__ = ("notification_show", "notification_remove")

import sys
from typing import Dict, Union, Optional, Any

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

from htmltools import TagList, TagChildArg

from .._utils import run_coro_sync, rand_hex
from ..session import Session, require_active_session


def notification_show(
    ui: TagChildArg,
    action: Optional[TagList] = None,
    duration: Optional[Union[int, float]] = 5,
    close_button: bool = True,
    id: Optional[str] = None,
    type: Literal["default", "message", "warning", "error"] = "default",
    session: Optional[Session] = None,
) -> None:
    session = require_active_session(session)

    ui_ = session.process_ui(ui)
    action_ = session.process_ui(action)

    payload: Dict[str, Any] = {
        "html": ui_["html"],
        "action": action_["html"],
        "deps": ui_["deps"] + action_["deps"],
        "closeButton": close_button,
        "id": id if id else rand_hex(8),
        "type": type,
    }

    if duration:
        payload.update({"duration": duration * 1000})

    run_coro_sync(
        session.send_message({"notification": {"type": "show", "message": payload}})
    )


def notification_remove(id: str, session: Optional[Session] = None) -> str:
    session = require_active_session(session)
    run_coro_sync(
        session.send_message({"notification": {"type": "remove", "message": None}})
    )
    return id
