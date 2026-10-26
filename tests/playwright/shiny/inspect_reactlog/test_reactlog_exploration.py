import re
from collections.abc import Generator

import pytest
from playwright.sync_api import Page, expect

from shiny._inspect import format_reactlog_html, generate_reactlog


@pytest.fixture(autouse=True)
def no_report_errors(page: Page) -> Generator[None, None, None]:
    errors = []

    def on_error(error):
        errors.append(str(error))

    page.on("pageerror", on_error)
    yield
    page.remove_listener("pageerror", on_error)
    assert errors == []


CODE = """from shiny import reactive, render
@reactive.calc
def doubled():
    return input.x() * 2
@render.text
def result():
    return doubled()
@render.text
def other():
    return input.y()
"""


def report():
    data = generate_reactlog(
        CODE,
        recorded_actions=[
            {"type": "input", "name": "x", "value": 2, "timestamp": 1000},
            {"type": "input", "name": "y", "value": 3, "timestamp": 2000},
        ],
    )
    for node in data["nodes"]:
        if node["id"] in ("calc:doubled", "output:result"):
            node["module"] = "analysis"
    return data


def test_overview_drills_into_module_and_returns_without_losing_scope(page: Page):
    page.set_content(format_reactlog_html(report(), CODE))
    page.locator("#btn-mode-overview").click()
    expect(page.locator("#module-overview-panel")).to_be_visible()
    expect(page.locator("#overview-activity-count")).to_have_text("(3 updates)")
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
    expect(page.locator("#sidebar")).to_be_visible()
    expect(page.locator("#why-story")).to_contain_text("input.x")
    page.get_by_role("button", name="Zoom in", exact=True).click()
    transform = page.locator("#viewport-g").get_attribute("transform")
    assert transform is not None
    page.get_by_role("button", name="Back to overview").click()
    expect(page.locator("#module-overview-panel")).to_be_visible()
    expect(page.locator("#sidebar")).to_be_hidden()
    expect(page.get_by_role("button", name="Remove module filter")).to_be_visible()
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


def test_root_module_search_and_stage_filters_clear_together(page: Page):
    page.set_content(format_reactlog_html(report(), CODE))
    page.locator("#search-input").fill("module:__root__")
    expect(page.locator("#filter-node-count")).to_have_text("3 of 5 nodes")
    page.locator("#btn-mode-full").click()
    expect(page.locator("#filter-node-count")).to_have_text("3 of 5 nodes")
    page.get_by_role("button", name="Clear all filters").click()
    expect(page.locator("#search-input")).to_have_value("")
    expect(page.locator("#active-filters button")).to_have_count(0)
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
    data = generate_reactlog(
        CODE,
        recorded_actions=[
            {"type": "input", "name": "x", "value": i, "timestamp": i * 1000}
            for i in range(1, 111)
        ],
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
    expect(page.locator(".module-card")).to_have_count(18)
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
    expect(page.locator("#active-flush-label")).to_contain_text("Update 1 of 3")
    page.locator("#btn-next-action").click()
    expect(page.locator("#active-flush-label")).to_contain_text("Update 2 of 3 · x")
    expect(page.locator(".graph-node")).to_have_count(3)
    page.locator("#btn-next-action").click()
    expect(page.locator("#active-flush-label")).to_contain_text("Update 3 of 3 · y")
    expect(page.locator(".graph-node")).to_have_count(2)
    page.locator("#btn-prev-action").click()
    expect(page.locator("#active-flush-label")).to_contain_text("Update 2 of 3 · x")


def test_progress_bar_supports_pointer_keyboard_and_idle_markers(page: Page):
    data = report()
    page.set_content(format_reactlog_html(data, CODE))
    expect(page.locator(".timeline-marker.is-idle")).to_have_count(1)
    slider = page.get_by_role("slider", name="Timeline step scrubber")
    slider.focus()
    page.keyboard.press("ArrowRight")
    expect(slider).to_have_value("1")
    box = slider.bounding_box()
    assert box is not None
    page.mouse.click(box["x"] + box["width"] - 8, box["y"] + box["height"] / 2)
    expect(slider).to_have_value(str(len(data["events"]) - 1))
    expect(page.locator("#active-flush-label")).to_contain_text("Update 3 of 3")
    expect(slider).to_have_attribute("aria-valuetext", re.compile("Update 3 of 3"))
    page.keyboard.press("Home")
    expect(slider).to_have_value("0")


def test_recording_floats_below_timeline_and_rail_stays_40px(page: Page):
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
        assert video["width"] <= 240
        assert video["x"] + video["width"] < rail["x"]
        assert timeline["y"] + timeline["height"] <= video["y"]
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


@pytest.mark.parametrize("query", ["module:analysis", "analysis", "MODULE:ANALYSIS"])
def test_module_search_filters_nodes_and_clears(page: Page, query: str):
    page.set_content(format_reactlog_html(report(), CODE))
    page.locator("#btn-mode-full").click()
    page.locator("#search-input").fill(query)
    expect(page.locator(".graph-node")).to_have_count(2)
    expect(page.locator("#search-results button")).to_have_count(2)
    page.get_by_role("button", name="Clear all filters").click()
    expect(page.locator(".graph-node")).to_have_count(5)
    expect(page.locator("#module-filter-select, #phase-filter-select")).to_have_count(0)


def test_timeline_and_controls_are_above_graph(page: Page):
    page.set_content(format_reactlog_html(report(), CODE))
    graph = page.locator("#graph-container").bounding_box()
    for selector in ("#trace-timeline-bar", "#bottom-timeline-bar"):
        timeline = page.locator(selector).bounding_box()
        assert graph and timeline
        assert timeline["y"] + timeline["height"] <= graph["y"]


def test_replay_uses_r_states_dependencies_and_idle_navigation(page: Page):
    data = report()
    actions = [
        "enter",
        "invalidateStart",
        "invalidateEnd",
        "exit",
        "freeze",
        "thaw",
        "idle",
        "dependsOnRemove",
        "dependsOn",
        "queueEmpty",
    ]
    data["events"] = [
        {
            "action": action,
            "event": action,
            "node_id": "calc:doubled" if action not in ("idle", "queueEmpty") else None,
            "edge_from": "input:x" if action.startswith("dependsOn") else None,
            "edge_to": "calc:doubled" if action.startswith("dependsOn") else None,
            "time_sec": i,
            "phase": "interaction",
        }
        for i, action in enumerate(actions)
    ]
    page.set_content(format_reactlog_html(data, CODE))
    page.locator("#btn-mode-full").click()
    node = page.locator('.graph-node[data-id="calc:doubled"]')
    for step, (state, color) in enumerate(
        [
            ("calculating", "#fcbf49"),
            ("invalidating", "#969696"),
            ("invalidated", "#d9d9d9"),
            ("ready", "#a3c586"),
            ("frozen", "#2171b5"),
            ("ready", "#a3c586"),
        ]
    ):
        page.locator("#scrubber-range").fill(str(step))
        expect(node).to_have_attribute("data-state", state)
        expect(node.locator(".node-card")).to_have_attribute("fill", color)
    page.get_by_role("button", name="Next idle", exact=True).click()
    expect(page.locator("#scrubber-range")).to_have_value("6")
    expect(page.locator("#trace-status-line")).to_have_text("Idle")
    page.locator("#scrubber-range").fill("7")
    edge = page.locator('.graph-edge[data-from="input:x"][data-to="calc:doubled"]')
    expect(edge).to_have_class(re.compile("is-inactive"))
    expect(edge).to_have_css("stroke-dasharray", "1px, 4px")
    node.hover()
    page.locator(".toolbar").hover()
    expect(edge).to_have_css("stroke", "rgb(129, 129, 129)")
    page.locator("#scrubber-range").fill("8")
    expect(edge).not_to_have_class(re.compile("is-inactive"))
    page.get_by_role("button", name="Next idle", exact=True).click()
    expect(page.locator("#scrubber-range")).to_have_value("9")
    page.get_by_role("button", name="Previous idle", exact=True).click()
    expect(page.locator("#scrubber-range")).to_have_value("6")

    page.locator("#scrubber-range").fill("0")
    expect(node).to_have_attribute("data-state", "calculating")
    expect(node.locator(".node-card")).to_have_attribute("fill", "#fcbf49")


def timeline_report():
    data = report()
    entries = [
        ("define", "output:result"),
        ("enter", "output:result"),
        ("enter", "calc:doubled"),
        ("exit", "calc:doubled"),
        ("exit", "output:result"),
        ("idle", None),
        ("userMark", None),
        ("enter", "output:other"),
        ("exit", "output:other"),
        ("queueEmpty", None),
        ("userMark", None),
    ]
    data["events"] = [
        {
            "action": action,
            "event": action,
            "node_id": node_id,
            "time_sec": step / 2,
            "phase": "interaction",
            "details": "Check the result" if action == "userMark" else action,
        }
        for step, (action, node_id) in enumerate(entries)
    ]
    return data


def test_timeline_marks_are_inside_band_and_click_to_seek(page: Page):
    page.set_content(format_reactlog_html(timeline_report(), CODE))
    expect(page.locator(".timeline-marker.is-output")).to_have_count(2)
    expect(page.locator(".timeline-marker.is-idle")).to_have_count(2)
    expect(page.locator(".timeline-marker.is-mark")).to_have_count(2)
    band = page.locator("#trace-track-wrap").bounding_box()
    idle = page.locator('.timeline-marker[data-step="5"]')
    idle_box = idle.bounding_box()
    assert band and idle_box
    assert idle_box["y"] == band["y"]
    assert idle_box["height"] == band["height"]
    idle.hover()
    expect(page.get_by_role("tooltip")).to_contain_text("Idle · Step 5 · 2.5s")
    idle.click()
    expect(page.locator("#scrubber-range")).to_have_value("5")
    page.locator('.timeline-marker[data-step="6"]').click()
    expect(page.locator("#scrubber-range")).to_have_value("6")
    expect(page.locator("#trace-status-line")).to_contain_text("User mark")
    expect(page.locator("#timeline-key")).to_contain_text("Output calculation")


def test_timeline_navigates_user_marks_and_outer_calculations(page: Page):
    page.set_content(format_reactlog_html(timeline_report(), CODE))
    page.get_by_role("button", name="Next output calculation", exact=True).click()
    expect(page.locator("#scrubber-range")).to_have_value("4")
    page.get_by_role("button", name="Next user mark", exact=True).click()
    expect(page.locator("#scrubber-range")).to_have_value("6")
    page.get_by_role("button", name="Next user mark", exact=True).click()
    expect(page.locator("#scrubber-range")).to_have_value("10")
    page.get_by_role("button", name="Previous user mark", exact=True).click()
    expect(page.locator("#scrubber-range")).to_have_value("6")
    page.get_by_role("button", name="Previous output calculation", exact=True).click()
    expect(page.locator("#scrubber-range")).to_have_value("4")
    page.keyboard.press("Alt+ArrowRight")
    expect(page.locator("#scrubber-range")).to_have_value("8")


def test_timeline_can_drag_from_a_mark_across_the_band(page: Page):
    page.set_content(format_reactlog_html(timeline_report(), CODE))
    marker = page.locator('.timeline-marker[data-step="5"]').bounding_box()
    band = page.locator("#trace-track-wrap").bounding_box()
    assert marker and band
    page.mouse.move(
        marker["x"] + marker["width"] / 2, marker["y"] + marker["height"] / 2
    )
    page.mouse.down()
    page.mouse.move(
        band["x"] + band["width"] * 0.8, band["y"] + band["height"] / 2, steps=5
    )
    page.mouse.up()
    expect(page.locator("#scrubber-range")).to_have_value("8")


def test_update_labels_and_view_controls(page: Page):
    page.set_content(format_reactlog_html(report(), CODE))
    current = page.get_by_role("button", name="Current update", exact=True)
    all_items = page.get_by_role("button", name="All items", exact=True)
    expect(current).to_be_visible()
    expect(all_items).to_have_attribute("title", "Show all items")
    expect(page.locator("#flush-counter-badge")).to_contain_text("Update 1 of 3")
    expect(page.locator("#active-flush-label")).to_contain_text("Update 1 of 3")
    all_items.click()
    expect(page.locator(".graph-node")).to_have_count(5)
    current.click()
    expect(page.get_by_role("button", name="Remove update filter")).to_be_visible()
    page.locator("#btn-next-action").click()
    expect(page.locator("#active-flush-label")).to_contain_text("Update 2 of 3")
    expect(page.locator(".graph-node")).to_have_count(3)
    page.get_by_role("button", name="Node details", exact=True).click()
    expect(page.locator("#flush-card-title")).to_contain_text("Update 2:")
    expect(page.locator("#flush-card-outputs")).to_have_text("Outputs that ran: 1")
