from __future__ import annotations

from playwright.sync_api import Page, expect

from shiny._inspect import format_reactlog_html, generate_reactlog


def test_connections_only_appear_for_hover_and_timeline_context(page: Page) -> None:
    code = """from shiny.express import input, render, ui
from shiny import reactive

ui.input_numeric("x", "X", 1)
ui.input_numeric("y", "Y", 2)

@reactive.calc
def doubled():
    return input.x() * 2

@render.text
def result():
    return str(doubled())

@render.text
def other():
    return str(input.y())
"""
    reactlog = generate_reactlog(code, inputs={"x": 1, "y": 2})
    dependency_step = next(
        index
        for index, event in enumerate(reactlog["events"])
        if event["event"] == "dependsOn"
        and event["node_id"] == "doubled"
        and "'x'" in event["details"]
    )
    page.set_content(
        format_reactlog_html(reactlog, source_code=code),
        wait_until="domcontentloaded",
    )

    edges = page.locator(".graph-edge")
    assert edges.count() == 3
    assert edges.evaluate_all(
        "elements => elements.map(edge => edge.style.opacity)"
    ) == [
        "0",
        "0",
        "0",
    ]

    page.locator('.graph-node[data-id="doubled"]').hover()
    page.wait_for_function(
        "document.querySelectorAll('.graph-edge[style*=\"opacity: 1\"]').length === 2"
    )

    page.locator(".toolbar").hover()
    page.wait_for_function(
        "Array.from(document.querySelectorAll('.graph-edge')).every(edge => edge.style.opacity === '0')"
    )

    page.locator(".event-item").nth(dependency_step).click()
    page.wait_for_function(
        "Array.from(document.querySelectorAll('.graph-edge')).reduce((count, edge) => count + (edge.style.opacity !== '0' ? 1 : 0), 0) === 2"
    )
    assert (
        edges.evaluate_all(
            "elements => elements.reduce((count, edge) => count + (edge.dataset.active === 'true' ? 1 : 0), 0)"
        )
        == 1
    )


def test_app_code_tab_reveals_embedded_source(page: Page) -> None:
    code = """from shiny.express import input, render, ui
ui.input_text("name", "Name")
@render.text
def greeting():
    return f"Hello, {input.name()}"
"""
    reactlog = generate_reactlog(code, inputs={"name": "Ada"})
    input_step = next(
        index
        for index, event in enumerate(reactlog["events"])
        if event["event"] == "define" and event["node_id"] == "name"
    )
    output_step = next(
        index
        for index, event in enumerate(reactlog["events"])
        if event["event"] == "define" and event["node_id"] == "greeting"
    )
    page.set_content(
        format_reactlog_html(reactlog, source_code=code),
        wait_until="domcontentloaded",
    )

    source_panel = page.get_by_role("tabpanel", name="App code")
    expect(source_panel).to_be_hidden()

    page.get_by_role("tab", name="App code").click()

    expect(source_panel).to_be_visible()
    expect(source_panel).to_have_text(code)
    assert source_panel.locator(".syntax-keyword").all_text_contents() == [
        "from",
        "import",
        "def",
        "return",
    ]
    assert source_panel.locator(".syntax-string").count() >= 2
    expect(page.get_by_role("tabpanel", name="Timeline")).to_be_hidden()

    source_highlight = page.locator("#source-line-highlight")
    expect(source_highlight).to_be_hidden()

    page.locator("#scrubber-range").fill(str(input_step))
    expect(source_highlight).to_be_visible()
    expect(source_highlight).to_have_attribute("data-line", "2")

    page.locator("#scrubber-range").fill(str(output_step))
    expect(source_highlight).to_have_attribute("data-line", "4")
