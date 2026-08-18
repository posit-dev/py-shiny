from __future__ import annotations

import inspect
from typing import Any, Dict, List, Optional

from . import render, ui

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


def list_components(category: Optional[str] = None) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for item in COMPONENT_CATALOG.values():
        if not category or item.get("category") == category:
            results.append(item)
    return results


def get_component_doc(name: str) -> Optional[Dict[str, Any]]:
    lookup_name = name
    if not lookup_name.startswith("ui.") and not lookup_name.startswith("render."):
        if f"ui.{lookup_name}" in COMPONENT_CATALOG:
            lookup_name = f"ui.{lookup_name}"
        elif f"render.{lookup_name}" in COMPONENT_CATALOG:
            lookup_name = f"render.{lookup_name}"

    if lookup_name not in COMPONENT_CATALOG:
        return None

    doc_item = dict(COMPONENT_CATALOG[lookup_name])
    obj = None
    if lookup_name.startswith("ui."):
        attr = lookup_name.removeprefix("ui.")
        obj = getattr(ui, attr, None)
    elif lookup_name.startswith("render."):
        attr = lookup_name.removeprefix("render.")
        obj = getattr(render, attr, None)

    if obj is not None:
        try:
            doc_item["signature"] = str(inspect.signature(obj))
        except Exception:
            pass
        if obj.__doc__:
            doc_item["docstring"] = obj.__doc__

    return doc_item
