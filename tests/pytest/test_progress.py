from __future__ import annotations

from typing import Any, cast

from shiny import ui
from shiny.express._stub_session import ExpressStubSession


def test_progress_set_normalizes_zero():
    sent: list[dict[str, Any]] = []
    session = ExpressStubSession()
    session._send_progress = lambda type, message: sent.append(
        cast("dict[str, Any]", message)
    )

    progress = ui.Progress(min=-10, max=10, session=session)
    values: list[float] = []
    for value in (-5, 0, 5):
        progress.set(value)
        values.append(sent[-1]["value"])

    assert values == [0.25, 0.5, 0.75]
