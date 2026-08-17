from __future__ import annotations

import asyncio
import json

from shiny.mcp import ShinyMCPServer


async def run_mcp_demo() -> None:
    server = ShinyMCPServer()

    print("=" * 70)
    print("Shiny for Python - Model Context Protocol (MCP) Server Demo")
    print("=" * 70)

    # 1. MCP Initialization
    print("\n[Step 1] Initializing Protocol Connection...")
    init_res = await server.handle_request(
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
    )
    print(
        f"Connected to: {init_res['result']['serverInfo']['name']} (v{init_res['result']['serverInfo']['version']})"
    )
    print(f"Capabilities: {list(init_res['result']['capabilities'].keys())}")

    # 2. List Tools
    print("\n[Step 2] Listing MCP Tools...")
    tools_res = await server.handle_request(
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
    )
    for tool in tools_res["result"]["tools"]:
        print(f"  • {tool['name']:<28} - {tool['description'][:60]}...")

    # 3. Static AST Validation Demo
    print("\n[Step 3] Calling 'shiny_validate_code' on buggy code...")
    buggy_snippet = """
from shiny import shinyApp, fluidPage, ui

ui.input_slider("num", "Number", 1, 10, 5)
ui.input_slider("num", "Duplicate Number", 1, 10, 5)

def server(input, output, session):
    input.num = 100
"""
    val_res = await server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "shiny_validate_code",
                "arguments": {"code": buggy_snippet},
            },
        }
    )
    val_data = json.loads(val_res["result"]["content"][0]["text"])
    print(f"  Valid: {val_data['valid']}")
    print(f"  Mode: {val_data['mode']}")
    print("  Detected Errors:")
    for err in val_data["errors"]:
        print(f"    - Line {err['line']}: [{err['code']}] {err['message']}")
    print("  Detected Warnings:")
    for warn in val_data["warnings"]:
        print(f"    - Line {warn['line']}: [{warn['code']}] {warn['message']}")

    # 4. Headless Simulation Demo
    print("\n[Step 4] Calling 'shiny_simulate_app' (In-Memory Headless Runner)...")
    app_snippet = """
from shiny.express import input, render, ui

ui.input_slider("n", "Slider N", 1, 100, 10)
ui.input_numeric("multiplier", "Multiplier", 3)

@render.text
def computed_total():
    return f"Computed Total = {input.n() * input.multiplier()}"
"""
    sim_res = await server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "shiny_simulate_app",
                "arguments": {
                    "code": app_snippet,
                    "inputs": {"n": 25, "multiplier": 4},
                },
            },
        }
    )
    sim_data = json.loads(sim_res["result"]["content"][0]["text"])
    print(f"  Simulation Success: {sim_data['success']}")
    print(f"  Calculated Reactive Outputs: {sim_data['outputs']}")

    # 5. Component Introspection
    print("\n[Step 5] Calling 'shiny_get_component_doc' for 'ui.page_sidebar'...")
    doc_res = await server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "shiny_get_component_doc",
                "arguments": {"name": "ui.page_sidebar"},
            },
        }
    )
    doc_data = json.loads(doc_res["result"]["content"][0]["text"])
    print(f"  Signature: {doc_data.get('name')}{doc_data.get('signature', '()')}")
    print(f"  Snippet: {doc_data.get('snippet')}")

    # 6. Read MCP Resource
    print("\n[Step 6] Reading MCP Resource 'shiny://docs/reactivity'...")
    res_data = await server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "resources/read",
            "params": {"uri": "shiny://docs/reactivity"},
        }
    )
    guide_text = res_data["result"]["contents"][0]["text"]
    first_line = guide_text.splitlines()[0] if guide_text else ""
    print(f"  Resource URI: {res_data['result']['contents'][0]['uri']}")
    print(f"  Heading: {first_line}")
    print(f"  Length: {len(guide_text)} characters")

    print("\n" + "=" * 70)
    print("Demo completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_mcp_demo())
