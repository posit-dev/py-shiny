# Shiny + WebMCP Sales Explorer

[WebMCP](https://developer.chrome.com/docs/ai/webmcp) lets browser agents discover named tools and call them in an open web page. This integration connects a live Shiny session to those tools so a person and an agent can share and update the same dashboard controls.

## 1. Quickstart

Run the bundled sales explorer app:

```sh
# From this directory:
shiny run app.py

# Or from the repository root:
shiny run examples/webmcp/app.py
```

Open the dashboard in a WebMCP-supported browser (e.g. Chrome launched with `--enable-blink-features=WebMCP`), and ask your browser agent:

> "Compare West online sales with retail, and leave the dashboard showing online sales."

The agent queries the custom tool `compare_channels` to calculate revenue without altering the view, then calls `shiny_set_inputs` to update the dropdown filters.

> Standard browsers without WebMCP support still run the dashboard normally.

## 2. Automatic Tools

When enabled, Shiny automatically provides these built-in browser-agent tools:

| Tool | What an agent gets |
| --- | --- |
| `shiny_describe_app` | Discovers visible inputs, labels, values, schemas, exposed actions, and outputs. |
| `shiny_set_inputs` | Updates a batch of inputs by ID and returns dashboard state after a reactive flush. |
| `shiny_read_outputs` | Reads displayed text/code outputs, optionally filtered by ID. |
| `shiny_invoke_action` | Triggers an action button explicitly marked with `attrs["data-webmcp"] = "action"`. |

Supported controls include text, textarea, numbers, checkboxes/groups, radio buttons, select/Selectize, numeric sliders/ranges, and dates/ranges. To exclude an input or container from discovery, add `data-webmcp="exclude"`.

## 3. Enable in Your App

No custom JavaScript is required:

```python
# Core
app = App(app_ui, server, webmcp=True)

# Express
from shiny.express import app_opts

app_opts(webmcp=True)
```

Or enable via CLI for any existing app without code changes:

```sh
SHINY_WEBMCP=1 shiny run app.py
```

## 4. Add Custom Python Tools

Use `@webmcp.tool` inside your server function to expose domain calculations or structured data:

```python
from shiny import App, Inputs, Outputs, Session, ui, webmcp


def server(input: Inputs, output: Outputs, session: Session):
    @webmcp.tool(
        description="Multiply current quantity by a factor.",
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

Tools run in an isolated reactive context in their own session and must return JSON-serializable data.
