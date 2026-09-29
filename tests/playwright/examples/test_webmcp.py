import json
from typing import Any

import pytest
from conftest import create_example_fixture
from playwright.sync_api import Browser, BrowserType, Page, expect

from shiny.run import ShinyAppProc

webmcp_app = create_example_fixture("webmcp")

# CI browsers need not implement the experimental WebMCP API. Capture only tool
# registration; execute the real callbacks against a real Shiny WebSocket server.
CAPTURE_TOOLS = """
window.registeredTools = {};
Object.defineProperty(document, 'modelContext', {value: {
    async registerTool(tool) { window.registeredTools[tool.name] = tool; }
}});
"""


def test_agent_and_human_share_the_dashboard(
    browser: Browser, webmcp_app: ShinyAppProc
):
    context = browser.new_context()
    try:
        context.add_init_script(CAPTURE_TOOLS)
        page = context.new_page()
        page.goto(webmcp_app.url)
        expect(page.locator("#webmcp-status")).to_have_text("Agent tools ready")
        result = page.evaluate("""async () => JSON.parse(await registeredTools
            .set_sales_filters.execute({region: 'West', channel: 'Online'}))""")
        assert result["revenue"] == 600
        expect(page.locator("#region")).to_have_value("West")
        expect(page.locator("#channel")).to_have_value("Online")
        assert json.loads(page.locator("#summary").inner_text())["revenue"] == 600

        # A repeated call must finish even when neither filter changes.
        assert page.evaluate("""async () => JSON.parse(await registeredTools
            .set_sales_filters.execute({region: 'West', channel: 'Online'})).revenue
        """) == 600
        page.locator("#channel").select_option("Retail")
        expect(page.locator("#headline")).to_have_text("2 orders · $300 USD")
        assert page.evaluate("""async () => JSON.parse(await registeredTools
            .get_sales_summary.execute({})).revenue""") == 300

        # Schema validation is not a substitute for validating the callback.
        errors = page.evaluate("""async () => {
            const errors = [];
            for (const filters of [{region: 'Mars', channel: 'Online'}, null, false, {}]) {
                try { await registeredTools.set_sales_filters.execute(filters); }
                catch (error) { errors.push(error.message); }
            }
            return errors;
        }""")
        assert len(errors) == 4
        assert all("region" in error for error in errors)
        expect(page.locator("#region")).to_have_value("West")
        expect(page.locator("#channel")).to_have_value("Retail")

        # A stale result cannot satisfy a new tool call, and simultaneous calls
        # must not overwrite each other's dashboard state.
        results = page.evaluate("""async () => {
            const first = registeredTools.set_sales_filters.execute({region: 'North', channel: 'Online'});
            $(document).trigger({type: 'shiny:value', name: 'summary',
                value: JSON.stringify({request_id: 'stale', revenue: -1})});
            const second = registeredTools.get_sales_summary.execute({});
            return Promise.allSettled([first, second]).then(results =>
                results.map(r => r.status === 'fulfilled'
                    ? JSON.parse(r.value) : {error: r.reason.message}));
        }""")
        assert results[0]["revenue"] == 200
        assert "already running" in results[1]["error"]

        # Cancelling a wait must release the bridge for the next request.
        cancelled = page.evaluate("""async () => {
            const controller = new AbortController();
            const result = registeredTools.get_sales_summary.execute({}, {signal: controller.signal})
                .catch(error => error.message);
            controller.abort();
            return result;
        }""")
        assert "cancelled" in cancelled
        assert page.evaluate("""async () => JSON.parse(await registeredTools
            .get_sales_summary.execute({})).revenue""") == 200

        error = page.evaluate("""async () => {
            $(document).trigger('shiny:disconnected');
            try { await registeredTools.get_sales_summary.execute({}); }
            catch (error) { return error.message; }
        }""")
        assert "disconnected" in error

    finally:
        context.close()


def test_native_webmcp(
    browser_type: BrowserType,
    browser_type_launch_args: dict[str, Any],
    webmcp_app: ShinyAppProc,
):
    if browser_type.name != "chromium":
        pytest.skip("Native WebMCP smoke test requires a supporting Chromium build")
    options: dict[str, Any] = {
        **browser_type_launch_args,
        "args": [
            *browser_type_launch_args.get("args", []),
            "--enable-blink-features=WebMCP",
        ],
    }
    browser = browser_type.launch(**options)
    try:
        page = browser.new_page()
        page.goto(webmcp_app.url)
        if not page.evaluate("typeof document.modelContext?.getTools === 'function'"):
            pytest.skip("This Chromium build does not expose native WebMCP")
        expect(page.locator("#webmcp-status")).to_have_text("Agent tools ready")
        # Chrome 153/154 require JSON-string arguments; 155+ accepts objects.
        string_arguments = int(browser.version.split(".")[0]) < 155
        for channel, revenue in [("Online", 600), ("Retail", 300), ("Online", 600)]:
            arguments = {"region": "West", "channel": channel}
            result = page.evaluate(
                """async args => {
                    const tools = await document.modelContext.getTools();
                    const tool = tools.find(t => t.name === 'set_sales_filters');
                    return JSON.parse(await document.modelContext.executeTool(tool, args));
                }""",
                json.dumps(arguments) if string_arguments else arguments,
            )
            assert result["revenue"] == revenue
            expect(page.locator("#region")).to_have_value("West")
            expect(page.locator("#channel")).to_have_value(channel)
            assert (
                json.loads(page.locator("#summary").inner_text())["revenue"] == revenue
            )
    finally:
        browser.close()


def test_normal_browser_still_works(browser: Browser, webmcp_app: ShinyAppProc):
    context = browser.new_context()
    try:
        context.add_init_script(
            "Object.defineProperty(document, 'modelContext', {value: undefined});"
        )
        page: Page = context.new_page()
        page.goto(webmcp_app.url)
        page.locator("#region").select_option("South")
        page.locator("#channel").select_option("Online")
        expect(page.locator("#headline")).to_have_text("1 orders · $150 USD")
        expect(page.locator("#webmcp-status")).to_contain_text("WebMCP unavailable")

    finally:
        context.close()
