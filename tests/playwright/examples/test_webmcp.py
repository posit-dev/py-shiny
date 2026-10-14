import json
from typing import Any, Callable

import pytest
from conftest import create_example_fixture
from playwright.sync_api import Browser, BrowserType, expect

from shiny.run import ShinyAppProc

webmcp_app = create_example_fixture("webmcp")


def test_native_webmcp(
    browser_type: BrowserType,
    browser_type_launch_args: dict[str, Any],
    launch_browser: Callable[..., Browser],
    webmcp_app: ShinyAppProc,
):
    if browser_type.name != "chromium":
        pytest.skip("Native WebMCP requires a supporting Chromium build")
    browser = launch_browser(
        args=[
            *browser_type_launch_args.get("args", []),
            "--enable-blink-features=WebMCP",
        ],
    )
    try:
        page = browser.new_page()
        page.goto(webmcp_app.url)
        if not page.evaluate("typeof document.modelContext?.getTools === 'function'"):
            pytest.skip("This Chromium build does not expose native WebMCP")
        page.wait_for_function(
            "async () => (await document.modelContext.getTools()).some(t => t.name === 'compare_channels')"
        )
        string_arguments = int(browser.version.split(".")[0]) < 155
        for channel, revenue in [("Online", 600), ("Retail", 300), ("Online", 600)]:
            arguments = {"values": {"region": "West", "channel": channel}}
            result = page.evaluate(
                """async args => {
                    const tools = await document.modelContext.getTools();
                    const tool = tools.find(t => t.name === 'shiny_set_inputs');
                    return JSON.parse(await document.modelContext.executeTool(tool, args));
                }""",
                json.dumps(arguments) if string_arguments else arguments,
            )
            assert (
                json.loads(result["outputs"]["summary"]["value"])["revenue"] == revenue
            )
            expect(page.locator("#region")).to_have_value("West")
            expect(page.locator("#channel")).to_have_value(channel)
        result = page.evaluate(
            """async args => {
                const tool = (await document.modelContext.getTools()).find(t => t.name === 'compare_channels');
                return JSON.parse(await document.modelContext.executeTool(tool, args));
            }""",
            json.dumps({"region": "West"}) if string_arguments else {"region": "West"},
        )
        assert result == {
            "region": "West",
            "currency": "USD",
            "Online": 600,
            "Retail": 300,
            "online_minus_retail": 300,
        }
    finally:
        browser.close()


def test_normal_browser_still_works(browser: Browser, webmcp_app: ShinyAppProc):
    context = browser.new_context()
    try:
        context.add_init_script(
            "Object.defineProperty(document, 'modelContext', {value: undefined});"
        )
        page = context.new_page()
        page.goto(webmcp_app.url)
        page.locator("#region").select_option("South")
        page.locator("#channel").select_option("Online")
        expect(page.locator("#headline")).to_have_text("1 orders · $150 USD")
    finally:
        context.close()
