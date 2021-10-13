from typing import Optional, Literal
from htmltools import TagList
from .shinysession import ShinySession, get_current_session
from .utils import process_deps


def ui_insert(
    selector: str,
    ui: TagList,
    where: Literal["beforeEnd", "beforeBegin", "afterBegin", "afterEnd"] = "beforeEnd",
    multiple: bool = False,
    immediate: bool = False,
    session: Optional[ShinySession] = None,
):
    if not session:
        session = get_current_session()

    def callback():
        msg = {
            "selector": selector,
            "multiple": multiple,
            "where": where,
            "content": process_deps(ui, session),
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
    if not session:
        session = get_current_session()

    def callback():
        session.send_message(
            {"shiny-remove-ui": {"selector": selector, "multiple": multiple}}
        )

    callback() if immediate else session.on_flush(callback, once=True)
