from __future__ import annotations

from pathlib import Path

from playwright.sync_api import Page

from shiny._inspect import format_reactlog_html, generate_reactlog


def test_connections_only_appear_for_hover_and_timeline_context(
    page: Page, tmp_path: Path
) -> None:
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
    html_file = tmp_path / "reactlog.html"
    html_file.write_text(format_reactlog_html(reactlog), encoding="utf-8")

    page.goto(html_file.as_uri(), wait_until="domcontentloaded")

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
        "Array.from(document.querySelectorAll('.graph-edge')).filter(edge => edge.style.opacity !== '0').length === 2"
    )
    assert (
        edges.evaluate_all(
            "elements => elements.filter(edge => edge.dataset.active === 'true').length"
        )
        == 1
    )
