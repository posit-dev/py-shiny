from __future__ import annotations

from typing import Any, Dict, List

from .._components import (
    get_component_doc,
    get_template,
    list_components,
)
from .._inspect import inspect_reactive_graph
from .._simulator import simulate_shiny_app
from .._validate import validate_shiny_code


def get_mcp_tools_definitions() -> List[Dict[str, Any]]:
    return [
        {
            "name": "shiny_validate_code",
            "description": "Perform static AST analysis and validation on Shiny for Python code to detect reactivity errors, duplicate IDs, and mode mismatches.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The Python source code of the Shiny application.",
                    },
                },
                "required": ["code"],
            },
        },
        {
            "name": "shiny_simulate_app",
            "description": "Run a Shiny app headlessly in-memory without a browser to test startup, simulate input events, flush reactivity, and capture output values or runtime errors.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Optional Python code string to simulate.",
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Optional path to a Shiny app file to simulate.",
                    },
                    "inputs": {
                        "type": "object",
                        "description": "Dictionary of initial input values to simulate (e.g. {'n': 25, 'region': 'North'}).",
                    },
                    "timeout_secs": {
                        "type": "number",
                        "description": "Timeout in seconds for app execution (default 3.0).",
                    },
                },
            },
        },
        {
            "name": "shiny_list_components",
            "description": "List all available Shiny for Python UI components, layouts, inputs, outputs, and renderers.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["layout", "cards", "inputs", "outputs", "renderers"],
                        "description": "Optional filter by component category.",
                    },
                },
            },
        },
        {
            "name": "shiny_get_component_doc",
            "description": "Get detailed documentation, signature, and code snippet for a specific Shiny component or renderer.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The fully qualified function name (e.g. 'ui.page_sidebar', 'ui.layout_columns', 'render.data_frame').",
                    },
                },
                "required": ["name"],
            },
        },
        {
            "name": "shiny_scaffold_app",
            "description": "Generate a production-ready starter template for a Shiny application.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "template": {
                        "type": "string",
                        "enum": ["express_dashboard", "core_dashboard", "ai_chat"],
                        "description": "The template to scaffold.",
                    },
                },
                "required": ["template"],
            },
        },
        {
            "name": "shiny_inspect_reactive_graph",
            "description": "Parse a Shiny application to extract inputs, reactive calcs, effects, and outputs, generating a reactive dependency map.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The Python source code of the Shiny application.",
                    },
                },
                "required": ["code"],
            },
        },
    ]


async def dispatch_mcp_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    if name == "shiny_validate_code":
        code = arguments.get("code", "")
        return validate_shiny_code(code)

    elif name == "shiny_simulate_app":
        code = arguments.get("code")
        file_path = arguments.get("file_path")
        inputs = arguments.get("inputs")
        timeout = float(arguments.get("timeout_secs", 3.0))
        return await simulate_shiny_app(
            code=code,
            file_path=file_path,
            inputs=inputs,
            timeout_secs=timeout,
        )

    elif name == "shiny_list_components":
        category = arguments.get("category")
        return {"components": list_components(category)}

    elif name == "shiny_get_component_doc":
        comp_name = arguments.get("name", "")
        doc_item = get_component_doc(comp_name)
        if doc_item is not None:
            return doc_item
        return {"error": f"Component '{comp_name}' not found in catalog."}

    elif name == "shiny_scaffold_app":
        tmpl_name = arguments.get("template", "express_dashboard")
        tmpl = get_template(tmpl_name)
        if tmpl is not None:
            return tmpl
        return {"error": f"Template '{tmpl_name}' not found."}

    elif name == "shiny_inspect_reactive_graph":
        code = arguments.get("code", "")
        return inspect_reactive_graph(code)

    return {"error": f"Unknown tool: '{name}'"}
