from __future__ import annotations

from typing import Optional

from ... import Session
from ..._utils import drop_none
from ...session import require_active_session


def toggle_switch(
    id: str, value: Optional[bool] = None, session: Optional[Session] = None
):
    """
    Toggle a switch input.

    Parameters
    ----------
    id
        The id of the switch input.
    value
        The new value of the switch input. If `NULL`, the value will be toggled.
    session
        The session object passed to `server()`.
    """

    if value is not None and not isinstance(value, bool):
        raise TypeError("`value` must be `None` or a single boolean value.")

    msg = drop_none({"id": id, "value": value})
    session = require_active_session(session)

    def callback():
        # Question: Any suggestions on how to get around the async/await requirement?
        # `session.send_custom_message("bslib.toggle-input-binary", msg)`
        # Answer (2023-08-15): Using a sync version of `send_custom_message` as this is being
        # used in place of `session.send_input_message` due to code changes not being
        # done in rstudio/shiny
        session._send_message_sync({"custom": {"bslib.toggle-input-binary": msg}})

    session.on_flush(callback, once=True)
