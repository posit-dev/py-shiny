from __future__ import annotations

from typing import Any, Dict, List, Optional

PROMPTS_REGISTRY: Dict[str, Dict[str, Any]] = {
    "scaffold_dashboard": {
        "name": "scaffold_dashboard",
        "description": "Generate a modern, responsive Shiny dashboard using Shiny Express or Core mode.",
        "arguments": [
            {
                "name": "mode",
                "description": "App mode: 'express' (recommended for new apps) or 'core'.",
                "required": False,
            },
            {
                "name": "theme",
                "description": "Desired visual theme or domain (e.g. sales, biotech, iot, finance).",
                "required": False,
            },
        ],
        "template": """You are an expert Shiny for Python engineer.
Please create a high-quality, responsive Shiny dashboard.
Mode: {mode}
Domain/Theme: {theme}

Design Guidelines:
- In Express mode, use `ui.page_opts(title="...", fillable=True)` with `ui.layout_columns` and `ui.card`.
- In Core mode, use `app_ui = ui.page_sidebar(...)` and `def server(input, output, session):`.
- Use modern UI components: `ui.value_box`, `ui.input_select`, `ui.input_slider`, `ui.card_header`.
- Implement clean reactive data flow with `@reactive.calc` and `@render.*` decorators.
- Ensure all inputs and outputs have unique IDs.
""",
    },
    "debug_reactive_cycle": {
        "name": "debug_reactive_cycle",
        "description": "Debug reactive dependency cycles, silent failures, or unexpected re-executions.",
        "arguments": [
            {
                "name": "error_description",
                "description": "The symptom, traceback, or unexpected reactive behavior observed.",
                "required": True,
            },
        ],
        "template": """You are an expert in Shiny for Python reactive programming.
Please diagnose the following issue:
{error_description}

Checklist:
1. Are inputs read inside reactive scopes (renderers, calcs, effects) using call syntax `input.x()`?
2. Are reactive values modified using `val.set(...)` rather than assignment `val = ...`?
3. Is `reactive.isolate()` used appropriately when reading a reactive without creating a dependency?
4. Is `@reactive.event(...)` applied correctly to button clicks?
5. Are all output IDs matching between UI and server definitions?
""",
    },
    "convert_core_to_express": {
        "name": "convert_core_to_express",
        "description": "Convert a Shiny Core application (app_ui + server) into a clean Shiny Express application.",
        "arguments": [
            {
                "name": "core_code",
                "description": "The existing Shiny Core source code.",
                "required": True,
            },
        ],
        "template": """Convert the following Shiny Core application to modern Shiny Express mode:

```python
{core_code}
```

Conversion Rules:
1. Replace `from shiny import App, ui, render, reactive` with `from shiny.express import input, render, ui`.
2. Remove `app_ui = ...` and top-level layout nesting; replace with `ui.page_opts(...)` and `with ui.card():` context blocks.
3. Remove `def server(input, output, session):` wrapper. Place reactive definitions directly at module level.
4. Replace `ui.output_text("txt")` + server `@render.text def txt():` with inline `@render.text def txt():` in Express layout.
5. Ensure `app = App(...)` is removed (Express files are executed directly).
""",
    },
    "write_shiny_tests": {
        "name": "write_shiny_tests",
        "description": "Generate unit and Playwright integration tests for a Shiny app.",
        "arguments": [
            {
                "name": "app_code",
                "description": "The Shiny application code to write tests for.",
                "required": True,
            },
        ],
        "template": """Write unit tests and Playwright integration tests for this Shiny application:

```python
{app_code}
```

Testing Guidelines:
- Use `shiny.playwright.controller` for input interactions and assertions.
- Use `shiny.pytest.create_app_fixture` to manage the app lifecycle.
- Prefer auto-waiting `.expect_*()` controller methods over manual sleeps.
""",
    },
}


def list_mcp_prompts() -> List[Dict[str, Any]]:
    return [
        {
            "name": p["name"],
            "description": p["description"],
            "arguments": p.get("arguments", []),
        }
        for p in PROMPTS_REGISTRY.values()
    ]


def get_mcp_prompt(
    name: str, arguments: Optional[Dict[str, str]] = None
) -> Optional[Dict[str, Any]]:
    if name not in PROMPTS_REGISTRY:
        return None

    prompt_def = PROMPTS_REGISTRY[name]
    args = arguments or {}
    mode = args.get("mode", "express")
    theme = args.get("theme", "general")
    error_desc = args.get("error_description", "")
    core_code = args.get("core_code", "")
    app_code = args.get("app_code", "")

    content = prompt_def["template"].format(
        mode=mode,
        theme=theme,
        error_description=error_desc,
        core_code=core_code,
        app_code=app_code,
    )

    return {
        "description": prompt_def["description"],
        "messages": [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": content.strip(),
                },
            }
        ],
    }
