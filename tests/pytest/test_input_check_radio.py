"""
Tests for `input_checkbox_group()` / `input_radio_buttons()` and their `update_*()`
counterparts.

The `update_*()` functions must coerce choice values to strings the same way the
input constructors do, so that `choices={0: "a"}, selected=[0]` behaves identically
to `choices={"0": "a"}, selected=["0"]` (https://github.com/posit-dev/py-shiny/issues/2272).
"""

from __future__ import annotations

from typing import Any

import pytest
from htmltools import TagChild, TagList

from shiny import ui
from shiny.express._stub_session import ExpressStubSession
from shiny.session import Session, session_context
from shiny.session._session import RenderedDeps

CHOICES_INT: dict[int, str] = {0: "a", 1: "b", 2: "c"}
CHOICES_STR: dict[str, str] = {"0": "a", "1": "b", "2": "c"}


class _MessageCapturingSession(ExpressStubSession):
    """Stub session that records `send_input_message()` payloads and renders UI."""

    def __init__(self) -> None:
        super().__init__()
        self.messages: list[dict[str, object]] = []

    def send_input_message(self, id: str, message: dict[str, object]) -> None:
        self.messages.append(message)

    def _process_ui(self, ui: TagChild) -> RenderedDeps:
        return {"deps": [], "html": TagList(ui).get_html_string()}


@pytest.fixture
def session() -> _MessageCapturingSession:
    return _MessageCapturingSession()


def _send(session: Session, fn: Any, **kwargs: Any) -> dict[str, object]:
    with session_context(session):
        fn("x", **kwargs)
    messages = session.messages  # pyright: ignore[reportAttributeAccessIssue]
    assert len(messages) == 1
    return messages.pop()


# ============================================================================
# input_checkbox_group() / input_radio_buttons(): int keys work today
# ============================================================================
def test_input_checkbox_group_int_keys_match_str_keys():
    int_html = ui.input_checkbox_group(
        "x", "L", CHOICES_INT, selected=[0, 2]  # pyright: ignore[reportArgumentType]
    ).get_html_string()
    str_html = ui.input_checkbox_group(
        "x", "L", CHOICES_STR, selected=["0", "2"]
    ).get_html_string()
    assert int_html == str_html
    assert int_html.count('checked="checked"') == 2


def test_input_radio_buttons_int_keys_match_str_keys():
    int_html = ui.input_radio_buttons(
        "x", "L", CHOICES_INT, selected=1  # pyright: ignore[reportArgumentType]
    ).get_html_string()
    str_html = ui.input_radio_buttons(
        "x", "L", CHOICES_STR, selected="1"
    ).get_html_string()
    assert int_html == str_html


# ============================================================================
# update_checkbox_group(): the wire payload must match the string-keyed one
# ============================================================================
def test_update_checkbox_group_int_keys_match_str_keys(
    session: _MessageCapturingSession,
):
    int_msg = _send(
        session,
        ui.update_checkbox_group,
        choices=CHOICES_INT,
        selected=list(CHOICES_INT.keys()),
    )
    str_msg = _send(
        session,
        ui.update_checkbox_group,
        choices=CHOICES_STR,
        selected=list(CHOICES_STR.keys()),
    )
    assert int_msg == str_msg
    # The client matches `value` against the HTML `value` attributes, which are
    # always strings.
    assert int_msg["value"] == ["0", "1", "2"]


def test_update_checkbox_group_int_selected_without_choices(
    session: _MessageCapturingSession,
):
    msg = _send(session, ui.update_checkbox_group, selected=[0, 2])
    assert msg == {"value": ["0", "2"]}


def test_update_checkbox_group_selected_tuple_becomes_list_of_str(
    session: _MessageCapturingSession,
):
    msg = _send(session, ui.update_checkbox_group, selected=(0, 1))
    assert msg == {"value": ["0", "1"]}


def test_update_checkbox_group_scalar_selected_stays_scalar(
    session: _MessageCapturingSession,
):
    # A scalar `selected` must not become a list -- the client handles both, but
    # the shape should round-trip unchanged (apart from the `str()` coercion).
    msg = _send(session, ui.update_checkbox_group, selected=1)
    assert msg == {"value": "1"}


# ============================================================================
# update_radio_buttons(): same defect, same file
# ============================================================================
def test_update_radio_buttons_int_keys_match_str_keys(
    session: _MessageCapturingSession,
):
    int_msg = _send(session, ui.update_radio_buttons, choices=CHOICES_INT, selected=1)
    str_msg = _send(session, ui.update_radio_buttons, choices=CHOICES_STR, selected="1")
    assert int_msg == str_msg
    assert int_msg["value"] == "1"


def test_update_radio_buttons_int_selected_without_choices(
    session: _MessageCapturingSession,
):
    msg = _send(session, ui.update_radio_buttons, selected=2)
    assert msg == {"value": "2"}


# ============================================================================
# `selected=None` must stay absent from the payload (drop_none)
# ============================================================================
def test_update_choice_input_none_selected_is_dropped(
    session: _MessageCapturingSession,
):
    msg = _send(session, ui.update_checkbox_group, label="New label")
    assert "value" not in msg
