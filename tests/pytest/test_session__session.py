from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, AsyncIterable, cast
from unittest.mock import AsyncMock, MagicMock, patch

import htmltools
import pytest
from starlette.requests import Request
from starlette.responses import (
    HTMLResponse,
    PlainTextResponse,
    Response,
    StreamingResponse,
)
from starlette.types import Scope

from shiny import App, render, ui
from shiny._connection import MockConnection
from shiny._namespaces import ResolvedId
from shiny.bookmark._button import BOOKMARK_ID
from shiny.reactive import Value, effect, flush, isolate
from shiny.reactive._core import ReactiveWarning
from shiny.session import Session, session_context
from shiny.session._session import (
    AppSession,
    ClientData,
    DownloadInfo,
    Inputs,
    SessionProxy,
)
from shiny.types import (
    FileInfo,
    SafeException,
    SilentCancelOutputException,
    SilentException,
    SilentOperationInProgressException,
)


def _make_request(method: str) -> Request:
    scope: Scope = {
        "type": "http",
        "method": method,
        "path": "/",
        "scheme": "http",
        "headers": [],
        "query_string": b"",
    }
    return Request(scope)


async def _collect_streaming_response(response: StreamingResponse) -> bytes:
    body_parts: list[bytes] = []
    async for chunk in response.body_iterator:
        if isinstance(chunk, str):
            body_parts.append(chunk.encode())
        else:
            body_parts.append(bytes(chunk))
    return b"".join(body_parts)


@pytest.mark.asyncio
async def test_manage_inputs_with_type_handler(monkeypatch: pytest.MonkeyPatch):
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)

    def fake_process_value(type: str, value: Any, name: ResolvedId, session: Session):
        return f"{type}:{value}:{name}"

    monkeypatch.setattr(
        "shiny.session._session.input_handlers._process_value", fake_process_value
    )

    session._manage_inputs({"x:custom": "value"})
    assert session.input[ResolvedId("x")]._value == "custom:value:x"


def test_manage_inputs_invalid_key():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)

    with pytest.raises(ValueError, match="not allowed"):
        session._manage_inputs({"a:b:c": "value"})


def test_output_message_queues_set_value_and_error():
    queues = AppSession(
        App(ui.page_fluid(), None), "id", MockConnection()
    )._outbound_message_queues
    queues.set_value("x", 1)
    queues.set_error("x", "err")
    assert "x" in queues.errors
    assert "x" not in queues.values
    queues.set_value("x", 2)
    assert queues.values["x"] == 2
    assert "x" not in queues.errors
    queues.reset()
    assert queues.values == {}
    assert queues.errors == {}
    assert queues.input_messages == []


def test_appsession_reads_credentials_header():
    conn = MockConnection()
    conn._http_conn = MagicMock(
        headers={"shiny-server-credentials": '{"user":"u","groups":["g"]}'}
    )
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)
    assert session.user == "u"
    assert session.groups == ["g"]


def test_appsession_reads_connect_credentials_header():
    conn = MockConnection()
    conn._http_conn = MagicMock(
        headers={"rstudio-connect-credentials": '{"user":"u2","groups":["g2"]}'}
    )
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)
    assert session.user == "u2"
    assert session.groups == ["g2"]


def test_appsession_bad_credentials_json_logs_error(capsys: pytest.CaptureFixture[str]):
    conn = MockConnection()
    conn._http_conn = MagicMock(headers={"shiny-server-credentials": "{bad json"})
    app = App(ui.page_fluid(), None)
    AppSession(app, "id", conn)
    captured = capsys.readouterr()
    assert "Error parsing credentials header" in captured.err


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
    session.bookmark._set_restore_context = lambda ctx: setattr(session.bookmark, "_restore_context_value", ctx)  # type: ignore[assignment]

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
    session._print_error_message = lambda _: (_ for _ in ()).throw(RuntimeError("fail"))  # type: ignore[assignment]

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
    session.bookmark._set_restore_context = lambda ctx: setattr(session.bookmark, "_restore_context_value", ctx)  # type: ignore[assignment]

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
    session.bookmark._set_restore_context = lambda ctx: setattr(session.bookmark, "_restore_context_value", ctx)  # type: ignore[assignment]

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
    session.bookmark._set_restore_context = lambda ctx: setattr(session.bookmark, "_restore_context_value", ctx)  # type: ignore[assignment]

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
    session.bookmark._set_restore_context = lambda ctx: setattr(session.bookmark, "_restore_context_value", ctx)  # type: ignore[assignment]

    async def handler():
        raise RuntimeError("boom")

    session.set_message_handler("boom", handler)
    conn.cause_receive('{"method":"init","data":{}}')
    conn.cause_receive('{"method":"boom","args":[],"tag":1}')
    conn.cause_disconnect()

    await session._run()


def test_send_insert_and_remove_ui_messages():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)
    sent: list[dict[str, Any]] = []

    async def fake_send(msg: dict[str, Any]) -> None:
        sent.append(
            {
                "values": dict(msg.get("values", {})),
                "errors": dict(msg.get("errors", {})),
                "inputMessages": list(msg.get("inputMessages", [])),
            }
        )

    session._send_message = fake_send  # type: ignore[assignment]
    session._send_message_sync = lambda msg: sent.append(msg)  # type: ignore[assignment]

    session._send_insert_ui("body", False, "afterEnd", {"deps": [], "html": "<div/>"})
    session._send_remove_ui("body", True)
    assert sent[0]["shiny-insert-ui"]["selector"] == "body"
    assert sent[1]["shiny-remove-ui"]["multiple"] is True


@pytest.mark.asyncio
async def test_send_custom_message():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)
    sent: list[dict[str, Any]] = []

    async def fake_send(msg: dict[str, Any]) -> None:
        sent.append(msg)

    session._send_message = fake_send  # type: ignore[assignment]
    await session.send_custom_message("x", {"y": 1})
    assert sent[-1] == {"custom": {"x": {"y": 1}}}


@pytest.mark.asyncio
async def test_send_error_response_requires_tag():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)
    with pytest.raises(RuntimeError, match="No `tag` key"):
        await session._send_error_response({"method": "test"}, "err")  # type: ignore[arg-type]


def test_on_flush_and_on_flushed_register_callbacks():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)
    called: list[str] = []

    def cb():
        called.append("flush")

    def cb2():
        called.append("flushed")

    session.on_flush(cb)
    session.on_flushed(cb2)
    assert called == []


@pytest.mark.asyncio
async def test_flush_sends_values_and_resets():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)
    restore_context = MagicMock(flush_pending=MagicMock())
    session.bookmark._set_restore_context(restore_context)  # type: ignore[arg-type]
    session._outbound_message_queues.set_value(ResolvedId("x"), 1)
    sent: list[dict[str, Any]] = []

    async def fake_send(msg: dict[str, Any]) -> None:
        sent.append(
            {
                "values": dict(msg.get("values", {})),
                "errors": dict(msg.get("errors", {})),
                "inputMessages": list(msg.get("inputMessages", [])),
            }
        )

    session._send_message = fake_send  # type: ignore[assignment]
    await session._flush()
    assert sent[-1]["values"].get(ResolvedId("x")) == 1
    restore_context.flush_pending.assert_called_once()
    session.bookmark._set_restore_context(None)  # type: ignore[arg-type]
    session._outbound_message_queues.set_value(ResolvedId("y"), 2)
    await session._flush()
    assert sent[-1]["values"].get(ResolvedId("y")) == 2
    assert session._outbound_message_queues.values == {}


def test_increment_and_decrement_busy_count():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)
    sent: list[dict[str, Any]] = []
    session._send_message_sync = lambda msg: sent.append(msg)  # type: ignore[assignment]
    session._increment_busy_count()
    session._decrement_busy_count()
    session._increment_busy_count()
    session._increment_busy_count()
    session._decrement_busy_count()
    session._decrement_busy_count()
    assert sent == [
        {"busy": "busy"},
        {"busy": "idle"},
        {"busy": "busy"},
        {"busy": "idle"},
    ]


@pytest.mark.asyncio
async def test_session_download_decorator_registers_and_renders_url():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)

    @session.download()
    def handler():
        return [b"data"]

    assert "handler" in session._downloads
    renderer = session.output._outputs[ResolvedId("handler")].renderer
    with session_context(session):
        url = await renderer.render()
    assert isinstance(url, str)
    assert "download" in url


def test_session_dynamic_route_returns_url():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)
    path = session.dynamic_route("name", lambda req: PlainTextResponse("ok"))
    assert "dynamic_route" in path


@pytest.mark.asyncio
async def test_unhandled_error_prints_and_closes(capsys: pytest.CaptureFixture[str]):
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)
    app._sessions[session.id] = session
    session._conn.close = AsyncMock()  # type: ignore[assignment]
    await session._unhandled_error(RuntimeError("boom"))
    captured = capsys.readouterr()
    assert "Unhandled error: boom" in captured.err


@pytest.mark.asyncio
async def test_make_scope_and_session_proxy_methods():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)
    app._sessions[session.id] = session
    proxy = session.make_scope("mod")
    assert isinstance(proxy, SessionProxy)
    assert proxy._is_hidden("x") is True
    assert proxy.is_stub_session() is False
    proxy.send_input_message("x", {"value": 1})
    proxy.on_ended(lambda: None)
    proxy._increment_busy_count()
    proxy._decrement_busy_count()
    proxy._send_insert_ui("body", False, "afterEnd", {"deps": [], "html": "<div/>"})
    proxy._send_remove_ui("body", True)
    proxy._send_progress("binding", {"id": ResolvedId("x")})
    proxy._send_message_sync({"msg": 1})
    proxy.on_flush(lambda: None)
    proxy.on_flushed(lambda: None)
    assert session._busy_count == 0


def test_process_ui_registers_dependencies():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)
    dep = htmltools.HTMLDependency(
        "test-dep", "1.0", source={"href": "https://example.com"}
    )
    tag = htmltools.tags.div(htmltools.tags.head(dep), "body")
    session._process_ui(tag)
    assert "test-dep-1.0" in app._registered_dependencies


def test_inputs_requires_value_type():
    inputs = Inputs({})
    with pytest.raises(TypeError, match="reactive.Value"):
        inputs["x"] = "bad"  # type: ignore[assignment]


@pytest.mark.asyncio
async def test_inputs_contains_tracks_is_set_false_when_unset():
    inputs = Inputs({})
    seen: list[bool] = []

    @effect
    def _():
        seen.append("x" in inputs)

    await flush()
    assert seen == [False]


def test_inputs_attribute_access_and_delete():
    inputs = Inputs({})
    inputs["x"] = Value(1)
    with isolate():
        assert inputs.x() == 1
    inputs.y = Value(2)
    assert "y" in inputs.__dir__()
    _ = inputs._map
    del inputs.x
    assert isinstance(inputs["x"], Value)


def test_clientdata_read_input_requires_existing_key():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)
    clientdata = ClientData(session)

    def _():
        with isolate():
            clientdata.url_hash()

    with pytest.raises(ValueError, match="not found"):
        _()


def test_clientdata_read_output_requires_id():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)
    clientdata = ClientData(session)

    def _():
        with isolate():
            clientdata.output_width()

    with pytest.raises(ValueError, match="requires an id"):
        _()


@pytest.mark.asyncio
async def test_clientdata_read_output_returns_none_when_missing():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)
    clientdata = ClientData(session)

    result: dict[str, Any] = {}

    @effect
    def _():
        result["width"] = clientdata.output_width("missing")

    await flush()
    assert result["width"] is None


@pytest.mark.asyncio
async def test_clientdata_url_accessors_and_output_name_context():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)
    clientdata = ClientData(session)
    session.input[ResolvedId(".clientdata_url_hash_initial")]._set("#hash")
    session.input[ResolvedId(".clientdata_url_hostname")]._set("host")
    session.input[ResolvedId(".clientdata_url_pathname")]._set("/path")
    session.input[ResolvedId(".clientdata_url_port")]._set(80)
    session.input[ResolvedId(".clientdata_url_protocol")]._set("http:")
    session.input[ResolvedId(".clientdata_url_search")]._set("?q=1")
    session.input[ResolvedId(".clientdata_pixelratio")]._set(2)
    session.input[ResolvedId(".clientdata_output_plot_height")]._set(100)
    session.input[ResolvedId(".clientdata_output_plot_hidden")]._set(True)
    session.input[ResolvedId(".clientdata_output_plot_bg")]._set("white")
    session.input[ResolvedId(".clientdata_output_plot_fg")]._set("black")
    session.input[ResolvedId(".clientdata_output_plot_accent")]._set("blue")
    session.input[ResolvedId(".clientdata_output_plot_font")]._set("sans")

    result: dict[str, Any] = {}

    @effect
    def _():
        result["hash_initial"] = clientdata.url_hash_initial()
        result["hostname"] = clientdata.url_hostname()
        result["pathname"] = clientdata.url_pathname()
        result["port"] = clientdata.url_port()
        result["protocol"] = clientdata.url_protocol()
        result["search"] = clientdata.url_search()
        result["pixelratio"] = clientdata.pixelratio()
        result["height"] = clientdata.output_height("plot")
        result["hidden"] = clientdata.output_hidden("plot")
        result["bg"] = clientdata.output_bg_color("plot")
        result["fg"] = clientdata.output_fg_color("plot")
        result["accent"] = clientdata.output_accent_color("plot")
        result["font"] = clientdata.output_font("plot")

    await flush()
    assert result["hash_initial"] == "#hash"
    assert result["hostname"] == "host"
    assert result["pathname"] == "/path"
    assert result["port"] == 80
    assert result["protocol"] == "http:"
    assert result["search"] == "?q=1"
    assert result["pixelratio"] == 2
    assert result["height"] == 100
    assert result["hidden"] is True
    assert result["bg"] == "white"
    assert result["fg"] == "black"
    assert result["accent"] == "blue"
    assert result["font"] == "sans"


def test_clientdata_output_name_context_resets():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)
    clientdata = ClientData(session)
    output_name = ResolvedId("name")

    with clientdata._output_name_ctx(output_name):
        assert clientdata._current_output_name == output_name
    assert clientdata._current_output_name is None


@pytest.mark.asyncio
async def test_clientdata_output_name_context_defaults_id():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)
    clientdata = ClientData(session)
    session.input[ResolvedId(".clientdata_output_auto_width")]._set(321)

    result: dict[str, Any] = {}

    with clientdata._output_name_ctx(ResolvedId("auto")):

        @effect
        def _():
            result["width"] = clientdata.output_width()

        await flush()

    assert result["width"] == 321


@pytest.mark.asyncio
async def test_outputs_register_remove_and_suspend():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)
    session.app._request_flush = lambda _session: None  # type: ignore[assignment]

    @session.output(id="out", suspend_when_hidden=False)
    @render.text
    def _():
        return "ok"

    await flush()
    output_info = session.output._outputs[ResolvedId("out")]
    output_info.effect.destroy()
    session.output.remove("out")
    assert ResolvedId("out") not in session.output._outputs


@pytest.mark.asyncio
async def test_session_proxy_delegates_methods():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)
    app._sessions[session.id] = session
    proxy = SessionProxy(session, ResolvedId("mod"))
    session._send_message = AsyncMock()  # type: ignore[assignment]

    proxy.on_flush(lambda: None)
    proxy.on_flushed(lambda: None)
    proxy.dynamic_route("route", lambda req: PlainTextResponse("ok"))
    proxy.set_message_handler("handler", lambda: "ok")
    proxy._increment_busy_count()
    proxy._decrement_busy_count()
    assert session._busy_count == 0

    proxy.send_input_message("x", {"value": 1})
    assert session._outbound_message_queues.input_messages[0]["id"] == "mod-x"
    session.set_message_handler("handler", None)
    assert "handler" not in session._message_handlers

    proxy._send_message_sync({"msg": 1})
    await proxy._send_message({"msg": 2})
    await proxy.send_custom_message("type", {"value": 1})
    await proxy._unhandled_error(RuntimeError("boom"))
    proxy.download(id="file")(lambda: [b"x"])
    proxy._process_ui(htmltools.tags.div("hi"))
    assert session._outbound_message_queues.values == {}


def test_is_hidden_defaults_true_for_missing():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)

    assert session._is_hidden("missing") is True


def test_is_hidden_reads_value_when_set():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)

    hidden_key = ResolvedId(".clientdata_output_output_hidden")
    session.input[hidden_key]._set(False)

    assert session._is_hidden("output") is False


@pytest.mark.asyncio
async def test_dispatch_unknown_handler_sends_error():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)

    messages: list[dict[str, Any]] = []

    async def fake_send(msg: dict[str, Any]) -> None:
        messages.append(msg)

    session._send_message = fake_send  # type: ignore[assignment]

    await session._dispatch({"method": "missing", "args": [], "tag": 1})

    assert messages
    assert messages[-1]["response"]["error"].startswith("Unknown method")


@pytest.mark.asyncio
async def test_dispatch_handles_attribute_error():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)

    class _HandlerMap(dict[str, Any]):
        def __getitem__(self, key: str) -> Any:
            raise AttributeError("missing")

    session._message_handlers = _HandlerMap()  # type: ignore[assignment]

    messages: list[dict[str, Any]] = []

    async def fake_send(msg: dict[str, Any]) -> None:
        messages.append(msg)

    session._send_message = fake_send  # type: ignore[assignment]

    await session._dispatch({"method": "missing", "args": [], "tag": 1})

    assert messages[-1]["response"]["error"].startswith("Unknown method")


@pytest.mark.asyncio
async def test_dispatch_sanitizes_errors():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    app.sanitize_errors = True
    app.sanitize_error_msg = "sanitized"
    session = AppSession(app, "id", conn)

    async def handler():
        raise ValueError("boom")

    session.set_message_handler("test", handler)

    messages: list[dict[str, Any]] = []

    async def fake_send(msg: dict[str, Any]) -> None:
        messages.append(msg)

    session._send_message = fake_send  # type: ignore[assignment]

    await session._dispatch({"method": "test", "args": [], "tag": 2})

    assert messages[-1]["response"]["error"] == "sanitized"


@pytest.mark.asyncio
async def test_dispatch_safe_exception_not_sanitized():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    app.sanitize_errors = True
    session = AppSession(app, "id", conn)

    async def handler():
        raise SafeException("safe")

    session.set_message_handler("test", handler)

    messages: list[dict[str, Any]] = []

    async def fake_send(msg: dict[str, Any]) -> None:
        messages.append(msg)

    session._send_message = fake_send  # type: ignore[assignment]

    await session._dispatch({"method": "test", "args": [], "tag": 3})

    assert messages[-1]["response"]["error"] == "safe"


@pytest.mark.asyncio
async def test_dispatch_success_response():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)

    async def handler() -> str:
        return "ok"

    session.set_message_handler("test", handler)

    messages: list[dict[str, Any]] = []

    async def fake_send(msg: dict[str, Any]) -> None:
        messages.append(msg)

    session._send_message = fake_send  # type: ignore[assignment]

    await session._dispatch({"method": "test", "args": [], "tag": 4})

    assert messages[-1]["response"]["value"] == "ok"


@pytest.mark.asyncio
async def test_upload_init_sets_mime_type():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)

    handler, _ = session._message_handlers["uploadInit"]
    file_infos = [
        {"name": "test.txt", "size": 1, "type": ""},
        {"name": "ok.bin", "size": 1, "type": "custom"},
    ]
    response = await handler(file_infos)

    assert isinstance(response, dict)
    assert response["jobId"]
    assert file_infos[0]["type"] == "text/plain"
    assert file_infos[1]["type"] == "custom"


@pytest.mark.asyncio
async def test_upload_init_debug_prints(capsys: pytest.CaptureFixture[str]):
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn, debug=True)

    handler, _ = session._message_handlers["uploadInit"]
    await handler([{"name": "test.txt", "size": 1, "type": ""}])
    captured = capsys.readouterr()
    assert "Upload init:" in captured.out


@pytest.mark.asyncio
async def test_upload_end_handles_missing_job():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)

    handler, _ = session._message_handlers["uploadEnd"]
    with pytest.warns(RuntimeWarning, match="upload operation"):
        assert await handler("missing", "input") is None


@pytest.mark.asyncio
async def test_upload_end_sets_value_and_serializer(tmp_path: Path):
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)

    file_infos: list[FileInfo] = [
        {"name": "test.txt", "size": 1, "type": "text/plain", "datapath": ""}
    ]
    job_id = session._file_upload_manager.create_upload_operation(file_infos)

    upload_op = session._file_upload_manager.get_upload_operation(job_id)
    assert upload_op is not None
    with upload_op:
        upload_op.write_chunk(b"abc")

    handler, _ = session._message_handlers["uploadEnd"]
    await handler(job_id, "file")

    assert session.input[ResolvedId("file")]._value is not None
    assert "file" in session.input._serializers


@pytest.mark.asyncio
async def test_handle_request_upload_bad_request():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)

    response = await session._handle_request_impl(_make_request("POST"), "upload", None)
    assert isinstance(response, HTMLResponse)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_handle_request_tracks_busy_count(tmp_path: Path):
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)

    file_path = tmp_path / "data.txt"
    file_path.write_text("hello")

    session._downloads["file"] = DownloadInfo(
        filename=None,
        content_type=None,
        handler=lambda: str(file_path),
        encoding="utf-8",
    )

    await session._handle_request(_make_request("GET"), "download", "file")
    assert session._busy_count == 0


@pytest.mark.asyncio
async def test_handle_request_upload_unknown_job():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)

    response = await session._handle_request_impl(
        _make_request("POST"), "upload", "missing"
    )
    assert isinstance(response, HTMLResponse)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_handle_request_upload_success(tmp_path: Path):
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)

    file_infos: list[FileInfo] = [
        {"name": "test.txt", "size": 1, "type": "text/plain", "datapath": ""}
    ]
    job_id = session._file_upload_manager.create_upload_operation(file_infos)

    async def stream():
        yield b"hello"

    request = _make_request("POST")
    request.stream = stream  # type: ignore[assignment]

    response = await session._handle_request_impl(request, "upload", job_id)
    assert isinstance(response, PlainTextResponse)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_handle_request_download_file(tmp_path: Path):
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)

    file_path = tmp_path / "data.txt"
    file_path.write_text("hello")

    session._downloads["file"] = DownloadInfo(
        filename=None,
        content_type=None,
        handler=lambda: str(file_path),
        encoding="utf-8",
    )

    response = await session._handle_request_impl(
        _make_request("GET"), "download", "file"
    )
    assert isinstance(response, Response)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_handle_request_download_iterable_sets_filename_and_warns():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)

    session._downloads["iter"] = DownloadInfo(
        filename=None,
        content_type=None,
        handler=lambda: ["a", b"b"],
        encoding="utf-8",
    )

    with pytest.warns(RuntimeWarning, match="Unable to infer"):
        response = await session._handle_request_impl(
            _make_request("GET"), "download", "iter"
        )
    response_missing = await session._handle_request_impl(
        _make_request("GET"), "download", "missing"
    )

    assert isinstance(response, StreamingResponse)
    assert response.headers.get("Transfer-Encoding") == "chunked"
    body = await _collect_streaming_response(response)
    assert body == b"ab"
    assert isinstance(response_missing, Response)
    assert response_missing.status_code == 404


@pytest.mark.asyncio
async def test_handle_request_download_async_iterable():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)

    async def handler() -> AsyncIterable[bytes]:
        yield b"a"
        yield b"b"

    session._downloads["async"] = DownloadInfo(
        filename="name.txt",
        content_type="text/plain",
        handler=handler,
        encoding="utf-8",
    )

    response = await session._handle_request_impl(
        _make_request("GET"), "download", "async"
    )

    assert isinstance(response, StreamingResponse)
    body = await _collect_streaming_response(response)
    assert body == b"ab"


@pytest.mark.asyncio
async def test_handle_request_download_content_disposition_encoded():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)

    session._downloads["encoded"] = DownloadInfo(
        filename="f il e.txt",
        content_type="text/plain",
        handler=lambda: [b"data"],
        encoding="utf-8",
    )

    response = await session._handle_request_impl(
        _make_request("GET"), "download", "encoded"
    )
    assert isinstance(response, Response)
    assert "filename*" in response.headers.get("Content-Disposition", "")


@pytest.mark.asyncio
async def test_handle_request_dynamic_route_sync_and_async():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)

    def sync_handler(request: Request):
        return PlainTextResponse("sync")

    async def async_handler(request: Request):
        return PlainTextResponse("async")

    session._dynamic_routes["sync"] = sync_handler
    session._dynamic_routes["async"] = cast(Any, async_handler)

    response = await session._handle_request_impl(
        _make_request("GET"), "dynamic_route", "sync"
    )
    assert isinstance(response, PlainTextResponse)
    assert response.body == b"sync"

    response = await session._handle_request_impl(
        _make_request("GET"), "dynamic_route", "async"
    )
    assert isinstance(response, PlainTextResponse)
    assert response.body == b"async"


@pytest.mark.asyncio
async def test_handle_request_dynamic_route_missing():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)

    response = await session._handle_request_impl(
        _make_request("GET"), "dynamic_route", "missing"
    )
    assert isinstance(response, Response)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_handle_request_not_found():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)

    response = await session._handle_request_impl(_make_request("GET"), "other", None)
    assert isinstance(response, Response)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_send_input_message_queues_and_flushes():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)

    called: list[Session] = []

    def request_flush(_: Session) -> None:
        called.append(session)

    session.app._request_flush = request_flush  # type: ignore[assignment]
    session.send_input_message("x", {"value": 1})

    assert session._outbound_message_queues.input_messages
    assert called == [session]


@pytest.mark.asyncio
async def test_send_message_debug_prints(capsys: pytest.CaptureFixture[str]):
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn, debug=True)
    session._conn.send = AsyncMock()  # type: ignore[assignment]
    await session._send_message({"test": "value"})
    captured = capsys.readouterr()
    assert "SEND:" in captured.out


@pytest.mark.asyncio
async def test_send_message_sync_uses_run_coro_hybrid():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)

    result = {}

    async def fake_send(msg: dict[str, Any]) -> None:
        result["msg"] = msg

    session._send_message = fake_send  # type: ignore[assignment]
    session._send_message_sync({"test": True})
    await asyncio.sleep(0)

    assert result["msg"] == {"test": True}


def test_outputs_decorator_rejects_non_renderer():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)

    def bad_renderer():
        return "bad"

    with pytest.raises(TypeError, match="must be applied"):
        session.output(bad_renderer)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_outputs_runs_and_handles_silent_exceptions():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)

    @session.output(id="silent", suspend_when_hidden=False)
    @render.text
    def _():
        raise SilentException()

    await flush()
    assert session._outbound_message_queues.values[ResolvedId("silent")] is None

    @session.output(id="cancel", suspend_when_hidden=False)
    @render.text
    def _():
        raise SilentCancelOutputException()

    await flush()
    assert ResolvedId("cancel") not in session._outbound_message_queues.values


@pytest.mark.asyncio
async def test_outputs_reports_errors():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    app.sanitize_errors = False
    session = AppSession(app, "id", conn)

    @session.output(id="boom", suspend_when_hidden=False)
    @render.text
    def _():
        raise RuntimeError("boom")

    await flush()
    assert (
        "boom" in session._outbound_message_queues.errors[ResolvedId("boom")]["message"]
    )


@pytest.mark.asyncio
async def test_outputs_reports_sanitized_errors():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    app.sanitize_errors = True
    app.sanitize_error_msg = "sanitized"
    session = AppSession(app, "id", conn)

    @session.output(id="boom", suspend_when_hidden=False)
    @render.text
    def _():
        raise RuntimeError("boom")

    await flush()
    assert (
        session._outbound_message_queues.errors[ResolvedId("boom")]["message"]
        == "sanitized"
    )


@pytest.mark.asyncio
async def test_outputs_sends_progress_on_invalidate():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)
    value = Value(1)

    messages: list[dict[str, Any]] = []

    async def fake_send(msg: dict[str, Any]) -> None:
        messages.append(msg)

    session._send_message = fake_send  # type: ignore[assignment]

    @session.output(id="test", suspend_when_hidden=False)
    @render.text
    def _():
        return str(value())

    await flush()
    value.set(2)
    await asyncio.sleep(0)

    assert any("progress" in msg for msg in messages)


@pytest.mark.asyncio
async def test_outputs_manage_hidden_suspends_and_resumes():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)

    hidden_key = ResolvedId(".clientdata_output_test_hidden")
    session.input[hidden_key]._set(True)

    @session.output(id="test", suspend_when_hidden=True)
    @render.text
    def _():
        return "ok"

    output_info = session.output._outputs[ResolvedId("test")]
    assert output_info.effect._suspended

    session.output._manage_hidden()
    assert output_info.effect._suspended

    session.input[hidden_key]._set(False)
    session.output._manage_hidden()
    assert not output_info.effect._suspended

    output_info.effect.suspend()
    session.output._manage_hidden()
    assert not output_info.effect._suspended


@pytest.mark.asyncio
async def test_outputs_raise_with_stub_session_and_silent_progress():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)
    session.is_stub_session = lambda: True  # type: ignore[assignment]

    @session.output(id="out", suspend_when_hidden=False)
    @render.text
    def _():
        return "ok"

    with pytest.warns(ReactiveWarning, match="stub session"):
        await flush()

    session.is_stub_session = lambda: False  # type: ignore[assignment]

    @session.output(id="progress", suspend_when_hidden=False)
    @render.text
    def _():
        raise SilentOperationInProgressException()

    await flush()
    assert session._outbound_message_queues.values.get(ResolvedId("progress")) is None

    @session.output(id="progress2", suspend_when_hidden=False)
    @render.text
    def _():
        raise SilentOperationInProgressException()

    await flush()
    assert session._outbound_message_queues.values.get(ResolvedId("progress2")) is None

    session.output._session.is_stub_session = lambda: True  # type: ignore[assignment]
    with pytest.raises(RuntimeError, match="stub session"):
        session.output._outputs[ResolvedId("progress2")].effect._invalidate_callbacks[
            0
        ]()


def test_outputs_remove_destroys_effect():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)

    @session.output(id="test")
    @render.text
    def _():
        return "ok"

    assert ResolvedId("test") in session.output._outputs
    session.output.remove("test")
    assert ResolvedId("test") not in session.output._outputs


def test_session_proxy_delegates():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)

    proxy = SessionProxy(session, ResolvedId("mod"))
    proxy.send_input_message("x", {"value": 1})

    assert session._outbound_message_queues.input_messages[0]["id"] == "mod-x"


@pytest.mark.asyncio
async def test_session_proxy_methods_delegate_calls():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)
    app._sessions[session.id] = session
    proxy = SessionProxy(session, ResolvedId("mod"))
    session._conn.close = AsyncMock()  # type: ignore[assignment]

    await proxy.close()
    assert session._has_run_session_ended_tasks is True
    assert proxy.root_scope() is session
    assert proxy.make_scope("child").ns("x") == ResolvedId("mod-child-x")

    proxy.send_input_message("x", {"value": 1})
    assert session._outbound_message_queues.input_messages[-1]["id"] == "mod-x"

    proxy._send_insert_ui("body", False, "afterEnd", {"deps": [], "html": "<div/>"})
    proxy._send_remove_ui("body", True)
    proxy._send_progress("binding", {"id": ResolvedId("x")})
    proxy._send_message_sync({"msg": 1})


@pytest.mark.asyncio
async def test_clientdata_read_input_and_output():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)
    clientdata = ClientData(session)

    session.input[ResolvedId(".clientdata_url_hash")]._set("#hash")
    session.input[ResolvedId(".clientdata_output_plot_width")]._set(123)

    result: dict[str, Any] = {}

    @effect
    def _():
        result["hash"] = clientdata.url_hash()
        result["width"] = clientdata.output_width("plot")

    await flush()
    assert result["hash"] == "#hash"
    assert result["width"] == 123


@pytest.mark.asyncio
async def test_inputs_attr_helpers_and_serialize_filters():
    inputs = Inputs({})
    inputs["x"] = Value(1)
    inputs[".clientdata_meta"]._set(1)
    inputs[BOOKMARK_ID]._set(2)
    inputs._map[ResolvedId(f"ns{ResolvedId._sep}{BOOKMARK_ID}")] = Value(3)

    assert inputs.__getattr__("_map") is inputs._map
    assert "x" in inputs.__dir__()

    del inputs.x
    inputs.x = Value(4)
    assert isinstance(inputs.x, Value)

    inputs._serializers = {}  # type: ignore[assignment]
    inputs.__setattr__("_serializers", cast(Any, inputs._serializers))

    result = await inputs._serialize(exclude=[], state_dir=None)
    assert ".clientdata_meta" not in result
    assert BOOKMARK_ID not in result


def test_clientdata_requires_reactive_context():
    conn = MockConnection()
    app = App(ui.page_fluid(), None)
    session = AppSession(app, "id", conn)
    clientdata = ClientData(session)

    with pytest.raises(RuntimeError, match="reactive context"):
        clientdata.url_hash()


def test_inputs_basic_operations():
    inputs = Inputs({})
    inputs["x"] = Value(1)

    with isolate():
        assert inputs["x"]() == 1
        assert inputs.x() == 1

    del inputs["x"]
    with pytest.raises(SilentException):
        with isolate():
            inputs.x()


@pytest.mark.asyncio
async def test_inputs_serialize_excludes_and_custom_serializer():
    inputs = Inputs({})
    inputs[".clientdata_url_search"]._set("?q=1")
    inputs["normal"]._set(1)
    inputs["exclude"]._set(2)

    inputs.set_serializer("normal", lambda value, state_dir: {"value": value})
    result = await inputs._serialize(exclude=["exclude"], state_dir=None)

    assert "normal" in result
    assert result["normal"]["value"] == 1
    assert "exclude" not in result
    assert ".clientdata_url_search" not in result


@pytest.mark.asyncio
async def test_inputs_serialize_skips_unset_and_unserializable():
    inputs = Inputs({})
    inputs["unset"] = Value(read_only=True)
    inputs["good"]._set(1)

    async def serializer(value: Any, state_dir: Path | None):
        from shiny.bookmark._serializers import Unserializable

        return Unserializable()

    inputs.set_serializer("good", serializer)
    result = await inputs._serialize(exclude=[], state_dir=None)

    assert "good" not in result


@pytest.mark.asyncio
async def test_inputs_contains_tracks_is_set():
    inputs = Inputs({})
    results: list[bool] = []

    @effect
    def _():
        results.append("x" in inputs)

    await flush()
    inputs["x"]._set(1)
    await flush()

    assert results == [False, True]
