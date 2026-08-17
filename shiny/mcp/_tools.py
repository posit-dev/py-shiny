from __future__ import annotations

import ast
import inspect
from typing import Any, Dict, List, Optional, Set

from .. import render, ui
from ._simulator import simulate_shiny_app
from ._validator import validate_shiny_code

COMPONENT_CATALOG: Dict[str, Dict[str, Any]] = {
    "ui.page_sidebar": {
        "name": "ui.page_sidebar",
        "category": "layout",
        "description": "A dashboard page layout with a collapsible sidebar and main content area.",
        "snippet": "ui.page_sidebar(ui.sidebar(ui.input_slider('n', 'N', 1, 100, 50)), ui.card(ui.output_text('res')))",
    },
    "ui.page_fluid": {
        "name": "ui.page_fluid",
        "category": "layout",
        "description": "A fluid container page layout that scales dynamically to the browser viewport width.",
        "snippet": "ui.page_fluid(ui.h2('Header'), ui.input_text('txt', 'Enter text:'))",
    },
    "ui.page_opts": {
        "name": "ui.page_opts",
        "category": "layout",
        "description": "Express-mode page configuration options (title, fillable, window_title, lang).",
        "snippet": "ui.page_opts(title='My Dashboard', fillable=True)",
    },
    "ui.layout_columns": {
        "name": "ui.layout_columns",
        "category": "layout",
        "description": "Modern multi-column responsive layout based on CSS grid / 12-column layout.",
        "snippet": "ui.layout_columns(ui.card('Col 1'), ui.card('Col 2'), col_widths=(6, 6))",
    },
    "ui.card": {
        "name": "ui.card",
        "category": "cards",
        "description": "Bootstrap card container for grouping UI elements with optional headers and footers.",
        "snippet": "ui.card(ui.card_header('Summary'), ui.output_text('summary_text'))",
    },
    "ui.card_header": {
        "name": "ui.card_header",
        "category": "cards",
        "description": "Card header container for titles, badges, and controls.",
        "snippet": "ui.card_header('Card Title')",
    },
    "ui.value_box": {
        "name": "ui.value_box",
        "category": "cards",
        "description": "Prominent metric / KPI container with title, value, and optional showcase icon.",
        "snippet": "ui.value_box('Total Users', '1,240', showcase=ui.span('📈'))",
    },
    "ui.accordion": {
        "name": "ui.accordion",
        "category": "cards",
        "description": "Collapsible accordion panel group for progressive disclosure of complex settings.",
        "snippet": "ui.accordion(ui.accordion_panel('Section 1', 'Content 1'), ui.accordion_panel('Section 2', 'Content 2'))",
    },
    "ui.input_slider": {
        "name": "ui.input_slider",
        "category": "inputs",
        "description": "Slider control for numeric values or ranges.",
        "snippet": "ui.input_slider('num', 'Select Value:', min=0, max=100, value=25)",
    },
    "ui.input_select": {
        "name": "ui.input_select",
        "category": "inputs",
        "description": "Dropdown select menu for choosing from a list of choices.",
        "snippet": "ui.input_select('var', 'Variable:', choices=['Option A', 'Option B', 'Option C'])",
    },
    "ui.input_text": {
        "name": "ui.input_text",
        "category": "inputs",
        "description": "Single-line text input field.",
        "snippet": "ui.input_text('name', 'Enter name:', placeholder='John Doe')",
    },
    "ui.input_numeric": {
        "name": "ui.input_numeric",
        "category": "inputs",
        "description": "Numeric input field with increment/decrement steppers.",
        "snippet": "ui.input_numeric('count', 'Count:', value=10, min=1, max=100)",
    },
    "ui.input_checkbox": {
        "name": "ui.input_checkbox",
        "category": "inputs",
        "description": "Single boolean checkbox input.",
        "snippet": "ui.input_checkbox('show_all', 'Show all records', value=False)",
    },
    "ui.input_action_button": {
        "name": "ui.input_action_button",
        "category": "inputs",
        "description": "Action button triggering reactive effects or events.",
        "snippet": "ui.input_action_button('btn', 'Submit', class_='btn-primary')",
    },
    "ui.input_task_button": {
        "name": "ui.input_task_button",
        "category": "inputs",
        "description": "Action button with built-in loading spinner and disabled state while task runs.",
        "snippet": "ui.input_task_button('calc_btn', 'Run Calculation')",
    },
    "ui.input_dark_mode": {
        "name": "ui.input_dark_mode",
        "category": "inputs",
        "description": "Light/dark mode toggle button with automatic theme switching.",
        "snippet": "ui.input_dark_mode(mode='light')",
    },
    "ui.output_text": {
        "name": "ui.output_text",
        "category": "outputs",
        "description": "Text output container rendering plain text strings.",
        "snippet": "ui.output_text('greeting')",
    },
    "ui.output_data_frame": {
        "name": "ui.output_data_frame",
        "category": "outputs",
        "description": "Interactive data table with sorting, filtering, selection, and editing.",
        "snippet": "ui.output_data_frame('grid')",
    },
    "ui.output_plot": {
        "name": "ui.output_plot",
        "category": "outputs",
        "description": "Static plot container rendering matplotlib, seaborn, or plotnine figures.",
        "snippet": "ui.output_plot('plot')",
    },
    "ui.output_ui": {
        "name": "ui.output_ui",
        "category": "outputs",
        "description": "Dynamic UI output container rendering arbitrary HTML tags or component trees.",
        "snippet": "ui.output_ui('dynamic_controls')",
    },
    "render.text": {
        "name": "render.text",
        "category": "renderers",
        "description": "Renderer decorator for text outputs.",
        "snippet": "@render.text\ndef greeting():\n    return f'Hello, {input.name()}!'",
    },
    "render.data_frame": {
        "name": "render.data_frame",
        "category": "renderers",
        "description": "Renderer decorator for interactive data frame outputs supporting pandas, polars, narwhals.",
        "snippet": "@render.data_frame\ndef grid():\n    return render.DataGrid(df, selection_mode='rows')",
    },
    "render.plot": {
        "name": "render.plot",
        "category": "renderers",
        "description": "Renderer decorator for matplotlib/seaborn figures.",
        "snippet": "@render.plot\ndef plot():\n    fig, ax = plt.subplots()\n    ax.hist(data)\n    return fig",
    },
    "render.ui": {
        "name": "render.ui",
        "category": "renderers",
        "description": "Renderer decorator for dynamic HTML tags and nested UI components.",
        "snippet": "@render.ui\ndef dynamic_controls():\n    return ui.TagList(ui.input_text('dyn', 'Dynamic'))",
    },
}

TEMPLATE_CATALOG: Dict[str, Dict[str, Any]] = {
    "express_dashboard": {
        "name": "express_dashboard",
        "description": "Modern responsive KPI dashboard using Shiny Express mode.",
        "code": """from shiny.express import input, render, ui

ui.page_opts(title="Sales Performance Dashboard", fillable=True)

with ui.sidebar(title="Filters"):
    ui.input_select("region", "Region:", choices=["North", "South", "East", "West"])
    ui.input_slider("threshold", "Sales Threshold ($k):", min=10, max=500, value=100)

with ui.layout_columns():
    with ui.value_box("Total Revenue", showcase=ui.span("💰")):
        @render.text
        def revenue():
            return f"${input.threshold() * 12.5:,.0f}k"

    with ui.value_box("Active Customers", showcase=ui.span("👥")):
        @render.text
        def customers():
            return f"{input.threshold() * 4:,}"

with ui.card():
    ui.card_header("Region Summary")
    @render.text
    def summary():
        return f"Selected Region: {input.region()} | Minimum Threshold: ${input.threshold()}k"
""",
    },
    "core_dashboard": {
        "name": "core_dashboard",
        "description": "Classic Shiny Core dashboard structure with app_ui and server function.",
        "code": """from shiny import App, render, ui

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_select("dataset", "Dataset:", choices=["iris", "penguins", "mtcars"]),
        ui.input_slider("sample_size", "Sample Size:", min=10, max=200, value=50),
    ),
    ui.card(
        ui.card_header("Summary Statistics"),
        ui.output_text("summary"),
    ),
    title="Data Explorer (Core Mode)",
    fillable=True,
)

def server(input, output, session):
    @output
    @render.text
    def summary():
        return f"Dataset: {input.dataset()} | Samples: {input.sample_size()}"

app = App(app_ui, server)
""",
    },
    "ai_chat": {
        "name": "ai_chat",
        "description": "Interactive AI Chat assistant template using shinychat.",
        "code": """from shiny.express import ui
from shinychat import chat_ui, Chat

ui.page_opts(title="AI Assistant", fillable=True)

chat = Chat("chat")
chat_ui("chat")

@chat.on_user_submit
async def handle_user_input(user_input: str):
    response = f"Echo: {user_input}"
    await chat.append_message_stream(response)
""",
    },
}


def inspect_reactive_graph(code: str) -> Dict[str, Any]:
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return {
            "success": False,
            "error": f"SyntaxError: {e.msg}",
            "nodes": [],
            "edges": [],
        }

    inputs: Set[str] = set()
    calcs: Dict[str, Set[str]] = {}
    outputs: Dict[str, Set[str]] = {}

    class GraphVisitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.current_calc: Optional[str] = None
            self.current_output: Optional[str] = None

        def visit_Call(self, node: ast.Call) -> None:
            func_name = ""
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    func_name = f"{node.func.value.id}.{node.func.attr}"

            if (
                func_name.startswith("ui.input_")
                and node.args
                and isinstance(node.args[0], ast.Constant)
            ):
                inputs.add(str(node.args[0].value))

            if (
                isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "input"
            ):
                target_input = node.func.attr
                if self.current_output:
                    outputs.setdefault(self.current_output, set()).add(target_input)
                elif self.current_calc:
                    calcs.setdefault(self.current_calc, set()).add(target_input)

            self.generic_visit(node)

        def _get_decorator_name(self, d: ast.AST) -> str:
            if isinstance(d, ast.Call):
                d = d.func
            if isinstance(d, ast.Name):
                return d.id
            elif isinstance(d, ast.Attribute) and isinstance(d.value, ast.Name):
                return f"{d.value.id}.{d.attr}"
            return ""

        def _handle_func_def(
            self, node: ast.FunctionDef | ast.AsyncFunctionDef
        ) -> None:
            decorators: List[str] = [
                name
                for d in node.decorator_list
                if (name := self._get_decorator_name(d))
            ]

            is_render = any(
                d.startswith("render.") or d.startswith("render_") for d in decorators
            )
            is_calc = any(
                "calc" in d or "event" in d or "effect" in d for d in decorators
            )

            prev_out = self.current_output
            prev_calc = self.current_calc

            if is_render:
                self.current_output = node.name
                outputs.setdefault(node.name, set())
            elif is_calc:
                self.current_calc = node.name
                calcs.setdefault(node.name, set())

            self.generic_visit(node)

            self.current_output = prev_out
            self.current_calc = prev_calc

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            self._handle_func_def(node)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            self._handle_func_def(node)

    visitor = GraphVisitor()
    visitor.visit(tree)

    nodes: List[Dict[str, Any]] = []
    for inp in sorted(inputs):
        nodes.append({"id": inp, "type": "input", "label": f"input.{inp}"})
    for c in sorted(calcs.keys()):
        nodes.append({"id": c, "type": "calc", "label": f"calc:{c}"})
    for out in sorted(outputs.keys()):
        nodes.append({"id": out, "type": "output", "label": f"output:{out}"})

    edges: List[Dict[str, str]] = []
    for out_name, deps in outputs.items():
        for dep in sorted(deps):
            edges.append({"from": dep, "to": out_name})
    for calc_name, deps in calcs.items():
        for dep in sorted(deps):
            edges.append({"from": dep, "to": calc_name})

    return {
        "success": True,
        "nodes": nodes,
        "edges": edges,
        "summary": f"{len(inputs)} inputs, {len(calcs)} reactives/calcs, {len(outputs)} outputs",
    }


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
        results: List[Dict[str, Any]] = []
        for item in COMPONENT_CATALOG.values():
            if not category or item.get("category") == category:
                results.append(item)
        return {"components": results}

    elif name == "shiny_get_component_doc":
        comp_name = arguments.get("name", "")
        if comp_name in COMPONENT_CATALOG:
            doc_item = dict(COMPONENT_CATALOG[comp_name])
            obj = None
            if comp_name.startswith("ui."):
                attr = comp_name.removeprefix("ui.")
                obj = getattr(ui, attr, None)
            elif comp_name.startswith("render."):
                attr = comp_name.removeprefix("render.")
                obj = getattr(render, attr, None)

            if obj is not None:
                try:
                    doc_item["signature"] = str(inspect.signature(obj))
                except Exception:
                    pass
                if obj.__doc__:
                    doc_item["docstring"] = obj.__doc__
            return doc_item
        return {"error": f"Component '{comp_name}' not found in catalog."}

    elif name == "shiny_scaffold_app":
        tmpl_name = arguments.get("template", "express_dashboard")
        if tmpl_name in TEMPLATE_CATALOG:
            return TEMPLATE_CATALOG[tmpl_name]
        return {"error": f"Template '{tmpl_name}' not found."}

    elif name == "shiny_inspect_reactive_graph":
        code = arguments.get("code", "")
        return inspect_reactive_graph(code)

    return {"error": f"Unknown tool: '{name}'"}
