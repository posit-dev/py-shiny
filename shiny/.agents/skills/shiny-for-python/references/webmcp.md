# WebMCP browser-agent tools

WebMCP exposes named tools in a person's open browser tab. Use Shiny's opt-in
adapter to let an agent share a live dashboard; do not add app-specific JavaScript
for standard controls. Use Python tools for business operations and structured
results that the automatic tools cannot infer.

## Enable an existing app

Run a Core or Express app with `SHINY_WEBMCP=1 shiny run app.py`. In Core,
`App(app_ui, server, webmcp=True)` enables it; in Express, `app_opts(webmcp=True)`. Explicit `False` overrides the
environment. The default is disabled. Apps work normally in browsers without the
experimental `document.modelContext.registerTool` API. The agent needs a browser
integration that supports WebMCP; Shiny does not supply an LLM or a remote MCP
server.

| Tool | Use |
| --- | --- |
| `shiny_describe_app` | Discover visible supported inputs, their IDs/labels/values/schemas, actions and output status. |
| `shiny_set_inputs` | Set `{"values": {"input_id": value}}` and read results after a server reactive flush. |
| `shiny_read_outputs` | Read displayed text/code outputs; optionally pass `{"ids": ["output_id"]}`. |
| `shiny_invoke_action` | Invoke an explicitly exposed button with `{"id": "button_id"}`. |

Supported inputs include text/textarea, number, checkbox/group, radio,
select/Selectize, numeric slider/range and date/range. Use the returned schemas;
choices and bounds can change. Use fully namespaced IDs inside modules. Disabled
controls cannot be set. Hidden, password, file, date/time slider and custom
controls are omitted. Selectize lists currently loaded choices, so remote search
needs an app-defined tool.

Only explicitly marked action buttons are exposed:

```python
from shiny import ui

run_button = ui.input_action_button("run", "Run analysis")
run_button.attrs["data-webmcp"] = "action"
# Place run_button in the app UI.
```

Omit controls or output subtrees with
`ui.div(..., **{"data-webmcp": "exclude"})`. Markers govern discovery, not access
control. Retain server permission checks, and remember ordinary input changes
can trigger effects too.

## Define a semantic tool

Define tools inside a Core server or module server, or at the top level of an
Express app. They run in their own session's isolated reactive context.

```python
from shiny import webmcp
from shiny.express import input, ui

ui.input_numeric("quantity", "Quantity", 2)

@webmcp.tool(
    description="Multiply the current quantity by a factor and return the product.",
    input_schema={
        "type": "object",
        "properties": {"factor": {"type": "number"}},
        "required": ["factor"],
        "additionalProperties": False,
    },
    read_only=True,
)
def multiply(factor: float):
    return {"product": input.quantity() * factor}
```

Start this Express app with `SHINY_WEBMCP=1 shiny run app.py`. Arguments are
validated using JSON Schema 2020-12 and passed as keyword arguments. Use a
self-contained object schema; external references are unsupported.
`additionalProperties` defaults to `False`, so unknown arguments are rejected
with a validation error rather than reaching the function. Optional
arguments need Python defaults; schema defaults do not fill them in. Return
JSON-serializable values from sync or async functions. The decorator preserves
the original callable. Names default to function names and gain module
namespaces. The `shiny_` prefix is reserved; duplicate names are errors. Tools
are removed on session or module destruction.

`read_only=True` and `consequential=True` describe effects to agents; neither
enforces permissions. Calls share the existing session WebSocket and the app's
error-sanitization setting.

## Limits and testing

Automatic output tools read displayed text/code, truncated at 20,000 characters
per output, with status metadata. Plots, HTML, tables and data frames return
`unsupported` metadata. Expose a Python tool for structured results instead of
scraping hidden data or enabling Shiny test mode in a deployed app.

A tool response follows a reactive flush, not completion of background or
extended tasks. Provide explicit status/result tools for those. Concurrent calls
are rejected; call tools sequentially. Cancellation and the 30-second timeout
stop browser waiting, but Python work already dispatched can still complete.

Use `local_server`/`test_server` for reactive calculations and invalid-input
recovery. Use browser tests for discovery, widget synchronization and native
WebMCP invocation. A deterministic tool test does not establish that an LLM can
choose the right calls from a natural-language request.
