from typing import Any, Iterator

import pytest
from playwright.sync_api import Browser, Page, expect

from shiny.run import ShinyAppProc

CAPTURE = """
window.tools = {};
Object.defineProperty(document, 'modelContext', {value: {
  async registerTool(tool, {signal} = {}) {
    if (window.tools[tool.name]) throw new Error('Duplicate tool: ' + tool.name);
    window.tools[tool.name] = tool;
    signal?.addEventListener('abort', () => { delete window.tools[tool.name]; });
  }
}});
"""


@pytest.fixture
def agent_page(browser: Browser, local_app: ShinyAppProc) -> Iterator[Page]:
    context = browser.new_context()
    context.add_init_script(CAPTURE)
    page = context.new_page()
    page.goto(local_app.url)
    page.wait_for_function("!!window.tools.shiny_set_inputs", timeout=5000)
    yield page
    context.close()


def call(page: Page, name: str, args: object) -> dict[str, Any]:
    return page.evaluate(
        "async ([name,args]) => JSON.parse(await window.tools[name].execute(args))",
        [name, args],
    )


def test_automatic_controls_and_custom_tools(agent_page: Page):
    page = agent_page
    state = call(page, "shiny_describe_app", {})
    inputs_by_id = {item["id"]: item for item in state["inputs"]}
    ids = list(inputs_by_id.keys())
    assert "password" not in ids
    assert "private" not in ids
    assert "left-choice" in ids
    assert inputs_by_id["enabled"]["label"] == "Enabled"
    assert inputs_by_id["multi_label"]["label"] == "First Second"
    assert [a["id"] for a in state["actions"]] == ["run"]
    result = page.evaluate(
        "async () => { try { await tools.shiny_invoke_action.execute({id: 'disabled_link'}); } catch(e) { return e.message; } }"
    )
    assert "Action is unavailable" in result
    state = call(
        page,
        "shiny_set_inputs",
        {
            "values": {
                "n": 7,
                "name": "Grace",
                "enabled": False,
                "colors": ["blue"],
                "mode": "two",
                "range": [3, 9],
                "left-choice": "b",
            }
        },
    )
    assert state["outputs"]["result"]["value"].startswith(
        "Grace:7:False:blue:two:(3, 9):0"
    )
    expect(page.locator("#n")).to_have_value("7")
    assert call(page, "left-selection", {}) == {"choice": "b"}
    assert call(page, "right-selection", {}) == {"choice": "a"}
    assert call(page, "multiply", {"factor": 3}) == {"product": 21}
    state = call(page, "shiny_invoke_action", {"id": "run"})
    assert state["outputs"]["result"]["value"].endswith(":1")
    page.locator("#name").fill("Lin")
    page.locator("#name").press("Tab")
    expect(page.locator("#result")).to_contain_text("Lin:")
    assert call(page, "shiny_read_outputs", {})["result"]["value"].startswith("Lin:")


def test_schema_updates_and_validation_before_mutation(agent_page: Page):
    page = agent_page
    call(page, "shiny_set_inputs", {"values": {"n": 7}})
    page.wait_for_function(
        "'extra' in window.tools.shiny_set_inputs.inputSchema.properties.values.properties"
    )
    call(page, "shiny_set_inputs", {"values": {"extra": "y"}})
    call(page, "shiny_set_inputs", {"values": {"n": 2}})
    page.wait_for_function(
        "!('extra' in window.tools.shiny_set_inputs.inputSchema.properties.values.properties)"
    )
    for values in [
        {"name": "Wrong", "n": 11},
        {"left-choice": "missing"},
        {"password": "exposed"},
        {"extra": "x"},
        {"n": True},
        {"range": [9, 2]},
    ]:
        result = page.evaluate(
            "async values => {try { await window.tools.shiny_set_inputs.execute({values}); } catch(e) {return e.message;}}",
            values,
        )
        assert result
        expect(page.locator("#name")).to_have_value("Ada")
        expect(page.locator("#n")).to_have_value("2")
    call(page, "shiny_set_inputs", {"values": {"n": 10}})
    page.wait_for_function(
        "window.tools.shiny_set_inputs.inputSchema.properties.values.properties['left-choice'].enum.includes('d')"
    )
    assert call(page, "left-selection", {}) == {"choice": "d"}


def test_custom_tool_flush_and_module_teardown(agent_page: Page):
    page = agent_page
    assert call(page, "set_factor", {"factor": 9}) == {"factor": 9}
    # No auto-wait: the tool's RPC response follows its rendered output.
    assert page.locator("#factor").inner_text() == "9"
    page.evaluate("() => {window.oldSelection = tools['left-selection'].execute;}")
    call(page, "shiny_set_inputs", {"values": {"remove_left": True}})
    page.wait_for_function("!tools['left-selection']")
    assert page.evaluate(
        "async () => {try {await oldSelection({});} catch(e) {return e.message;}}"
    )
    assert call(page, "right-selection", {}) == {"choice": "a"}


def test_overlap_cancellation_and_disconnect(agent_page: Page):
    page = agent_page
    result = page.evaluate("""async () => {
        const first = tools.shiny_set_inputs.execute({values: {n: 4}});
        const second = tools.shiny_read_outputs.execute({}).catch(e => e.message);
        return [JSON.parse(await first), await second];
    }""")
    assert "already running" in result[1]
    assert result[0]["outputs"]["result"]["value"].startswith("Ada:4:")
    assert page.evaluate("""async () => {
        const controller = new AbortController();
        const pending = tools.shiny_read_outputs.execute({}, {signal: controller.signal}).catch(e => e.message);
        controller.abort();
        return pending;
    }""").startswith("Tool cancelled")
    assert call(page, "multiply", {"factor": 2}) == {"product": 8}
    page.evaluate(
        "window.oldRead = tools.shiny_read_outputs.execute; Shiny.shinyapp.$socket.close();"
    )
    page.wait_for_function("Object.keys(tools).length === 0")
    assert "disconnected" in page.evaluate(
        "async () => {try {await oldRead({});} catch(e) {return e.message;}}"
    )


@pytest.mark.parametrize("stop", ["cancel", "timeout"])
def test_slow_python_work_continues_after_browser_stops(agent_page: Page, stop: str):
    result = agent_page.evaluate(
        """async stop => {
            const events = [];
            let started;
            const onStarted = new Promise(resolve => { started = resolve; });
            Shiny.addCustomMessageHandler('slow-operation', ({state}) => {
                events.push(state);
                if (state === 'started') started();
            });
            const controller = new AbortController();
            const originalSetTimeout = window.setTimeout;
            let expire;
            // Trigger the actual 30-second timeout callback without waiting 30s.
            window.setTimeout = (callback, delay, ...args) => {
                if (delay === 30000) {
                    expire = callback;
                    return originalSetTimeout(callback, delay, ...args);
                }
                return originalSetTimeout(callback, delay, ...args);
            };
            try {
                const slow = tools.slow_operation.execute({}, {signal: controller.signal})
                    .catch(e => e.message);
                await onStarted;
                const blocked = await tools.shiny_describe_app.execute({})
                    .catch(e => e.message);
                if (stop === 'cancel') controller.abort();
                else expire();
                window.setTimeout = originalSetTimeout;
                const stopped = await slow;
                // A browser-only call is allowed while Python is still working.
                const state = JSON.parse(await tools.shiny_describe_app.execute({}));
                events.push('described');
                // This RPC queues behind the slow tool and sees its side effect.
                const factor = JSON.parse(await tools.read_factor.execute({}));
                events.push('next-rpc');
                return {blocked, stopped, state, factor, events};
            } finally {
                window.setTimeout = originalSetTimeout;
            }
        }""",
        stop,
    )
    assert "already running" in result["blocked"]
    if stop == "cancel":
        assert result["stopped"].startswith("Tool cancelled")
    else:
        assert result["stopped"].startswith("Shiny tool timed out after 30 seconds")
    assert result["events"] == ["started", "described", "finished", "next-rpc"]
    assert result["state"]["outputs"]["factor"]["value"] == "1"
    assert result["factor"] == {"factor": 42}
    expect(agent_page.locator("#factor")).to_have_text("42")


def test_dates_and_disabled_inputs(agent_page: Page):
    page = agent_page
    state = call(
        page,
        "shiny_set_inputs",
        {"values": {"day": "2026-10-01", "period": ["2026-10-02", "2026-10-04"]}},
    )
    assert (
        state["outputs"]["dates"]["value"]
        == "2026-10-01:(datetime.date(2026, 10, 2), datetime.date(2026, 10, 4))"
    )
    for values in [{"day": "2026-02-30"}, {"day": "2027-01-01"}, {"disabled": 2}]:
        error = page.evaluate(
            "async values => {try {await tools.shiny_set_inputs.execute({values});} catch(e) {return e.message;}}",
            values,
        )
        assert error


def test_disabled_choices_cannot_be_changed(agent_page: Page):
    page = agent_page
    call(page, "shiny_set_inputs", {"values": {"n": 7}})
    page.wait_for_selector("#extra")
    page.evaluate("document.querySelector('#extra option[value=y]').disabled = true")
    # Disabling one choice must not disable the whole select.
    call(page, "shiny_set_inputs", {"values": {"extra": "x"}})
    assert page.evaluate("""async () => {
        try { await tools.shiny_set_inputs.execute({values: {extra: 'y'}}); }
        catch(e) { return e.message; }
    }""")
    page.evaluate("document.querySelector('#colors input[value=red]').disabled = true")
    # A group's setter replaces the whole selection, so a disabled checked item
    # must not be cleared as a side effect of setting other choices.
    assert page.evaluate("""async () => {
        try { await tools.shiny_set_inputs.execute({values: {colors: ['blue']}}); }
        catch(e) { return e.message; }
    }""")
    expect(page.locator('#colors input[value="red"]')).to_be_checked()
