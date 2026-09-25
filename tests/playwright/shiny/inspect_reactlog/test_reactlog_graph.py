from __future__ import annotations

import re
from pathlib import Path

from playwright.sync_api import Page, expect

from shiny._inspect import (
    format_reactlog_html,
    generate_reactlog,
    record_shiny_session,
)


def test_graph_elements_visible_on_initialization(page: Page) -> None:
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
    page.set_content(
        format_reactlog_html(reactlog, source_code=code),
        wait_until="domcontentloaded",
    )

    nodes = page.locator(".graph-node")
    assert nodes.count() == 5

    edges = page.locator(".graph-edge")
    assert edges.count() == 3

    page.wait_for_function(
        "() => Array.from(document.querySelectorAll('.graph-edge')).every(edge => parseFloat(window.getComputedStyle(edge).opacity) > 0.5)"
    )


def test_hover_highlights_connections(page: Page) -> None:
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
    page.set_content(
        format_reactlog_html(reactlog, source_code=code),
        wait_until="domcontentloaded",
    )

    page.locator('.graph-node[data-id="calc:doubled"]').hover()
    page.wait_for_function(
        "() => Array.from(document.querySelectorAll('.graph-edge')).some(edge => parseFloat(edge.style.opacity) === 1)"
    )

    page.locator(".toolbar").hover()
    page.wait_for_function(
        "() => Array.from(document.querySelectorAll('.graph-edge')).every(edge => parseFloat(edge.style.opacity) >= 0.6)"
    )


def test_app_code_tab_and_scrubber(page: Page) -> None:
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
        if event["event"] == "define" and event["node_id"] == "input:name"
    )

    page.set_content(
        format_reactlog_html(reactlog, source_code=code),
        wait_until="domcontentloaded",
    )

    source_panel = page.get_by_role("tabpanel", name="App code")
    expect(source_panel).to_be_hidden()

    page.get_by_role("tab", name="App code").click()
    expect(source_panel).to_be_visible()

    page.locator("#scrubber-range").fill(str(input_step))
    source_highlight = page.locator("#source-line-highlight")
    expect(source_highlight).to_be_visible()
    expect(source_highlight).to_have_attribute("data-line", "2")


def test_recording_video_tab(page: Page) -> None:
    code = """from shiny.express import input, render, ui
ui.input_text("name", "Name")
@render.text
def greeting():
    return f"Hello, {input.name()}"
"""
    reactlog = generate_reactlog(code, video_path="demo.webm")
    page.set_content(
        format_reactlog_html(
            reactlog, source_code=code, video_path="/path/to/demo.webm"
        ),
        wait_until="domcontentloaded",
    )

    video_tab = page.get_by_role("tab", name="Recording")
    expect(video_tab).to_be_visible()

    video_tab.click()
    video_panel = page.get_by_role("tabpanel", name="Recording")
    expect(video_panel).to_be_visible()
    expect(page.locator("video")).to_be_visible()


def test_headless_recording_session(tmp_path: Path) -> None:
    app_file = tmp_path / "app.py"
    app_file.write_text(
        """from shiny.express import input, render, ui
ui.input_numeric("n", "Number", 10)
@render.text
def out():
    return f"N={input.n()}"
""",
        encoding="utf-8",
    )

    video_out = tmp_path / "test_session.webm"

    def record_actions(page: Page) -> None:
        page.wait_for_selector("input#n")
        page.fill("input#n", "42")
        page.wait_for_timeout(500)

    res = record_shiny_session(
        str(app_file),
        video_path=str(video_out),
        headless=True,
        record_script=record_actions,
    )

    assert res["success"] is True
    assert video_out.exists()
    assert len(res["actions"]) >= 1

    reactlog = generate_reactlog(
        app_file.read_text(),
        recorded_actions=res["actions"],
        video_path=str(video_out),
    )
    assert reactlog["success"] is True
    assert reactlog["trace_kind"] == "inferred_simulation_with_recorded_browser_events"


def test_phase_filter_and_skip_button(page: Page) -> None:
    code = """from shiny.express import input, render, ui
from shiny import reactive

ui.input_numeric("n", "N", 10)
@reactive.calc
def double_n():
    return input.n() * 2
@render.text
def out_txt():
    return f"Result: {double_n()}"
"""
    recorded_actions = [
        {"type": "input", "name": "n", "value": 25, "timestamp": 800},
        {"type": "output", "name": "out_txt", "timestamp": 1100},
    ]
    reactlog = generate_reactlog(
        code, recorded_actions=recorded_actions, video_path="demo.webm"
    )
    page.set_content(
        format_reactlog_html(reactlog, source_code=code, video_path="demo.webm"),
        wait_until="domcontentloaded",
    )

    skip_btn = page.locator("#btn-skip-init")
    expect(skip_btn).to_be_visible()
    skip_btn.click()

    first_interact_step = reactlog["first_interaction_step"]
    expect(page.locator("#step-display")).to_have_text(
        f"Step {first_interact_step} / {reactlog['steps_total'] - 1}"
    )

    phase_select = page.locator("#phase-filter-select")
    expect(phase_select).to_be_visible()
    phase_select.select_option("init")
    expect(page.locator(".event-item.is-current")).to_have_count(0)


def test_draggable_splitter_and_video_tab_resize(page: Page) -> None:
    code = """from shiny.express import input, render, ui
ui.input_numeric("val", "Val", 10)
@render.text
def out():
    return f"V={input.val()}"
"""
    reactlog = generate_reactlog(code, video_path="demo.webm")
    page.set_content(
        format_reactlog_html(reactlog, source_code=code, video_path="demo.webm"),
        wait_until="domcontentloaded",
    )

    resizer = page.locator("#split-resizer")
    expect(resizer).to_be_visible()

    # Keyboard resizing
    resizer.focus()
    page.keyboard.press("ArrowLeft")
    expect(resizer).to_have_attribute("aria-valuenow", "464")

    # Switching to recording tab widens sidebar
    video_tab = page.locator("#video-tab")
    video_tab.click()
    expect(page.locator("#video-panel")).to_be_visible()
    expect(page.locator("video")).to_be_visible()


def test_trace_timeline_scrubber_and_action_chips(page: Page) -> None:
    code = """from shiny.express import input, render, ui
ui.input_numeric("multiplier", "Mult", 5)
@render.text
def res():
    return str(input.multiplier() * 10)
"""
    recorded_actions = [
        {"type": "input", "name": "multiplier", "value": 8, "timestamp": 1200},
        {"type": "output", "name": "res", "timestamp": 1600},
    ]
    reactlog = generate_reactlog(
        code, recorded_actions=recorded_actions, video_path="demo.webm"
    )
    page.set_content(
        format_reactlog_html(reactlog, source_code=code, video_path="demo.webm"),
        wait_until="domcontentloaded",
    )

    trace_bar = page.locator("#trace-timeline-bar")
    expect(trace_bar).to_be_visible()
    expect(page.locator("#trace-playhead")).to_be_visible()
    expect(page.locator("#lane-inputs .trace-chip")).to_have_count(1)
    expect(page.locator("#lane-outputs .trace-chip")).to_have_count(2)
    expect(page.locator("#lane-calcs .trace-chip")).to_have_count(0)
    expect(page.locator(".trace-chip")).to_have_count(3)


def test_event_timeline_labels_initialization_and_recorded_actions(
    page: Page,
) -> None:
    code = """from shiny.express import input, render, ui
ui.input_numeric("multiplier", "Mult", 5)
@render.text
def res():
    return str(input.multiplier() * 10)
"""
    reactlog = generate_reactlog(
        code,
        recorded_actions=[
            {"type": "input", "name": "multiplier", "value": 8, "timestamp": 1200},
            {"type": "output", "name": "res", "timestamp": 1600},
        ],
        video_path="demo.webm",
    )
    page.set_content(
        format_reactlog_html(reactlog, source_code=code, video_path="demo.webm"),
        wait_until="domcontentloaded",
    )

    phase_labels = page.locator(".event-phase-label")
    expect(phase_labels).to_have_count(2)
    expect(phase_labels.nth(0)).to_have_text("Initialization")
    expect(phase_labels.nth(1)).to_have_text("Recorded actions")


def test_event_items_can_be_activated_with_keyboard(page: Page) -> None:
    code = """from shiny.express import input, render, ui
ui.input_numeric("multiplier", "Mult", 5)
@render.text
def res():
    return str(input.multiplier() * 10)
"""
    reactlog = generate_reactlog(code, inputs={"multiplier": 8})
    page.set_content(
        format_reactlog_html(reactlog, source_code=code),
        wait_until="domcontentloaded",
    )

    target = page.locator(".event-item").nth(2)
    target_step = target.get_attribute("data-step")
    assert target_step is not None
    target.focus()
    expect(target).to_be_focused()
    page.keyboard.press("Enter")
    expect(page.locator("#step-display")).to_have_text(
        f"Step {target_step} / {reactlog['steps_total'] - 1}"
    )


def test_event_inspector_describes_steps_without_graph_nodes(page: Page) -> None:
    code = """from shiny.express import input, render, ui
ui.input_numeric("multiplier", "Mult", 5)
@render.text
def res():
    return str(input.multiplier() * 10)
"""
    reactlog = generate_reactlog(code, inputs={"multiplier": 8})
    page.set_content(
        format_reactlog_html(reactlog, source_code=code),
        wait_until="domcontentloaded",
    )

    expect(page.locator("#insp-title")).to_have_text("session")
    expect(page.locator("#insp-type")).to_have_text("Initialization event")
    expect(page.locator("#insp-status")).to_have_text("active")


def test_video_playback_resumes_without_rewinding_after_last_graph_event(
    page: Page,
) -> None:
    code = """from shiny.express import input, render, ui
ui.input_numeric("multiplier", "Mult", 5)
@render.text
def res():
    return str(input.multiplier() * 10)
"""
    reactlog = generate_reactlog(
        code,
        recorded_actions=[
            {"type": "input", "name": "multiplier", "value": 8, "timestamp": 1200},
            {"type": "output", "name": "res", "timestamp": 1600},
        ],
        video_path="demo.webm",
    )
    page.set_content(
        format_reactlog_html(reactlog, source_code=code, video_path="demo.webm"),
        wait_until="domcontentloaded",
    )

    page.locator("#session-video").evaluate("""video => {
            let mediaTime = 2;
            Object.defineProperties(video, {
                currentTime: {
                    configurable: true,
                    get: () => mediaTime,
                    set: value => { mediaTime = value; },
                },
                duration: { configurable: true, get: () => 10 },
                ended: { configurable: true, get: () => false },
                paused: { configurable: true, get: () => true },
            });
            video.play = () => Promise.resolve();
        }""")
    page.evaluate(f"seekTo({reactlog['steps_total'] - 1}, true)")
    page.locator("#session-video").evaluate("video => { video.currentTime = 2; }")

    page.locator("#btn-play").click()

    assert page.locator("#session-video").evaluate("video => video.currentTime") == 2


def test_video_frame_callback_updates_graph_between_timeupdate_events(
    page: Page,
) -> None:
    code = """from shiny.express import input, render, ui
ui.input_numeric("multiplier", "Mult", 5)
@render.text
def res():
    return str(input.multiplier() * 10)
"""
    reactlog = generate_reactlog(
        code,
        recorded_actions=[
            {"type": "input", "name": "multiplier", "value": 8, "timestamp": 1200},
            {"type": "output", "name": "res", "timestamp": 1600},
        ],
        video_path="demo.webm",
    )
    page.set_content(
        format_reactlog_html(reactlog, source_code=code, video_path="demo.webm"),
        wait_until="domcontentloaded",
    )

    page.locator("#session-video").evaluate("""video => {
            Object.defineProperties(video, {
                paused: { configurable: true, get: () => false },
                ended: { configurable: true, get: () => false },
            });
            video.requestVideoFrameCallback = callback => {
                window.__videoFrameCallback = callback;
                return 1;
            };
            video.dispatchEvent(new Event('play'));
        }""")

    assert page.evaluate("Boolean(window.__videoFrameCallback)") is True
    page.evaluate("window.__videoFrameCallback(performance.now(), { mediaTime: 1.25 })")
    expect(page.locator("#step-display")).to_have_text(
        f"Step {reactlog['first_interaction_step']} / {reactlog['steps_total'] - 1}"
    )


def test_theme_toggle_button_and_modes(page: Page) -> None:
    code = """from shiny.express import input, render, ui
ui.input_numeric("val", "Val", 10)
@render.text
def out():
    return f"V={input.val()}"
"""
    reactlog = generate_reactlog(code)
    page.set_content(
        format_reactlog_html(reactlog, source_code=code, theme="dark"),
        wait_until="domcontentloaded",
    )

    html_el = page.locator("html")
    expect(html_el).to_have_attribute("data-theme", "dark")

    theme_btn = page.locator("#btn-theme-toggle")
    expect(theme_btn).to_be_visible()
    theme_btn.click()

    expect(html_el).to_have_attribute("data-theme", "light")

    theme_btn.click()
    expect(html_el).to_have_attribute("data-theme", "dark")


def test_in_browser_load_reactlog_json(page: Page) -> None:
    code = """from shiny.express import input, render, ui
ui.input_numeric("val", "Val", 10)
@render.text
def out():
    return f"V={input.val()}"
"""
    reactlog = generate_reactlog(code)
    page.set_content(
        format_reactlog_html(reactlog, source_code=code),
        wait_until="domcontentloaded",
    )

    r_reactlog_data = {
        "version": "1.0",
        "session": "test_sess",
        "log": [
            {
                "action": "define",
                "id": "input:alpha",
                "label": "alpha",
                "type": "observable",
                "time": 0.1,
            },
            {
                "action": "define",
                "id": "calc:beta",
                "label": "beta",
                "type": "calc",
                "time": 0.2,
            },
            {
                "action": "dependsOn",
                "id": "calc:beta",
                "dependsOn": "input:alpha",
                "time": 0.3,
            },
            {
                "action": "define",
                "id": "output:gamma",
                "label": "gamma",
                "type": "observer",
                "time": 0.4,
            },
            {
                "action": "dependsOn",
                "id": "output:gamma",
                "dependsOn": "calc:beta",
                "time": 0.5,
            },
        ],
    }

    page.evaluate("data => loadReactlogObject(data)", r_reactlog_data)

    expect(page.locator("#stat-nodes")).to_have_text("3")
    expect(page.locator("#stat-edges")).to_have_text("2")
    expect(page.locator(".graph-node")).to_have_count(3)
    expect(page.locator(".graph-edge")).to_have_count(2)


def test_why_did_this_run_causal_inspector(page: Page) -> None:
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
"""
    reactlog = generate_reactlog(code, inputs={"x": 10, "y": 20})
    page.set_content(
        format_reactlog_html(reactlog, source_code=code),
        wait_until="domcontentloaded",
    )

    calc_node = page.locator('.graph-node[data-id="calc:doubled"]')
    calc_node.click()

    why_title = page.locator("#why-title")
    expect(why_title).to_contain_text("Why did calc:doubled run?")

    why_story = page.locator("#why-story")
    expect(why_story).to_contain_text("doubled")

    flow_pills = page.locator("#why-cascade-flow .flow-node-pill")
    expect(flow_pills).to_have_count(2)
    expect(flow_pills.first).to_have_text("input.x")
    expect(flow_pills.last).to_have_text("calc:doubled")

    upstream_pills = page.locator("#insp-upstream-list .conn-pill")
    expect(upstream_pills).to_have_count(1)
    expect(upstream_pills.first).to_have_text("input.x")

    downstream_pills = page.locator("#insp-downstream-list .conn-pill")
    expect(downstream_pills).to_have_count(1)
    expect(downstream_pills.first).to_have_text("output:result")


def test_selection_keeps_all_nodes_visible(page: Page) -> None:
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
    page.set_content(
        format_reactlog_html(reactlog, source_code=code),
        wait_until="domcontentloaded",
    )

    expect(page.locator(".graph-node")).to_have_count(5)

    page.locator('.graph-node[data-id="calc:doubled"]').click()

    expect(page.locator(".path-controls")).to_have_count(0)
    expect(page.locator(".graph-node:not(.is-dimmed)")).to_have_count(5)
    page.locator('.graph-node[data-id="input:x"]').click()
    expect(page.locator(".graph-node:not(.is-dimmed)")).to_have_count(5)
    page.locator('.graph-node[data-id="output:other"]').click()
    expect(page.locator(".graph-node:not(.is-dimmed)")).to_have_count(5)
    expect(page.locator('.graph-node[data-id="output:other"]')).to_have_class(
        re.compile("is-selected")
    )


def test_recording_summary_popover_toggle(page: Page) -> None:
    code = """from shiny.express import input, render, ui
ui.input_numeric("a", "A", 10)
@render.text
def out():
    return f"A={input.a()}"
"""
    reactlog = generate_reactlog(code)
    page.set_content(
        format_reactlog_html(reactlog, source_code=code),
        wait_until="domcontentloaded",
    )

    popover = page.locator("#recording-summary-popover")
    expect(popover).to_be_hidden()

    summary_btn = page.locator("#btn-summary-toggle")
    summary_btn.click()
    expect(popover).to_be_visible()
    expect(page.locator("#stat-nodes")).to_have_text("2")
    expect(page.locator("#stat-edges")).to_have_text("1")

    close_btn = popover.locator("button.mini")
    close_btn.click()
    expect(popover).to_be_hidden()


def test_actions_story_tab_and_inline_code_drawer(page: Page) -> None:
    code = """from shiny.express import input, render, ui
from shiny import reactive

ui.input_numeric("val", "Val", 5)
@reactive.calc
def calc_b():
    return input.val() + 1
@render.text
def out():
    return str(calc_b())
"""
    recorded_actions = [
        {"type": "input", "name": "val", "value": 42, "timestamp": 1000},
        {"type": "output", "name": "out", "timestamp": 1200},
    ]
    reactlog = generate_reactlog(code, recorded_actions=recorded_actions)
    page.set_content(
        format_reactlog_html(reactlog, source_code=code),
        wait_until="domcontentloaded",
    )

    actions_tab = page.locator("#actions-tab")
    actions_tab.click()
    actions_panel = page.locator("#actions-panel")
    expect(actions_panel).to_be_visible()

    action_items = page.locator(".action-story-item")
    expect(action_items).to_have_count(1)

    events_tab = page.locator("#timeline-tab")
    events_tab.click()

    page.locator('.graph-node[data-id="calc:calc_b"]').click()
    drawer_toggle = page.locator("#btn-toggle-source-drawer")
    expect(drawer_toggle).to_be_visible()

    source_code = page.locator("#insp-source-code")
    expect(source_code).to_be_hidden()

    drawer_toggle.click()
    expect(source_code).to_be_visible()
    expect(source_code).to_contain_text("def calc_b():")


def test_id_lineage_filter_and_timeline_preservation(page: Page) -> None:
    code = """from shiny.express import input, render, ui
from shiny import reactive

ui.input_numeric("x", "X", 1)
ui.input_numeric("y", "Y", 10)
@reactive.calc
def c():
    return input.x() * 2
@render.text
def o():
    return str(c())
@render.text
def separate_out():
    return str(input.y())
"""
    reactlog = generate_reactlog(code)
    page.set_content(
        format_reactlog_html(reactlog, source_code=code),
        wait_until="domcontentloaded",
    )

    expect(page.locator(".graph-node")).to_have_count(5)

    search = page.locator("#search-input")
    search.fill("id:calc:c")
    expect(page.locator(".graph-node")).to_have_count(3)
    expect(page.locator('.graph-node[data-id="input:x"]')).to_be_visible()
    expect(page.locator('.graph-node[data-id="calc:c"]')).to_be_visible()
    expect(page.locator('.graph-node[data-id="output:o"]')).to_be_visible()
    expect(page.locator('.graph-node[data-id="input:y"]')).to_have_count(0)
    expect(page.locator('.graph-node[data-id="output:separate_out"]')).to_have_count(0)

    page.get_by_role("button", name="Step forward").click()
    expect(page.locator(".graph-node")).to_have_count(3)

    page.get_by_role("button", name="Reset view", exact=True).click()
    expect(page.locator(".graph-node")).to_have_count(5)


def test_timeline_activity_mode_and_realtime_toggle(page: Page) -> None:
    code = """from shiny.express import input, render, ui
from shiny import reactive

ui.input_numeric("val", "Val", 10)
@render.text
def out():
    return f"V={input.val()}"
"""
    recorded_actions = [
        {"type": "input", "name": "val", "value": 20, "timestamp": 1500},
    ]
    reactlog = generate_reactlog(code, recorded_actions=recorded_actions)
    page.set_content(
        format_reactlog_html(reactlog, source_code=code),
        wait_until="domcontentloaded",
    )

    mode_select = page.locator("#timeline-mode-select")
    expect(mode_select).to_be_visible()

    burst_anchors = page.locator("#trace-burst-track .burst-anchor")
    expect(burst_anchors).to_have_count(2)

    mode_select.select_option("realtime")
    expect(mode_select).to_have_value("realtime")

    mode_select.select_option("activity")
    expect(mode_select).to_have_value("activity")


def test_trace_tooltip_is_hidden_until_timeline_drag(page: Page) -> None:
    code = """from shiny.express import input, render, ui
ui.input_numeric("value", "Value", 1)
@render.text
def result():
    return str(input.value())
"""
    recorded_actions = [
        {"type": "input", "name": "value", "value": 2, "timestamp": 1000},
    ]
    reactlog = generate_reactlog(code, recorded_actions=recorded_actions)
    page.set_content(
        format_reactlog_html(reactlog, source_code=code),
        wait_until="domcontentloaded",
    )

    tooltip = page.locator("#trace-tooltip")
    expect(tooltip).to_be_hidden()

    track = page.locator("#trace-track-wrap")
    track_box = track.bounding_box()
    assert track_box is not None
    start_x = track_box["x"] + track_box["width"] * 0.75
    drag_y = track_box["y"] + 2
    page.mouse.move(start_x, drag_y)
    page.mouse.down()
    page.mouse.move(start_x + 10, drag_y)
    expect(tooltip).to_be_visible()
    expect(tooltip).to_contain_text("s")
    page.mouse.up()
    expect(tooltip).to_be_hidden()


def test_timeline_seismograph_and_burst_anchors(page: Page) -> None:
    code = """from shiny.express import input, render, ui
from shiny import reactive

ui.input_numeric("x", "X", 1)
@reactive.calc
def doubled():
    return input.x() * 2
@render.text
def res():
    return str(doubled())
"""
    recorded_actions = [
        {"type": "input", "name": "x", "value": 5, "timestamp": 1200},
    ]
    reactlog = generate_reactlog(code, recorded_actions=recorded_actions)
    page.set_content(
        format_reactlog_html(reactlog, source_code=code),
        wait_until="domcontentloaded",
    )

    seismograph = page.locator("#trace-seismograph")
    expect(seismograph).to_be_visible()

    next_btn = page.locator("#btn-next-action")
    prev_btn = page.locator("#btn-prev-action")
    expect(next_btn).to_be_visible()
    expect(prev_btn).to_be_visible()

    next_btn.click()
    status_line = page.locator("#trace-status-line")
    expect(status_line).to_be_visible()


def test_multi_parent_dag_tree_and_single_target_synchronization(page: Page) -> None:
    code = """from shiny.express import input, render, ui
from shiny import reactive

ui.input_numeric("a", "A", 1)
ui.input_numeric("b", "B", 2)

@reactive.calc
def calc_a():
    return input.a() * 10

@reactive.calc
def calc_b():
    return input.b() * 20

@render.text
def merged():
    return f"Sum: {calc_a() + calc_b()}"
"""
    reactlog = generate_reactlog(code)
    page.set_content(
        format_reactlog_html(reactlog, source_code=code),
        wait_until="domcontentloaded",
    )

    merged_node = page.locator('.graph-node[data-id="output:merged"]')
    merged_node.click()

    status_line = page.locator("#trace-status-line")
    expect(status_line).to_contain_text("Selected: output:merged")

    why_title = page.locator("#why-title")
    expect(why_title).to_contain_text("Why did output:merged render?")

    dag_pills = page.locator("#why-cascade-flow .flow-node-pill")
    expect(dag_pills).to_have_count(3)

    why_story = page.locator("#why-story")
    expect(why_story).to_contain_text("Immediate causes:")
    expect(why_story).to_contain_text("calc:calc_a")
    expect(why_story).to_contain_text("calc:calc_b")


def test_activity_mode_equidistant_distribution_and_group_popover(page: Page) -> None:
    code = """from shiny.express import input, render, ui
from shiny import reactive

ui.input_numeric("units", "Units", 10)
@reactive.calc
def subtotal():
    return input.units() * 5

@render.text
def out_a():
    return f"A: {subtotal()}"

@render.text
def out_b():
    return f"B: {subtotal()}"
"""
    recorded_actions = [
        {"type": "input", "name": "units", "value": 20, "timestamp": 1200},
    ]
    reactlog = generate_reactlog(code, recorded_actions=recorded_actions)
    page.set_content(
        format_reactlog_html(reactlog, source_code=code),
        wait_until="domcontentloaded",
    )

    burst_cols = page.locator(".burst-region-column")
    expect(burst_cols).to_have_count(2)

    group_chip = page.locator("#lane-outputs .trace-chip.is-grouped").first
    expect(group_chip).to_be_visible()
    expect(group_chip).to_contain_text("2 outputs")

    group_chip.click()
    popover = page.locator("#group-chip-popover")
    expect(popover).to_be_visible()
    expect(popover).to_contain_text("2 Outputs in burst")


def test_humanized_timeline_dynamic_verbs_and_causal_summary(page: Page) -> None:
    code = """from shiny.express import input, render, ui
from shiny import reactive

ui.input_numeric("price", "Price", 25)
@reactive.calc
def subtotal():
    return input.price() * 2

@render.text
def summary():
    return f"Subtotal: {subtotal()}"
"""
    recorded_actions = [
        {"type": "input", "name": "price", "value": 30, "timestamp": 1200},
    ]
    reactlog = generate_reactlog(code, recorded_actions=recorded_actions)
    page.set_content(
        format_reactlog_html(reactlog, source_code=code),
        wait_until="domcontentloaded",
    )

    # 1. Humanized Timeline Anchor
    burst_anchors = page.locator(".burst-anchor")
    expect(burst_anchors).to_have_count(2)
    expect(burst_anchors.nth(1)).to_contain_text("price")
    expect(burst_anchors.nth(1)).to_have_attribute(
        "title", re.compile(r"price: 25 → 30")
    )

    # 2. Causal Story Banner above graph
    causal_banner = page.locator("#causal-summary-banner")
    expect(causal_banner).to_be_visible()

    # 3. Dynamic Why Question for Input
    page.locator('.graph-node[data-id="input:price"]').click()
    why_title = page.locator("#why-title")
    expect(why_title).to_contain_text("Why did input.price change?")

    # 4. Dynamic Why Question for Calc
    page.locator('.graph-node[data-id="calc:subtotal"]').click()
    expect(why_title).to_contain_text("Why did calc:subtotal run?")

    # 5. Dynamic Why Question for Output
    page.locator('.graph-node[data-id="output:summary"]').click()
    expect(why_title).to_contain_text("Why did output:summary render?")

    # 6. Streamlined Toolbar & Phase Filter
    phase_select = page.locator("#phase-filter-select")
    expect(phase_select).to_be_visible()


def test_action_scoped_causal_story_and_did_not_run_explanation(page: Page) -> None:
    code = """from shiny.express import input, render, ui
from shiny import reactive

ui.input_numeric("price", "Price", 25)
ui.input_numeric("units", "Units", 10)
ui.input_text("client", "Client", "Acme")

@reactive.calc
def subtotal():
    return input.price() * input.units()

@reactive.calc
def discount():
    return 0.1 if input.client() == "Acme" else 0.0

@render.text
def order_summary():
    return f"Order: {subtotal()}"

@render.text
def client_badge():
    return f"Client: {input.client()} (Discount: {discount()})"
"""
    recorded_actions = [
        {"type": "input", "name": "price", "value": 30, "timestamp": 1200},
    ]
    reactlog = generate_reactlog(code, recorded_actions=recorded_actions)
    page.set_content(
        format_reactlog_html(reactlog, source_code=code),
        wait_until="domcontentloaded",
    )

    # 1. Skip to the price action burst
    page.locator("#btn-skip-init").click()

    # 2. Live story contains only nodes downstream of price (subtotal, order_summary)
    causal_text = page.locator("#causal-summary-text")
    expect(causal_text).to_contain_text("Price changed 25 → 30")
    expect(causal_text).to_contain_text("subtotal")
    expect(causal_text).to_contain_text("order_summary")
    causal_str = causal_text.text_content() or ""
    assert "discount" not in causal_str
    assert "client_badge" not in causal_str

    # 3. Clicking output:order_summary shows why it rendered in this burst
    page.locator('.graph-node[data-id="output:order_summary"]').click()
    why_title = page.locator("#why-title")
    expect(why_title).to_contain_text("Why did output:order_summary render?")
    why_story = page.locator("#why-story")
    expect(why_story).to_contain_text("subtotal")

    # Selecting an output preserves the full graph.
    expect(page.locator(".graph-node.is-dimmed")).to_have_count(0)

    # 5. Clicking unaffected node (client) shows did not change in this action
    page.locator('.graph-node[data-id="input:client"]').click()
    expect(why_title).to_contain_text("input.client did not change")
    expect(page.locator("#why-story")).to_contain_text("Did not change during")

    # Selecting an input also preserves the full graph.
    expect(page.locator(".graph-node.is-dimmed")).to_have_count(0)


def test_malicious_node_id_no_code_execution_xss_protection(page: Page) -> None:
    code = """from shiny.express import input, render, ui
ui.input_numeric("val", "Val", 10)
@render.text
def out():
    return f"V: {input.val()}"
"""
    reactlog = generate_reactlog(code)
    malicious_json = {
        "version": "1.0",
        "session": "pwn_test",
        "nodes": [
            {
                "id": "calc:safe_node",
                "label": "calc:safe_node",
                "role": "conductor",
                "type": "calc",
            },
            {
                "id": "output:xss'); window.__pwned=1; ('",
                "label": "<img src=x onerror=window.__pwned=1>",
                "role": "observer",
                "type": "output",
            },
        ],
        "edges": [
            {
                "from": "calc:safe_node",
                "to": "output:xss'); window.__pwned=1; ('",
            }
        ],
        "events": [
            {
                "step": 0,
                "event": "define",
                "action": "define",
                "id": "calc:safe_node",
                "node_id": "calc:safe_node",
                "phase": "init",
                "provenance": "observed",
            },
            {
                "step": 1,
                "event": "define",
                "action": "define",
                "id": "output:xss'); window.__pwned=1; ('",
                "node_id": "output:xss'); window.__pwned=1; ('",
                "phase": "init",
                "provenance": "observed",
            },
            {
                "step": 2,
                "event": "dependsOn",
                "action": "dependsOn",
                "edge_from": "calc:safe_node",
                "edge_to": "output:xss'); window.__pwned=1; ('",
                "node_id": "output:xss'); window.__pwned=1; ('",
                "phase": "init",
                "provenance": "observed",
            },
        ],
    }

    page.set_content(
        format_reactlog_html(reactlog, source_code=code),
        wait_until="domcontentloaded",
    )
    page.evaluate("data => loadReactlogObject(data)", malicious_json)

    # Click nodes and buttons to trigger any handlers
    page.locator('.graph-node[data-id="calc:safe_node"]').click()
    is_pwned = page.evaluate("() => Boolean(window.__pwned)")
    assert is_pwned is False


def test_app_code_tab_and_drawer_show_line_numbers(page: Page) -> None:
    code = """from shiny.express import input, render, ui
from shiny import reactive

ui.input_numeric("val", "Val", 10)

@reactive.calc
def double_val():
    return input.val() * 2

@render.text
def out():
    return f"Result: {double_val()}"
"""
    reactlog = generate_reactlog(code)
    page.set_content(
        format_reactlog_html(reactlog, source_code=code),
        wait_until="domcontentloaded",
    )

    # 1. Check App code tab line numbers
    page.get_by_role("tab", name="App code").click()
    source_panel = page.get_by_role("tabpanel", name="App code")
    expect(source_panel).to_be_visible()

    line_nums = page.locator("#source-panel .source-line-num")
    expect(line_nums.first).to_have_text("1")
    expect(line_nums.nth(3)).to_have_text("4")

    # 2. Check inline drawer line numbers
    page.get_by_role("tab", name="Inspector").click()
    page.locator('.graph-node[data-id="calc:double_val"]').click()
    page.locator("#btn-toggle-source-drawer").click()

    drawer_line_nums = page.locator("#insp-source-code .source-line-num")
    expect(drawer_line_nums.first).to_have_text("7")


def test_r_import_search_preserves_all_nodes(page: Page) -> None:
    from shiny._inspect import load_reactlog_json

    raw = [
        {"action": "invalidateStart", "reactId": "r2"},
        {
            "action": "define",
            "reactId": "r1$x",
            "type": "reactiveValuesKey",
            "label": "input$x",
        },
        {
            "action": "define",
            "reactId": "r2",
            "type": "observable",
            "label": "doubled_value",
        },
        {
            "action": "define",
            "reactId": "r3",
            "type": "observer",
            "label": "output$result",
        },
        {"action": "define", "reactId": "r4", "type": "observer", "label": "unrelated"},
        {"action": "dependsOn", "reactId": "r2", "depOnReactId": "r1$x"},
        {"action": "dependsOn", "reactId": "r3", "depOnReactId": "r2"},
        {"action": "dependsOn", "reactId": "r4", "depOnReactId": "r1$x"},
    ]
    page.set_content(format_reactlog_html(load_reactlog_json(raw), source_code=""))
    # Exercise the separate browser file-import normalizer as well.
    page.evaluate("raw => loadReactlogObject(raw)", raw)
    expect(page.locator('.graph-node[data-id="r1$x"]')).to_have_attribute(
        "data-role", "source"
    )
    expect(page.locator('.graph-node[data-id="r2"]')).to_have_attribute(
        "data-role", "conductor"
    )
    expect(page.locator('.graph-node[data-id="r3"]')).to_have_attribute(
        "data-role", "observer"
    )
    page.locator("#search-input").fill("dblvl")
    expect(page.locator("#search-results button")).to_have_count(1)
    page.locator("#search-input").fill("id:r2")
    page.locator("#search-results button").click()
    expect(page.locator(".graph-node")).to_have_count(3)
    expect(page.locator('.graph-node[data-id="r4"]')).to_have_count(0)
    expect(page.locator("#search-results")).to_be_hidden()
    page.get_by_role("button", name="Reset view", exact=True).click()
    expect(page.locator(".graph-node")).to_have_count(4)
    page.locator("#search-input").fill("no match xyz")
    expect(page.locator("#search-results")).to_contain_text("0 matches")
    page.locator("#search-input").press("Escape")
    expect(page.locator(".graph-node")).to_have_count(4)


def test_fit_large_graph(page: Page) -> None:
    from shiny._inspect import load_reactlog_json

    raw = [
        {
            "action": "define",
            "reactId": f"r{i}",
            "type": "observable",
            "label": f"reactive {i}",
        }
        for i in range(200)
    ]
    page.set_content(format_reactlog_html(load_reactlog_json(raw), source_code=""))
    page.get_by_role("button", name="Fit graph to view", exact=True).click()
    bounds = page.evaluate("""() => {
        const svg = document.getElementById('reactlog-svg').getBoundingClientRect();
        const graph = document.getElementById('viewport-g').getBoundingClientRect();
        return {fits: graph.top >= svg.top && graph.bottom <= svg.bottom && graph.left >= svg.left && graph.right <= svg.right, zoom: zoomLevel};
    }""")
    assert bounds["fits"]
    assert bounds["zoom"] < 0.4


def test_search_keyboard_and_reset_view(page: Page) -> None:
    code = """from shiny.express import input, render, ui
ui.input_numeric("x", "X", 1)
@render.text
def result():
    return str(input.x())
"""
    page.set_content(format_reactlog_html(generate_reactlog(code), code))
    search = page.locator("#search-input")
    search.fill("id:output:result")
    search.press("ArrowDown")
    expect(page.locator("#search-results button")).to_be_focused()
    page.keyboard.press("Enter")
    expect(page.locator("#search-results")).to_be_hidden()
    page.get_by_role("button", name="Reset view", exact=True).click()
    expect(page.locator(".graph-node")).to_have_count(2)
    search.fill("unfindablenode")
    expect(page.locator("#search-results")).to_contain_text(
        "0 matches. Try a node name"
    )
    search.press("Escape")
    expect(search).to_be_focused()
    expect(page.locator(".graph-node")).to_have_count(2)


def test_narrow_report_keeps_graph_and_controls_accessible(page: Page) -> None:
    code = """from shiny.express import input, render, ui
ui.input_numeric("x", "X", 1)
@render.text
def result():
    return str(input.x())
"""
    original_viewport = page.viewport_size
    try:
        for width in (390, 768):
            page.set_viewport_size({"width": width, "height": 844})
            page.set_content(format_reactlog_html(generate_reactlog(code), code))
            bounds = page.evaluate("""() => {
                const graph = document.getElementById('graph-container').getBoundingClientRect();
                const sidebar = document.getElementById('sidebar').getBoundingClientRect();
                const controls = document.querySelector('.toolbar').getBoundingClientRect();
                return {width: document.documentElement.scrollWidth,
                    viewport: innerWidth, graphWidth: graph.width,
                    stacked: sidebar.top >= graph.bottom,
                    controlsFit: controls.right <= innerWidth};
            }""")
            assert bounds["width"] <= bounds["viewport"]
            assert bounds["graphWidth"] == width
            assert bounds["stacked"]
            assert bounds["controlsFit"]
            page.locator("#search-input").fill("result")
            expect(page.locator("#search-results button")).to_have_count(1)
    finally:
        if original_viewport:
            page.set_viewport_size(original_viewport)


def test_dependency_depth_and_cycles(page: Page) -> None:
    code = """
from shiny import reactive, render
@reactive.calc
def subtotal():
    return input.units() * input.price()
@reactive.calc
def discount_multiplier():
    return input.discount()
@reactive.calc
def total_revenue():
    return subtotal() * discount_multiplier()
@render.text
def result():
    return total_revenue()
"""
    report = generate_reactlog(code)
    page.set_content(format_reactlog_html(report, code))
    positions = page.locator(".graph-node").evaluate_all(
        "nodes => Object.fromEntries(nodes.map(n => [n.dataset.id, +n.querySelector('rect').getAttribute('x')]))"
    )
    assert positions["calc:total_revenue"] > positions["calc:subtotal"]
    assert positions["calc:total_revenue"] > positions["calc:discount_multiplier"]
    assert positions["output:result"] > positions["calc:total_revenue"]
    assert page.locator(".stage-label").count() == 0
    ranks = page.evaluate(
        "Object.fromEntries(dependencyRanks([{id:'a'}, {id:'b'}, {id:'c'}], [{from:'a',to:'b'}, {from:'b',to:'a'}, {from:'b',to:'c'}]))"
    )
    assert ranks["a"] == ranks["b"] < ranks["c"]


def test_module_toggle_preserves_boundary_edges(page: Page) -> None:
    code = """
from shiny import module, reactive, render
@module.server
def sales(input, output, session):
    @reactive.calc
    def total():
        return input.units()
    return total
def server(input, output, session):
    west = sales("west")
    east = sales("east")
    @render.text
    def combined():
        return west() + east()
"""
    page.set_content(format_reactlog_html(generate_reactlog(code), code))
    assert page.locator(".module-box").count() == 2
    page.locator('.module-box[data-module="west"] text').dblclick()
    expect(page.locator('.graph-node[data-id="module:west"]')).to_have_attribute(
        "aria-expanded", "false"
    )
    assert page.locator('.graph-node[data-id="calc:west-total"]').count() == 0
    assert (
        page.locator(
            '.graph-edge[data-from="module:west"][data-to="output:combined"]'
        ).count()
        == 1
    )
    assert page.locator('.graph-node[data-id="calc:east-total"]').count() == 1
    page.locator('.graph-node[data-id="module:west"]').dblclick()
    assert page.locator('.graph-node[data-id="calc:west-total"]').count() == 1
    page.locator('.module-box[data-module="west"]').focus()
    page.keyboard.press("Enter")
    assert page.locator('.graph-node[data-id="module:west"]').count() == 1
    page.locator('.graph-node[data-id="module:west"]').focus()
    page.keyboard.press("Space")
    assert page.locator('.module-box[data-module="west"]').count() == 1


def test_plot_preview_follows_timeline_without_future_images(page: Page) -> None:
    code = """
from shiny import render
@render.plot
def chart():
    return input.n()
"""
    src = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a7S8AAAAASUVORK5CYII="
    report = generate_reactlog(
        code,
        recorded_actions=[
            {
                "type": "output",
                "name": "chart",
                "timestamp": 1000,
                "plot": {"src": src, "alt": "First plot"},
            },
            {
                "type": "output",
                "name": "chart",
                "timestamp": 2000,
                "plot": {"src": src, "alt": "Updated plot"},
            },
        ],
    )
    steps = [i for i, e in enumerate(report["events"]) if e.get("plot")]
    page.set_content(format_reactlog_html(report, code))
    page.evaluate("selectNode('output:chart')")
    expect(page.locator("#insp-plot-image")).to_be_hidden()
    page.evaluate(f"seekTo({steps[0]})")
    expect(page.locator("#insp-plot-image")).to_be_visible()
    expect(page.locator("#insp-plot-image")).to_have_attribute("alt", "First plot")
    page.evaluate(f"seekTo({steps[1]})")
    expect(page.locator("#insp-plot-image")).to_have_attribute("alt", "Updated plot")
    page.evaluate("seekTo(0); selectNode('output:chart')")
    expect(page.locator("#insp-plot-image")).to_be_hidden()


def test_paused_video_seek_keeps_selected_plot_event(page: Page) -> None:
    code = """
from shiny import render
@render.plot
def chart():
    return input.n()
@render.text
def summary():
    return input.n()
"""
    report = generate_reactlog(
        code,
        recorded_actions=[
            {"type": "output", "name": "chart", "timestamp": 1000},
            {"type": "output", "name": "summary", "timestamp": 1000},
        ],
        video_path="recording.webm",
    )
    step = next(
        i for i, e in enumerate(report["events"]) if e["event"] == "outputUpdated"
    )
    page.set_content(format_reactlog_html(report, code))
    page.evaluate(
        f"seekTo({step}); document.getElementById('session-video').dispatchEvent(new Event('timeupdate'))"
    )
    expect(page.locator("#insp-title")).to_contain_text("output:chart")
    page.evaluate(
        "document.getElementById('session-video').dispatchEvent(new Event('seeked'))"
    )
    expect(page.locator("#insp-title")).to_contain_text("output:chart")


def test_imported_module_source_navigation(page: Page, tmp_path: Path) -> None:
    module_source = """from shiny import module, reactive
@module.server
def sales(input, output, session):
    @reactive.calc
    def revenue():
        return input.units() * 25
    return revenue
"""
    (tmp_path / "sales.py").write_text(module_source)
    code = """from sales import sales
from shiny import render
revenue = sales("west")
@render.text
def result():
    return revenue()
"""
    app = tmp_path / "app.py"
    app.write_text(code)
    report = generate_reactlog(code, source_path=app)
    page.set_content(format_reactlog_html(report, code))
    page.locator('.graph-node[data-id="calc:west-revenue"]').click()
    expect(page.locator("#insp-meta-line")).to_have_text("sales.py · Line 5")
    page.locator("#btn-toggle-source-drawer").click()
    expect(page.locator("#insp-source-code")).to_contain_text(
        "return input.units() * 25"
    )
    page.get_by_role("tab", name="App code").click()
    expect(page.get_by_label("Source file")).to_have_value("sales.py")
    expect(page.locator("#source-panel code")).to_contain_text(
        module_source.splitlines()[-1]
    )
    expect(page.locator("#source-panel .source-line.is-active")).to_contain_text(
        "def revenue():"
    )
    page.get_by_label("Source file").select_option("app.py")
    expect(page.locator("#source-panel code")).to_contain_text(
        "from sales import sales"
    )
    page.locator('.graph-node[data-id="output:result"]').click()
    expect(page.get_by_label("Source file")).to_have_value("app.py")
    expect(page.locator("#source-panel .source-line.is-active")).to_contain_text(
        "def result():"
    )
    page.evaluate("data => loadReactlogObject(data)", report)
    page.locator('.graph-node[data-id="calc:west-revenue"]').click()
    expect(page.get_by_label("Source file")).to_have_value("sales.py")


def test_source_highlighting_survives_file_switches_and_json_import(page: Page) -> None:
    sources = {
        "app.py": "from shiny import reactive\n# A comment\n@reactive.calc\ndef amount():\n    return 25 + 2\n",
        "module.py": '"""Module docs\nMore docs <img src=x onerror=alert(1)>\n"""\ndef label():\n    return "Revenue"\n',
    }
    report = generate_reactlog(sources["app.py"])
    report.update(sources=sources, entry_file="app.py")
    page.set_content(format_reactlog_html(report, sources["app.py"]))
    page.get_by_role("tab", name="App code").click()
    source = page.locator("#source-panel code")
    expect(source.locator(".syntax-keyword").first).to_have_text("from")
    expect(source.locator(".syntax-number").first).to_have_text("25")
    expect(source.locator(".syntax-comment")).to_have_text("# A comment")
    for theme in ("light", "dark"):
        page.locator("html").evaluate("(el, theme) => el.dataset.theme = theme", theme)
        assert source.locator(".syntax-keyword").first.evaluate(
            "(el) => getComputedStyle(el).color !== getComputedStyle(el.parentElement).color"
        )
    page.get_by_label("Source file").select_option("module.py")
    expect(source.locator(".source-line")).to_have_count(5)
    expect(source.locator('.source-line[data-line="2"] .syntax-string')).to_have_text(
        "More docs <img src=x onerror=alert(1)>"
    )
    expect(source.locator("img")).to_have_count(0)
    expect(source.locator('.source-line[data-line="4"] .syntax-keyword')).to_have_text(
        "def"
    )
    page.get_by_label("Source file").select_option("app.py")
    expect(source.locator(".syntax-keyword").first).to_have_text("from")
    # New source arriving through Open JSON must also be highlighted locally.
    replacement = dict(
        report,
        sources={"other.py": '# Imported\nvalue = "New file"\n'},
        entry_file="other.py",
    )
    page.evaluate("report => loadReactlogObject(report)", replacement)
    page.get_by_role("tab", name="App code").click()
    expect(source.locator(".syntax-comment")).to_have_text("# Imported")
    expect(source.locator(".syntax-string")).to_have_text('"New file"')


def test_inline_source_snippet_has_syntax_highlighting(page: Page) -> None:
    code = "from shiny import reactive\n@reactive.calc\ndef amount():\n    return input.units() * 25\n"
    page.set_content(format_reactlog_html(generate_reactlog(code), code))
    page.locator('.graph-node[data-id="calc:amount"]').click()
    page.locator("#btn-toggle-source-drawer").click()
    snippet = page.locator("#insp-source-code")
    expect(snippet.locator(".syntax-keyword").first).to_have_text("def")
    expect(snippet.locator(".syntax-number")).to_have_text("25")
    expect(snippet.locator(".source-line.is-active")).to_contain_text("def amount():")


def test_reactlog_keyboard_navigation_and_shortcuts_modal(page: Page) -> None:
    code = "from shiny.express import input, render\n@render.text\ndef out():\n    return f'{input.x()}'"
    rlog = generate_reactlog(
        code,
        recorded_actions=[
            {"type": "input", "name": "x", "value": 1, "timestamp": 10},
            {"type": "input", "name": "x", "value": 2, "timestamp": 20},
        ],
    )
    page.set_content(format_reactlog_html(rlog, code))

    modal = page.locator("#shortcuts-modal")
    expect(modal).to_be_hidden()

    page.keyboard.press("?")
    expect(modal).to_be_visible()

    page.keyboard.press("Escape")
    expect(modal).to_be_hidden()

    scrubber = page.locator("#scrubber-range")
    init_val = int(scrubber.input_value())
    page.keyboard.press("ArrowRight")
    assert int(scrubber.input_value()) == init_val + 1


def test_reactlog_isolated_edge_styling(page: Page) -> None:
    code = """from shiny import reactive
from shiny.express import input, render

@reactive.calc
def isolated_calc():
    with reactive.isolate():
        val = input.untracked()
    return val + input.tracked()

@render.text
def txt():
    return f"{isolated_calc()}"
"""
    rlog = generate_reactlog(code)
    page.set_content(format_reactlog_html(rlog, code))

    isolated_edges = page.locator(".graph-edge.is-isolated")
    expect(isolated_edges).to_have_count(1)
    expect(isolated_edges).to_have_attribute("stroke-dasharray", "5 4")
    expect(page.locator(".legend")).to_contain_text("Isolated read")


def test_reactlog_hotspot_badge(page: Page) -> None:
    code = """from shiny import reactive
from shiny.express import input, render

@reactive.calc
def compute():
    return input.val() * 2

@render.text
def txt():
    return f"{compute()}"
"""
    actions = [
        {"type": "input", "name": "val", "value": 1, "timestamp": 10},
        {"type": "input", "name": "val", "value": 2, "timestamp": 20},
        {"type": "input", "name": "val", "value": 3, "timestamp": 30},
        {"type": "input", "name": "val", "value": 4, "timestamp": 40},
    ]
    rlog = generate_reactlog(code, recorded_actions=actions)
    page.set_content(format_reactlog_html(rlog, code))

    badge = page.locator(
        '.graph-node[data-id="calc:compute"] .node-exec-badge.is-hotspot'
    )
    expect(badge).to_be_visible()
    expect(badge).to_contain_text("4×")
    expect(badge.locator("path")).to_be_visible()

    page.locator('.graph-node[data-id="calc:compute"]').click()
    expect(page.locator("#insp-runs-badge")).to_contain_text("Runs: 4×")
    expect(page.locator("#insp-runs-badge svg.flame-icon")).to_be_visible()
