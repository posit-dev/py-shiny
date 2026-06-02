"""Tests for Shiny test mode (Phase A)."""

from __future__ import annotations

import pytest
from starlette.requests import Request

from shiny import reactive  # noqa: F401  # shared import for later test-mode tasks
from shiny import App, ui
from shiny._connection import MockConnection
from shiny._utils import is_test_mode
from shiny.session._session import AppSession, OutBoundMessageQueues
from shiny.session._utils import (  # noqa: F401  # shared import for later tasks
    session_context,
)


def test_is_test_mode_reads_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SHINY_TESTMODE", raising=False)
    assert is_test_mode() is False

    monkeypatch.setenv("SHINY_TESTMODE", "1")
    assert is_test_mode() is True

    monkeypatch.setenv("SHINY_TESTMODE", "0")
    assert is_test_mode() is False

    monkeypatch.setenv("SHINY_TESTMODE", "true")
    assert is_test_mode() is False


def test_app_reads_test_mode_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SHINY_TESTMODE", "1")
    app_on = App(ui.TagList(), None)
    assert app_on._test_mode is True

    monkeypatch.delenv("SHINY_TESTMODE", raising=False)
    app_off = App(ui.TagList(), None)
    assert app_off._test_mode is False


def _make_app_session() -> AppSession:
    """Create a real AppSession backed by a MockConnection.

    Construct AFTER setting/clearing SHINY_TESTMODE so `app._test_mode` reflects
    the desired state.
    """
    conn = MockConnection()
    return App(ui.TagList(), None)._create_session(conn)


def _snapshot_request() -> Request:
    return Request(
        {
            "type": "http",
            "method": "GET",
            "headers": [],
            "query_string": b"",
            "path": "/",
        }
    )


def test_outbound_queue_records_when_on() -> None:
    omq = OutBoundMessageQueues(record_test_values=True)

    omq.set_value("out1", 42)
    omq.reset()  # a flush clears the transient queues...
    assert omq.test_values == {"out1": 42}  # ...but not the test record

    # set_error supersedes a recorded value for the same id
    omq.set_error("out1", {"message": "boom"})
    assert "out1" not in omq.test_values
    assert omq.test_errors == {"out1": {"message": "boom"}}

    # set_value supersedes a recorded error for the same id
    omq.set_value("out1", 7)
    assert omq.test_values == {"out1": 7}
    assert "out1" not in omq.test_errors


def test_outbound_queue_no_record_when_off() -> None:
    omq = OutBoundMessageQueues(record_test_values=False)
    omq.set_value("out1", 42)
    omq.set_error("out2", {"message": "boom"})
    assert omq.test_values == {}
    assert omq.test_errors == {}


def test_app_session_wires_record_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SHINY_TESTMODE", "1")
    session = _make_app_session()
    assert session._outbound_message_queues._record_test_values is True

    monkeypatch.delenv("SHINY_TESTMODE", raising=False)
    session_off = _make_app_session()
    assert session_off._outbound_message_queues._record_test_values is False
