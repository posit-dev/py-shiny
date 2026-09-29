# Shiny + WebMCP

[WebMCP](https://developer.chrome.com/docs/ai/webmcp) lets a browser agent discover
named tools with argument schemas and call them in a person's open page. This
experimental integration exposes a live Shiny session through those tools. The
person and agent see and update the same controls.

## Enable it in an existing app

With a Shiny version containing this feature, start an existing Core or Express
app with:

```sh
SHINY_WEBMCP=1 shiny run app.py
```

No app-specific JavaScript is required. For Core apps, you can also opt in in code:

```python
app = App(app_ui, server, webmcp=True)
```

An explicit `webmcp=False` overrides the environment variable. The default is off:
Shiny only loads the adapter and installs its session RPC handlers when enabled.
Browsers without `document.modelContext.registerTool` still run the app normally.
Consult Chrome's [setup instructions](https://developer.chrome.com/docs/ai/webmcp)
for current browser support and feature flags. WebMCP is evolving; this adapter
uses the imperative `document.modelContext` API.

## Automatic tools

| Tool | What an agent gets |
| --- | --- |
| `shiny_describe_app` | Visible supported inputs, labels, values, schemas, explicitly exposed actions, and output status. |
| `shiny_set_inputs` | Updates a batch of inputs by ID; returns the dashboard after the server's reactive flush. |
| `shiny_read_outputs` | Currently displayed text/code outputs, optionally selected by ID. |
| `shiny_invoke_action` | Clicks an explicitly exposed action button and returns the dashboard after a flush. Only registered when an exposed button is available. |

The adapter uses Shiny's input bindings to update both the widgets and the server.
It discovers dynamic controls and refreshes schemas when choices or bounds change.
Module IDs keep their namespaces. An agent can call, for example:

```json
{"values": {"region": "West", "channel": "Online"}}
```

Supported controls are text/textarea, numbers, checkboxes/groups, radio buttons,
select/Selectize, numeric sliders/ranges, and dates/date ranges. Argument types,
choices, numeric/date bounds, and range order are checked before changing any
widget. Selectize exposes currently loaded choices; remote search and creating
new choices need custom tools. Disabled controls cannot be set; groups containing
disabled inputs are read-only to avoid changing them through a group setter. Hidden controls,
passwords, file uploads, date/time sliders, navigation, and custom bindings are
not exposed by the automatic input tools.

Actions need an explicit marker because button clicks may have consequences:

```python
run_button = ui.input_action_button("run", "Run analysis")
run_button.attrs["data-webmcp"] = "action"
# Include run_button in the app's UI.
```

To omit an input, output, or subtree from automatic discovery, wrap it:

```python
ui.div(ui.input_text("notes", "Notes"), **{"data-webmcp": "exclude"})
```

These markers control discovery, not authorization. Keep application permission
checks in server code. Changes to ordinary inputs may also trigger side effects.

Text/code results are limited to 20,000 characters per output and include status
and truncation information. Plots, tables, HTML, and data frames return metadata
with `status: "unsupported"`; their underlying data is not extracted. Expose a
custom tool when an agent needs structured data or a domain-specific operation.

## Add Python tools

Define tools in a Core server, an Express app, or a module server:

```python
from shiny import App, Inputs, Outputs, Session, ui, webmcp


def server(input: Inputs, output: Outputs, session: Session):
    @webmcp.tool(
        description="Multiply the dashboard's current quantity by a factor.",
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


app = App(ui.page_fluid(ui.input_numeric("quantity", "Quantity", 2)), server, webmcp=True)
```

`@webmcp.tool` returns the original callable. Tools run in an isolated reactive
context in their own session and can be synchronous or asynchronous. JSON Schema
2020-12 validates arguments on the server; schemas must be self-contained object
schemas. Return JSON-serializable data. Schema defaults do not supply arguments;
use Python defaults for optional parameters. Tool names default to the function
name, are module-namespaced, and cannot start with the reserved `shiny_` prefix.

Registration ends with the session or module. Calls use the existing session's
WebSocket and error-sanitization settings. `read_only` and `consequential` are
agent hints, not enforced permission checks. Exposure is disabled unless the app
opts in, even if it defines decorated functions.

Calls are serialized in the browser and time out after 30 seconds. Cancellation
or a timeout stops waiting; already-dispatched Python work may still finish.
Results follow a reactive flush, which does not wait for background/extended
tasks. Use app-specific status/result tools for those workflows.

## Try the sales explorer

```sh
shiny run examples/webmcp/app.py
```

The example enables automatic tools and adds one semantic tool,
`compare_channels`, which compares revenue without changing the dashboard. Ask a
WebMCP-capable browser agent:

> Compare West online sales with retail, and leave the dashboard showing online sales.

It can call `compare_channels({"region":"West"})` to get Online **$600**, Retail
**$300**, and a **$300** difference, then call `shiny_set_inputs` to select West and
Online. Or it can perform the comparison using automatic tools alone. The eight
orders are fictional and small enough to verify by hand.

Compared with Playwright, the benefit is a discoverable contract: named
operations, allowed arguments, structured results, and a defined reactive flush
boundary. Playwright remains useful for visual checks, unsupported controls, and
end-to-end tests. WebMCP does not run an LLM or create a remote MCP server; an agent
still needs a browser integration that discovers and invokes these tools.

## Tests

The `local_server` fixture introduced in [#2495](https://github.com/posit-dev/py-shiny/pull/2495)
checks the example's server calculations and invalid-input recovery without a
browser. WebSocket tests cover tool schemas, module/session isolation and error
sanitization. Browser tests exercise the adapter against live Shiny apps,
including unmodified Core and Express examples, dynamic controls, dates,
cancellation and module teardown. A separate smoke test uses native WebMCP;
it skips if the browser lacks the API. These tests verify tool behavior, not an
LLM's ability to choose the right calls from a prompt.

```sh
uv run pytest tests/pytest/test_webmcp.py tests/pytest/test_webmcp_example.py
uv run pytest -c tests/playwright/playwright-pytest.ini \
  tests/playwright/examples/test_webmcp.py tests/playwright/shiny/webmcp \
  -o addopts='' -o asyncio_default_fixture_loop_scope=function \
  --browser chromium --browser-channel chrome -n 0
```

The native test enables `WebMCP` in an isolated Chrome process. It does not alter
your browser profile. Omit `--browser-channel chrome` to use Playwright's bundled
Chromium; the adapter tests also work with a captured registration interface.
