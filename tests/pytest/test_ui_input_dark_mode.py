from __future__ import annotations

import pytest
from htmltools import Tag

from shiny import App, ui
from shiny._connection import MockConnection
from shiny.session._session import AppSession
from shiny.ui._input_dark_mode import (
    input_dark_mode,
    update_dark_mode,
    validate_dark_mode_option,
)


def test_validate_dark_mode_option() -> None:
    assert validate_dark_mode_option("light") == "light"
    assert validate_dark_mode_option("dark") == "dark"
    with pytest.raises(ValueError, match="either 'light' or 'dark'"):
        validate_dark_mode_option("auto")  # type: ignore[arg-type]


def test_input_dark_mode_tag() -> None:
    tag = input_dark_mode(id="mode", mode="dark")
    assert isinstance(tag, Tag)
    assert tag.name == "bslib-input-dark-mode"
    assert tag.attrs.get("id") == "mode"
    assert tag.attrs.get("attribute") == "data-bs-theme"
    assert tag.attrs.get("mode") == "dark"


def test_update_dark_mode_sends_message() -> None:
    session = AppSession(App(ui.page_fluid(), None), "id", MockConnection())
    sent: list[dict[str, object]] = []

    def fake_send(msg: dict[str, object]) -> None:
        sent.append(msg)

    session._send_message_sync = fake_send  # type: ignore[assignment]

    update_dark_mode("dark", session=session)
    assert sent == [
        {"custom": {"bslib.toggle-dark-mode": {"method": "toggle", "value": "dark"}}}
    ]
