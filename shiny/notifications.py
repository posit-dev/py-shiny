
from typing import TYPE_CHECKING, Union, Optional, Literal, Dict, List, Any
from .utils import run_coro_sync, process_deps, rand_hex
from .shinysession import ShinySession, get_current_session
from htmltools import tag_list

def notification_show(ui, action: Optional[tag_list]=None, duration: Optional[Union[int, float]]=5, close_button: bool=True, id: Optional[str]=None,
                      type: Literal["default", "message", "warning", "error"]="default", session: Optional[ShinySession] = None):
    if session is None:
        session = get_current_session()

    ui_ = process_deps(ui, session)
    action_ = process_deps(action, session)

    payload = {
        "html": ui_["html"],
        "action": action_["html"],
        "deps": ui_["dependencies"] + action_["dependencies"],
        "closeButton": close_button,
        "id": id if id else rand_hex(8),
        "type": type
    }

    if duration:
        payload.update({"duration": duration * 1000})

    return run_coro_sync(session.send_message({"notification": {"type": "show", "message": payload}}))

def notification_remove(id: str, session: Optional[ShinySession] = None):
    if session is None:
        session = get_current_session()
    run_coro_sync(session.send_message({"notification": {"type": "remove", "message": None}}))
    return id
