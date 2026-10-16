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


@pytest.fixture
def recorded_flushes() -> dict[str, Any]:
    return load_reactlog_json(
        [
            {
                "action": "define",
                "reactId": "x",
                "label": "input.x",
                "type": "input",
                "time": 0,
            },
            {
                "action": "define",
                "reactId": "y",
                "label": "input.y",
                "type": "input",
                "time": 0,
            },
            {
                "action": "define",
                "reactId": "out",
                "label": "output result",
                "type": "output",
                "time": 0,
            },
            {
                "action": "valueChange",
                "reactId": "x",
                "type": "input",
                "value": 1,
                "time": 0,
            },
            {"action": "enter", "reactId": "out", "time": 0.01},
            {"action": "exit", "reactId": "out", "time": 0.02},
            {"action": "queueEmpty", "time": 0.03},
            {"action": "queueEmpty", "time": 0.03},
            {"action": "enter", "reactId": "out", "time": 0.04},
            {"action": "exit", "reactId": "out", "time": 0.4},
            {"action": "queueEmpty", "time": 0.41},
            {
                "action": "valueChange",
                "reactId": "x",
                "type": "input",
                "value": 2,
                "time": 2.981,
            },
            {"action": "invalidateStart", "reactId": "out", "time": 2.981},
            {"action": "enter", "reactId": "out", "time": 2.981},
            {"action": "exit", "reactId": "out", "time": 3.098},
            {"action": "queueEmpty", "time": 3.1},
            {"action": "invalidateStart", "reactId": "out", "time": 9.255},
        ]
    )


def test_recorded_flushes_preserve_startup_and_empty_boundaries(
    page: Page, recorded_flushes: dict[str, Any]
):
    page.set_content(format_reactlog_html(recorded_flushes, ""))
    expect(page.locator("#flush-counter-badge")).to_have_text("Flush 1 / 4")
    expect(page.locator(".timeline-marker.is-flush")).to_have_count(4)
    page.locator("#btn-next-flush").click()
    expect(page.locator("#scrubber-range")).to_have_value("7")
    expect(page.locator("#flush-counter-badge")).to_have_text("Flush 2 / 4")
    expect(page.locator(".graph-node")).to_have_count(0)
    page.locator("#btn-next-flush").click()
    expect(page.locator("#scrubber-range")).to_have_value("8")
    page.locator("#btn-next-flush").click()
    expect(page.locator("#active-flush-label")).to_contain_text(
        "Flush 4 / 4 · x: 1 → 2"
    )


def test_recorded_flush_keeps_slow_work_and_batched_inputs_together(
    page: Page, recorded_flushes: dict[str, Any]
):
    events = recorded_flushes["events"]
    events.insert(
        13,
        {
            "action": "valueChange",
            "node_id": "y",
            "node_label": "input.y",
            "type": "input",
            "value": "3",
            "time_sec": 3.0,
        },
    )
    events[14]["time_sec"] = 3.4
    events[15]["time_sec"] = 3.6
    events[16]["time_sec"] = 3.7
    page.set_content(format_reactlog_html(recorded_flushes, ""))
    expect(page.locator(".timeline-marker.is-flush")).to_have_count(4)
    page.evaluate("seekTo(16)")
    expect(page.locator(".graph-node")).to_have_count(3)
    page.locator("#flush-counter-badge").click()
    expect(page.locator("#secondary-timeline-meta")).to_contain_text("1 outputs")
    expect(page.locator(".secondary-stage-pill.is-active")).to_contain_text("Settled")


def test_video_uses_recorded_flush_completion_time(
    page: Page, recorded_flushes: dict[str, Any]
):
    page.set_content(format_reactlog_html(recorded_flushes, "", video_path="demo.webm"))
    page.locator("#flush-counter-badge").click()
    page.locator("#session-video").evaluate("""video => {
        Object.defineProperties(video, {
            currentTime: { configurable: true, get: () => 3.0 },
            paused: { configurable: true, get: () => false },
        });
        video.dispatchEvent(new Event('timeupdate'));
    }""")
    expect(page.locator(".pill-output.is-active")).to_have_count(0)
    page.locator("#session-video").evaluate("""video => {
        Object.defineProperties(video, {
            currentTime: { configurable: true, get: () => 3.1 },
            paused: { configurable: true, get: () => false },
        });
        video.dispatchEvent(new Event('timeupdate'));
    }""")
    expect(page.locator("#scrubber-range")).to_have_value("15")
    expect(page.locator(".secondary-stage-pill.is-active")).to_contain_text("Settled")


@pytest.mark.parametrize("end", [14, 15])
def test_unfinished_recorded_flush_is_not_shown_as_settled(
    page: Page, recorded_flushes: dict[str, Any], end: int
):
    recorded_flushes["events"] = recorded_flushes["events"][:end]
    page.set_content(format_reactlog_html(recorded_flushes, ""))
    page.evaluate(f"seekTo({end - 1})")
    page.locator("#flush-counter-badge").click()
    expect(page.locator(".pill-idle")).to_have_count(0)
    expect(page.locator(".pill-output")).to_have_count(1 if end == 15 else 0)
    expect(page.locator("#active-flush-label")).to_contain_text("in progress")


def test_bookmarks_do_not_create_recorded_flushes(
    page: Page, recorded_flushes: dict[str, Any]
):
    recorded_flushes["events"].insert(
        14,
        {
            "action": "userMark",
            "event": "userMark",
            "node_label": "checkpoint",
            "phase": "interaction",
            "time_sec": 3.0,
        },
    )
    page.set_content(format_reactlog_html(recorded_flushes, ""))
    expect(page.locator(".timeline-marker.is-flush")).to_have_count(4)
    expect(page.locator(".timeline-marker.is-mark")).to_have_count(1)
    page.evaluate("seekTo(14)")
    expect(page.locator("#active-flush-label")).to_contain_text("checkpoint")
    expect(page.locator("#flush-counter-badge")).to_have_text("Flush 4 / 4")


def test_overview_drills_into_module_and_returns_without_losing_scope(page: Page):
    page.set_content(format_reactlog_html(report(), CODE))
    page.keyboard.press("o")
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
    expect(page.locator("#overview-activity button")).to_have_count(4)
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
    viewport = page.locator("#viewport-g")
    initial_transform = viewport.get_attribute("transform")
    assert initial_transform is not None
    page.locator("#reactlog-svg").hover(position={"x": 20, "y": 20})
    page.mouse.wheel(0, -100)
    expect(viewport).not_to_have_attribute("transform", initial_transform)
    transform = viewport.get_attribute("transform")
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


@pytest.mark.parametrize("selection", ["click", "enter", "arrow-enter"])
def test_input_search_selection_opens_secondary_timeline(page: Page, selection: str):
    page.set_content(format_reactlog_html(report(), CODE))
    search = page.locator("#search-input")
    search.fill("id:input:x")
    expect(page.locator("#secondary-timeline-bar")).to_be_hidden()
    if selection == "click":
        page.locator("#search-results button").click()
    elif selection == "enter":
        search.press("Enter")
    else:
        search.press("ArrowDown")
        page.locator("#search-results button").press("Enter")

    expect(page.locator("#secondary-timeline-bar")).to_be_visible()
    expect(page.locator("#search-results")).to_be_hidden()
    expect(page.locator('.graph-node[data-id="input:x"]')).to_have_class(
        re.compile(r"is-selected")
    )
    expect(page.locator("#filter-node-count")).to_have_text("3 of 5 nodes")
    last_pill = page.locator(".secondary-stage-pill").last
    last_step = last_pill.get_attribute("data-step")
    last_pill.click()
    expect(page.locator("#scrubber-range")).to_have_value(str(last_step))
    page.locator("#btn-close-secondary-timeline").click()
    expect(page.locator("#secondary-timeline-bar")).to_be_hidden()


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
    page.keyboard.press("o")
    page.locator("#overview-activity-section > summary").click()
    page.get_by_label("Activity interval start").select_option("2")
    page.get_by_label("Activity interval end").select_option("2")
    expect(page.locator("#filter-node-count")).to_have_text("3 of 5 nodes")
    page.locator("#overview-activity button").nth(2).click()
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
    page.evaluate("setViewMode('full')")
    expect(page.locator("#filter-node-count")).to_have_text("3 of 5 nodes")
    page.get_by_role("button", name="Clear all filters").click()
    expect(page.locator("#module-filter-select")).to_have_value("")
    expect(page.locator("#phase-filter-select")).to_have_value("all")
    expect(page.locator("#active-filters button")).to_have_count(0)
    page.evaluate("setViewMode('full')")
    expect(page.locator("#filter-node-count")).to_have_text("5 of 5 nodes")


def test_empty_recording_can_open_overview_and_graph(page: Page):
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.set_content(format_reactlog_html({"nodes": [], "edges": [], "events": []}, ""))
    expect(page.locator("#module-overview-panel")).to_be_hidden()
    expect(page.locator("#filter-node-count")).to_have_text("0 of 0 nodes")
    page.evaluate("setViewMode('full')")
    expect(page.locator(".graph-node")).to_have_count(0)
    assert errors == []


def test_clear_all_restores_entire_graph_from_active_flush(page: Page):
    page.set_content(format_reactlog_html(report(), CODE))
    page.keyboard.press("o")
    page.locator("#overview-activity-section > summary").click()
    page.locator("#overview-activity button").nth(2).click()
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
    page.keyboard.press("o")
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
    expect(page.get_by_role("group", name="Graph view mode")).to_be_hidden()
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
    expect(page.locator("#active-flush-label")).to_contain_text("Flush 1 / 4")
    page.locator("#btn-next-flush").click()
    expect(page.locator("#active-flush-label")).to_contain_text("Flush 2 / 4 · Init")
    expect(page.locator(".graph-node")).to_have_count(0)
    page.locator("#btn-next-flush").click()
    expect(page.locator("#active-flush-label")).to_contain_text("Flush 3 / 4 · x")
    expect(page.locator(".graph-node")).to_have_count(3)
    page.locator("#btn-next-flush").click()
    expect(page.locator("#active-flush-label")).to_contain_text("Flush 4 / 4 · y")
    expect(page.locator(".graph-node")).to_have_count(2)
    page.locator("#btn-prev-flush").click()
    expect(page.locator("#active-flush-label")).to_contain_text("Flush 3 / 4 · x")


@pytest.mark.parametrize("theme", ["dark", "light"])
def test_progress_bar_supports_pointer_keyboard_and_flush_markers(
    page: Page, theme: str
):
    data = report()
    page.set_content(format_reactlog_html(data, CODE, theme=theme))
    expect(page.locator(".timeline-marker.is-flush")).to_have_count(4)
    slider = page.get_by_role("slider", name="Timeline step scrubber")
    timeline = page.locator("#trace-timeline-bar").bounding_box()
    box = slider.bounding_box()
    assert timeline is not None and box is not None
    assert box["y"] + box["height"] <= timeline["y"] + timeline["height"]
    marker_bounds = page.locator(".timeline-marker").evaluate_all(
        "els => els.map(el => el.getBoundingClientRect().bottom)"
    )
    assert all(bottom < box["y"] + box["height"] / 2 for bottom in marker_bounds)
    slider.focus()
    page.keyboard.press("ArrowRight")
    expect(slider).to_have_value("1")
    box = slider.bounding_box()
    assert box is not None
    page.mouse.click(box["x"] + box["width"] - 8, box["y"] + box["height"] / 2)
    expect(slider).to_have_value(str(len(data["events"]) - 1))
    expect(page.locator("#active-flush-label")).to_contain_text("Flush 4 / 4")
    expect(slider).to_have_attribute("aria-valuetext", re.compile("Flush 4 / 4"))
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


def test_secondary_timeline_displays_friendly_node_names_for_anonymous_effects(
    page: Page,
):
    raw_report = {
        "version": "1.0",
        "nodes": [
            {
                "id": "r18",
                "label": "input.button",
                "role": "source",
                "type": "input",
                "module": "counter2_wrapper-counter",
            },
            {
                "id": "r19",
                "label": "reactive.effect event counter2_wrapper-counter:<anonymous>",
                "role": "observer",
                "type": "output",
                "module": "counter2_wrapper-counter",
                "line": 24,
            },
            {
                "id": "r30",
                "label": "reactive.effect event counter3:<anonymous>",
                "role": "observer",
                "type": "output",
                "module": "counter3",
                "line": 24,
            },
        ],
        "edges": [
            {"from": "r18", "to": "r19"},
            {"from": "r18", "to": "r30"},
        ],
        "events": [
            {
                "step": 0,
                "action": "valueChange",
                "phase": "interaction",
                "id": "r18",
                "value": "1",
                "details": "button changed",
            },
            {
                "step": 1,
                "action": "invalidate",
                "id": "r19",
                "invalidated_node_ids": ["r19", "r30"],
            },
            {"step": 2, "action": "output", "id": "r19", "type": "output"},
            {"step": 3, "action": "output", "id": "r30", "type": "output"},
        ],
    }
    loaded = load_reactlog_json(raw_report)
    page.set_content(format_reactlog_html(loaded, ""))
    page.locator("#flush-counter-badge").click()
    expect(page.locator("#secondary-timeline-bar")).to_be_visible()

    inv_pill = page.locator(".secondary-stage-pill.pill-invalidation")
    expect(inv_pill).to_be_visible()
    expect(inv_pill.locator(".stage-icon svg")).to_be_visible()
    expect(
        page.locator(".secondary-stage-pill.pill-trigger .stage-icon svg")
    ).to_be_visible()
    expect(inv_pill).to_contain_text("effect (counter2), effect (counter3)")
    expect(inv_pill).not_to_contain_text("r19")
    expect(inv_pill).not_to_contain_text("r30")
