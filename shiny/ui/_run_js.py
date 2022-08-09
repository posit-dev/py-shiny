__all__ = "run_js"

import sys
from typing import Optional

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

from .._docstring import add_example
from ..session import Session, require_active_session


@add_example()
def run_js(
    code: str, immediate: bool = False, session: Optional[Session] = None
) -> None:
    """
    Run JavaScript from server

    Parameters
    ----------
    code
        The arbitrary code snippet you want the session client to run.
    immediate
        Whether the javascript code should be ran immediately, or whether
        Shiny should wait until all outputs have been updated and all effects
        have been run (default).
    session
        A :class:`~shiny.Session` instance. If not provided, it is inferred via
       :func:`~shiny.session.get_current_session`.
    """

    session = require_active_session(session)

    def callback() -> None:
        session._send_run_js(code=code)

    if immediate:
        callback()
    else:
        session.on_flushed(callback, once=True)
