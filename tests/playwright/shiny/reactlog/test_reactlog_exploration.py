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


def test_search_selection_opens_details_and_filters_events(page: Page):
    page.set_content(format_reactlog_html(report(), CODE))
    page.locator("#search-input").fill("id:calc:doubled")
    page.locator("#search-results button").click()
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


def test_empty_recording_can_open_graph(page: Page):
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.set_content(format_reactlog_html({"nodes": [], "edges": [], "events": []}, ""))
    expect(page.locator("#filter-node-count")).to_have_text("0 of 0 nodes")
    page.locator("#btn-mode-full").click()
    expect(page.locator(".graph-node")).to_have_count(0)
    assert errors == []


def test_clear_all_restores_entire_graph_from_active_flush(page: Page):
    page.set_content(format_reactlog_html(report(), CODE))
    page.locator("#btn-mode-flush").click()
    page.locator("#timeline-more-controls").evaluate("element => element.open = true")
    page.locator("#btn-next-action").click()
    expect(page.locator(".graph-node")).to_have_count(3)
    page.get_by_role("button", name="Clear all filters").click()
    expect(page.locator(".graph-node")).to_have_count(5)


def test_compact_layout_opens_graph_and_only_shows_current_flush(page: Page):
    page.set_content(format_reactlog_html(report(), CODE))
    page.locator("#btn-mode-flush").click()
    expect(page.locator("#reactlog-svg")).to_be_visible()
    expect(page.locator("#sidebar")).to_be_hidden()
    expect(page.locator("#sidebar-rail")).to_have_css("width", "40px")
    expect(page.locator("#btn-toggle-inspector")).to_have_text("")
    expect(
        page.locator(
            "#timeline-tab, #actions-tab, #btn-summary-toggle, #flush-pipeline-bar, #timeline-sidebar, #flush-select"
        )
    ).to_have_count(0)
    expect(page.locator("#active-flush-label")).to_contain_text("Activity 1 of 3")
    page.locator("#timeline-more-controls").evaluate("element => element.open = true")
    page.locator("#btn-next-action").click()
    expect(page.locator("#active-flush-label")).to_contain_text("Activity 2 of 3 · x")
    expect(page.locator(".graph-node")).to_have_count(3)
    page.locator("#timeline-more-controls").evaluate("element => element.open = true")
    page.locator("#btn-next-action").click()
    expect(page.locator("#active-flush-label")).to_contain_text("Activity 3 of 3 · y")
    expect(page.locator(".graph-node")).to_have_count(2)
    page.locator("#timeline-more-controls").evaluate("element => element.open = true")
    page.locator("#btn-prev-action").click()
    expect(page.locator("#active-flush-label")).to_contain_text("Activity 2 of 3 · x")


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
    expect(page.locator("#active-flush-label")).to_contain_text("Activity 3 of 3")
    expect(slider).to_have_attribute("aria-valuetext", re.compile("Activity 3 of 3"))
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
    page.get_by_role("button", name="Show all nodes", exact=True).click()
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
    page.locator("#timeline-more-controls").evaluate("element => element.open = true")
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
    page.locator("#timeline-more-controls").evaluate("element => element.open = true")
    page.get_by_role("button", name="Next idle", exact=True).click()
    expect(page.locator("#scrubber-range")).to_have_value("9")
    page.locator("#timeline-more-controls").evaluate("element => element.open = true")
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
    page.locator("#timeline-more-controls").evaluate("element => element.open = true")
    page.get_by_role("button", name="Next output calculation", exact=True).click()
    expect(page.locator("#scrubber-range")).to_have_value("4")
    page.locator("#timeline-more-controls").evaluate("element => element.open = true")
    page.get_by_role("button", name="Next user mark", exact=True).click()
    expect(page.locator("#scrubber-range")).to_have_value("6")
    page.locator("#timeline-more-controls").evaluate("element => element.open = true")
    page.get_by_role("button", name="Next user mark", exact=True).click()
    expect(page.locator("#scrubber-range")).to_have_value("10")
    page.locator("#timeline-more-controls").evaluate("element => element.open = true")
    page.get_by_role("button", name="Previous user mark", exact=True).click()
    expect(page.locator("#scrubber-range")).to_have_value("6")
    page.locator("#timeline-more-controls").evaluate("element => element.open = true")
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
    current = page.get_by_role("button", name="Current activity", exact=True)
    all_items = page.get_by_role("button", name="All items", exact=True)
    expect(current).to_be_visible()
    expect(all_items).to_have_attribute("title", "Show all items")
    expect(page.locator("#flush-counter-badge")).to_contain_text("Activity 1 of 3")
    expect(page.locator("#active-flush-label")).to_contain_text("Activity 1 of 3")
    all_items.click()
    expect(page.locator(".graph-node")).to_have_count(5)
    current.click()
    expect(page.get_by_role("button", name="Remove activity filter")).to_be_visible()
    page.locator("#timeline-more-controls").evaluate("element => element.open = true")
    page.locator("#btn-next-action").click()
    expect(page.locator("#active-flush-label")).to_contain_text("Activity 2 of 3")
    expect(page.locator(".graph-node")).to_have_count(3)
    page.get_by_role("button", name="Node details", exact=True).click()
    expect(page.locator("#flush-card-title")).to_contain_text("Activity 2:")
    expect(page.locator("#flush-card-outputs")).to_have_text("Outputs that ran: 1")


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
    page.get_by_role("button", name="Show all nodes", exact=True).click()

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

    picker_btn = page.locator("#btn-flush-picker")
    picker_menu = page.locator("#flush-picker-menu")
    expect(picker_menu).to_be_hidden()
    picker_btn.click()
    expect(picker_menu).to_be_visible()
    picker_menu.locator('.flush-picker-item[data-flush-index="1"]').click()
    expect(picker_menu).to_be_hidden()
    expect(page.locator("#flush-counter-badge")).to_contain_text("Activity 2 of 3")

    page.get_by_role("button", name="All items", exact=True).click()
    expect(page.locator(".graph-node")).to_have_count(6)

    client_btn = page.locator("#btn-toggle-clientdata")
    expect(client_btn).to_be_visible()
    client_btn.click()
    expect(page.locator(".graph-node")).to_have_count(5)
    expect(
        page.get_by_role("button", name="Show clientdata", exact=True)
    ).to_be_visible()
    page.get_by_role("button", name="Show clientdata", exact=True).click()
    expect(page.locator(".graph-node")).to_have_count(6)

    calc_role_btn = page.locator('.legend-role-btn[data-role="conductor"]')
    calc_role_btn.click()
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

    page.get_by_role("button", name="Close Inspector", exact=True).click()
    expect(page.locator("#sidebar")).to_be_hidden()
    expect(page.locator("#btn-inspect-selection")).to_be_visible()
    expect(page.locator("#btn-toggle-inspector-bottom")).to_have_class(
        re.compile(r"has-selection")
    )
    page.locator("#btn-inspect-selection").click()
    expect(page.locator("#sidebar")).to_be_visible()

    page.get_by_role("tab", name="App code").click()
    expect(page.locator("#source-panel .source-line.is-active")).to_have_attribute(
        "data-line", "51"
    )


@pytest.mark.parametrize("width,height", [(1366, 768), (1024, 600), (390, 700)])
def test_node_details_events_remain_readable_in_small_windows(
    page: Page, width: int, height: int
):
    page.set_viewport_size({"width": width, "height": height})
    code = CODE.replace("doubled", "filtered_data_with_a_very_long_reactive_name")
    data = generate_reactlog(code)
    page.set_content(format_reactlog_html(data, code))
    page.locator("#btn-mode-full").click()
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
    page.get_by_role("button", name="All items", exact=True).click()
    expect(page.locator(".graph-node")).to_have_count(5)
    page.get_by_role("button", name="Current activity", exact=True).click()
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
    page.get_by_role("button", name="All items", exact=True).click()
    expect(
        page.locator('.graph-node[data-id="input:.clientdata_pixelratio"]')
    ).to_have_count(0)
    page.get_by_role("button", name="Show clientdata", exact=True).click()
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
    expect(page.locator(".app-header #filter-node-count")).to_be_visible()
    expect(page.locator(".app-header #btn-toggle-clientdata")).to_have_count(1)
    expect(page.locator("body > .filter-state")).to_have_count(0)
    expect(
        page.get_by_role("button", name="Current activity", exact=True)
    ).to_be_visible()


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
    page.get_by_role("button", name="All items", exact=True).click()
    expect(page.locator('.graph-node[data-id="input:fixed"]')).to_have_count(0)
    expect(page.locator('.graph-node[data-id="input:changed"]')).to_have_count(1)
    expect(page.locator('.graph-node[data-id="input:x"]')).to_have_count(0)
    expect(page.locator('.graph-node[data-id="output:result"]')).to_have_count(0)
    page.get_by_role("button", name="Show all nodes", exact=True).click()
    expect(page.locator('.graph-node[data-id="input:fixed"]')).to_have_count(1)


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
    expect(page.locator('.graph-node[data-id="output:other"]')).to_have_count(0)


def test_empty_changed_graph_explains_how_to_show_all_nodes(page: Page):
    data = report()
    data["events"] = [
        {"action": "valueChange", "node_id": "input:x", "value": "1"},
        {"action": "queueEmpty"},
    ]
    page.set_content(format_reactlog_html(data, CODE))
    expect(
        page.get_by_text("No recorded changes or executions in this view.")
    ).to_be_visible()
    page.get_by_role("button", name="Show all nodes", exact=True).click()
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
    page.get_by_role("button", name="Clear all filters").click()
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
    expect(page.locator("#search-results button")).to_have_count(1)
    expect(page.locator("#search-results button").first).to_contain_text("input:x")


def test_search_escape_closes_dropdown_after_keyboard_navigation(page: Page):
    page.set_content(format_reactlog_html(report(), CODE))
    search = page.locator("#search-input")
    search.focus()
    page.keyboard.press("ArrowDown")
    page.keyboard.press("Escape")
    expect(page.locator("#search-results")).to_be_hidden()
    expect(search).to_have_attribute("aria-expanded", "false")
    expect(search).to_be_focused()


def test_timeline_prioritizes_activity_navigation(page: Page):
    page.set_content(format_reactlog_html(report(), CODE))
    more = page.locator("#timeline-more-controls")
    expect(more).not_to_have_attribute("open", "")
    expect(
        page.get_by_role("button", name="Previous activity", exact=True)
    ).to_be_visible()
    expect(page.get_by_role("button", name="Next activity", exact=True)).to_be_visible()
    expect(page.locator("#btn-step-forward")).to_be_hidden()
    expect(page.locator("#step-display")).to_be_hidden()
    page.get_by_role("button", name="Next activity", exact=True).click()
    expect(page.locator("#flush-counter-badge")).to_contain_text("Activity 2")
    page.get_by_role("button", name="Previous activity", exact=True).click()
    expect(page.locator("#flush-counter-badge")).to_contain_text("Activity 1")
    page.get_by_text("More controls", exact=True).click()
    expect(page.locator("#btn-step-forward")).to_be_visible()
    expect(page.locator("#step-display")).to_be_visible()
    page.locator("#btn-step-forward").click()
    expect(page.locator("#step-display")).to_contain_text("Step 1 /")


def test_timeline_more_controls_fit_small_screen(page: Page):
    page.set_viewport_size({"width": 390, "height": 844})
    page.set_content(format_reactlog_html(report(), CODE))
    page.get_by_text("More controls", exact=True).click()
    panel = page.locator(".timeline-advanced").bounding_box()
    assert panel is not None
    assert panel["x"] >= 0
    assert panel["x"] + panel["width"] <= 390


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
