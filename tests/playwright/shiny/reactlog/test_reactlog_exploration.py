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


def set_activity_mode(page: Page, mode: str) -> None:
    if not page.locator("#activity-select").is_visible():
        page.locator("#btn-settings").click()
    page.locator("#activity-select").select_option(mode)
    if page.locator("#settings-menu").is_visible():
        page.locator("#btn-settings").click()


def set_clientdata_mode(page: Page, mode: str) -> None:
    if not page.locator("#clientdata-select").is_visible():
        page.locator("#btn-settings").click()
    page.locator("#clientdata-select").select_option(mode)
    if page.locator("#settings-menu").is_visible():
        page.locator("#btn-settings").click()


def reset_graph_view(page: Page) -> None:
    if not page.locator("#btn-reset-view").is_visible():
        page.locator("#btn-settings").click()
    page.locator("#btn-reset-view").click()


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
    expect(page.locator("#flush-counter-badge")).to_have_text("Update 1 of 4")
    expect(page.locator(".timeline-marker.is-idle")).to_have_count(4)
    page.evaluate("selectFlush(1)")
    expect(page.locator("#scrubber-range")).to_have_value("7")
    expect(page.locator("#flush-counter-badge")).to_have_text("Update 2 of 4")
    expect(page.locator(".graph-node")).to_have_count(0)
    page.evaluate("selectFlush(2)")
    expect(page.locator("#scrubber-range")).to_have_value("8")
    page.evaluate("selectFlush(3)")
    expect(page.locator("#active-flush-label")).to_contain_text(
        "Update 4 of 4 · x: 1 → 2"
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
    expect(page.locator(".timeline-marker.is-idle")).to_have_count(4)
    page.evaluate("seekTo(16)")
    expect(page.locator(".graph-node")).to_have_count(3)
    page.locator("#flush-counter-badge").click()
    expect(page.locator("#secondary-timeline-meta")).to_contain_text("1 outputs")
    expect(page.locator(".secondary-stage-pill.is-active")).to_contain_text("Idle")


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
    expect(page.locator(".secondary-stage-pill.is-active")).to_contain_text("Idle")


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
    expect(page.locator(".timeline-marker.is-idle")).to_have_count(4)
    expect(page.locator(".timeline-marker.is-mark")).to_have_count(1)
    page.evaluate("seekTo(14)")
    expect(page.locator("#active-flush-label")).to_contain_text("checkpoint")
    expect(page.locator("#flush-counter-badge")).to_have_text("Update 4 of 4")


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
    clear_btn = page.locator("#search-clear")
    expect(clear_btn).to_be_hidden()
    page.locator("#search-input").fill("id:calc:doubled")
    expect(clear_btn).to_be_visible()
    page.locator("#search-results button").click()
    page.locator("#btn-play").hover()
    expect(clear_btn).to_be_visible()
    page.locator("#btn-toggle-inspector").click()
    expect(page.locator("#sidebar")).to_be_visible()
    expect(page.locator("#search-input")).to_have_value("calc:doubled")
    expect(page.locator("#active-filters button")).to_have_count(0)
    expect(page.locator(".graph-node")).to_have_count(3)
    expect(page.locator("#filter-node-count")).to_have_text("3 of 5 nodes")
    assert page.locator("#event-list .event-name").all_text_contents()
    assert all(
        "other" not in name and "input.y" not in name
        for name in page.locator("#event-list .event-name").all_text_contents()
    )
    page.get_by_role("button", name="Show node choices").click()
    checked = page.locator("#search-results button.is-selected")
    expect(checked).to_have_count(1)
    expect(checked).to_have_attribute("aria-selected", "true")
    expect(checked.locator(".search-check svg")).to_be_visible()
    checked.click()
    expect(page.locator(".graph-node")).to_have_count(5)
    expect(page.locator("#search-input")).to_have_value("")
    expect(clear_btn).to_be_hidden()

    page.get_by_role("button", name="Close Inspector", exact=True).click()
    page.locator('.graph-node[data-id="calc:doubled"]').dblclick()
    expect(page.locator("#search-input")).to_have_value("calc:doubled")
    expect(clear_btn).to_be_visible()
    expect(page.locator(".graph-node")).to_have_count(3)
    expect(page.locator("#filter-node-count")).to_have_text("3 of 5 nodes")
    clear_btn.click()
    expect(page.locator("#search-input")).to_have_value("")
    expect(clear_btn).to_be_hidden()
    expect(page.locator(".graph-node")).to_have_count(5)


def test_root_module_search_and_stage_filters_clear_together(page: Page):
    page.set_content(format_reactlog_html(report(), CODE))
    page.locator("#search-input").fill("module:__root__")
    expect(page.locator("#filter-node-count")).to_have_text("3 of 5 nodes")
    set_activity_mode(page, "full")
    expect(page.locator("#filter-node-count")).to_have_text("3 of 5 nodes")
    reset_graph_view(page)
    expect(page.locator("#search-input")).to_have_value("")
    expect(page.locator("#active-filters button")).to_have_count(0)
    expect(page.locator("#filter-node-count")).to_have_text("5 of 5 nodes")


def test_empty_recording_can_open_graph(page: Page):
    errors: list[str] = []

    def on_error(error: Error) -> None:
        errors.append(str(error))

    page.on("pageerror", on_error)
    page.set_content(format_reactlog_html({"nodes": [], "edges": [], "events": []}, ""))
    expect(page.locator("#filter-node-count")).to_have_text("0 of 0 nodes")
    set_activity_mode(page, "full")
    expect(page.locator(".graph-node")).to_have_count(0)


def test_clear_all_restores_entire_graph_from_active_flush(page: Page):
    page.set_content(format_reactlog_html(report(), CODE))
    set_activity_mode(page, "flush")
    page.locator("#btn-play").focus()
    page.keyboard.press("ArrowDown")
    expect(page.locator(".graph-node")).to_have_count(3)
    reset_graph_view(page)
    expect(page.locator(".graph-node")).to_have_count(5)


def test_compact_layout_opens_graph_and_only_shows_current_flush(page: Page):
    page.set_content(format_reactlog_html(report(), CODE))
    set_activity_mode(page, "flush")
    expect(page.locator("#reactlog-svg")).to_be_visible()
    expect(page.locator("#sidebar")).to_be_hidden()
    expect(page.locator("#sidebar-rail")).to_have_css("width", "40px")
    expect(page.locator("#btn-toggle-inspector")).to_have_text("")
    expect(
        page.locator(
            "#timeline-tab, #actions-tab, #btn-summary-toggle, #flush-pipeline-bar, #timeline-sidebar, #flush-select"
        )
    ).to_have_count(0)
    expect(page.locator("#active-flush-label")).to_contain_text("Initial render")
    page.locator("#btn-play").focus()
    page.keyboard.press("ArrowDown")
    expect(page.locator("#active-flush-label")).to_contain_text("x")
    expect(page.locator(".graph-node")).to_have_count(3)
    page.locator("#btn-play").focus()
    page.keyboard.press("ArrowDown")
    expect(page.locator("#active-flush-label")).to_contain_text("y")
    expect(page.locator(".graph-node")).to_have_count(2)
    page.locator("#btn-play").focus()
    page.keyboard.press("ArrowUp")
    expect(page.locator("#active-flush-label")).to_contain_text("x")


@pytest.mark.parametrize("theme", ["dark", "light"])
def test_progress_bar_supports_pointer_keyboard_and_idle_markers(
    page: Page, theme: str
):
    data = report()
    page.set_content(format_reactlog_html(data, CODE, theme=theme))
    expect(page.locator(".timeline-marker.is-idle")).to_have_count(4)
    slider = page.get_by_role("slider", name="Timeline step scrubber")
    timeline = page.locator("#trace-timeline-bar").bounding_box()
    box = slider.bounding_box()
    assert timeline is not None and box is not None
    assert box["y"] + box["height"] <= timeline["y"] + timeline["height"]
    marker_bounds = page.locator(".timeline-marker").evaluate_all(
        "els => els.map(el => el.getBoundingClientRect().bottom)"
    )
    assert all(bottom <= box["y"] + box["height"] for bottom in marker_bounds)
    slider.focus()
    page.keyboard.press("ArrowRight")
    expect(slider).to_have_value("1")
    box = slider.bounding_box()
    assert box is not None
    page.mouse.click(box["x"] + box["width"] - 8, box["y"] + box["height"] / 2)
    expect(slider).to_have_value(str(len(data["events"]) - 1))
    expect(page.locator("#active-flush-label")).to_contain_text("y")
    expect(slider).to_have_attribute(
        "aria-valuetext", re.compile(r"Step 20 of 20\. y.*Idle")
    )
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
        assert video["width"] <= 440
        assert video["x"] + video["width"] < rail["x"]
        assert timeline["y"] + timeline["height"] <= video["y"]
        assert graph["width"] == width - 40
    page.get_by_role("button", name="Hide recording", exact=True).click()
    expect(player).to_be_hidden()
    page.get_by_role("button", name="Toggle recording").click()
    expect(player).to_be_visible()


def test_details_sidebar_docks_and_resizes_graph(page: Page):
    page.set_content(format_reactlog_html(report(), CODE))
    graph = page.locator("#graph-container")
    before = graph.bounding_box()
    assert before is not None
    page.get_by_role("button", name="Node details", exact=True).click()
    expect(page.locator("#sidebar")).to_be_visible()
    sidebar_box = page.locator("#sidebar").bounding_box()
    after = graph.bounding_box()
    assert sidebar_box is not None and after is not None
    assert after["width"] < before["width"]
    assert after["x"] + after["width"] <= sidebar_box["x"] + 1
    page.get_by_role("tab", name="App code").click()
    expect(page.locator("#source-panel")).to_be_visible()
    expect(page.locator("#timeline-panel")).to_be_hidden()
    assert graph.bounding_box() == after


@pytest.mark.parametrize("query", ["module:analysis", "analysis", "MODULE:ANALYSIS"])
def test_module_search_filters_nodes_and_clears(page: Page, query: str):
    page.set_content(format_reactlog_html(report(), CODE))
    set_activity_mode(page, "full")
    page.locator("#search-input").fill(query)
    expect(page.locator(".graph-node")).to_have_count(2)
    expect(page.locator("#search-results button")).to_have_count(2)
    page.locator("#search-input").press("Escape")
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
    set_activity_mode(page, "full")
    node = page.locator('.graph-node[data-id="calc:doubled"]')
    for step, (state, color) in enumerate(
        [
            ("calculating", "var(--state-calculating)"),
            ("invalidating", "var(--state-invalidating)"),
            ("invalidated", "var(--state-invalidated)"),
            ("ready", "var(--state-ready)"),
            ("frozen", "var(--state-frozen)"),
            ("ready", "var(--state-ready)"),
        ]
    ):
        page.locator("#scrubber-range").fill(str(step))
        expect(node).to_have_attribute("data-state", state)
        expect(node.locator(".node-card")).to_have_attribute("fill", color)
    page.locator("#btn-play").focus()
    page.keyboard.press("Shift+ArrowRight")
    expect(page.locator("#scrubber-range")).to_have_value("6")
    expect(page.locator("#trace-status-line")).to_have_text("Idle")
    page.locator("#scrubber-range").fill("7")
    edge = page.locator('.graph-edge[data-from="input:x"][data-to="calc:doubled"]')
    expect(edge).to_have_class(re.compile("is-inactive"))
    expect(edge).to_have_css("stroke-dasharray", "1px, 5px")
    node.hover()
    page.locator(".toolbar").hover()
    expect(edge).to_have_css("stroke", "rgb(145, 161, 179)")
    page.locator("#scrubber-range").fill("8")
    expect(edge).not_to_have_class(re.compile("is-inactive"))
    page.locator("#btn-play").focus()
    page.keyboard.press("Shift+ArrowRight")
    expect(page.locator("#scrubber-range")).to_have_value("9")
    page.locator("#btn-play").focus()
    page.keyboard.press("Shift+ArrowLeft")
    expect(page.locator("#scrubber-range")).to_have_value("6")

    page.locator("#scrubber-range").fill("0")
    expect(node).to_have_attribute("data-state", "calculating")
    expect(node.locator(".node-card")).to_have_attribute(
        "fill", "var(--state-calculating)"
    )


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
    page.locator("#btn-play").focus()
    page.keyboard.press("Alt+ArrowRight")
    expect(page.locator("#scrubber-range")).to_have_value("4")
    page.locator("#btn-play").focus()
    page.keyboard.press("Alt+ArrowDown")
    expect(page.locator("#scrubber-range")).to_have_value("6")
    page.locator("#btn-play").focus()
    page.keyboard.press("Alt+ArrowDown")
    expect(page.locator("#scrubber-range")).to_have_value("10")
    page.locator("#btn-play").focus()
    page.keyboard.press("Alt+ArrowUp")
    expect(page.locator("#scrubber-range")).to_have_value("6")
    page.locator("#btn-play").focus()
    page.keyboard.press("Alt+ArrowLeft")
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
    page.locator("#btn-settings").click()
    activity_select = page.locator("#activity-select")
    expect(activity_select).to_be_visible()
    expect(activity_select).to_have_value("full")
    expect(page.locator("#flush-counter-badge")).to_have_count(0)
    expect(page.locator("#active-flush-label")).to_contain_text("Initial render")
    expect(page.locator(".graph-node")).to_have_count(5)
    activity_select.select_option("flush")
    expect(activity_select).to_have_value("flush")
    page.locator("#btn-settings").click()
    expect(page.locator("#active-filters button")).to_have_count(0)
    page.locator("#btn-play").focus()
    page.keyboard.press("ArrowDown")
    expect(page.locator("#active-flush-label")).to_contain_text("x")
    expect(page.locator(".graph-node")).to_have_count(3)
    page.get_by_role("button", name="Node details", exact=True).click()
    expect(page.locator("#flush-card-title")).to_contain_text("Activity 3:")
    expect(page.locator("#flush-card-outputs")).to_have_text("Outputs that ran: 1")
    page.locator("#flush-counter-badge").click()
    expect(page.locator("#secondary-timeline-tag")).to_have_text("Update 3 of 4")


def test_ui_improvements_picker_roles_clientdata_and_ergonomics(page: Page):
    data = timeline_report()
    data["nodes"].append(
        {
            "id": "input:.clientdata_output_result_hidden",
            "name": ".clientdata_output_result_hidden",
            "label": ".clientdata_output_result_hidden",
            "type": "input",
            "role": "source",
            "module": "",
        }
    )
    long_code = "\n".join([f"# padding line {i}" for i in range(1, 50)] + [CODE])
    for node in data["nodes"]:
        if node.get("id") == "calc:doubled":
            node["line"] = 51
    page.set_viewport_size({"width": 1280, "height": 720})
    page.set_content(format_reactlog_html(data, long_code, video_path="demo.webm"))

    idle_bg = page.locator(".timeline-marker.is-idle").first.evaluate(
        "el => getComputedStyle(el).backgroundColor"
    )
    out_bg = page.locator(".timeline-marker.is-output").first.evaluate(
        "el => getComputedStyle(el).backgroundColor"
    )
    assert idle_bg != out_bg

    track_bg = page.locator("#trace-track-wrap").evaluate(
        "el => getComputedStyle(el).backgroundColor"
    )
    assert track_bg == "rgb(27, 38, 52)"

    expect(page.locator("#btn-flush-picker")).to_have_count(0)
    expect(page.locator("#flush-picker-menu")).to_have_count(0)
    expect(page.locator("#flush-counter-badge")).to_have_count(0)
    expect(page.locator("#btn-toggle-clientdata")).to_have_count(0)
    expect(page.locator("#btn-toggle-changes")).to_have_count(0)

    page.locator("#btn-settings").click()
    page.locator("#activity-select").select_option("full")
    expect(page.locator(".graph-node")).to_have_count(5)

    client_select = page.locator("#clientdata-select")
    expect(client_select).to_be_visible()
    expect(client_select).to_have_value("hide")
    client_select.select_option("show")
    expect(page.locator(".graph-node")).to_have_count(6)
    client_select.select_option("hide")
    expect(page.locator(".graph-node")).to_have_count(5)
    client_select.select_option("show")
    expect(page.locator(".graph-node")).to_have_count(6)
    page.locator("#btn-settings").click()

    expect(page.locator(".legend-role-btn")).to_have_count(0)
    page.evaluate("toggleRoleFilter('conductor')")
    expect(page.locator(".graph-node")).to_have_count(5)
    expect(page.get_by_role("button", name="Remove role filter")).to_be_visible()
    page.get_by_role("button", name="Remove role filter").click()
    expect(page.locator(".graph-node")).to_have_count(6)

    edge_titles = page.locator(".graph-edge title").count()
    assert edge_titles >= 3

    video_box_closed = page.locator("#video-panel").bounding_box()
    assert video_box_closed and video_box_closed["width"] >= 440
    page.locator('.graph-node[data-id="calc:doubled"]').click()
    expect(page.locator("#sidebar")).to_be_visible()
    expect(page.locator("#main-view")).to_have_class(re.compile(r"is-inspector-open"))
    video_box_open = page.locator("#video-panel").bounding_box()
    sidebar_box = page.locator("#sidebar").bounding_box()
    assert video_box_closed and video_box_open and sidebar_box
    assert video_box_open["x"] < video_box_closed["x"]
    assert video_box_open["x"] + video_box_open["width"] <= sidebar_box["x"]

    page.locator("#btn-toggle-inspector").click()
    expect(page.locator("#sidebar")).to_be_hidden()
    expect(page.locator("#btn-toggle-inspector-bottom")).to_have_class(
        re.compile(r"has-selection")
    )
    page.locator("#btn-toggle-inspector").click()
    expect(page.locator("#sidebar")).to_be_visible()

    page.get_by_role("tab", name="App code").click()
    expect(page.locator("#source-panel .source-line.is-active")).to_have_attribute(
        "data-line", "51"
    )

    page.get_by_role("button", name="Close Inspector", exact=True).click()
    expect(page.locator("#sidebar")).to_be_hidden()
    expect(page.locator("#btn-toggle-inspector-bottom")).not_to_have_class(
        re.compile(r"has-selection")
    )


@pytest.mark.parametrize("width,height", [(1366, 768), (1024, 600), (390, 700)])
def test_node_details_events_remain_readable_in_small_windows(
    page: Page, width: int, height: int
):
    page.set_viewport_size({"width": width, "height": height})
    code = CODE.replace("doubled", "filtered_data_with_a_very_long_reactive_name")
    data = report()
    for event in data["events"]:
        event["node_label"] = str(
            event.get("node_label") or event.get("label") or ""
        ).replace("doubled", "filtered_data_with_a_very_long_reactive_name")
    page.set_content(format_reactlog_html(data, code))
    set_activity_mode(page, "full")
    page.locator("#btn-toggle-inspector-bottom").click()
    page.locator("#event-history > summary").click()
    history = page.locator("#event-history")
    # The panel must scroll as a whole, without a collapsed nested event scroller.
    assert history.evaluate("el => el.clientHeight >= el.scrollHeight - 1")
    events = page.locator("#event-list .event-item")
    expect(events.first).to_be_visible()
    events.last.scroll_into_view_if_needed()
    expect(events.last).to_be_in_viewport()
    for selector in (".event-item", ".event-header", ".event-name"):
        assert page.locator(f"#event-list {selector}").evaluate_all(
            "els => els.every(el => el.scrollWidth <= el.clientWidth + 1)"
        ), selector


def test_report_has_two_graph_views_and_no_overview(page: Page):
    page.set_content(format_reactlog_html(report(), CODE))
    expect(page.get_by_role("button", name="Overview", exact=True)).to_have_count(0)
    expect(page.locator("#module-overview-panel")).to_have_count(0)
    page.keyboard.press("o")
    expect(page.locator("#reactlog-svg")).to_be_visible()
    set_activity_mode(page, "full")
    expect(page.locator(".graph-node")).to_have_count(5)
    set_activity_mode(page, "flush")
    expect(page.locator("#reactlog-svg")).to_be_visible()
    page.get_by_role("button", name="Shortcuts").click()
    expect(page.locator("#shortcuts-modal")).not_to_contain_text("Overview")


def test_clientdata_is_hidden_by_default_and_can_be_shown(page: Page):
    data = report()
    data["nodes"].append(
        {
            "id": "input:.clientdata_pixelratio",
            "label": ".clientdata_pixelratio",
            "role": "source",
            "type": "input",
        }
    )
    page.set_content(format_reactlog_html(data, CODE))
    set_activity_mode(page, "full")
    expect(
        page.locator('.graph-node[data-id="input:.clientdata_pixelratio"]')
    ).to_have_count(0)
    set_clientdata_mode(page, "show")
    expect(
        page.locator('.graph-node[data-id="input:.clientdata_pixelratio"]')
    ).to_have_count(1)


def test_search_dropdown_opens_and_filters_nodes(page: Page):
    page.set_content(format_reactlog_html(report(), CODE))
    page.get_by_role("button", name="Show node choices").click()
    expect(page.locator("#search-results")).to_be_visible()
    expect(page.locator("#search-results button")).not_to_have_count(0)
    page.locator("#search-input").fill("doubled")
    expect(page.locator("#search-results button")).to_have_count(1)
    page.keyboard.press("Enter")
    expect(page.locator("#search-results")).to_be_hidden()
    expect(page.locator('.graph-node[data-id="calc:doubled"]')).to_be_visible()


def test_node_count_and_controls_share_header(page: Page):
    page.set_content(format_reactlog_html(report(), CODE))
    expect(page.locator(".zoom-controls #filter-node-count")).to_be_visible()
    expect(page.locator(".app-header #filter-node-count")).to_have_count(0)
    expect(page.locator(".app-header #clientdata-select")).to_have_count(0)
    expect(page.locator(".app-header #activity-select")).to_have_count(0)
    expect(page.locator("#btn-settings")).to_be_visible()
    expect(page.locator("#settings-menu")).to_be_hidden()
    page.locator("#btn-settings").click()
    expect(page.locator("#settings-menu")).to_be_visible()
    expect(page.locator("#settings-menu #clientdata-select")).to_be_visible()
    expect(page.locator("#settings-menu #activity-select")).to_be_visible()
    expect(page.locator("#settings-menu #btn-toggle-collapse-all")).to_be_visible()
    expect(page.locator("#settings-menu #btn-reset-view")).to_be_visible()
    expect(page.locator(".zoom-controls > #btn-toggle-collapse-all")).to_have_count(0)
    expect(page.locator(".zoom-controls > #btn-reset-view")).to_have_count(0)
    expect(page.locator(".app-header #btn-toggle-clientdata")).to_have_count(0)
    expect(page.locator(".app-header #btn-toggle-changes")).to_have_count(0)
    expect(page.get_by_role("button", name="Clear all filters")).to_have_count(0)
    expect(page.locator("body > .filter-state")).to_have_count(0)


def test_only_nodes_with_recorded_value_changes_are_shown(page: Page):
    data = report()
    data["nodes"].extend(
        [
            {
                "id": "input:fixed",
                "label": "input.fixed",
                "role": "source",
                "type": "input",
            },
            {
                "id": "input:changed",
                "label": "input.changed",
                "role": "source",
                "type": "input",
            },
        ]
    )
    data["events"] = [
        {"action": "valueChange", "node_id": "input:fixed", "value": "1"},
        {"action": "valueChange", "node_id": "input:changed", "value": "1"},
        {"action": "queueEmpty"},
        {"action": "valueChange", "node_id": "input:fixed", "value": "1"},
        {"action": "valueChange", "node_id": "input:changed", "value": "2"},
    ]
    page.set_content(format_reactlog_html(data, CODE))
    set_activity_mode(page, "full")
    expect(page.locator('.graph-node[data-id="input:fixed"]')).to_have_count(1)
    expect(page.locator('.graph-node[data-id="input:changed"]')).to_have_count(1)


def test_default_graph_includes_observed_executions(page: Page):
    data = report()
    data["events"] = [
        {"action": "queueEmpty"},
        {"action": "enter", "node_id": "calc:doubled", "provenance": "observed"},
        {"action": "enter", "node_id": "output:result", "provenance": "observed"},
        {"action": "enter", "node_id": "output:other", "provenance": "inferred"},
    ]
    page.set_content(format_reactlog_html(data, CODE))
    expect(page.locator('.graph-node[data-id="calc:doubled"]')).to_have_count(1)
    expect(page.locator('.graph-node[data-id="output:result"]')).to_have_count(1)


def test_empty_changed_graph_explains_how_to_show_all_nodes(page: Page):
    data = report()
    data["events"] = [
        {"action": "valueChange", "node_id": "input:x", "value": "1"},
        {"action": "queueEmpty"},
    ]
    page.set_content(format_reactlog_html(data, CODE))
    expect(
        page.get_by_text("No recorded changes or executions in this view.")
    ).to_be_hidden()
    expect(page.locator(".graph-node")).to_have_count(5)


def test_clear_all_shows_hidden_nodes(page: Page):
    data = report()
    data["nodes"].append(
        {
            "id": "input:.clientdata_pixelratio",
            "label": ".clientdata_pixelratio",
            "role": "source",
            "type": "input",
        }
    )
    data["events"] = [{"action": "queueEmpty"}]
    page.set_content(format_reactlog_html(data, CODE))
    reset_graph_view(page)
    expect(
        page.locator('.graph-node[data-id="input:.clientdata_pixelratio"]')
    ).to_have_count(1)
    expect(page.locator('.graph-node[data-id="output:result"]')).to_have_count(1)


def test_search_can_reveal_a_node_hidden_by_default(page: Page):
    data = report()
    data["nodes"].append(
        {
            "id": "input:.clientdata_pixelratio",
            "label": ".clientdata_pixelratio",
            "role": "source",
            "type": "input",
        }
    )
    data["events"] = [{"action": "queueEmpty"}]
    page.set_content(format_reactlog_html(data, CODE))
    search = page.locator("#search-input")
    search.fill("id:input:.clientdata_pixelratio")
    expect(search).to_have_attribute("aria-expanded", "true")
    page.keyboard.press("Enter")
    expect(search).to_have_attribute("aria-expanded", "false")
    expect(
        page.locator('.graph-node[data-id="input:.clientdata_pixelratio"]')
    ).to_be_visible()
    expect(page.locator("#sidebar")).to_be_visible()


def test_empty_search_choices_respect_default_filters(page: Page):
    data = report()
    data["nodes"].append(
        {
            "id": "input:.clientdata_pixelratio",
            "label": ".clientdata_pixelratio",
            "role": "source",
            "type": "input",
        }
    )
    data["events"] = [
        {"action": "valueChange", "node_id": "input:x", "value": "1"},
        {"action": "queueEmpty"},
        {"action": "valueChange", "node_id": "input:x", "value": "2"},
    ]
    page.set_content(format_reactlog_html(data, CODE))
    page.get_by_role("button", name="Show node choices").click()
    expect(page.locator("#search-results button")).to_have_count(5)
    expect(page.locator("#search-results button").first).to_contain_text("input.x")


def test_search_escape_closes_dropdown_after_keyboard_navigation(page: Page):
    page.set_content(format_reactlog_html(report(), CODE))
    search = page.locator("#search-input")
    search.focus()
    page.keyboard.press("ArrowDown")
    page.keyboard.press("Escape")
    expect(page.locator("#search-results")).to_be_hidden()
    expect(search).to_have_attribute("aria-expanded", "false")
    expect(search).to_be_focused()


def test_timeline_uses_keyboard_navigation(page: Page):
    page.set_content(format_reactlog_html(report(), CODE))
    expect(page.locator("#timeline-more-controls")).to_have_count(0)
    expect(
        page.get_by_role("button", name="Previous activity", exact=True)
    ).to_have_count(0)
    expect(page.get_by_role("button", name="Next activity", exact=True)).to_have_count(
        0
    )
    expect(page.locator("#step-display")).to_be_visible()
    page.locator("#btn-play").focus()
    page.keyboard.press("ArrowDown")
    expect(page.locator("#active-flush-label")).to_contain_text("x")
    page.keyboard.press("ArrowUp")
    expect(page.locator("#active-flush-label")).to_contain_text("Initial render")
    page.keyboard.press("ArrowRight")
    expect(page.locator("#step-display")).to_contain_text("Step 1 /")


def test_smooth_connecting_edges_and_header_dropdowns(page: Page):
    page.set_content(format_reactlog_html(report(), CODE))
    page.locator("#btn-settings").click()
    client_select = page.locator("#settings-menu #clientdata-select")
    activity_select = page.locator("#settings-menu #activity-select")
    expect(client_select).to_be_visible()
    expect(activity_select).to_be_visible()
    expect(client_select.locator("option")).to_have_text(
        ["Hide clientdata", "Show clientdata"]
    )
    expect(activity_select.locator("option")).to_have_text(
        ["Show all activity", "Show current activity"]
    )
    page.locator("#btn-settings").click()
    edges = page.locator(".graph-edge")
    expect(edges).not_to_have_count(0)
    for i in range(edges.count()):
        d_attr = edges.nth(i).get_attribute("d") or ""
        assert " C " in d_attr
        assert " L " not in d_attr


def test_timeline_controls_fit_small_screen(page: Page):
    page.set_viewport_size({"width": 390, "height": 844})
    page.set_content(format_reactlog_html(report(), CODE))
    controls = page.locator(".timeline-navigation").bounding_box()
    assert controls is not None
    assert controls["x"] >= 0
    assert controls["x"] + controls["width"] <= 390


def test_report_uses_names_and_highlights_module_names(page: Page):
    data: dict[str, Any] = {
        "nodes": [
            {
                "id": "R45",
                "label": "input.scatter-y_var",
                "module": "scatter",
                "type": "input",
                "role": "source",
            },
            {
                "id": "r49",
                "label": "output summary:summary",
                "module": "summary",
                "type": "output",
                "role": "observer",
            },
        ],
        "edges": [{"from": "R45", "to": "r49"}],
        "events": [
            {
                "action": "dependsOn",
                "node_id": "r49",
                "edge_from": "R45",
                "edge_to": "r49",
                "details": "Dependency: 'R45' used by 'r49'",
                "step": 0,
                "time": 0.1,
            }
        ],
    }
    page.set_content(format_reactlog_html(data, ""))
    expect(page.locator("#trace-status-line")).to_have_text(
        "Dependency: 'input.scatter-y_var' used by 'output summary:summary'"
    )
    expect(page.locator("#trace-status-line")).not_to_contain_text("R45")
    expect(page.locator("#trace-status-line")).not_to_contain_text("r49")
    node = page.locator('.graph-node[data-id="R45"]')
    expect(node).to_have_attribute("aria-label", re.compile("input.scatter-y_var"))
    expect(node.locator(".module-name")).to_have_text("scatter")
    expect(node.locator(".module-name")).to_have_css("fill", "rgb(59, 7, 100)")
    search = page.locator("#search-input")
    search.fill("scatter")
    choice = page.locator("#search-results button").first
    expect(choice).to_contain_text("input.scatter-y_var")
    expect(choice).not_to_contain_text("R45")
    expect(choice.locator(".module-name")).to_have_css("color", "rgb(196, 181, 253)")
    choice.click()
    expect(search).to_have_value("input.scatter-y_var")
    expect(page.locator("#insp-title .module-name")).to_have_text("scatter")


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
