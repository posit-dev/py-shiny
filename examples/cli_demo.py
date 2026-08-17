from __future__ import annotations

import asyncio
from shiny._components import get_component_doc, get_template, list_components
from shiny._inspect import format_graph_mermaid, inspect_reactive_graph
from shiny._simulator import simulate_shiny_app
from shiny._validate import validate_shiny_code


async def run_cli_demo() -> None:
    print("=" * 70)
    print("Shiny for Python - Developer CLI & Engine Demo")
    print("=" * 70)

    # 1. Validation
    print("\n[Step 1] Validating Shiny code statically...")
    code = """from shiny.express import input, render, ui
ui.page_opts(title="Demo")
ui.input_slider("n", "N", 1, 100, 25)
@render.text
def res():
    return f"Calculated: {input.n() * 4}"
"""
    val_res = validate_shiny_code(code)
    print(f"  Valid: {val_res['valid']} (Mode: {val_res['mode']})")
    print(f"  Detected inputs: {val_res['detected_inputs']}")
    print(f"  Detected outputs: {val_res['detected_outputs']}")

    # 2. Simulation
    print("\n[Step 2] Simulating app headlessly with custom inputs...")
    sim_res = await simulate_shiny_app(code=code, inputs={"n": 50})
    print(f"  Success: {sim_res['success']}")
    print(f"  Rendered outputs: {sim_res['outputs']}")

    # 3. Dependency Graph & Mermaid
    print("\n[Step 3] Inspecting reactive dependency graph...")
    graph = inspect_reactive_graph(code)
    print(f"  Summary: {graph['summary']}")
    print("  Mermaid Diagram:")
    print(format_graph_mermaid(graph))

    # 4. Component Catalog
    print("\n[Step 4] Querying component catalog...")
    layouts = list_components("layout")
    print(f"  Layout components: {[c['name'] for c in layouts]}")
    sidebar_doc = get_component_doc("ui.page_sidebar")
    if sidebar_doc:
        print(f"  page_sidebar signature: {sidebar_doc.get('signature')}")

    # 5. Templates
    print("\n[Step 5] Scaffolding templates...")
    tmpl = get_template("express_dashboard")
    if tmpl:
        print(f"  Loaded template: {tmpl['name']} ({len(tmpl['code'])} chars)")

    print("\n" + "=" * 70)
    print("CLI engine demo completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_cli_demo())
