from __future__ import annotations

from typing import cast

from shiny import App, ui
from shiny._connection import MockConnection
from shiny.session._session import AppSession
from shiny.ui._navs_dynamic import insert_nav_panel, remove_nav_panel, update_nav_panel


def test_insert_nav_panel_sends_message() -> None:
    session = AppSession(App(ui.page_fluid(), None), "id", MockConnection())
    sent: list[dict[str, object]] = []

    def fake_send(msg: dict[str, object]) -> None:
        sent.append(msg)

    session._send_message_sync = fake_send  # type: ignore[assignment]

    nav_panel = ui.nav_panel("Title", "Body", value="tab1")
    insert_nav_panel(
        "tabs",
        nav_panel,
        target="target",
        position="before",
        select=True,
        session=session,
    )

    msg = cast(dict[str, object], sent[0]["shiny-insert-tab"])
    assert msg["inputId"] == "tabs"
    assert msg["target"] == "target"
    assert msg["position"] == "before"
    assert msg["select"] is True
    assert "html" in cast(dict[str, object], msg["liTag"])
    assert "html" in cast(dict[str, object], msg["divTag"])


def test_insert_nav_panel_with_string() -> None:
    session = AppSession(App(ui.page_fluid(), None), "id", MockConnection())
    sent: list[dict[str, object]] = []

    def fake_send(msg: dict[str, object]) -> None:
        sent.append(msg)

    session._send_message_sync = fake_send  # type: ignore[assignment]

    insert_nav_panel("tabs", "---", session=session)
    assert "shiny-insert-tab" in sent[0]


def test_remove_and_update_nav_panel() -> None:
    session = AppSession(App(ui.page_fluid(), None), "id", MockConnection())
    sent: list[dict[str, object]] = []

    def fake_send(msg: dict[str, object]) -> None:
        sent.append(msg)

    session._send_message_sync = fake_send  # type: ignore[assignment]

    remove_nav_panel("tabs", "t1", session=session)
    update_nav_panel("tabs", "t1", "hide", session=session)

    remove_msg = cast(dict[str, object], sent[0]["shiny-remove-tab"])
    update_msg = cast(dict[str, object], sent[1]["shiny-change-tab-visibility"])
    assert remove_msg["inputId"] == "tabs"
    assert remove_msg["target"] == "t1"
    assert update_msg["type"] == "hide"
