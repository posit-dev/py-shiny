from __future__ import annotations

from typing import cast

import pytest

from shiny import App, ui
from shiny._connection import MockConnection
from shiny.session._session import AppSession
from shiny.ui._notification import notification_remove, notification_show


def test_notification_show_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    session = AppSession(App(ui.page_fluid(), None), "id", MockConnection())
    sent: list[dict[str, object]] = []

    def fake_process_ui(x: object) -> dict[str, object]:
        if x is None:
            return {"html": "", "deps": []}
        return {"html": f"<{x}>", "deps": ["dep"]}

    def fake_send(msg: dict[str, object]) -> None:
        sent.append(msg)

    def fake_rand_hex(_: int) -> str:
        return "abcd1234"

    monkeypatch.setattr("shiny.ui._notification.rand_hex", fake_rand_hex)
    session._process_ui = fake_process_ui  # type: ignore[assignment]
    session._send_message_sync = fake_send  # type: ignore[assignment]

    result_id = notification_show(
        "hello",
        action="do",
        duration=None,
        close_button=False,
        type="warning",
        session=session,
    )

    assert result_id == "abcd1234"
    notification = cast(dict[str, object], sent[0]["notification"])
    payload = cast(dict[str, object], notification["message"])
    assert payload["html"] == "<hello>"
    assert payload["action"] == "<do>"
    assert payload["deps"] == ["dep", "dep"]
    assert payload["closeButton"] is False
    assert payload["type"] == "warning"
    assert payload["duration"] is None


def test_notification_show_duration_zero(monkeypatch: pytest.MonkeyPatch) -> None:
    session = AppSession(App(ui.page_fluid(), None), "id", MockConnection())
    sent: list[dict[str, object]] = []

    session._process_ui = lambda _: {"html": "", "deps": []}  # type: ignore[assignment]
    session._send_message_sync = lambda msg: sent.append(msg)  # type: ignore[assignment]

    notification_show("x", duration=0, session=session)
    notification = cast(dict[str, object], sent[0]["notification"])
    payload = cast(dict[str, object], notification["message"])
    assert "duration" not in payload


def test_notification_remove_sends_message() -> None:
    session = AppSession(App(ui.page_fluid(), None), "id", MockConnection())
    sent: list[dict[str, object]] = []

    session._send_message_sync = lambda msg: sent.append(msg)  # type: ignore[assignment]

    result = notification_remove("note", session=session)
    assert result == "note"
    assert sent == [{"notification": {"type": "remove", "message": "note"}}]
