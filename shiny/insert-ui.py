import sys
from typing import Optional

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

from htmltools import TagList

from .shinysession import ShinySession, _require_active_session, _process_deps


def ui_insert(
    selector: str,
    ui: TagList,
    where: Literal["beforeEnd", "beforeBegin", "afterBegin", "afterEnd"] = "beforeEnd",
    multiple: bool = False,
    immediate: bool = False,
    session: Optional[ShinySession] = None,
):
    session = _require_active_session(session)

    def callback():
        msg = {
            "selector": selector,
            "multiple": multiple,
            "where": where,
            "content": _process_deps(ui, session),
        }
        session.send_message({"shiny-insert-ui": msg})

    # TODO: Should session have an on_flush() method? If not, how to get context object from session?
    callback() if immediate else session.on_flush(callback, once=True)


def ui_remove(
    selector: str,
    multiple: bool = False,
    immediate: bool = False,
    session: Optional[ShinySession] = None,
):
    session = _require_active_session(session)

    def callback():
        session.send_message(
            {"shiny-remove-ui": {"selector": selector, "multiple": multiple}}
        )

    callback() if immediate else session.on_flush(callback, once=True)
