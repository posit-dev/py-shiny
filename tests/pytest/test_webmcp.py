import json
from pathlib import Path
from typing import Any

import pytest
from starlette.testclient import TestClient, WebSocketTestSession

from shiny import App, Inputs, Outputs, Session, module, reactive, render, ui, webmcp

SCHEMA = {
    "type": "object",
    "properties": {"amount": {"type": "integer", "minimum": 1}},
    "required": ["amount"],
    "additionalProperties": False,
}


def request(ws: WebSocketTestSession, method: str, args: list[Any]) -> dict[str, Any]:
    ws.send_json({"method": method, "args": args, "tag": 100})
    while True:
        msg = ws.receive_json()
        if "response" in msg:
            return msg["response"]


@module.server
def counter(input: Inputs, output: Outputs, session: Session):
    total = reactive.Value(0)

    @webmcp.tool(input_schema=SCHEMA, description="Add to this session's total")
    async def add(amount: int):
        total.set(total() + amount)
        return {"total": total()}

    @render.text
    def result():
        return str(total())


def server(input: Inputs, output: Outputs, session: Session):
    counter("left")
    counter("right")

    @webmcp.tool(
        input_schema={
            "type": "object",
            "properties": {"values": {"type": "array", "items": {"type": "number"}}},
            "required": ["values"],
        },
        description="Sum a list",
        read_only=True,
    )
    def sum_values(values: list[float]):
        return {"sum": sum(values)}

    @webmcp.tool(input_schema={"type": "object", "properties": {}}, description="Fail")
    def broken():
        raise ValueError("private detail")


@pytest.mark.parametrize("enabled", [False, True])
def test_opt_in(monkeypatch: pytest.MonkeyPatch, enabled: bool):
    monkeypatch.setenv("SHINY_WEBMCP", "1")
    app = App(ui.page_fluid(), server, webmcp=enabled)
    with TestClient(app) as client, client.websocket_connect("/websocket/") as ws:
        assert "sessionId" in ws.receive_json()["config"]
        assert ("shiny-webmcp" in client.get("/").text) is enabled
        ws.send_json({"method": "init", "data": {}})
        response = request(ws, "shiny_webmcp_describe", [])
        if enabled:
            names = [t["name"] for t in response["value"]]
            assert names == ["left-add", "right-add", "sum_values", "broken"]
        else:
            assert "error" in response


def test_environment_opt_in(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("SHINY_WEBMCP", "1")
    assert App(ui.page_fluid(), None)._webmcp_enabled
    monkeypatch.delenv("SHINY_WEBMCP")
    assert not App(ui.page_fluid(), None)._webmcp_enabled


def test_express_app_opts_webmcp(tmp_path: Path):
    from shiny.express._run import wrap_express_app

    app_file = tmp_path / "app.py"
    app_file.write_text("from shiny.express import app_opts\napp_opts(webmcp=True)\n")
    assert wrap_express_app(app_file)._webmcp_enabled is True

    app_file.write_text("from shiny.express import app_opts\napp_opts(webmcp=False)\n")
    assert wrap_express_app(app_file)._webmcp_enabled is False


def test_custom_tools_validation_modules_and_session_isolation():
    app = App(ui.page_fluid(), server, webmcp=True)
    with TestClient(app) as client:
        for _ in range(2):
            with client.websocket_connect("/websocket/") as ws:
                ws.receive_json()
                ws.send_json({"method": "init", "data": {}})
                assert request(ws, "shiny_webmcp_invoke", ["left-add", {"amount": 3}])[
                    "value"
                ] == {"total": 3}
                assert request(ws, "shiny_webmcp_invoke", ["right-add", {"amount": 2}])[
                    "value"
                ] == {"total": 2}
                for args in [
                    {"amount": -1},
                    {"amount": True},
                    {"amount": "3"},
                    {"amount": 1, "extra": 2},
                ]:
                    assert "error" in request(
                        ws, "shiny_webmcp_invoke", ["left-add", args]
                    )
                assert request(ws, "shiny_webmcp_invoke", ["left-add", {"amount": 1}])[
                    "value"
                ] == {"total": 4}
                assert "error" in request(ws, "shiny_webmcp_invoke", ["missing", {}])


def test_custom_tool_errors_respect_sanitization():
    app = App(ui.page_fluid(), server, webmcp=True)
    app.sanitize_errors = True
    with TestClient(app) as client, client.websocket_connect("/websocket/") as ws:
        ws.receive_json()
        ws.send_json({"method": "init", "data": {}})
        response = request(ws, "shiny_webmcp_invoke", ["broken", {}])
        assert response["error"] == app.sanitize_error_msg
        assert "private detail" not in json.dumps(response)


def test_array_arguments_use_json_schema_array_semantics():
    app = App(ui.page_fluid(), server, webmcp=True)
    with TestClient(app) as client, client.websocket_connect("/websocket/") as ws:
        ws.receive_json()
        ws.send_json({"method": "init", "data": {}})
        assert request(
            ws, "shiny_webmcp_invoke", ["sum_values", {"values": [1, 2, 3]}]
        )["value"] == {"sum": 6}


def test_document_dependency_does_not_mutate_shared_ui():
    document = ui.page_html(
        '<html><head><meta name="shiny-dependency-placeholder" content=""></head>'
        "<body>Hello</body></html>"
    )
    enabled = App(document, None, webmcp=True)
    disabled = App(document, None, webmcp=False)
    with TestClient(enabled) as client:
        assert "webmcp.js" in client.get("/").text
    with TestClient(disabled) as client:
        assert "webmcp.js" not in client.get("/").text


@pytest.mark.parametrize(
    "schema",
    [
        {"type": "array"},
        {"type": "object", "properties": {"x": {"$ref": "https://example.com/x"}}},
        {"type": "object", "$defs": {"x": {"$dynamicRef": "other.json"}}},
    ],
)
def test_invalid_tool_schemas(schema: dict[str, Any]):
    with pytest.raises(ValueError):
        webmcp.tool(input_schema=schema, description="Invalid schema")
