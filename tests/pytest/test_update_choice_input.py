"""Unit tests for choice-input updates (update_checkbox_group / update_radio_buttons)."""

from __future__ import annotations

from typing import Any, cast

from shiny import ui
from shiny.session import Session
from shiny.ui._input_update import _stringify_selected


class _CaptureSession:
    """Minimal session that records send_input_message calls."""

    def __init__(self) -> None:
        self.messages: list[tuple[str, dict[str, Any]]] = []

    def send_input_message(self, id: str, message: dict[str, Any]) -> None:
        self.messages.append((id, message))


def test_stringify_selected() -> None:
    assert _stringify_selected(None) is None
    assert _stringify_selected("a") == "a"
    assert _stringify_selected(cast(str, 0)) == "0"
    assert _stringify_selected(cast("list[str]", [0, 1, 2])) == ["0", "1", "2"]
    assert _stringify_selected(cast("tuple[str, ...]", (0, 1))) == ["0", "1"]
    assert _stringify_selected(["a", "b"]) == ["a", "b"]


def test_update_checkbox_group_stringifies_int_selected() -> None:
    # Regression for #2272: input_checkbox_group accepts integer choice keys in
    # `selected`, but update_checkbox_group sent them unchanged, so they never
    # matched the (string) option values on the client. They must be stringified.
    sess = _CaptureSession()
    ui.update_checkbox_group(
        "grp", selected=cast("list[str]", [0, 2]), session=cast(Session, sess)
    )
    assert sess.messages == [("grp", {"value": ["0", "2"]})]


def test_update_radio_buttons_stringifies_int_selected() -> None:
    sess = _CaptureSession()
    ui.update_radio_buttons(
        "grp", selected=cast(str, 1), session=cast(Session, sess)
    )
    assert sess.messages == [("grp", {"value": "1"})]
