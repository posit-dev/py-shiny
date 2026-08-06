"""Tests for hard-disconnect: session.close(hard=True, message=...).

Plan A of the hard-disconnect design (server-side only). The matching
client-side handling (4001 close-code recognition, hardDisconnectConfig
custom-message handler, distinct closed-state overlay) lives in R shiny's
srcts and reaches py-shiny when shiny.js is vendored from a release that
includes Plan A's client-side work.
"""

from __future__ import annotations

import json
from typing import Any, Optional, cast

import pytest

from shiny import ui
from shiny._app import App
from shiny._connection import MockConnection
from shiny.session._session import (
    HARD_DISCONNECT_CLOSE_CODE,
    HARD_DISCONNECT_DEFAULT_MESSAGE,
    HARD_DISCONNECT_REASON,
    AppSession,
)


class RecordingConnection(MockConnection):
    """MockConnection that records send() and close() invocations."""

    def __init__(self) -> None:
        super().__init__()
        self.sent: list[str] = []
        self.close_code: Optional[int] = None
        self.close_reason: Optional[str] = None
        self.close_called: bool = False

    async def send(self, message: str) -> None:
        self.sent.append(message)

    async def close(self, code: int, reason: Optional[str]) -> None:
        self.close_called = True
        self.close_code = code
        self.close_reason = reason


def _make_session(
    *, hard_disconnect_message: str | None = None
) -> tuple[AppSession, RecordingConnection]:
    conn = RecordingConnection()
    app = App(ui.TagList(), None, hard_disconnect_message=hard_disconnect_message)
    session = app._create_session(conn)
    return session, conn


def _custom_messages(conn: RecordingConnection) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for payload in conn.sent:
        parsed: Any = json.loads(payload)
        if isinstance(parsed, dict) and "custom" in parsed:
            out.append(cast("dict[str, Any]", parsed["custom"]))
    return out


# ---------------------------------------------------------------------------
# App() arg plumbing
# ---------------------------------------------------------------------------


def test_app_defaults_hard_disconnect_message_to_none():
    app = App(ui.TagList(), None)
    assert app._hard_disconnect_message is None


def test_app_stores_hard_disconnect_message():
    app = App(ui.TagList(), None, hard_disconnect_message="Bye!")
    assert app._hard_disconnect_message == "Bye!"


# ---------------------------------------------------------------------------
# session.close() — soft close (backward compatible)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_soft_close_uses_supplied_code_and_no_custom_message():
    session, conn = _make_session()

    await session.close()  # no args -> soft

    assert conn.close_called is True
    assert conn.close_code == 1001
    assert conn.close_reason is None
    assert _custom_messages(conn) == []
    assert session._was_hard_close is False


@pytest.mark.asyncio
async def test_soft_close_respects_explicit_code():
    session, conn = _make_session()

    await session.close(code=1008)

    assert conn.close_code == 1008
    assert conn.close_reason is None
    assert session._was_hard_close is False


# ---------------------------------------------------------------------------
# session.close(hard=True) — wire protocol
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_hard_close_sends_hard_disconnect_config_and_uses_4001():
    session, conn = _make_session()

    await session.close(hard=True, message="All done.")

    customs = _custom_messages(conn)
    assert len(customs) == 1
    assert customs[0] == {"hardDisconnectConfig": {"message": "All done."}}

    assert conn.close_called is True
    assert conn.close_code == HARD_DISCONNECT_CLOSE_CODE == 4001
    assert conn.close_reason == HARD_DISCONNECT_REASON == "shiny-hard-disconnect"
    assert session._was_hard_close is True


@pytest.mark.asyncio
async def test_hard_close_sends_message_before_close():
    """FIFO ordering: the custom message must be sent before the close frame."""
    session, conn = _make_session()

    # Capture order: record close as a "sent" sentinel for sequencing.
    sequence: list[str] = []

    original_send = conn.send

    async def tracked_send(message: str) -> None:
        sequence.append("send")
        await original_send(message)

    async def tracked_close(code: int, reason: Optional[str]) -> None:
        sequence.append("close")
        conn.close_called = True
        conn.close_code = code
        conn.close_reason = reason

    conn.send = tracked_send  # type: ignore[method-assign]
    conn.close = tracked_close  # type: ignore[method-assign]

    await session.close(hard=True, message="bye")

    assert sequence == ["send", "close"]


# ---------------------------------------------------------------------------
# Message fallback chain
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_hard_close_falls_back_to_app_default_when_message_is_none():
    session, conn = _make_session(hard_disconnect_message="App default text")

    await session.close(hard=True)

    customs = _custom_messages(conn)
    assert customs[0]["hardDisconnectConfig"] == {"message": "App default text"}


@pytest.mark.asyncio
async def test_hard_close_falls_back_to_framework_default_when_nothing_set():
    session, conn = _make_session()

    await session.close(hard=True)

    customs = _custom_messages(conn)
    assert customs[0]["hardDisconnectConfig"] == {
        "message": HARD_DISCONNECT_DEFAULT_MESSAGE
    }
    assert HARD_DISCONNECT_DEFAULT_MESSAGE == "This app has closed."


@pytest.mark.asyncio
async def test_hard_close_per_call_message_overrides_app_default():
    session, conn = _make_session(hard_disconnect_message="App default text")

    await session.close(hard=True, message="Per-call text wins")

    customs = _custom_messages(conn)
    assert customs[0]["hardDisconnectConfig"] == {"message": "Per-call text wins"}


# ---------------------------------------------------------------------------
# Root-level cleanup
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_soft_close_leaves_root_collections_in_place():
    session, _conn = _make_session()

    session._downloads["dl1"] = "info"  # type: ignore[assignment]
    session._dynamic_routes["route1"] = lambda req: None  # type: ignore[arg-type]
    session.set_message_handler("ping", lambda: "pong")

    await session.close()

    # Soft close: the destroy walk does not touch these root collections.
    assert "dl1" in session._downloads
    assert "route1" in session._dynamic_routes
    assert "ping" in session._message_handlers


@pytest.mark.asyncio
async def test_hard_close_clears_root_collections():
    session, _conn = _make_session()

    session._downloads["dl1"] = "info"  # type: ignore[assignment]
    session._dynamic_routes["route1"] = lambda req: None  # type: ignore[arg-type]
    session.set_message_handler("ping", lambda: "pong")

    await session.close(hard=True, message="bye")

    assert session._downloads == {}
    assert session._dynamic_routes == {}
    assert session._message_handlers == {}


# ---------------------------------------------------------------------------
# on_ended ordering: callbacks run BEFORE hard cleanup
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_on_ended_callbacks_see_live_state_before_hard_cleanup():
    session, _conn = _make_session()

    session._downloads["sentinel"] = "still here"  # type: ignore[assignment]

    observed: dict[str, object] = {}

    def on_ended_cb() -> None:
        observed["downloads_at_callback"] = dict(session._downloads)

    session.on_ended(on_ended_cb)

    await session.close(hard=True)

    assert observed["downloads_at_callback"] == {"sentinel": "still here"}
    # And after close completes, the root collection is cleared.
    assert session._downloads == {}


# ---------------------------------------------------------------------------
# SessionProxy.close forwards new kwargs
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_session_proxy_forwards_hard_and_message():
    session, conn = _make_session()
    proxy = session.make_scope("mod1")

    await proxy.close(hard=True, message="from proxy")

    customs = _custom_messages(conn)
    assert len(customs) == 1
    assert customs[0]["hardDisconnectConfig"] == {"message": "from proxy"}
    assert conn.close_code == 4001
    assert session._was_hard_close is True
