from __future__ import annotations

from typing import cast

import pytest

from shiny import App, ui
from shiny._connection import MockConnection
from shiny.session._session import AppSession
from shiny.ui._progress import Progress


def test_progress_lifecycle_and_updates(monkeypatch: pytest.MonkeyPatch) -> None:
    session = AppSession(App(ui.page_fluid(), None), "id", MockConnection())
    calls: list[tuple[str, dict[str, object]]] = []

    def fake_send(kind: str, msg: dict[str, object]) -> None:
        calls.append((kind, msg))

    def fake_rand_hex(_: int) -> str:
        return "abcd"

    monkeypatch.setattr("shiny.ui._progress.rand_hex", fake_rand_hex)
    session._send_progress = fake_send  # type: ignore[assignment]

    with Progress(min=0, max=10, session=session) as prog:
        prog.set(5, message="half", detail="detail")
        prog.inc(2)
        prog.set(0)
        prog.set(None)

    assert calls[0][0] == "open"
    assert cast(str, calls[0][1]["id"]).endswith("abcd")
    assert calls[1][0] == "update"
    assert calls[1][1]["value"] == 0.5
    assert calls[1][1]["message"] == "half"
    assert calls[1][1]["detail"] == "detail"
    assert calls[-1][0] == "close"


def test_progress_warns_on_double_close(monkeypatch: pytest.MonkeyPatch) -> None:
    session = AppSession(App(ui.page_fluid(), None), "id", MockConnection())
    session._send_progress = lambda *_: None  # type: ignore[assignment]

    prog = Progress(session=session)
    prog.close()
    with pytest.warns(UserWarning, match="already closed"):
        prog.close()
    with pytest.warns(UserWarning, match="already closed"):
        prog.set(1)
