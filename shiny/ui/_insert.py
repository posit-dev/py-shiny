__all__ = ("insert_ui", "remove_ui")

import sys
from typing import Optional

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

from htmltools import TagChildArg

from ..session import Session, require_active_session


def insert_ui(
    ui: TagChildArg,
    selector: str,
    where: Literal["beforeBegin", "afterBegin", "beforeEnd", "afterEnd"] = "beforeEnd",
    multiple: bool = False,
    immediate: bool = False,
    session: Optional[Session] = None,
) -> None:

    session = require_active_session(session)

    def callback() -> None:
        session.send_insert_ui(
            selector=selector,
            multiple=multiple,
            where=where,
            content=session.process_ui(ui),
        )

    if immediate:
        callback()
    else:
        session.on_flushed(callback, once=True)


def remove_ui(
    selector: str,
    multiple: bool = False,
    immediate: bool = False,
    session: Optional[Session] = None,
) -> None:

    session = require_active_session(session)

    def callback():
        session.send_remove_ui(selector=selector, multiple=multiple)

    if immediate:
        callback()
    else:
        session.on_flushed(callback, once=True)
