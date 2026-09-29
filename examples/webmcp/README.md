# Shiny + WebMCP: explore a dashboard together

This example lets a browser agent operate a Shiny sales dashboard through two
named tools. The person and agent share the same controls, Python calculations,
and visible results. It uses eight fictional orders and no extra dependencies.

Try asking an agent:

> Compare West online sales with retail, and leave the dashboard showing online sales.

The expected answer is **$600 online versus $300 retail**, with two orders in
each channel. The final visible filters should be **West / Online**. This is a
suggested agent evaluation, not a recorded model run.

## Run it

From a checkout with Shiny installed:

```sh
shiny run examples/webmcp/app.py --port 8000
```

Open `http://localhost:8000`. The filters work in ordinary browsers. To use native
tools, follow Chrome's [WebMCP setup instructions](https://developer.chrome.com/docs/ai/webmcp)
and enable `chrome://flags/#enable-webmcp-testing` in a supporting Chrome build.
The sidebar says **Agent tools ready** when registration succeeds. Chrome's
Model Context Tool Inspector extension, linked in those instructions, can list
and invoke the tools and provide an agent chat for the prompt above.

This example targets the current [imperative API](https://developer.chrome.com/docs/ai/webmcp/imperative-api),
using `document.modelContext`. Older experimental builds
using `navigator.modelContext` are not supported. WebMCP is evolving; follow the
linked documentation for browser availability and deployment requirements.

In a supporting browser, this DevTools snippet exercises native discovery and
execution without a model or API key:

```js
const tools = await document.modelContext.getTools();
const filter = tools.find((tool) => tool.name === "set_sales_filters");
const result = await document.modelContext.executeTool(filter, {
  region: "West",
  channel: "Online",
});
console.log(JSON.parse(result)); // revenue: 600, orders: 2
```

The snippet uses Chrome 155+ object arguments. In Chrome 153/154, pass
`JSON.stringify({ region: "West", channel: "Online" })` as the second argument
to `executeTool` instead. This changes the caller, not the app's tool callbacks.

## What the agent can do

| Tool                | Arguments                                                         | Result                                                            |
| ------------------- | ----------------------------------------------------------------- | ----------------------------------------------------------------- |
| `set_sales_filters` | `region`: All, North, South, West; `channel`: All, Online, Retail | Updates both visible filters and returns the computed summary.    |
| `get_sales_summary` | `{}`                                                              | Reads the current summary, including the person's filter changes. |

Both return a JSON string containing the actual filters, order count, revenue,
average order, and currency. Only the read tool is annotated `readOnlyHint`:
filtering changes the shared dashboard. No arbitrary input setter or session
inspection tool is exposed.

## How the bridge works

1. `webmcp.js` waits for Shiny initialization and registers tools if WebMCP exists.
2. A filter call updates the plain select controls and uses `Shiny.setInputValue`
   to send those values and a unique request token in the normal input batch.
3. The server computes the same reactive `sales()` result used by the dashboard.
   Its `summary` output includes the token.
4. The tool waits for the matching `shiny:value` event and the next animation
   frame, then returns the result. It ignores older responses; a new token also
   makes repeated calls with identical filters complete.

The browser validates tool arguments and Python validates input values again.
Calls run one at a time. Disconnects, cancellation, and a ten-second deadline
reject the pending call and remove its listeners. Cancelling stops the wait; it
does not undo filters already applied. If a person edits during a call, the
returned `filters` describe the server's computed result. The dashboard remains
interactive throughout.

This is an app-owned example, not a new Shiny API. It does not start an MCP
server, enable test mode, expose Python objects, or require a hosted model.
WebMCP supplies browser tool discovery and invocation; Shiny supplies the live
session and reactive calculation.

## Reusing #2495: two layers of tests

[`local_server` from #2495](https://github.com/posit-dev/py-shiny/pull/2495)
provides the fast server-side test harness. The tests select this example via
indirect parametrization, set inputs, and inspect the resulting JSON:

```python
@pytest.mark.parametrize(
    "local_server", ["../../examples/webmcp/app.py"], indirect=True
)
def test_sales(local_server):
    local_server.set_inputs(
        region="West", channel="Online", webmcp_request_id="one"
    )
    result = json.loads(local_server.get_output("summary").value)
    assert result["request_id"] == "one"
    assert result["revenue"] == 600
```

The relative path above is for a test in `tests/pytest/`. These tests exercise
real reactive calculations, request correlation, and invalid-input recovery.
`local_server` does **not** execute JavaScript or provide a browser agent session.

The portable Playwright tests run a real app and execute its registered callbacks.
They check visible controls, returned results, human edits, repeated requests,
stale responses, overlapping calls, cancellation, disconnects, and the browser
fallback. Only WebMCP registration is replaced with a test double so CI does not
depend on an experimental browser feature. These tests establish the Shiny
bridge's behavior independently of native browser API compatibility.

A separate native smoke test enables WebMCP in a fresh Chromium browser, discovers
the tools with `getTools()`, and invokes `executeTool()` for the comparison above.
It skips on browsers without the API, and handles the Chrome 153/154 argument
format. It was verified in Chrome 153.0.8010.53. None of these deterministic tests
establishes whether a model will choose the right tools; use the agent prompt
above for that evaluation.

```sh
pytest tests/pytest/test_webmcp_example.py -n 0
pytest -c tests/playwright/playwright-pytest.ini \
  tests/playwright/examples/test_webmcp.py -o addopts='' \
  -o asyncio_default_fixture_loop_scope=function --browser chromium -n 0
```

Add `--browser-channel chrome` to use an installed Chrome with native WebMCP
instead of Playwright's bundled Chromium. The native test enables the feature in
its isolated browser process; it does not change your browser profile or flags.
