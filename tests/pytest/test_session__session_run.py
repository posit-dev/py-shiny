from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from shiny import App, ui
from shiny._connection import MockConnection
from shiny._namespaces import ResolvedId
from shiny.session._session import AppSession


@pytest.mark.asyncio
async def test_close_removes_session_from_app_and_invokes_on_ended(
    capsys: pytest.CaptureFixture[str],
):
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    app._debug = True  # type: ignore[assignment]
    session = AppSession(app, "id", conn, debug=True)
    app._sessions[session.id] = session
    session._conn.close = AsyncMock()  # type: ignore[assignment]
    called: list[str] = []

    @session.on_ended
    async def _():
        called.append("done")

    await session.close()
    assert called == ["done"]
    assert session.id not in app._sessions
    captured = capsys.readouterr()
    assert "remove_session:" in captured.out


@pytest.mark.asyncio
async def test_session_on_ended_callbacks_and_close():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)
    app._sessions[session.id] = session
    session._conn.close = AsyncMock()  # type: ignore[assignment]
    called: list[str] = []

    @session.on_ended
    async def _():
        called.append("done")

    await session.close()
    assert called == ["done"]


@pytest.mark.asyncio
async def test_run_handles_invalid_json_and_missing_method():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)
    app._sessions[session.id] = session
    conn.cause_receive("not-json")
    await session._run()

    conn = MockConnection()
    session = AppSession(app, "id2", conn)
    app._sessions[session.id] = session
    conn.cause_receive("{}")
    await session._run()


@pytest.mark.asyncio
async def test_run_handles_init_and_update_messages(monkeypatch: pytest.MonkeyPatch):
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    app._request_flush = lambda _session: None  # type: ignore[assignment]
    session = AppSession(app, "id", conn)
    app._sessions[session.id] = session

    session.app.server = lambda input, output, sess: None
    monkeypatch.setattr(
        "shiny.session._session.reactive_flush", lambda: asyncio.sleep(0)
    )
    session.bookmark._create_effects = lambda: None  # type: ignore[assignment]

    def _set_restore_context(ctx: object) -> None:
        setattr(session.bookmark, "_restore_context_value", ctx)

    session.bookmark._set_restore_context = _set_restore_context  # type: ignore[assignment, attr-defined]

    conn.cause_receive('{"method":"init","data":{".clientdata_pixelratio":1}}')
    conn.cause_receive('{"method":"update","data":{".clientdata_pixelratio":2}}')
    conn.cause_disconnect()

    await session._run()
    assert session.input[ResolvedId(".clientdata_pixelratio")]._value == 2
    assert session.bookmark._restore_context is not None
    assert session.bookmark._restore_context.active is False


@pytest.mark.asyncio
async def test_run_handles_unhandled_errors():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    app._request_flush = lambda _session: None  # type: ignore[assignment]
    session = AppSession(app, "id", conn)
    app._sessions[session.id] = session
    session.app.server = lambda input, output, sess: None

    def _raise():
        raise RuntimeError("boom")

    session._print_error_message = _raise  # type: ignore[assignment]

    conn.cause_receive('{"method":"init","data":{}}')
    conn.cause_disconnect()

    await session._run()


@pytest.mark.asyncio
async def test_run_init_requires_bookmark_app(monkeypatch: pytest.MonkeyPatch):
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    app._request_flush = lambda _session: None  # type: ignore[assignment]
    session = AppSession(app, "id", conn)
    app._sessions[session.id] = session
    session.app.server = lambda input, output, sess: None
    monkeypatch.setattr(
        "shiny.session._session.reactive_flush", lambda: asyncio.sleep(0)
    )
    session.bookmark = object()  # type: ignore[assignment]
    session._print_error_message = lambda _: (_ for _ in ()).throw(
        RuntimeError("fail")
    )  # type: ignore[assignment]

    conn.cause_receive('{"method":"init","data":{}}')
    conn.cause_disconnect()

    await session._run()


@pytest.mark.asyncio
async def test_run_init_with_bookmark_url_search(monkeypatch: pytest.MonkeyPatch):
    conn = MockConnection()
    app = App(lambda req: ui.page_fluid(), None, bookmark_store="url")
    app._request_flush = lambda _session: None  # type: ignore[assignment]
    session = AppSession(app, "id", conn, debug=True)
    app._sessions[session.id] = session
    session.app.server = lambda input, output, sess: None
    monkeypatch.setattr(
        "shiny.session._session.reactive_flush", lambda: asyncio.sleep(0)
    )
    session.bookmark._create_effects = lambda: None  # type: ignore[assignment]
    conn.cause_receive('{"method":"init","data":{".clientdata_url_search":"?a=1"}}')
    conn.cause_disconnect()

    await session._run()
    assert session.bookmark._restore_context is not None
    assert session.bookmark._restore_context.active is True


@pytest.mark.asyncio
async def test_run_dispatches_request_messages(monkeypatch: pytest.MonkeyPatch):
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    app._request_flush = lambda _session: None  # type: ignore[assignment]
    session = AppSession(app, "id", conn)
    app._sessions[session.id] = session
    session.app.server = lambda input, output, sess: None
    monkeypatch.setattr(
        "shiny.session._session.reactive_flush", lambda: asyncio.sleep(0)
    )
    session.bookmark._create_effects = lambda: None  # type: ignore[assignment]

    def _set_restore_context(ctx: object) -> None:
        setattr(session.bookmark, "_restore_context_value", ctx)

    session.bookmark._set_restore_context = _set_restore_context  # type: ignore[assignment, attr-defined]

    handled: list[list[Any]] = []

    async def handler(value: int):
        handled.append([value])
        return "ok"

    session.set_message_handler("echo", handler)
    conn.cause_receive('{"method":"init","data":{}}')
    conn.cause_receive('{"method":"echo","args":[1],"tag":1}')
    conn.cause_disconnect()

    await session._run()
    assert handled == [[1]]


@pytest.mark.asyncio
async def test_run_sends_protocol_error_on_invalid_state(
    monkeypatch: pytest.MonkeyPatch,
):
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    app._request_flush = lambda _session: None  # type: ignore[assignment]
    session = AppSession(app, "id", conn)
    app._sessions[session.id] = session
    session.app.server = lambda input, output, sess: None
    monkeypatch.setattr(
        "shiny.session._session.reactive_flush", lambda: asyncio.sleep(0)
    )
    session.bookmark._create_effects = lambda: None  # type: ignore[assignment]

    def _set_restore_context(ctx: object) -> None:
        setattr(session.bookmark, "_restore_context_value", ctx)

    session.bookmark._set_restore_context = _set_restore_context  # type: ignore[assignment, attr-defined]

    async def fake_send(message: dict[str, Any]) -> None:
        sent.append(message)

    sent: list[dict[str, Any]] = []
    session._send_message = fake_send  # type: ignore[assignment]

    conn.cause_receive('{"method":"update","data":{}}')
    conn.cause_disconnect()
    await session._run()
    assert sent


@pytest.mark.asyncio
async def test_run_handles_unrecognized_method(monkeypatch: pytest.MonkeyPatch):
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    app._request_flush = lambda _session: None  # type: ignore[assignment]
    session = AppSession(app, "id", conn)
    app._sessions[session.id] = session
    session.app.server = lambda input, output, sess: None
    monkeypatch.setattr(
        "shiny.session._session.reactive_flush", lambda: asyncio.sleep(0)
    )
    session.bookmark._create_effects = lambda: None  # type: ignore[assignment]

    def _set_restore_context(ctx: object) -> None:
        setattr(session.bookmark, "_restore_context_value", ctx)

    session.bookmark._set_restore_context = _set_restore_context  # type: ignore[assignment, attr-defined]

    with patch.object(session, "_print_error_message") as mocked:
        conn.cause_receive('{"method":"init","data":{}}')
        conn.cause_receive('{"method":"noop"}')
        conn.cause_disconnect()
        await session._run()
    mocked.assert_called()


@pytest.mark.asyncio
async def test_run_handles_dispatch_errors(monkeypatch: pytest.MonkeyPatch):
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    app._request_flush = lambda _session: None  # type: ignore[assignment]
    session = AppSession(app, "id", conn)
    app._sessions[session.id] = session
    session.app.server = lambda input, output, sess: None
    monkeypatch.setattr(
        "shiny.session._session.reactive_flush", lambda: asyncio.sleep(0)
    )
    session.bookmark._create_effects = lambda: None  # type: ignore[assignment]

    def _set_restore_context(ctx: object) -> None:
        setattr(session.bookmark, "_restore_context_value", ctx)

    session.bookmark._set_restore_context = _set_restore_context  # type: ignore[assignment, attr-defined]

    async def handler():
        raise RuntimeError("boom")

    session.set_message_handler("boom", handler)
    conn.cause_receive('{"method":"init","data":{}}')
    conn.cause_receive('{"method":"boom","args":[],"tag":1}')
    conn.cause_disconnect()

    await session._run()
