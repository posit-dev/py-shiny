"""Tests for Session.allow_reconnect() method."""

from __future__ import annotations

import asyncio
import json

import pytest

from shiny import App, Inputs, Outputs, Session, ui
from shiny._connection import MockConnection


@pytest.mark.asyncio
async def test_allow_reconnect_true():
    """Test that allow_reconnect(True) sends the correct message."""
    messages: list[str] = []

    def server(input: Inputs, output: Outputs, session: Session):
        session.allow_reconnect(True)

    conn = MockConnection()
    # Capture all messages sent by the session
    original_send = conn.send

    async def capture_send(message: str):
        messages.append(message)
        await original_send(message)

    conn.send = capture_send

    sess = App(ui.TagList(), server)._create_session(conn)

    async def mock_client():
        conn.cause_receive('{"method":"init","data":{}}')
        await asyncio.sleep(0.1)  # Give time for the server to process
        conn.cause_disconnect()

    await asyncio.gather(mock_client(), sess._run())

    # Check that allowReconnect message was sent
    reconnect_messages = [
        msg for msg in messages if "allowReconnect" in msg and msg != "{}"
    ]
    assert len(reconnect_messages) > 0, "No allowReconnect message found"

    # Verify the message content
    for msg in reconnect_messages:
        parsed = json.loads(msg)
        if "allowReconnect" in parsed:
            assert parsed["allowReconnect"] is True
            break
    else:
        pytest.fail("allowReconnect message not found in sent messages")


@pytest.mark.asyncio
async def test_allow_reconnect_false():
    """Test that allow_reconnect(False) sends the correct message."""
    messages: list[str] = []

    def server(input: Inputs, output: Outputs, session: Session):
        session.allow_reconnect(False)

    conn = MockConnection()
    original_send = conn.send

    async def capture_send(message: str):
        messages.append(message)
        await original_send(message)

    conn.send = capture_send

    sess = App(ui.TagList(), server)._create_session(conn)

    async def mock_client():
        conn.cause_receive('{"method":"init","data":{}}')
        await asyncio.sleep(0.1)
        conn.cause_disconnect()

    await asyncio.gather(mock_client(), sess._run())

    # Check that allowReconnect message was sent with False
    reconnect_messages = [
        msg for msg in messages if "allowReconnect" in msg and msg != "{}"
    ]
    assert len(reconnect_messages) > 0, "No allowReconnect message found"

    for msg in reconnect_messages:
        parsed = json.loads(msg)
        if "allowReconnect" in parsed:
            assert parsed["allowReconnect"] is False
            break
    else:
        pytest.fail("allowReconnect message not found in sent messages")


@pytest.mark.asyncio
async def test_allow_reconnect_force():
    """Test that allow_reconnect('force') sends the correct message."""
    messages: list[str] = []

    def server(input: Inputs, output: Outputs, session: Session):
        session.allow_reconnect("force")

    conn = MockConnection()
    original_send = conn.send

    async def capture_send(message: str):
        messages.append(message)
        await original_send(message)

    conn.send = capture_send

    sess = App(ui.TagList(), server)._create_session(conn)

    async def mock_client():
        conn.cause_receive('{"method":"init","data":{}}')
        await asyncio.sleep(0.1)
        conn.cause_disconnect()

    await asyncio.gather(mock_client(), sess._run())

    # Check that allowReconnect message was sent with "force"
    reconnect_messages = [
        msg for msg in messages if "allowReconnect" in msg and msg != "{}"
    ]
    assert len(reconnect_messages) > 0, "No allowReconnect message found"

    for msg in reconnect_messages:
        parsed = json.loads(msg)
        if "allowReconnect" in parsed:
            assert parsed["allowReconnect"] == "force"
            break
    else:
        pytest.fail("allowReconnect message not found in sent messages")


def test_allow_reconnect_invalid_value():
    """Test that allow_reconnect raises ValueError for invalid values."""
    from shiny._connection import MockConnection
    from shiny.session._session import AppSession

    conn = MockConnection()
    sess = AppSession(
        app=App(ui.TagList(), lambda i, o, s: None), id="test", conn=conn
    )

    # Test invalid values
    with pytest.raises(ValueError, match='value must be True, False, or "force"'):
        sess.allow_reconnect("invalid")  # type: ignore

    with pytest.raises(ValueError, match='value must be True, False, or "force"'):
        sess.allow_reconnect(None)  # type: ignore

    with pytest.raises(ValueError, match='value must be True, False, or "force"'):
        sess.allow_reconnect(1)  # type: ignore
