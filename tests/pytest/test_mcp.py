from __future__ import annotations

import io
import json

import pytest
from click.testing import CliRunner

from shiny._main import main
from shiny.mcp import (
    ShinyMCPServer,
    simulate_shiny_app,
    validate_shiny_code,
)
from shiny.mcp._prompts import get_mcp_prompt, list_mcp_prompts
from shiny.mcp._resources import list_mcp_resources, read_mcp_resource
from shiny.mcp._tools import (
    dispatch_mcp_tool,
    get_mcp_tools_definitions,
    inspect_reactive_graph,
)


def test_validator_valid_express_code():
    code = """
from shiny.express import input, render, ui

ui.page_opts(title="Express Test")
ui.input_slider("n", "N", 1, 100, 20)

@render.text
def txt():
    return f"Value is {input.n()}"
"""
    result = validate_shiny_code(code)
    assert result["valid"] is True
    assert result["mode"] == "express"
    assert "n" in result["detected_inputs"]
    assert "txt" in result["detected_outputs"]
    assert len(result["errors"]) == 0


def test_validator_valid_core_code():
    code = """
from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.input_text("name", "Name:"),
    ui.output_text("greeting"),
)

def server(input, output, session):
    @output
    @render.text
    def greeting():
        return f"Hello, {input.name()}"

app = App(app_ui, server)
"""
    result = validate_shiny_code(code)
    assert result["valid"] is True
    assert result["mode"] == "core"
    assert "name" in result["detected_inputs"]
    assert "greeting" in result["detected_outputs"]
    assert len(result["errors"]) == 0


def test_validator_detects_r_shiny_idioms():
    code = """
from shiny import shinyApp, fluidPage, ui

app = shinyApp(ui=fluidPage(), server=lambda i, o, s: None)
"""
    result = validate_shiny_code(code)
    assert result["valid"] is False
    codes = [e["code"] for e in result["errors"]]
    assert "R_SHINY_IDIOM" in codes


def test_validator_detects_input_assignment():
    code = """
from shiny import App, ui

def server(input, output, session):
    input.x = 10
"""
    result = validate_shiny_code(code)
    assert result["valid"] is False
    codes = [e["code"] for e in result["errors"]]
    assert "INPUT_ASSIGNMENT" in codes


def test_validator_detects_uncalled_input():
    code = """
from shiny.express import input, render, ui

ui.input_slider("n", "N", 1, 10, 5)

@render.text
def out():
    val = input.n + 10
    return f"Val={val}"
"""
    result = validate_shiny_code(code)
    warn_codes = [w["code"] for w in result["warnings"]]
    assert "UNCALLED_INPUT" in warn_codes


def test_validator_detects_duplicate_ids():
    code = """
from shiny.express import ui

ui.input_slider("num", "Slider 1", 1, 10, 5)
ui.input_slider("num", "Slider 2", 1, 10, 5)
"""
    result = validate_shiny_code(code)
    assert len(result["warnings"]) > 0
    assert any(w["code"] == "DUPLICATE_ID" for w in result["warnings"])


def test_validator_syntax_error():
    code = "def bad_syntax(:"
    result = validate_shiny_code(code)
    assert result["valid"] is False
    assert result["errors"][0]["code"] == "SYNTAX_ERROR"


@pytest.mark.asyncio
async def test_simulate_express_app():
    code = """
from shiny.express import input, render, ui

ui.input_slider("n", "N", 1, 100, 42)

@render.text
def greeting():
    return f"Selected: {input.n()}"
"""
    result = await simulate_shiny_app(code=code, inputs={"n": 50})
    assert result["success"] is True
    assert "greeting" in result["outputs"]
    assert result["outputs"]["greeting"] == "Selected: 50"


@pytest.mark.asyncio
async def test_simulate_core_app():
    code = """
from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.input_numeric("val", "Value", 10),
    ui.output_text("doubled"),
)

def server(input, output, session):
    @output
    @render.text
    def doubled():
        return str(input.val() * 2)

app = App(app_ui, server)
"""
    result = await simulate_shiny_app(code=code, inputs={"val": 15})
    assert result["success"] is True
    assert result["outputs"]["doubled"] == "30"


@pytest.mark.asyncio
async def test_simulate_app_with_error():
    code = """
from shiny.express import input, render, ui

@render.text
def error_output():
    raise ValueError("Calculation failed intentionally")
"""
    result = await simulate_shiny_app(code=code)
    assert result["success"] is False
    assert "error_output" in result["errors"]


@pytest.mark.asyncio
async def test_simulate_app_invalid_inputs():
    result = await simulate_shiny_app()
    assert result["success"] is False
    assert "Either 'code' or 'file_path'" in result["error"]


def test_inspect_reactive_graph():
    code = """
from shiny import App, reactive, render, ui

app_ui = ui.page_fluid(
    ui.input_slider("n", "N", 1, 10, 5),
    ui.output_text("calc_out"),
)

def server(input, output, session):
    @reactive.calc
    def doubled():
        return input.n() * 2

    @render.text
    def calc_out():
        return f"Result: {input.n()}"
"""
    graph = inspect_reactive_graph(code)
    assert graph["success"] is True
    assert len(graph["nodes"]) >= 2
    assert any(n["id"] == "n" for n in graph["nodes"])
    assert any(n["id"] == "calc_out" for n in graph["nodes"])


def test_tools_definitions():
    tools = get_mcp_tools_definitions()
    tool_names = [t["name"] for t in tools]
    assert "shiny_validate_code" in tool_names
    assert "shiny_simulate_app" in tool_names
    assert "shiny_list_components" in tool_names
    assert "shiny_get_component_doc" in tool_names
    assert "shiny_scaffold_app" in tool_names
    assert "shiny_inspect_reactive_graph" in tool_names


@pytest.mark.asyncio
async def test_dispatch_tools():
    # test list components
    comps = await dispatch_mcp_tool("shiny_list_components", {"category": "inputs"})
    assert len(comps["components"]) > 0
    assert all(c["category"] == "inputs" for c in comps["components"])

    # test component doc
    doc = await dispatch_mcp_tool(
        "shiny_get_component_doc", {"name": "ui.page_sidebar"}
    )
    assert "snippet" in doc
    assert "signature" in doc

    # test scaffold app
    scaffold = await dispatch_mcp_tool(
        "shiny_scaffold_app", {"template": "express_dashboard"}
    )
    assert "code" in scaffold
    val = validate_shiny_code(scaffold["code"])
    assert val["valid"] is True


def test_resources_provider():
    resources = list_mcp_resources()
    assert len(resources) > 0
    uris = [r["uri"] for r in resources]
    assert "shiny://components/catalog" in uris
    assert "shiny://templates/list" in uris

    cat_res = read_mcp_resource("shiny://components/catalog")
    assert cat_res is not None
    assert "ui.page_sidebar" in cat_res["text"]

    tmpl_res = read_mcp_resource("shiny://templates/list")
    assert tmpl_res is not None
    assert "express_dashboard" in tmpl_res["text"]


def test_prompts_provider():
    prompts = list_mcp_prompts()
    assert len(prompts) >= 3
    names = [p["name"] for p in prompts]
    assert "scaffold_dashboard" in names
    assert "debug_reactive_cycle" in names

    prompt = get_mcp_prompt("scaffold_dashboard", {"mode": "express", "theme": "sales"})
    assert prompt is not None
    assert "messages" in prompt
    assert "Express" in prompt["messages"][0]["content"]["text"]


@pytest.mark.asyncio
async def test_mcp_server_protocol():
    server = ShinyMCPServer()

    # initialize
    init_res = await server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {},
        }
    )
    assert init_res is not None
    assert init_res["result"]["serverInfo"]["name"] == "shiny-mcp-server"

    # ping
    ping_res = await server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "ping",
        }
    )
    assert ping_res == {"jsonrpc": "2.0", "id": 2, "result": {}}

    # tools/list
    tools_res = await server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/list",
        }
    )
    assert tools_res is not None
    assert len(tools_res["result"]["tools"]) >= 6

    # tools/call (validation)
    call_res = await server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "shiny_validate_code",
                "arguments": {
                    "code": "from shiny.express import ui\nui.input_slider('n', 'N', 1, 10, 5)"
                },
            },
        }
    )
    assert call_res is not None
    assert "valid" in call_res["result"]["content"][0]["text"]

    # resources/list
    res_list = await server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "resources/list",
        }
    )
    assert res_list is not None
    assert len(res_list["result"]["resources"]) > 0

    # resources/read
    res_read = await server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "resources/read",
            "params": {"uri": "shiny://components/catalog"},
        }
    )
    assert res_read is not None
    assert "contents" in res_read["result"]

    # prompts/list
    p_list = await server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "prompts/list",
        }
    )
    assert p_list is not None
    assert len(p_list["result"]["prompts"]) >= 3

    # unknown method
    unknown_res = await server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 8,
            "method": "unknown/method",
        }
    )
    assert unknown_res is not None
    assert "error" in unknown_res
    assert unknown_res["error"]["code"] == -32601


@pytest.mark.asyncio
async def test_mcp_server_run_stdio():
    server = ShinyMCPServer()
    input_data = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "ping"}) + "\n"
    stdin_stream = io.StringIO(input_data)
    stdout_stream = io.StringIO()

    await server.run_stdio(stdin_stream, stdout_stream)
    output_lines = stdout_stream.getvalue().strip().splitlines()
    assert len(output_lines) == 1
    resp = json.loads(output_lines[0])
    assert resp["id"] == 1
    assert resp["result"] == {}


def test_cli_mcp_info():
    runner = CliRunner()
    result = runner.invoke(main, ["mcp", "info"])
    assert result.exit_code == 0
    assert "Shiny for Python MCP Server" in result.output
    assert "shiny_validate_code" in result.output
    assert "shiny://components/catalog" in result.output
    assert "mcpServers" in result.output
