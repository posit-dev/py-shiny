import sys
from typing import Dict, Union, Optional, Any

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

from htmltools import TagList, TagChildArg

from .utils import run_coro_sync, process_deps, rand_hex
from .shinysession import ShinySession, _require_active_session


def notification_show(
    ui: TagChildArg,
    action: Optional[TagList] = None,
    duration: Optional[Union[int, float]] = 5,
    close_button: bool = True,
    id: Optional[str] = None,
    type: Literal["default", "message", "warning", "error"] = "default",
    session: Optional[ShinySession] = None,
):
    session = _require_active_session(session, "notification_show")

    ui_ = process_deps(ui, session)
    action_ = process_deps(action, session)

    payload: Dict[str, Any] = {
        "html": ui_["html"],
        "action": action_["html"],
        "deps": ui_["dependencies"] + action_["dependencies"],
        "closeButton": close_button,
        "id": id if id else rand_hex(8),
        "type": type,
    }

    if duration:
        payload.update({"duration": duration * 1000})

    return run_coro_sync(
        session.send_message({"notification": {"type": "show", "message": payload}})
    )


def notification_remove(id: str, session: Optional[ShinySession] = None):
    session = _require_active_session(session, "notification_show")
    run_coro_sync(
        session.send_message({"notification": {"type": "remove", "message": None}})
    )
    return id
