import re
from collections.abc import Generator
from typing import Any

import pytest
from playwright.sync_api import Error, Page, expect

from shiny import reactive, render
from shiny.reactive._reactlog._viewer import format_reactlog_html, load_reactlog_json
from tests.pytest._reactlog_fixtures import record_export


@pytest.fixture(autouse=True)
def no_report_errors(page: Page) -> Generator[None, None, None]:
    errors: list[str] = []

    def on_error(error: Error) -> None:
        errors.append(str(error))

    page.on("pageerror", on_error)
    yield
    page.remove_listener("pageerror", on_error)
    assert errors == []


CODE = """from shiny import reactive, render
@reactive.calc
def doubled() -> int:
    return input.x() * 2
@render.text
def result() -> str:
    return doubled()
@render.text
def other() -> str:
    return input.y()
"""


def report(steps: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    def server(input: Any, output: Any, session: Any) -> None:
        @reactive.calc
        def doubled() -> int:
            return input.x() * 2

        @output
        @render.text
        def result() -> str:
            return str(doubled())

        @output
        @render.text
        def other() -> str:
            return str(input.y())

    data = load_reactlog_json(
        record_export(
            server,
            steps
            or [
                {
                    "x": 1,
                    "y": 2,
                    ".clientdata_output_result_hidden": False,
                    ".clientdata_output_other_hidden": False,
                },
                {"x": 2},
                {"y": 3},
            ],
        )
    )
    labels = {
        "input.x": "input:x",
        "input.y": "input:y",
        "reactive.calc doubled": "calc:doubled",
        "output result": "output:result",
        "output other": "output:other",
    }
    data["nodes"] = [n for n in data["nodes"] if n["label"] in labels]
    ids = {n["id"]: labels[n["label"]] for n in data["nodes"]}
    for node in data["nodes"]:
        node["id"] = ids[node["id"]]
        if node["id"] in ("calc:doubled", "output:result"):
            node["module"] = "analysis"
    for edge in data["edges"]:
        for key in ("from", "to"):
            edge[key] = ids.get(edge[key], edge[key])
    for event in data["events"]:
        for key in ("id", "node_id", "edge_from", "edge_to"):
            if key in event:
                event[key] = ids.get(event[key], event[key])
    return data


def test_overview_drills_into_module_and_returns_without_losing_scope(page: Page):
    page.set_content(format_reactlog_html(report(), CODE))
    page.locator("#btn-mode-overview").click()
    expect(page.locator("#module-overview-panel")).to_be_visible()
    expect(page.locator("#sidebar")).to_be_hidden()
    expect(page.get_by_role("button", name="Back to overview")).to_be_hidden()
    expect(page.locator(".graph-topbar")).to_be_hidden()
    expect(page.locator("#overview-activity button").first).to_contain_text(
        "5 active nodes"
    )
    expect(page.locator("#overview-connections")).to_contain_text(
        "App (Root) → analysis"
    )
    expect(page.locator("#overview-activity button")).to_have_count(3)
    page.locator('.module-card[data-module="analysis"]').get_by_role(
        "button", name="Zoom into Module"
    ).click()
    expect(page.locator(".graph-node")).to_have_count(2)
    expect(page.locator("#filter-node-count")).to_have_text("2 of 5 nodes")
    page.locator('.graph-node[data-id="calc:doubled"]').click()
    expect(page.locator('.graph-node[data-id="calc:doubled"]')).to_have_class(
        re.compile(r"is-selected")
    )
    page.locator("#btn-toggle-inspector").click()
    expect(page.locator("#sidebar")).to_be_visible()
    expect(page.locator("#why-story")).to_contain_text("input.x")
    page.get_by_role("button", name="Zoom in", exact=True).click()
    transform = page.locator("#viewport-g").get_attribute("transform")
    assert transform is not None
    page.get_by_role("button", name="Back to overview").click()
    expect(page.locator("#module-overview-panel")).to_be_visible()
    expect(page.locator("#sidebar")).to_be_hidden()
    expect(page.locator("#module-filter-select")).to_have_value("analysis")
    page.locator('.module-card[data-module="analysis"]').get_by_role(
        "button", name="Zoom into Module"
    ).click()
    expect(page.locator("#viewport-g")).to_have_attribute("transform", transform)
    page.get_by_role("button", name="Back to overview").click()
    page.get_by_role("button", name="Remove module filter").click()
    expect(page.locator("#filter-node-count")).to_have_text("5 of 5 nodes")


def test_search_selection_opens_details_and_filters_events(page: Page):
    page.set_content(format_reactlog_html(report(), CODE))
    page.locator("#search-input").fill("id:calc:doubled")
    page.locator("#search-results button").click()
    expect(page.locator("#module-overview-panel")).to_be_hidden()
    page.locator("#btn-toggle-inspector").click()
    expect(page.locator("#sidebar")).to_be_visible()
    expect(page.locator(".graph-node")).to_have_count(3)
    expect(page.locator("#filter-node-count")).to_have_text("3 of 5 nodes")
    assert page.locator("#event-list .event-name").all_text_contents()
    assert all(
        "other" not in name and "input.y" not in name
        for name in page.locator("#event-list .event-name").all_text_contents()
    )
    page.get_by_role("button", name="Clear all filters").click()
    expect(page.locator(".graph-node")).to_have_count(5)
    expect(page.locator("#search-input")).to_have_value("")


def test_activity_interval_filters_graph_and_preserves_selected_action(page: Page):
    page.set_content(format_reactlog_html(report(), CODE))
    page.locator("#btn-mode-overview").click()
    page.locator("#overview-activity-section > summary").click()
    page.get_by_label("Activity interval start").select_option("1")
    page.get_by_label("Activity interval end").select_option("1")
    expect(page.locator("#filter-node-count")).to_have_text("3 of 5 nodes")
    page.locator("#overview-activity button").nth(1).click()
    expect(page.locator("#module-overview-panel")).to_be_hidden()
    expect(page.locator(".graph-node")).to_have_count(3)
    step = page.locator("#scrubber-range").input_value()
    page.get_by_role("button", name="Back to overview").click()
    expect(page.locator("#scrubber-range")).to_have_value(step)
    page.get_by_role("button", name="Clear all filters").click()
    expect(page.locator("#filter-node-count")).to_have_text("5 of 5 nodes")
    expect(page.locator("#scrubber-range")).to_have_value(step)


def test_phase_stage_and_root_filters_share_scope_and_clear_together(page: Page):
    page.set_content(format_reactlog_html(report(), CODE))
    page.locator("#module-filter-select").select_option("__root__")
    expect(page.locator("#filter-node-count")).to_have_text("3 of 5 nodes")
    page.locator("#phase-filter-select").select_option("interaction")
    page.locator("#btn-mode-full").click()
    expect(page.locator("#filter-node-count")).to_have_text("3 of 5 nodes")
    page.get_by_role("button", name="Clear all filters").click()
    expect(page.locator("#module-filter-select")).to_have_value("")
    expect(page.locator("#phase-filter-select")).to_have_value("all")
    expect(page.locator("#active-filters button")).to_have_count(0)
    page.locator("#btn-mode-full").click()
    expect(page.locator("#filter-node-count")).to_have_text("5 of 5 nodes")


def test_empty_recording_can_open_overview_and_graph(page: Page):
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.set_content(format_reactlog_html({"nodes": [], "edges": [], "events": []}, ""))
    expect(page.locator("#module-overview-panel")).to_be_hidden()
    expect(page.locator("#filter-node-count")).to_have_text("0 of 0 nodes")
    page.locator("#btn-mode-full").click()
    expect(page.locator(".graph-node")).to_have_count(0)
    assert errors == []


def test_clear_all_restores_entire_graph_from_active_flush(page: Page):
    page.set_content(format_reactlog_html(report(), CODE))
    page.locator("#btn-mode-overview").click()
    page.locator("#overview-activity-section > summary").click()
    page.locator("#overview-activity button").nth(1).click()
    expect(page.locator(".graph-node")).to_have_count(3)
    page.get_by_role("button", name="Clear all filters").click()
    expect(page.locator(".graph-node")).to_have_count(5)


def test_large_overview_prioritizes_modules_and_reveals_activity_on_demand(page: Page):
    data = report(
        [
            {
                "x": 0,
                "y": 2,
                ".clientdata_output_result_hidden": False,
                ".clientdata_output_other_hidden": False,
            },
            *[{"x": i} for i in range(1, 111)],
        ]
    )
    for i in range(17):
        data["nodes"].append(
            {
                "id": f"calc:module-{i}",
                "label": f"module-{i}",
                "module": f"section-module-{i}",
                "role": "conductor",
                "type": "calc",
            }
        )
    page.set_content(format_reactlog_html(data, CODE))
    page.locator("#btn-mode-overview").click()
    expect(page.locator(".module-card")).to_have_count(19)
    expect(page.locator(".module-card").first).to_be_visible()
    expect(page.locator("#overview-activity")).to_be_hidden()
    expect(page.locator("#timeline-sidebar")).to_be_hidden()
    expect(page.locator("#trace-timeline-bar")).to_be_hidden()
    expect(page.locator(".module-card .module-active-nodes-list")).to_have_count(0)
    expect(page.locator(".module-execution-details").first).not_to_have_attribute(
        "open", ""
    )
    page.locator("#overview-activity-section > summary").click()
    expect(page.locator("#overview-activity")).to_be_visible()
    page.locator("#overview-activity button").nth(1).click()
    expect(page.locator("#reactlog-svg")).to_be_visible()
    expect(page.locator("#timeline-sidebar")).to_have_count(0)


def test_compact_layout_opens_graph_and_only_shows_current_flush(page: Page):
    page.set_content(format_reactlog_html(report(), CODE))
    expect(page.locator("#module-overview-panel")).to_be_hidden()
    expect(page.locator("#reactlog-svg")).to_be_visible()
    expect(page.locator("#sidebar")).to_be_hidden()
    expect(page.locator("#sidebar-rail")).to_have_css("width", "40px")
    expect(page.locator("#btn-toggle-inspector")).to_have_text("")
    expect(
        page.locator(
            "#timeline-tab, #actions-tab, #btn-summary-toggle, #flush-pipeline-bar, #timeline-sidebar, #flush-select"
        )
    ).to_have_count(0)
    expect(page.locator("#active-flush-label")).to_contain_text("Flush 1 / 3")
    page.locator("#btn-next-flush").click()
    expect(page.locator("#active-flush-label")).to_contain_text("Flush 2 / 3 · x")
    expect(page.locator(".graph-node")).to_have_count(3)
    page.locator("#btn-next-flush").click()
    expect(page.locator("#active-flush-label")).to_contain_text("Flush 3 / 3 · y")
    expect(page.locator(".graph-node")).to_have_count(2)
    page.locator("#btn-prev-flush").click()
    expect(page.locator("#active-flush-label")).to_contain_text("Flush 2 / 3 · x")


def test_progress_bar_supports_pointer_keyboard_and_flush_markers(page: Page):
    data = report()
    page.set_content(format_reactlog_html(data, CODE))
    expect(page.locator(".timeline-marker.is-flush")).to_have_count(3)
    slider = page.get_by_role("slider", name="Timeline step scrubber")
    slider.focus()
    page.keyboard.press("ArrowRight")
    expect(slider).to_have_value("1")
    box = slider.bounding_box()
    assert box is not None
    page.mouse.click(box["x"] + box["width"] - 8, box["y"] + box["height"] / 2)
    expect(slider).to_have_value(str(len(data["events"]) - 1))
    expect(page.locator("#active-flush-label")).to_contain_text("Flush 3 / 3")
    expect(slider).to_have_attribute("aria-valuetext", re.compile("Flush 3 / 3"))
    page.keyboard.press("Home")
    expect(slider).to_have_value("0")


def test_recording_floats_above_timeline_and_rail_stays_40px(page: Page):
    page.set_content(format_reactlog_html(report(), CODE, video_path="demo.webm"))
    player = page.get_by_role("region", name="Recording")
    expect(player).to_be_visible()
    for width in [1440, 800, 390]:
        page.set_viewport_size({"width": width, "height": 900})
        rail = page.locator("#sidebar-rail").bounding_box()
        video = player.bounding_box()
        timeline = page.locator("#trace-timeline-bar").bounding_box()
        graph = page.locator("#graph-container").bounding_box()
        assert rail and video and timeline and graph
        assert rail["width"] == 40
        assert video["width"] <= 440
        assert video["x"] + video["width"] < rail["x"]
        assert video["y"] + video["height"] < timeline["y"]
        assert graph["width"] == width - 40
    page.get_by_role("button", name="Hide recording", exact=True).click()
    expect(player).to_be_hidden()
    page.get_by_role("button", name="Toggle recording").click()
    expect(player).to_be_visible()


def test_details_overlay_does_not_resize_graph(page: Page):
    page.set_content(format_reactlog_html(report(), CODE))
    graph = page.locator("#graph-container")
    before = graph.bounding_box()
    page.get_by_role("button", name="Node details", exact=True).click()
    expect(page.locator("#sidebar")).to_be_visible()
    assert graph.bounding_box() == before
    page.get_by_role("tab", name="App code").click()
    expect(page.locator("#source-panel")).to_be_visible()
    expect(page.locator("#timeline-panel")).to_be_hidden()
    assert graph.bounding_box() == before


def test_node_click_highlights_without_opening_sidebar(page: Page):
    page.set_content(format_reactlog_html(report(), CODE))
    node = page.locator('.graph-node[data-id="calc:doubled"]')
    node.click()
    expect(node).to_have_class(re.compile(r"is-selected"))
    expect(page.locator("#sidebar")).to_be_hidden()

    node.dblclick()
    expect(page.locator("#search-input")).to_have_value(re.compile(r"doubled"))
    expect(page.locator("#secondary-timeline-bar")).to_be_visible()


def test_secondary_timeline_flush_milestones_and_seeking(page: Page):
    page.set_content(format_reactlog_html(report(), CODE))
    badge = page.locator("#flush-counter-badge")
    badge.click()
    sec_bar = page.locator("#secondary-timeline-bar")
    expect(sec_bar).to_be_visible()

    pills = page.locator(".secondary-stage-pill")
    expect(pills.first).to_be_visible()
    count = pills.count()
    assert count >= 2

    last_pill = pills.last
    last_step = last_pill.get_attribute("data-step")
    last_pill.click()
    expect(page.locator("#scrubber-range")).to_have_value(str(last_step))

    page.locator("#btn-close-secondary-timeline").click()
    expect(sec_bar).to_be_hidden()


def test_filtered_module_box_shows_fractional_node_count(page: Page):
    page.set_content(format_reactlog_html(report(), CODE))
    expect(page.locator(".app-box text")).to_have_text("App · 3 nodes")
    expect(page.locator('.module-box[data-module="analysis"] text')).to_have_text(
        "analysis · 2 nodes · double-click to collapse"
    )

    page.locator("#search-input").fill("other")
    expect(page.locator(".app-box text")).to_have_text("App · 1/3 nodes")
