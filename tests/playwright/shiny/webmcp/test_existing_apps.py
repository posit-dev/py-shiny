from typing import Iterator

import pytest
from playwright.sync_api import Browser, expect

from shiny.run import ShinyAppProc


@pytest.fixture(scope="module", autouse=True)
def enable_webmcp() -> Iterator[None]:
    with pytest.MonkeyPatch.context() as patch:
        patch.setenv("SHINY_WEBMCP", "1")
        yield


@pytest.mark.parametrize(
    "local_app",
    [
        "../../../../shiny/api-examples/input_numeric/app-core.py",
        "../../../../shiny/api-examples/input_numeric/app-express.py",
    ],
    indirect=True,
)
def test_existing_apps_without_edits(browser: Browser, local_app: ShinyAppProc):
    context = browser.new_context()
    try:
        context.add_init_script("""window.tools = {};
            Object.defineProperty(document, 'modelContext', {value: {
                async registerTool(tool, {signal} = {}) {
                    window.tools[tool.name] = tool;
                    signal?.addEventListener('abort', () => delete window.tools[tool.name]);
                }
            }});""")
        page = context.new_page()
        page.goto(local_app.url)
        page.wait_for_function("!!window.tools.shiny_set_inputs")
        result = page.evaluate(
            """async () => JSON.parse(await tools.shiny_set_inputs.execute({values: {obs: 42}}))"""
        )
        expect(page.locator("#obs")).to_have_value("42")
        assert result["outputs"]["value"]["value"] == "42"
    finally:
        context.close()


@pytest.mark.parametrize("local_app", ["app-express.py"], indirect=True)
def test_custom_tools_in_express(browser: Browser, local_app: ShinyAppProc):
    context = browser.new_context()
    try:
        context.add_init_script("""window.tools = {};
            Object.defineProperty(document, 'modelContext', {value: {
                async registerTool(tool, {signal} = {}) {
                    window.tools[tool.name] = tool;
                    signal?.addEventListener('abort', () => delete window.tools[tool.name]);
                }
            }});""")
        page = context.new_page()
        page.goto(local_app.url)
        page.wait_for_function("!!tools.double")
        result = page.evaluate("async () => JSON.parse(await tools.double.execute({}))")
        assert result == {"doubled": 4}
    finally:
        context.close()
