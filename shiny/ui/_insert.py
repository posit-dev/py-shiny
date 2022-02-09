__all__ = ("insert_ui", "remove_ui")

import sys
from typing import Optional

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

from htmltools import TagChildArg

from ..session import Session, _require_active_session, _process_deps


def insert_ui(
    ui: TagChildArg,
    selector: str,
    where: Literal["beforeBegin", "afterBegin", "beforeEnd", "afterEnd"] = "beforeEnd",
    multiple: bool = False,
    immediate: bool = False,
    session: Optional[Session] = None,
) -> None:

    session = _require_active_session(session)

    def callback() -> None:
        session.send_insert_ui(
            selector=selector,
            multiple=multiple,
            where=where,
            content=_process_deps(ui, session),
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

    session = _require_active_session(session)

    def callback():
        session.send_remove_ui(selector=selector, multiple=multiple)

    if immediate:
        callback()
    else:
        session.on_flushed(callback, once=True)
